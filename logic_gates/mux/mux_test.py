import cocotb
from cocotb.triggers import Timer
from collections import namedtuple


TruthTableEntry = namedtuple('TruthTableEntry', ['a', 'b', 'selector', 'output'])

TRUTH_TABLE = [
    TruthTableEntry(a=0, b=0, selector=0, output=0),
    TruthTableEntry(a=0, b=1, selector=0, output=0),
    TruthTableEntry(a=1, b=0, selector=0, output=1),
    TruthTableEntry(a=1, b=1, selector=0, output=1),
    TruthTableEntry(a=0, b=0, selector=1, output=0),
    TruthTableEntry(a=0, b=1, selector=1, output=1),
    TruthTableEntry(a=1, b=0, selector=1, output=0),
    TruthTableEntry(a=1, b=1, selector=1, output=1),
]


@cocotb.test()
async def test_or_truth_table(dut):
    for entry in TRUTH_TABLE:
        await Timer(time=1)
        dut.A.value = entry.a
        dut.B.value = entry.b
        dut.selector.value = entry.selector

        await Timer(time=1)
        assert dut.Y.value == entry.output