module mux_2(output wire Y, input wire A, input wire B, input wire selector);
    wire selector_not;
    not_1 selecter_inverter(selector_not, selector);

    wire A_and_not_selector;
    and_2 a_and(A_and_not_selector, A, selector_not);

    wire B_and_selector;
    and_2 b_and(B_and_selector, B, selector);

    or_2 output_or(Y, A_and_not_selector, B_and_selector);
endmodule
