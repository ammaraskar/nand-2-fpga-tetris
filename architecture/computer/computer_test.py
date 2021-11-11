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
0000000000000000  @0
1111110000010000  D = M
0000000000000001  @1
1111010011010000  D = D - M
0000000000001010  @OUTPUT_FIRST
1110001100000001  D; jgt
0000000000000001  @1
1111110000010000  D = M
0000000000001100  @OUTPUT_D
1110101010000111  0; jmp
0000000000000000  @0 (OUTPUT_FIRST)
1111110000010000  D = M
0000000000000010  @2 (OUTPUT_D)
1110001100001000  M = D
0000000000001110  @INFINITE_LOOP (INFINITE_LOOP)
1110101010000111  0; JMP
''')

    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    a = random.randint(-5000, 5000)
    b = random.randint(-5000, 5000)
    # Set up RAM[0] and RAM[1]
    dut.memory_unit.ram.reg_array[0].value = a
    dut.memory_unit.ram.reg_array[1].value = b

    # Reset the CPU.
    dut.reset.value = 1
    await FallingEdge(dut.clk)
    dut.reset.value = 0

    print("[SIMULATOR] Reseted")

    for i in range(15):
        await FallingEdge(dut.clk)
        await Timer(time=2, units="ns")
        #print("[SIMULATOR] State: instr={}, A={}, D={}, newPC={}, inM={}, outM={}, writeM={}".format(dut.cpu_unit.instruction.value, dut.cpu_unit.reg_a_value.value, dut.cpu_unit.reg_d_value.value, dut.cpu_unit.newPC.value.integer, dut.cpu_unit.inM.value, dut.cpu_unit.outM.value, dut.cpu_unit.writeM.value.integer))

    assert dut.memory_unit.ram.reg_array[2].value.signed_integer == max(a, b)

@cocotb.test()
async def can_deref_memory_into_register_a(dut):
    # Performs *(0) = 42;
    get_instructions(dut.instructions, '''\
0000000000101010  @42
1110110000010000  D = A
0000000000000000  @0
1111110000100000  A = M
1110001100001000  M = D
0000000000000101  @INFINITE_LOOP (INFINITE_LOOP)
1110101010000111  0; jmp
''')
    # Address to write 42 to
    dut.memory_unit.ram.reg_array[0].value = 3

    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    # Reset the CPU.
    dut.reset.value = 1
    await FallingEdge(dut.clk)
    await FallingEdge(dut.clk)
    dut.reset.value = 0

    print("[SIMULATOR] Reseted")

    for i in range(8):
        await FallingEdge(dut.clk)
        await Timer(time=2, units="ns")

    assert dut.memory_unit.ram.reg_array[3].value.signed_integer == 42

@cocotb.test()
async def runs_rect_program(dut):
    get_instructions(dut.instructions, '''\
0000000000000000  @0
1111110000010000  D = M
0000000000010111  @INFINITE_LOOP
1110001100000110  D; jle
0000000000010000  @counter
1110001100001000  M = D
0000100000000000  @SCREEN (Note I have altered where the screen is for now.)
1110110000010000  D = A
0000000000010001  @address
1110001100001000  M = D
0000000000010001  @address   (LOOP)
1111110000100000  A = M
1110111010001000  M = 0xFFFF
0000000000010001  @address
1111110000010000  D = M
0000000000100000  @32
1110000010010000  D = D + A
0000000000010001  @address
1110001100001000  M = D
0000000000010000  @counter
1111110010011000  MD = M - 1
0000000000001010  @LOOP
1110001100000001  D; jgt
0000000000010111  @INFINITE_LOOP (INFINITE_LOOP)
1110101010000111  0; jmp
''')
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    # Reset the CPU.
    dut.reset.value = 1
    await FallingEdge(dut.clk)
    dut.reset.value = 0

    print("[SIMULATOR] Reseted")
    # Number of rows to draw
    dut.cpu_unit.reg_d_value.value = 9
    dut.memory_unit.ram.reg_array[0].value = dut.cpu_unit.reg_d_value.value

    for i in range(2_000):
        await FallingEdge(dut.clk)
        await Timer(time=2, units="ns")
        #print("[SIMULATOR] State: {} A={}, D={}, newPC={}, inM={}, outM={}, addressM={}, writeM={}".format(dut.cpu_unit.instruction.value, dut.cpu_unit.reg_a_value.value.signed_integer, dut.cpu_unit.reg_d_value.value.signed_integer, dut.cpu_unit.newPC.value.integer, dut.cpu_unit.inM.value, dut.cpu_unit.outM.value.integer, dut.cpu_unit.addressM.value.integer, dut.cpu_unit.writeM.value.integer))

    for i in range(9):
        assert dut.memory_unit.ram.reg_array[2048 + 32*i].value.integer == 0xFFFF
