module program_counter(output [15:0] out,
                       input clk,
                       input [15:0] in_value,
                       input wire load,
                       input wire reset,
                       input wire increment);
    reg [15:0] counter;

    always @(posedge(clk)) begin
        if (reset) begin
            counter <= 0;
        end else if (load) begin
            counter <= in_value;
        end else if (increment) begin
            counter <= counter + 1;
        end
    end

    assign out = counter;
endmodule