`timescale 1ns / 1ps

`timescale 1ns/1ps
`include "memory.v"
`include "cpu.v"

module computer(input clk,
                input reset,
					 output[15:0] reg_d,
	             output HSync, output VSync,
	             output[1:0] Blue, output[2:0] Red, output[2:0] Green,
                input[5:0] Switch
					 );
	 // Video shit
	 wire clk_vga;
	 // Value retrieved from memory and fed to VGA module.
	 wire[15:0] vga_memory_in;
	 // Address to read memory for VGA module from.
	 wire[10:0] vga_memory_addr;
	 VGA vga(clk, vga_memory_in, vga_memory_addr, clk_vga, HSync, VSync, Blue, Red, Green);					 

    // Value retrieved from memory and fed to the CPU.
    wire[15:0] memory_out;
    // Value computed by the CPU and to be written into memory.
    wire[15:0] memory_in;
    // Whether to write `memory_in` to memory or not.
    wire memory_load;
    // The address to write `memory_in` to if `memory_load` is true.
    wire[14:0] memory_address;
    memory memory_unit(
        .out(memory_out), .clk(clk), 
        .in_value(memory_in), .load(memory_load), .address(memory_address),
        .second_clk(clk_vga), .second_address(vga_memory_addr), .second_out(vga_memory_in),
		  .Switch(Switch)
    );

    reg[15:0] instructions[65:0];
    initial begin
        $readmemb("program.hack", instructions, 0);
    end
	 
    wire[15:0] nextPC;
    reg[15:0] instruction;
    always @(negedge(clk)) begin
        instruction <= instructions[nextPC];
    end

    cpu cpu_unit(clk, memory_out, instruction, reset, 
                 memory_in, memory_load, memory_address, nextPC, reg_d);
endmodule
