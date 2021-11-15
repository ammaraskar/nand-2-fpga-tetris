module VGAClock(input clk, input reset, output vga_clk);

   DCM_SP #(
      .CLKDV_DIVIDE(2.0), // Divide by: 1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0,5.5,6.0,6.5
                          //   7.0,7.5,8.0,9.0,10.0,11.0,12.0,13.0,14.0,15.0 or 16.0
      .CLKFX_DIVIDE(12),   // Can be any integer from 1 to 32
      .CLKFX_MULTIPLY(25), // Can be any integer from 2 to 32
      .CLKIN_DIVIDE_BY_2("FALSE"), // TRUE/FALSE to enable CLKIN divide by two feature
      .CLKIN_PERIOD(83.333),  // Specify period of input clock
      .CLKOUT_PHASE_SHIFT("NONE"), // Specify phase shift of NONE, FIXED or VARIABLE
      .CLK_FEEDBACK("1X"),  // Specify clock feedback of NONE, 1X or 2X
      .DESKEW_ADJUST("SYSTEM_SYNCHRONOUS"), // SOURCE_SYNCHRONOUS, SYSTEM_SYNCHRONOUS or
                                            //   an integer from 0 to 15
      .DLL_FREQUENCY_MODE("LOW"),  // HIGH or LOW frequency mode for DLL
      .DUTY_CYCLE_CORRECTION("TRUE"), // Duty cycle correction, TRUE or FALSE
      .PHASE_SHIFT(0),     // Amount of fixed phase shift from -255 to 255
      .STARTUP_WAIT("FALSE")   // Delay configuration DONE until DCM LOCK, TRUE/FALSE
   ) DCM_SP_inst (
      .CLK0(CLK0),     // 0 degree DCM CLK output
      .CLK180(CLK180), // 180 degree DCM CLK output
      .CLK270(CLK270), // 270 degree DCM CLK output
      .CLK2X(CLK2X),   // 2X DCM CLK output
      .CLK2X180(CLK2X180), // 2X, 180 degree DCM CLK out
      .CLK90(CLK90),   // 90 degree DCM CLK output
      .CLKDV(CLKDV),   // Divided DCM CLK out (CLKDV_DIVIDE)
      .CLKFX(vga_clk),   // DCM CLK synthesis out (M/D)
      .CLKFX180(CLKFX180), // 180 degree CLK synthesis out
      .LOCKED(LOCKED), // DCM LOCK status output
      .PSDONE(PSDONE), // Dynamic phase adjust done output
      .STATUS(STATUS), // 8-bit DCM status bits output
      .CLKFB(CLKFB),   // DCM clock feedback
      .CLKIN(clk),   // Clock input (from IBUFG, BUFG or DCM)
      .PSCLK(PSCLK),   // Dynamic phase adjust clock input
      .PSEN(PSEN),     // Dynamic phase adjust enable input
      .PSINCDEC(PSINCDEC), // Dynamic phase adjust increment/decrement
      .RST(reset)        // DCM asynchronous reset input
   );

endmodule
