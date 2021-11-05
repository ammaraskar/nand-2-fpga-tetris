import cocotb
from cocotb.triggers import Timer


# This is a dumb way to write these tests, parameterizing them would be better
# but this is just for fun :)

@cocotb.test()
async def test_nand_0(dut):
    dut.A.value = 0
    dut.B.value = 0

    await Timer(2, units='ns')

    assert dut.Y.value == 1

@cocotb.test()
async def test_nand_1(dut):
    dut.A.value = 0
    dut.B.value = 1

    await Timer(2, units='ns')

    assert dut.Y.value == 1

@cocotb.test()
async def test_nand_2(dut):
    dut.A.value = 1
    dut.B.value = 0

    await Timer(2, units='ns')

    assert dut.Y.value == 1

@cocotb.test()
async def test_nand_3(dut):
    dut.A.value = 1
    dut.B.value = 1

    await Timer(2, units='ns')

    assert dut.Y.value == 0
