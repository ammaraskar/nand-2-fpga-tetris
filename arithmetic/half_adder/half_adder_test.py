import cocotb
from cocotb.triggers import Timer
import random


@cocotb.test()
async def test_with_random_values(dut):
    for i in range(512):
        a = random.randint(0, 1)
        b = random.randint(0, 1)
        sum_bit = ((a + b) & 0b01) == 0b01
        carry_bit = ((a + b) & 0b10) == 0b10

        await Timer(time=1)
        dut.a.value = a
        dut.b.value = b

        await Timer(time=1)
        assert dut.sum.value == sum_bit
        assert dut.carry.value == carry_bit
