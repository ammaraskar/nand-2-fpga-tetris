module ram16k(output [15:0] out,
              input clk,
              input [15:0] in_value,
              input wire load,
              input [13:0] address,
              input second_clk,
              input [13:0] second_address,
              output [15:0] second_out);

    parameter n = 14;
    reg [15:0] reg_array [(2**n)-1:0];

    reg[15:0] data;

    always @(posedge(clk)) begin
        data <= reg_array[address];
        if (load) begin
            reg_array[address] <= in_value;
        end
    end

    reg[15:0] second_data;
    always @(posedge(second_clk)) begin
        second_data <= reg_array[second_address];
    end

    assign out = data;
    assign second_out = second_data;
endmodule
