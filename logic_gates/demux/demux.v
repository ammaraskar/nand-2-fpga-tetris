module demux_2(output wire A, output wire B, input wire in_signal, input wire selector);
    wire selector_not;
    not_1 selecter_inverter(selector_not, selector);

    and_2 a_output(A, selector_not, in_signal);
    and_2 b_output(B, selector, in_signal);
endmodule
