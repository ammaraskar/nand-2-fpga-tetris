module or_2(output wire Y, input wire A, input wire B);
    wire APrime, BPrime;
    // Take the invert of the inputs
    not_1 invert_a(APrime, A);
    not_1 invert_b(BPrime, B);

    nand_2 output_combinator(Y, APrime, BPrime);
endmodule
