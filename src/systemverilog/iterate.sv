module iterate (
    range_i.agent   i_range,
    value_i.host    i_iter
);

reg                     rst;
reg [i_range.WIDTH-1:0] remaining;
reg [i_iter.WIDTH-1:0]  iter;
reg                     valid;
reg                     last;

assign i_iter.clk   = i_range.clk;
assign i_iter.rst   = rst;
assign i_iter.valid = valid;
assign i_iter.data  = iter;
assign i_iter.last  = last;

always_ff @(posedge i_range.clk) begin

    rst <= i_range.rst;

    if (i_range.rst) begin

        remaining   <= 0;
        iter        <= 0;
        valid       <= 0;
        last        <= 0;

    end else begin
        if (i_iter.ready) begin

            remaining   <= (remaining != 0) ? remaining - 1'b1
                         : i_range.valid ? i_range.count - 1'b1
                         : 0;
            iter    <= (remaining != 0) ? iter + 1'b1
                     : i_range.valid ? i_range.start
                     : iter;
            valid   <= (remaining != 0) ? 1
                     : i_range.valid ? 1
                     : 0;
            last    <= (remaining == 0) ? 1 : 0;

        end else begin

            remaining   <= remaining;
            iter        <= iter;
            valid       <= valid;
            last        <= last;

        end
    end
end

endmodule
