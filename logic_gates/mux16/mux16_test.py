import cocotb
from cocotb.triggers import Timer
import random


@cocotb.test()
async def test_with_random_values(dut):
    for i in range(512):
        a = random.randint(0, 0xFFFF)
        b = random.randint(0, 0xFFFF)
        selector = random.randint(0, 1)

        await Timer(time=1)
        dut.A.value = a
        dut.B.value = b
        dut.selector.value = selector

        await Timer(time=1)
        if selector == 0:
            assert dut.Y.value == a
        else:
            assert dut.Y.value == b
