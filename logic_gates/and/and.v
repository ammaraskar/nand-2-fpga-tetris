module and_2(output wire Y, input wire A, input wire B);
    // Use a NAND on A and B.
    wire Yb;
    nand input_nand(Yb, A, B);

    // Invert its output to get an AND :)
    not(Y, Yb);
endmodule
