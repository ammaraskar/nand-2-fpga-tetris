import cocotb
from cocotb.triggers import Timer
from collections import namedtuple


TruthTableEntry = namedtuple('TruthTableEntry', ['input', 'selector', 'a', 'b'])

TRUTH_TABLE = [
    TruthTableEntry(input=0, selector=0, a=0, b=0),
    TruthTableEntry(input=0, selector=1, a=0, b=0),
    TruthTableEntry(input=1, selector=0, a=1, b=0),
    TruthTableEntry(input=1, selector=1, a=0, b=1),
]


@cocotb.test()
async def test_or_truth_table(dut):
    for entry in TRUTH_TABLE:
        await Timer(time=1)
        dut.in_signal.value = entry.input
        dut.selector.value = entry.selector

        await Timer(time=1)
        assert dut.A.value == entry.a
        assert dut.B.value == entry.b
