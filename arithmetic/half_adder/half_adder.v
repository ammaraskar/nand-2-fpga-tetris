module half_adder(output wire carry,
                  output wire sum,
                  input wire a,
                  input wire b);
    assign carry = a & b;
    assign sum = a ^ b;
endmodule