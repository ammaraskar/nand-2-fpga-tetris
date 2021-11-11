`timescale 1ns/1ps
`include "../memory/memory.v"
`include "../cpu/cpu.v"

module computer(input clk, input reset);

    // Value retrieved from memory and fed to the CPU.
    reg[15:0] memory_out;
    // Value computed by the CPU and to be written into memory.
    reg[15:0] memory_in;
    // Whether to write `memory_in` to memory or not.
    reg memory_load;
    // The address to write `memory_in` to if `memory_load` is true.
    reg[14:0] memory_address;
    memory memory_unit(memory_out, clk, memory_in, memory_load, memory_address);

    reg[15:0] instructions[4095:0];
    reg[15:0] nextPC;
    reg[15:0] instruction;
    always @(negedge(clk)) begin
        instruction <= instructions[nextPC];
    end

    cpu cpu_unit(clk, memory_out, instruction, reset, 
                 memory_in, memory_load, memory_address, nextPC);
endmodule
