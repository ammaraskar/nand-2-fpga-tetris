module mux_4_way_16(output [15:0] Y,
                    input [15:0] A,
                    input [15:0] B,
                    input [15:0] C,
                    input [15:0] D,
                    input [1:0] selector);
    reg [15:0] left;
    mux_16 left_mux(left, A, B, selector[0]);

    reg [15:0] right;
    mux_16 right_mux(right, C, D, selector[0]);

    mux_16 final_mux(Y, left, right, selector[1]);
endmodule
