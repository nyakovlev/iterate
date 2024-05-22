from util import localize
localize("../../deps/pcie/src/cocotb/pcie.py")


from pcie import Pcie
import cocotb


class HostBridge:
    PIO_BYTE_WIDTH = 64

    def __init__(self, element):
        self.element = element
        self.log = cocotb.log
        self.u_pcie = Pcie(element.u_pcie)
    
    async def reset(self, duration=10):
        await self.u_pcie.i_bam.reset(duration=duration)
    
    async def read_64(self, address):
        shift = address % self.PIO_BYTE_WIDTH
        value = await self.u_pcie.i_bam.read(
            address     = (address // self.PIO_BYTE_WIDTH) * self.PIO_BYTE_WIDTH,
            byteenable  = 0xff << shift,
        )
        return value >> (shift * 8)
    
    async def write_64(self, address, value):
        shift = address % self.PIO_BYTE_WIDTH
        await self.u_pcie.i_bam.write(
            address     = (address // self.PIO_BYTE_WIDTH) * self.PIO_BYTE_WIDTH,
            byteenable  = 0xff << shift,
            data        = value << (shift * 8),
        )
