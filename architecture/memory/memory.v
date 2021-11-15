`timescale 1ns/1ps
`include "../../memory/ram16k/ram16k.v"

module memory(output [15:0] out,
              input clk,
              input [15:0] in_value,
              input wire load,
              input [14:0] address,
              input second_clk,
              input [14:0] second_address,
              output [15:0] second_out);
    // By convention, the bitmap for our 160*120 pixel screen which requires
    // 1200 16-bit values is held at:
    //   0x200 - 0x6B0 (512 - 1712)
    // Thus our memory map looks like:
    //     0x0 - 0x200   General Purpose RAM
    //   0x200 - 0x6B0   Video Bitmap
    //   0x6B0 - 0x800   General Purpose RAM
    ram16k ram(out, clk, in_value, load, address[13:0], second_clk, second_address, second_out);
endmodule