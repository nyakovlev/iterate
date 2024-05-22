from util import localize
localize("../../deps/avmm_i/src/cocotb/avmm_i.py")

from avmm_i import AvmmIAgent

import cocotb
from cocotb.binary import BinaryValue
from cocotb.triggers import Timer, FallingEdge
from host_bridge import HostBridge
import random
import inspect


def read(signal):
    value = signal.value
    if isinstance(value, BinaryValue): value = value.integer
    return value


@cocotb.test()
async def test_empty(tb):
    pass


@cocotb.test()
async def test_reset(tb):
    host_bridge = HostBridge(tb.u_dut)
    await host_bridge.reset(duration=10)
    await Timer(10, units='ns')


@cocotb.test()
async def test_root_signature(tb):
    root_addr = 0x0
    signature = 0xabba1234
    
    host_bridge = HostBridge(tb.u_dut)
    await host_bridge.reset(duration=10)

    value = await host_bridge.read_64(root_addr)
    host_bridge.log.info(f"0x{root_addr:016x}: 0x{value:016x}")
    assert hex(value & 0xffffffff) == hex(signature), "Signature not recognized"
    
    await Timer(10, units='ns')


@cocotb.test()
async def test_root_scratch(tb):
    scratch_addr = 0x18

    host_bridge = HostBridge(tb.u_dut)
    await host_bridge.reset(duration=10)

    value = await host_bridge.read_64(scratch_addr)
    host_bridge.log.info(f"0x{scratch_addr:016x}: 0x{value:016x}")
    assert hex(value) == hex(0x0), "Scratch does not initialize to 0"

    sample_value = random.randint(0x0, 0xffffffffffffffff)
    host_bridge.log.info(f"Testing scratch readback with: 0x{sample_value:x}")

    await host_bridge.write_64(scratch_addr, sample_value)
    value = await host_bridge.read_64(scratch_addr)
    host_bridge.log.info(f"0x{scratch_addr:016x}: 0x{value:016x}")
    assert hex(value) == hex(sample_value), "Scratch does not read back as expected"

    await Timer(10, units='ns')


@cocotb.test()
async def test_read_timeout(tb):
    invalid_addr = 0xa018
    invalid_value = 0xdeadffff
    
    host_bridge = HostBridge(tb.u_dut)
    await host_bridge.reset(duration=10)

    value = await host_bridge.read_64(invalid_addr)
    host_bridge.log.info(f"0x{invalid_addr:016x}: 0x{value:016x}")
    assert hex(value) == hex(invalid_value), "Timeout signature not recognized"
    
    await Timer(10, units='ns')


@cocotb.test()
async def test_command_loopback(tb):
    command_addr = 0x4_0000
    requests = []

    host_bridge = HostBridge(tb.u_dut)
    await host_bridge.reset(duration=10)
    
    # Assign ring address through page tree
    # ring_addr = 0x123456789abcdef0
    ring_addr = random.randint(0x0, 0xffffffffffffffff)
    ring_addr_config = 0x1020  # Page 0x1000, addr 0x20
    ring_index_addr  = 0x1028  # Page 0x1000, addr 0x28
    await host_bridge.write_64(ring_addr_config, ring_addr)
    ring_addr_readback = await host_bridge.read_64(ring_addr_config)
    assert hex(ring_addr_readback) == hex(ring_addr), "Ring address did not read back successfully"
    assert read(host_bridge.element.u_callback.i_page.ring_address) == ring_addr, "Ring address register does not reflect page write; perhaps the wrong address was targeted?"

    assert hex(await host_bridge.read_64(ring_index_addr)) == hex(0x1), "Ring index does not start at expected value"

    @host_bridge.u_pcie.i_bas.on_request
    def handle_bas(req):
        host_bridge.log.info(f"Got request: {req}")
        requests.append(req)

    await Timer(200, units='ns')  # TODO: determine if extent of backpressure is sensible

    async def ensure_bam_unblocked():
        bam = host_bridge.u_pcie.i_bam.element
        while 1:
            await FallingEdge(bam.clk)
            if (bam.waitrequest.value): raise Exception("BAM observed backpressure")
    bam_backpressure_monitor = cocotb.start_soon(ensure_bam_unblocked())

    await host_bridge.write_64(command_addr, 0x1234)
    await Timer(1, units='us')
    assert len(requests) > 0, "No callback to host bridge"
    assert len(requests) == 1, "Spurious BAS requests"
    req = requests[0]
    assert req.address == ring_addr, "BAS request did not target expected address"
    assert req.data == 0x1, "Callback ring index did not increment to expected value"

    bam_backpressure_monitor.kill()
    assert hex(await host_bridge.read_64(ring_index_addr)) == hex(0x2), "Ring index did not increment after invocation"
