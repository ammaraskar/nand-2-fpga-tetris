module ram16k(output [15:0] out,
              input clk,
              input [15:0] in_value,
              input wire load,
              input [13:0] address);

    parameter n = 14;
    reg [15:0] reg_array [(2**n)-1:0];

    always @(posedge(clk)) begin
        if (load) begin
            reg_array[address] <= in_value;
        end
    end

    assign out = reg_array[address];
endmodule
