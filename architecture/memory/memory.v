`timescale 1ns/1ps
`include "../../memory/ram16k/ram16k.v"

module memory(output [15:0] out,
              input clk,
              input [15:0] in_value,
              input wire load,
              input [14:0] address);
    ram16k ram(out, clk, in_value, load, address[13:0]);
endmodule