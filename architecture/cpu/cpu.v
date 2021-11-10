`include "../../memory/register/register.v"
`include "../../memory/program_counter/program_counter.v"
`include "../../arithmetic/alu/alu.v"

module cpu(input clk,
           input[15:0] inM,
           input[15:0] instruction,
           input reset,
           output[15:0] outM,
           output writeM,
           output[15:0] addressM,
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
    assign addressM = reg_a_value;
    // writeM is decided based on the lines in the posedge.
    reg writeM_out;
    assign writeM = writeM_out;

    // Input to PC value is always from register A, but loading it in is
    // conditional as per below.
    assign pc_in = reg_a_value;

    always @(posedge(clk)) begin
        $display("--- %d ---", pc_value);
        $display("Register values: A=%d, D=%d", reg_a_value, reg_d_value);

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

        // Reset handling.
        if (reset) begin
            // Zero out A-register.
            reg_a_in_value <= 0;
            reg_a_load <= 1;

            $display("Resetting...");            
        // A-instruction handling.
        end else if (instruction[15] == 0) begin
            // Load A from the immediate value held in the lower 15 bits of
            // the instruction.
            reg_a_load <= 1;
            reg_a_in_value <= instruction[14:0];

            reg_d_load <= 0;
            writeM_out <= 0;
            $display("I am loading immediate %d into A", instruction[14:0]);
        // C-instruction handling.
        end else begin
            // Route destination bits from the instruction to appropriate load bits.
            reg_a_load <= instruction[5];
            reg_d_load <= instruction[4];
            writeM_out <= instruction[3];

            // Route input to A from the ALU for C-instructions.
            reg_a_in_value <= alu_output;

            $display("ALU control bits: zx=%b nx=%b zy=%b ny=%b f=%b no=%b", zx_alu, nx_alu, zy_alu, ny_alu, f_alu, no_alu);
            $display("ALU inputs: x=%d and y=%d, output=%d", alu_x, alu_y, alu_output);
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

    always @(negedge(clk)) begin
        if (pc_load) begin
            $display("Jump taken with jump type: %d!", instruction[2:0]);
        end
        //if (instruction[15] == 1) begin
        //end
        $display("negedge ALU inputs: x=%d and y=%d, output=%d", alu_x, alu_y, alu_output);
        $display("Register in    : A=%d, D=%d", reg_a_in_value, reg_d_in_value);
        $display("Loading A=%b, D=%b, M=%b", reg_a_load, reg_d_load, writeM_out);
    end
endmodule