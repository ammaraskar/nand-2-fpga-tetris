module not_16(output [15:0] Y, input [15:0] A);
    genvar i;
    generate
        for (i = 0; i < 16; i = i + 1) begin
            not_1 invert_bit(Y[i], A[i]);
        end
    endgenerate
endmodule
