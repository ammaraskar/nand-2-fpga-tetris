import cocotb
from cocotb.triggers import Timer
import random


@cocotb.test()
async def test_with_random_values(dut):
    for i in range(512):
        a = random.randint(0, 0xFFFF)
        b = random.randint(0, 0xFFFF)
        

        await Timer(time=1)
        dut.A.value = a
        dut.B.value = b

        await Timer(time=1)
        assert dut.Y.value == (a | b)
