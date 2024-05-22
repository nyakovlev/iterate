`timescale 1ps/1ps

module tb ();

    range_i i_range ();
    value_i i_iter  ();

    range_i_host_stub   i_range_stub    (.i_range(i_range));
    value_i_agent_stub  i_iter_stub     (.i_value(i_iter));

    iterate u_dut (
        i_range (i_range),
        i_iter  (i_iter)
    );

endmodule
