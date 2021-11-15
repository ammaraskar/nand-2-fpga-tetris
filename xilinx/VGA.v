`include "VGAClock.v"

module VGA(input clk,
           output HSyncOut, output VSyncOut,
           output[1:0] Blue, output[2:0] Red, output[2:0] Green);
    wire clk_vga;
    VGAClock vga_clock(clk, reset, clk_vga);

    // constant declarations for VGA sync parameters
    localparam H_DISPLAY       = 640; // horizontal display area
    localparam H_L_BORDER      =  48; // horizontal left border
    localparam H_R_BORDER      =  16; // horizontal right border
    localparam H_RETRACE       =  96; // horizontal retrace
    localparam H_MAX           = H_DISPLAY + H_L_BORDER + H_R_BORDER + H_RETRACE - 1;
    localparam START_H_RETRACE = H_DISPLAY + H_R_BORDER;
    localparam END_H_RETRACE   = H_DISPLAY + H_R_BORDER + H_RETRACE - 1;
    
    localparam V_DISPLAY       = 480; // vertical display area
    localparam V_T_BORDER      =  10; // vertical top border
    localparam V_B_BORDER      =  33; // vertical bottom border
    localparam V_RETRACE       =   2; // vertical retrace
    localparam V_MAX           = V_DISPLAY + V_T_BORDER + V_B_BORDER + V_RETRACE - 1;
    localparam START_V_RETRACE = V_DISPLAY + V_B_BORDER;
    localparam END_V_RETRACE   = V_DISPLAY + V_B_BORDER + V_RETRACE - 1;
     
    reg[9:0] hcount = 0;
    reg[9:0] vcount = 0;

    // Negated because these are active-low.
    assign VSyncOut = !(vcount >= START_V_RETRACE && vcount <= END_V_RETRACE);
    assign HSyncOut = !(hcount >= START_H_RETRACE && hcount <= END_H_RETRACE);

    reg[1:0] blue_reg;
    reg[2:0] red_reg;
    reg[2:0] green_reg;

    always @(posedge clk_vga) begin
        if (hcount >= H_MAX) begin
            hcount <= 0;

            if (vcount >= V_MAX) begin
                vcount <= 0;
            end else begin
                vcount <= vcount + 1;
            end
        end else begin
            hcount <= hcount + 1;
        end

        if (hcount >= 20 && hcount <= 100) begin
            blue_reg <= 2'b11;
            red_reg <= 3'b000;
            green_reg <= 3'b000;
        end else if (hcount < H_DISPLAY && vcount < V_DISPLAY) begin
            blue_reg <= 2'b11;
            red_reg <= 3'b111;
            green_reg <= 3'b111;
        end else begin
            blue_reg <= 2'b00;
            red_reg <= 3'b000;
            green_reg <= 3'b000;            
        end
    end

    assign Blue = blue_reg;
    assign Red = red_reg;
    assign Green = green_reg;
endmodule
