module mux_16(output [15:0] Y, input [15:0] A, input [15:0] B, input wire selector);
    genvar i;
    generate
        for (i = 0; i < 16; i = i + 1) begin
            mux_2 mux_bit(Y[i], A[i], B[i], selector);
        end
    endgenerate
endmodule
