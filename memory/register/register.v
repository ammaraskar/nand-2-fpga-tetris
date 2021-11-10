module register(output [15:0] out,
                input clk,
                input [15:0] in_value,
                input wire load);
    reg [15:0] data;

    always @(negedge(clk)) begin
        if (load) begin
            data <= in_value;
        end
    end

    assign out = data;
endmodule