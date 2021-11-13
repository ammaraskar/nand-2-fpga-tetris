`timescale 1ns/1ps
`include "../../memory/register/register.v"
`include "../../memory/program_counter/program_counter.v"
`include "../../arithmetic/alu/alu.v"

module cpu(input clk,
           input[15:0] inM,
           input[15:0] instruction,
           input reset,
           output[15:0] outM,
           output writeM,
           output[14:0] addressM,
           output[15:0] newPC);

    // Zero out everything initially.


    reg[15:0] pc_value;
    reg[15:0] pc_in;
    reg pc_load;
    reg pc_increment;
    program_counter pc(pc_value, clk, pc_in, pc_load, reset, pc_increment);

    assign newPC = pc_value;

    reg[15:0] reg_a_value;
    reg[15:0] reg_a_in_value;
    reg reg_a_load;
    register register_a(reg_a_value, clk, reg_a_in_value, reg_a_load);

    reg[15:0] reg_d_value;
    reg[15:0] reg_d_in_value;
    reg reg_d_load;
    register register_d(reg_d_value, clk, reg_d_in_value, reg_d_load);

    reg[15:0] alu_output;
    reg zr_status; reg ng_status;
    reg[15:0] alu_x;
    reg[15:0] alu_y;
    reg zx_alu; reg nx_alu;
    reg zy_alu; reg ny_alu;
    reg f_alu;
    reg no_alu;
    alu alu_unit(alu_output, zr_status, ng_status, alu_x, alu_y,
                 zx_alu, nx_alu, zy_alu, ny_alu, f_alu, no_alu);

    // Memory output takes input from the ALU.
    assign outM = alu_output;
    // A-register might take input from the ALU or immediate in the instruction,
    // that part is decided below.

    // Route control-bits from the instruction into the ALU.
    assign {zx_alu, nx_alu, zy_alu, ny_alu, f_alu, no_alu} = instruction[11:6];

    // Always route the D-register's value into ALU's input.
    assign alu_x = reg_d_value;

    // Make D-register take input from the ALU.
    assign reg_d_in_value = alu_output;

    // Memory address is always given by A register value.
    assign addressM = reg_a_value[14:0];

    // Handle the load register bits.
    assign reg_a_load = !instruction[15] || (instruction[15] && instruction[5]);
    assign reg_d_load = instruction[15] && instruction[4];
    assign writeM = instruction[15] && instruction[3];

    // Input to PC value is always from register A, but loading it in is
    // conditional as per below.
    assign pc_in = reg_a_value;

    // Register-A input is either taken as an immediate from the instruction
    // or the output of the ALU.
    reg[15:0] instruction_immediate;
    assign instruction_immediate[15] = 0;
    assign instruction_immediate[14:0] = instruction[14:0];
    assign reg_a_in_value = instruction[15] ? alu_output : instruction_immediate;

    always @(posedge(clk)) begin
        // Set PC to increment by default.
        pc_load <= 0;
        pc_increment <= 1;

        // Choose between memory value or A-register value depending on
        // bit 12 in the instruction.
        if (instruction[12] == 0) begin
            alu_y <= reg_a_value;
        end else begin
            alu_y <= inM;
        end

        // Check whether we are going jump or not.
        case (instruction[2:0])
            // No jump.
            3'b000: pc_load <= 0;
            // ALU out > 0
            3'b001: pc_load <= (!ng_status && !zr_status) && instruction[15];
            // ALU out = 0
            3'b010: pc_load <= (zr_status) && instruction[15];
            // ALU out >= 0
            3'b011: pc_load <= (zr_status || !ng_status) && instruction[15];
            // ALU out < 0
            3'b100: pc_load <= (ng_status) && instruction[15];
            // ALU out != 0
            3'b101: pc_load <= (!zr_status) && instruction[15];
            // ALU out <= 0
            3'b110: pc_load <= (ng_status || zr_status) && instruction[15];
            // Unconditional jump.
            3'b111: pc_load <= (1) && instruction[15];
        endcase
    end
endmodule
