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

| # | Chapter               | Folder                           |
|---|-----------------------|----------------------------------|
| 1 | Boolean Logic         | [logic_gates/](./logic_gates/)   |
| 2 | Boolean Arithmetic    | [arithmetic/](./arithmetic/)     |
| 3 | Memory                | [memory/](./memory/)             |
| 4 | Machine Language      | (No hardware)                    |
| 5 | Computer Architecture | [architecture/](./architecture/) |
| 6 | Assembler             | [assembler/](./assembler/)       |

## Demo

Here is an assembly program running on an [Elbert V2](https://numato.com/product/elbert-v2-spartan-3a-fpga-development-board/)
dev board with a [Xilinx Spartan 3A](https://www.xilinx.com/products/silicon-devices/fpga/xa-spartan-3a.html) FPGA.

The 7-segment display is hooked up the to the D-register, and the CPU is clocked
at 12 Hz.

![Counter Program Demo](images/counter.gif)

Source Code:

```asm
start:
   // Initialize D to 9
   A := 9
   D = A
loop:
   D = D - 1
   A := @loop
   // If D is not zero, jump back up to loop
   D; jne

   // Jump back to start.
   A := @start
   0; jmp
```
