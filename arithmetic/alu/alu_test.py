import cocotb
from cocotb.triggers import Timer
from collections import namedtuple
import random


COMPARISON_TABLE = """\
       x         |        y         |zx |nx |zy |ny | f |no |       out        |zr |ng
0000000000000000 | 1111111111111111 | 1 | 0 | 1 | 0 | 1 | 0 | 0000000000000000 | 1 | 0
0000000000000000 | 1111111111111111 | 1 | 1 | 1 | 1 | 1 | 1 | 0000000000000001 | 0 | 0
0000000000000000 | 1111111111111111 | 1 | 1 | 1 | 0 | 1 | 0 | 1111111111111111 | 0 | 1
0000000000000000 | 1111111111111111 | 0 | 0 | 1 | 1 | 0 | 0 | 0000000000000000 | 1 | 0
0000000000000000 | 1111111111111111 | 1 | 1 | 0 | 0 | 0 | 0 | 1111111111111111 | 0 | 1
0000000000000000 | 1111111111111111 | 0 | 0 | 1 | 1 | 0 | 1 | 1111111111111111 | 0 | 1
0000000000000000 | 1111111111111111 | 1 | 1 | 0 | 0 | 0 | 1 | 0000000000000000 | 1 | 0
0000000000000000 | 1111111111111111 | 0 | 0 | 1 | 1 | 1 | 1 | 0000000000000000 | 1 | 0
0000000000000000 | 1111111111111111 | 1 | 1 | 0 | 0 | 1 | 1 | 0000000000000001 | 0 | 0
0000000000000000 | 1111111111111111 | 0 | 1 | 1 | 1 | 1 | 1 | 0000000000000001 | 0 | 0
0000000000000000 | 1111111111111111 | 1 | 1 | 0 | 1 | 1 | 1 | 0000000000000000 | 1 | 0
0000000000000000 | 1111111111111111 | 0 | 0 | 1 | 1 | 1 | 0 | 1111111111111111 | 0 | 1
0000000000000000 | 1111111111111111 | 1 | 1 | 0 | 0 | 1 | 0 | 1111111111111110 | 0 | 1
0000000000000000 | 1111111111111111 | 0 | 0 | 0 | 0 | 1 | 0 | 1111111111111111 | 0 | 1
0000000000000000 | 1111111111111111 | 0 | 1 | 0 | 0 | 1 | 1 | 0000000000000001 | 0 | 0
0000000000000000 | 1111111111111111 | 0 | 0 | 0 | 1 | 1 | 1 | 1111111111111111 | 0 | 1
0000000000000000 | 1111111111111111 | 0 | 0 | 0 | 0 | 0 | 0 | 0000000000000000 | 1 | 0
0000000000000000 | 1111111111111111 | 0 | 1 | 0 | 1 | 0 | 1 | 1111111111111111 | 0 | 1
0000000000010001 | 0000000000000011 | 1 | 0 | 1 | 0 | 1 | 0 | 0000000000000000 | 1 | 0
0000000000010001 | 0000000000000011 | 1 | 1 | 1 | 1 | 1 | 1 | 0000000000000001 | 0 | 0
0000000000010001 | 0000000000000011 | 1 | 1 | 1 | 0 | 1 | 0 | 1111111111111111 | 0 | 1
0000000000010001 | 0000000000000011 | 0 | 0 | 1 | 1 | 0 | 0 | 0000000000010001 | 0 | 0
0000000000010001 | 0000000000000011 | 1 | 1 | 0 | 0 | 0 | 0 | 0000000000000011 | 0 | 0
0000000000010001 | 0000000000000011 | 0 | 0 | 1 | 1 | 0 | 1 | 1111111111101110 | 0 | 1
0000000000010001 | 0000000000000011 | 1 | 1 | 0 | 0 | 0 | 1 | 1111111111111100 | 0 | 1
0000000000010001 | 0000000000000011 | 0 | 0 | 1 | 1 | 1 | 1 | 1111111111101111 | 0 | 1
0000000000010001 | 0000000000000011 | 1 | 1 | 0 | 0 | 1 | 1 | 1111111111111101 | 0 | 1
0000000000010001 | 0000000000000011 | 0 | 1 | 1 | 1 | 1 | 1 | 0000000000010010 | 0 | 0
0000000000010001 | 0000000000000011 | 1 | 1 | 0 | 1 | 1 | 1 | 0000000000000100 | 0 | 0
0000000000010001 | 0000000000000011 | 0 | 0 | 1 | 1 | 1 | 0 | 0000000000010000 | 0 | 0
0000000000010001 | 0000000000000011 | 1 | 1 | 0 | 0 | 1 | 0 | 0000000000000010 | 0 | 0
0000000000010001 | 0000000000000011 | 0 | 0 | 0 | 0 | 1 | 0 | 0000000000010100 | 0 | 0
0000000000010001 | 0000000000000011 | 0 | 1 | 0 | 0 | 1 | 1 | 0000000000001110 | 0 | 0
0000000000010001 | 0000000000000011 | 0 | 0 | 0 | 1 | 1 | 1 | 1111111111110010 | 0 | 1
0000000000010001 | 0000000000000011 | 0 | 0 | 0 | 0 | 0 | 0 | 0000000000000001 | 0 | 0
0000000000010001 | 0000000000000011 | 0 | 1 | 0 | 1 | 0 | 1 | 0000000000010011 | 0 | 0"""

TableEntry = namedtuple('TableEntry', ['x', 'y', 'zx', 'nx', 'zy', 'ny', 'f', 'no', 'out', 'zr', 'ng'])
entries = []
for row in COMPARISON_TABLE.split('\n')[1:]:
    nums = []
    for num in row.split('|'):
        nums.append(int(num.strip(), 2))
    entries.append(TableEntry(*nums))


@cocotb.test()
async def test_table(dut):
    for entry in entries:
        await Timer(time=2)
        dut.x.value = entry.x
        dut.y.value = entry.y
        dut.zx.value = entry.zx
        dut.nx.value = entry.nx
        dut.zy.value = entry.zy
        dut.ny.value = entry.ny
        dut.f.value = entry.f
        dut.no.value = entry.no

        await Timer(time=2)
        assert dut.out.value == entry.out
        assert dut.zr.value == entry.zr
        assert dut.ng.value == entry.ng

@cocotb.test()
async def test_addition(dut):
    for i in range(512):
        a = random.randint(0, 0xFFFF)
        b = random.randint(0, 0xFFFF)

        sum = (a + b) & 0xFFFF

        await Timer(time=1)
        dut.x.value = a
        dut.y.value = b
        dut.zx.value = 0
        dut.nx.value = 0
        dut.zy.value = 0
        dut.ny.value = 0
        dut.f.value = 1
        dut.no.value = 0

        await Timer(time=1)
        assert dut.out.value == sum
        assert dut.zr.value == int(sum == 0)


@cocotb.test()
async def test_identity_y(dut):
    a = 0
    b = random.randint(0, 0xFFFF)

    dut.x.value = a
    dut.y.value = b
    dut.zx.value = 1
    dut.nx.value = 1
    dut.zy.value = 0
    dut.ny.value = 0
    dut.f.value = 0
    dut.no.value = 0

    await Timer(time=1)
    assert dut.out.value == b


@cocotb.test()
async def test_weird_cpu_case(dut):
    dut.x.value = 0
    dut.y.value = 12345
    dut.zx.value = 1
    dut.nx.value = 1
    dut.zy.value = 0
    dut.ny.value = 0
    dut.f.value = 0
    dut.no.value = 0

    await Timer(time=1)
    assert dut.out.value == 12345
