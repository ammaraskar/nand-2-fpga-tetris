module or_16(output [15:0] Y, input [15:0] A, input [15:0] B);
    genvar i;
    generate
        for (i = 0; i < 16; i = i + 1) begin
            or_2 or_bit(Y[i], A[i], B[i]);
        end
    endgenerate
endmodule
