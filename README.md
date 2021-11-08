# SystemVerilog Nand2Tetris

Nand2Tetris implemented in SystemVerilog intended to be used on an FPGA. This
is mostly me playing around with Verilog and FPGAs so don't use this seriously.

## Building and Testing

This project uses [Icarus Verilog](http://iverilog.icarus.com/) for simulation
and [cocotb](https://github.com/cocotb/cocotb) for verification.

Running `make` from the top-level directory should cause a build and all tests
to run. After the initial build, tests will run incrementally on changed
sources. `make test` can be used to always run all the tests.

## Structure

| # | Chapter            | Folder                         |
|---|--------------------|--------------------------------|
| 1 | Boolean Logic      | [logic_gates/](./logic_gates/) |
| 2 | Boolean Arithmetic | [arithmetic/](./arithmetic/)   |
