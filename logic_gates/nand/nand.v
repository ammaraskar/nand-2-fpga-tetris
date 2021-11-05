module nand_2(output wire Y, input wire A, input wire B);
    wire Yd;
    and(Yd, A, B);
    not(Y, Yd);
endmodule
