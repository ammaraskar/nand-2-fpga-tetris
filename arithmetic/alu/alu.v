module alu(output [15:0] out,
           output wire zr,
           output wire ng,
           input [15:0] x,
           input [15:0] y,
           input wire zx,
           input wire nx,
           input wire zy,
           input wire ny,
           input wire f,
           input wire no);
    reg signed[15:0] result;

    reg zero_flag;
    reg negative_flag;

    reg[15:0] x_actual;
    reg[15:0] y_actual;

    reg[15:0] and_result;
    reg signed[15:0] sum_result;

    always @* begin
        if (zx) begin
            x_actual = 0;
        end else begin
            x_actual = x;
        end

        if (nx) begin
            x_actual = ~x_actual;
        end

        if (zy) begin
            y_actual = 0;
        end else begin
            y_actual = y;
        end
        if (ny) begin
            y_actual = ~y_actual;
        end

        and_result = x_actual & y_actual;
        sum_result = x_actual + y_actual;
        if (no) begin
            and_result = ~and_result;
            sum_result = ~sum_result;
        end

        if (f) begin
            result = sum_result;
        end else begin
            result = and_result;
        end

        if (result == 0) begin
            zero_flag = 1;
        end else begin
            zero_flag = 0;
        end
        if (result[15] == 1) begin
            negative_flag = 1;
        end else begin
            negative_flag = 0;
        end
    end

    assign out = result;
    assign zr = zero_flag;
    assign ng = negative_flag;
endmodule