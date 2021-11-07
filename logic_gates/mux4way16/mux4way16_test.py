import cocotb
from cocotb.triggers import Timer
import random


@cocotb.test()
async def test_with_random_values(dut):
    for i in range(512):
        a = random.randint(0, 0xFFFF)
        b = random.randint(0, 0xFFFF)
        c = random.randint(0, 0xFFFF)
        d = random.randint(0, 0xFFFF)
        selector = random.randint(0, 3)

        await Timer(time=1)
        dut.A.value = a
        dut.B.value = b
        dut.C.value = c
        dut.D.value = d
        dut.selector.value = selector

        await Timer(time=1)
        if selector == 0:
            assert dut.Y.value == a
        elif selector == 1:
            assert dut.Y.value == b
        elif selector == 2:
            assert dut.Y.value == c
        else:
            assert dut.Y.value == d
