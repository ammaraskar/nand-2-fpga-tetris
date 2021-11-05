module xor_2(output wire Y, input wire A, input wire B);
    wire or_inputs, nand_inputs;

    or_2 inputs_orred(or_inputs, A, B);
    nand_2 inputs_nanded(nand_inputs, A, B);

    and_2 output_combinator(Y, or_inputs, nand_inputs);
endmodule
