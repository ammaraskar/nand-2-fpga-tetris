module full_adder(output wire carry,
                  output wire sum,
                  input wire a,
                  input wire b,
                  input wire carryin);
    wire first_sum, first_carry;
    assign first_carry = a & b;
    assign first_sum = a ^ b;

    assign carry = first_carry | (first_sum & carryin);
    assign sum = first_sum ^ carryin;
endmodule