import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, Timer
from collections import namedtuple


@cocotb.test()
async def runs_some_basic_instructions(dut):
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # Reset the CPU.
    dut.reset.value = 1
    await FallingEdge(dut.clk)
    print("[SIMULATOR] Reseted")

    dut.inM.value = 0
    # @12345
    dut.instruction.value = 0b0011000000111001
    dut.reset.value = 0
    await FallingEdge(dut.clk)
    print("[SIMULATOR] First instruction executed")

    assert dut.newPC.value == 0
    assert dut.writeM.value == 0
    assert dut.reg_a_in_value.value == 12345

    # D = A
    dut.instruction.value = 0b1110110000010000
    await FallingEdge(dut.clk)
    print("[SIMULATOR] Second instruction executed")

    assert dut.newPC.value == 1
    assert dut.reg_a_value.value == 12345
    assert dut.reg_d_in_value.value == 12345

    # @23456
    dut.instruction.value = 0b0101101110100000
    await FallingEdge(dut.clk)

    assert dut.newPC.value == 2
    assert dut.reg_a_in_value.value == 23456

    # D = A - D
    dut.instruction.value = 0b1110000111010000
    await FallingEdge(dut.clk)

    assert dut.newPC.value == 3
    assert dut.reg_a_value.value == 23456
    assert dut.outM.value == 11111

    # @1000
    dut.instruction.value = 0b0000001111101000
    await FallingEdge(dut.clk)

    assert dut.newPC.value == 4
    assert dut.reg_d_value.value == 11111
    assert dut.reg_a_in_value.value == 1000

    # M = D
    dut.instruction.value = 0b1110001100001000
    await FallingEdge(dut.clk)

    assert dut.newPC.value == 5
    assert dut.writeM.value == 1
    assert dut.addressM.value == 1000
    assert dut.outM.value == 11111


TABLE = """\
time| inM  |  instruction   |reset| outM  |writeM |addre| pc  |DRegiste | instr
0+  |     0|0011000000111001|  0  |*******|   0   |    0|    0|      0  | @1234
1   |     0|0011000000111001|  0  |*******|   0   |12345|    1|      0  |
1+  |     0|1110110000010000|  0  |*******|   0   |12345|    1|      0  | D = A
2   |     0|1110110000010000|  0  |*******|   0   |12345|    2|  12345  |
2+  |     0|0101101110100000|  0  |*******|   0   |12345|    2|  12345  | @23456
3   |     0|0101101110100000|  0  |*******|   0   |23456|    3|  12345  |
3+  |     0|1110000111010000|  0  |*******|   0   |23456|    3|  12345  | D = A - D
4   |     0|1110000111010000|  0  |*******|   0   |23456|    4|  11111  | 
4+  |     0|0000001111101000|  0  |*******|   0   |23456|    4|  11111  | @1000
5   |     0|0000001111101000|  0  |*******|   0   | 1000|    5|  11111  |
5+  |     0|1110001100001000|  0  |  11111|   1   | 1000|    5|  11111  | M = D
6   |     0|1110001100001000|  0  |  11111|   1   | 1000|    6|  11111  |
6+  |     0|0000001111101001|  0  |*******|   0   | 1000|    6|  11111  | @1001
7   |     0|0000001111101001|  0  |*******|   0   | 1001|    7|  11111  |
7+  |     0|1110001110011000|  0  |  11110|   1   | 1001|    7|  11111  | M = D - 1
8   |     0|1110001110011000|  0  |  11109|   1   | 1001|    8|  11110  |
8+  |     0|0000001111101000|  0  |*******|   0   | 1001|    8|  11110  | @1000
9   |     0|0000001111101000|  0  |*******|   0   | 1000|    9|  11110  |
9+  | 11111|1111010011010000|  0  |*******|   0   | 1000|    9|  11110  | D = D - M
10  | 11111|1111010011010000|  0  |*******|   0   | 1000|   10|     -1  | 
10+ | 11111|0000000000001110|  0  |*******|   0   | 1000|   10|     -1  | @14
11  | 11111|0000000000001110|  0  |*******|   0   |   14|   11|     -1  |
11+ | 11111|1110001100000100|  0  |*******|   0   |   14|   11|     -1  | D; jlt
12  | 11111|1110001100000100|  0  |*******|   0   |   14|   14|     -1  |
12+ | 11111|0000001111100111|  0  |*******|   0   |   14|   14|     -1  | @999
13  | 11111|0000001111100111|  0  |*******|   0   |  999|   15|     -1  |
13+ | 11111|1110110111100000|  0  |*******|   0   |  999|   15|     -1  | A = A + 1
14  | 11111|1110110111100000|  0  |*******|   0   | 1000|   16|     -1  |
14+ | 11111|1110001100001000|  0  |     -1|   1   | 1000|   16|     -1  | M = D
15  | 11111|1110001100001000|  0  |     -1|   1   | 1000|   17|     -1  |
15+ | 11111|0000000000010101|  0  |*******|   0   | 1000|   17|     -1  | @21
16  | 11111|0000000000010101|  0  |*******|   0   |   21|   18|     -1  |
16+ | 11111|1110011111000010|  0  |*******|   0   |   21|   18|     -1  | D + 1; jeq
17  | 11111|1110011111000010|  0  |*******|   0   |   21|   21|     -1  |
17+ | 11111|0000000000000010|  0  |*******|   0   |   21|   21|     -1  | @2
18  | 11111|0000000000000010|  0  |*******|   0   |    2|   22|     -1  |
18+ | 11111|1110000010010000|  0  |*******|   0   |    2|   22|     -1  | D = D + A
19  | 11111|1110000010010000|  0  |*******|   0   |    2|   23|      1  |
19+ | 11111|0000001111101000|  0  |*******|   0   |    2|   23|      1  | @1000
20  | 11111|0000001111101000|  0  |*******|   0   | 1000|   24|      1  |
20+ | 11111|1110111010010000|  0  |*******|   0   | 1000|   24|      1  | D = -1
21  | 11111|1110111010010000|  0  |*******|   0   | 1000|   25|     -1  |
21+ | 11111|1110001100000001|  0  |*******|   0   | 1000|   25|     -1  | D; jgt
22  | 11111|1110001100000001|  0  |*******|   0   | 1000|   26|     -1  |
22+ | 11111|1110001100000010|  0  |*******|   0   | 1000|   26|     -1  | D; jeq
23  | 11111|1110001100000010|  0  |*******|   0   | 1000|   27|     -1  |
23+ | 11111|1110001100000011|  0  |*******|   0   | 1000|   27|     -1  | D; jge
24  | 11111|1110001100000011|  0  |*******|   0   | 1000|   28|     -1  |
24+ | 11111|1110001100000100|  0  |*******|   0   | 1000|   28|     -1  | D; jlt
25  | 11111|1110001100000100|  0  |*******|   0   | 1000| 1000|     -1  | 
25+ | 11111|1110001100000101|  0  |*******|   0   | 1000| 1000|     -1  | D; jne
26  | 11111|1110001100000101|  0  |*******|   0   | 1000| 1000|     -1  |
26+ | 11111|1110001100000110|  0  |*******|   0   | 1000| 1000|     -1  | D; jle
27  | 11111|1110001100000110|  0  |*******|   0   | 1000| 1000|     -1  |
27+ | 11111|1110001100000111|  0  |*******|   0   | 1000| 1000|     -1  | D; jmp
28  | 11111|1110001100000111|  0  |*******|   0   | 1000| 1000|     -1  |
28+ | 11111|1110101010010000|  0  |*******|   0   | 1000| 1000|      0  | D = 0
29  | 11111|1110101010010000|  0  |*******|   0   | 1000| 1001|      0  |
29+ | 11111|1110001100000001|  0  |*******|   0   | 1000| 1001|      0  | D; jgt
30  | 11111|1110001100000001|  0  |*******|   0   | 1000| 1002|      0  |
30+ | 11111|1110001100000010|  0  |*******|   0   | 1000| 1002|      0  | D; jeq
31  | 11111|1110001100000010|  0  |*******|   0   | 1000| 1000|      0  |
31+ | 11111|1110001100000011|  0  |*******|   0   | 1000| 1000|      0  | D; jge
32  | 11111|1110001100000011|  0  |*******|   0   | 1000| 1000|      0  |
32+ | 11111|1110001100000100|  0  |*******|   0   | 1000| 1000|      0  | D; jlt
33  | 11111|1110001100000100|  0  |*******|   0   | 1000| 1001|      0  |
33+ | 11111|1110001100000101|  0  |*******|   0   | 1000| 1001|      0  | D; jne
34  | 11111|1110001100000101|  0  |*******|   0   | 1000| 1002|      0  |
34+ | 11111|1110001100000110|  0  |*******|   0   | 1000| 1002|      0  | D; jle
35  | 11111|1110001100000110|  0  |*******|   0   | 1000| 1000|      0  |
35+ | 11111|1110001100000111|  0  |*******|   0   | 1000| 1000|      0  | D; jmp
36  | 11111|1110001100000111|  0  |*******|   0   | 1000| 1000|      0  |
36+ | 11111|1110111111010000|  0  |*******|   0   | 1000| 1000|      1  | D = 1
37  | 11111|1110111111010000|  0  |*******|   0   | 1000| 1001|      1  |
37+ | 11111|1110001100000001|  0  |*******|   0   | 1000| 1001|      1  | D; jgt
38  | 11111|1110001100000001|  0  |*******|   0   | 1000| 1000|      1  |
38+ | 11111|1110001100000010|  0  |*******|   0   | 1000| 1000|      1  | D; jeq
39  | 11111|1110001100000010|  0  |*******|   0   | 1000| 1001|      1  |
39+ | 11111|1110001100000011|  0  |*******|   0   | 1000| 1001|      1  | D; jge
40  | 11111|1110001100000011|  0  |*******|   0   | 1000| 1000|      1  |
40+ | 11111|1110001100000100|  0  |*******|   0   | 1000| 1000|      1  | D; jlt
41  | 11111|1110001100000100|  0  |*******|   0   | 1000| 1001|      1  |
41+ | 11111|1110001100000101|  0  |*******|   0   | 1000| 1001|      1  | D; jne
42  | 11111|1110001100000101|  0  |*******|   0   | 1000| 1000|      1  |
42+ | 11111|1110001100000110|  0  |*******|   0   | 1000| 1000|      1  | D; jle
43  | 11111|1110001100000110|  0  |*******|   0   | 1000| 1001|      1  |
43+ | 11111|1110001100000111|  0  |*******|   0   | 1000| 1001|      1  | D; jmp
44  | 11111|1110001100000111|  0  |*******|   0   | 1000| 1000|      1  |
44+ | 11111|1110001100000111|  1  |*******|   0   | 1000| 1000|      1  | RESET
45  | 11111|1110001100000111|  1  |*******|   0   | 1000|    0|      1  |
45+ | 11111|0111111111111111|  0  |*******|   0   | 1000|    0|      1  | @32767
46  | 11111|0111111111111111|  0  |*******|   0   |32767|    1|      1  |"""


TableEntry = namedtuple('TableEntry', ['time', 'inM', 'instruction', 'reset', 'outM', 'writeM', 'address', 'pc', 'd_register'])
entries = []
for row in TABLE.split('\n')[1:]:
    nums = []
    # We put the time value in to help with debugging failures.
    nums.append(row.split('|')[0].strip())
    for i, num in enumerate(row.split('|')[1:-1]):
        if '***' in num:
            nums.append(None)
        else:
            base = 2 if i == 1 else 10
            nums.append(int(num.strip(), base))
    entries.append(TableEntry(*nums))


@cocotb.test()
async def runs_according_to_table(dut):
    cocotb.start_soon(Clock(dut.clk, 20, units="ns").start())

    # Reset the CPU.
    dut.reset.value = 1
    dut.reg_d_value.value = 0
    dut.reg_a_value.value = 0
    await FallingEdge(dut.clk)
    await Timer(time=2, units="ns")
    print("[SIMULATOR] Reseted")

    for i, entry in enumerate(entries):
        dut.inM.value = entry.inM
        dut.instruction.value = entry.instruction
        dut.reset.value = entry.reset

        print("--- Executing ", end='')
        if i % 2 == 0:
            print("+")
            await RisingEdge(dut.clk)
        else:
            print("-")
            await FallingEdge(dut.clk)
        # Wait an additional 2ns for the values to stabilize.
        await Timer(time=2, units="ns")
        print("--- Execution Done ---")

        print("[SIMULATOR] State: A={}, D={}, newPC={}".format(dut.reg_a_value.value.signed_integer, dut.reg_d_value.value.signed_integer, dut.newPC.value.integer))

        # outM comparison
        if entry.outM:
            assert dut.outM.value.signed_integer == entry.outM
        # writeM comparison
        assert dut.writeM.value == entry.writeM
        # PC comparison
        assert dut.newPC.value == entry.pc
        # D-register comparison
        if dut.reg_d_value.value.is_resolvable:
            assert dut.reg_d_value.value.signed_integer == entry.d_register

        if i == 40:
            break
