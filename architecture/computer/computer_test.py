import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, Timer
from collections import namedtuple
import random


'''Takes a string representing instructions such as:

0000000000000010    @2
1110110000010000    D = A

and sets the instructions accordingly.
'''
def get_instructions(instructions, bitstring):
    for i, _ in enumerate(instructions):
        instructions[i].value = 0
    
    for i, instr in enumerate(bitstring.split('\n')):
        # Skip blank lines
        if not instr.strip():
            continue
        instructions[i].value = int(instr.split()[0], 2)


@cocotb.test()
async def runs_program_that_adds_two_numbers(dut):
    get_instructions(dut.instructions, '''\
0000000000000010   @2
1110110000010000   D = A
0000000000000011   @3
1110000010010000   D = D + A
0000000000000000   @0
1110001100001000   M = D
''')

    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # Reset the CPU.
    dut.reset.value = 1
    await FallingEdge(dut.clk)
    await FallingEdge(dut.clk)
    dut.reset.value = 0

    print("[SIMULATOR] Reseted")

    for i in range(7):
        await FallingEdge(dut.clk)
        await Timer(time=2, units="ns")

    assert dut.memory_unit.ram.reg_array[0].value.signed_integer == 5

@cocotb.test()
async def runs_program_that_maxes_two_numbers(dut):
    # Computes the max of two numbers stored in RAM[0], RAM[1] and stores the
    # result in RAM[2].
    get_instructions(dut.instructions, '''\
0000000000000010  @0
1111110000010000  D = M
0000000000000001  @1
1111010011010000  D = D - M
0000000000001010  @10
1110001100000001  D; jgt
0000000000000001  @1
1111110000010000  D = M
0000000000001100  @12
1110101010000111  0; jmp
0000000000000000  @0
1111110000010000  D = M
0000000000000010  @2
1110001100001000  M = D
0000000000001110  @14
1110101010000111  0; JMP
''')

    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    a = random.randint(-32768, 32767)
    b = random.randint(32767, 32767)
    # Set up RAM[0] and RAM[1]
    dut.memory_unit.ram.reg_array[0].value = a
    dut.memory_unit.ram.reg_array[1].value = b 

    # Reset the CPU.
    dut.reset.value = 1
    await FallingEdge(dut.clk)
    await FallingEdge(dut.clk)
    dut.reset.value = 0

    print("[SIMULATOR] Reseted")

    for i in range(100):
        await FallingEdge(dut.clk)
        await Timer(time=2, units="ns")

    assert dut.memory_unit.ram.reg_array[2].value.signed_integer == max(a, b)
