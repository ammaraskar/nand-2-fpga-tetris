import cocotb
from cocotb.triggers import Timer
import random


@cocotb.test()
async def test_with_random_values(dut):
    for i in range(512):
        value = random.randint(0, 0xFFFF)

        await Timer(time=1)
        dut.A.value = value

        await Timer(time=1)
        assert dut.Y.value == (~value & 0xFFFF)
