import cocotb
from cocotb.triggers import Timer
from collections import namedtuple


TruthTableEntry = namedtuple('TruthTableEntry', ['input', 'output'])

TRUTH_TABLE = [
    TruthTableEntry(input=0, output=1),
    TruthTableEntry(input=1, output=0),
]


@cocotb.test()
async def test_not_truth_table(dut):
    for entry in TRUTH_TABLE:
        await Timer(time=1)
        dut.A.value = entry.input

        await Timer(time=1)
        assert dut.Y.value == entry.output
