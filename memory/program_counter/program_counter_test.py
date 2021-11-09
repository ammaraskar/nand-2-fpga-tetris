import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge

@cocotb.test()
async def can_load_a_value(dut):
    cocotb.start_soon(Clock(dut.clk, 1, units="ns").start())

    dut.in_value.value = 0x1234
    dut.reset.value = 0
    dut.load.value = 1
    dut.increment.value = 0
    await FallingEdge(dut.clk)

    dut.in_value.value = 0
    dut.reset.value = 0
    dut.load.value = 0
    dut.increment.value = 0
    await FallingEdge(dut.clk)

    assert dut.out.value == 0x1234


@cocotb.test()
async def increments_from_a_point(dut):
    cocotb.start_soon(Clock(dut.clk, 1, units="ns").start())

    dut.in_value.value = 0x5
    dut.reset.value = 0
    dut.load.value = 1
    dut.increment.value = 0
    await FallingEdge(dut.clk)

    for i in range(10):
        dut.in_value.value = 0
        dut.reset.value = 0
        dut.load.value = 0
        dut.increment.value = 1

        assert dut.out.value == 0x5 + i
        await FallingEdge(dut.clk)

@cocotb.test()
async def rests_back_to_zero(dut):
    cocotb.start_soon(Clock(dut.clk, 1, units="ns").start())
    
    dut.in_value.value = 0x1234
    dut.reset.value = 0
    dut.load.value = 1
    dut.increment.value = 0
    await FallingEdge(dut.clk)

    dut.in_value.value = 0
    dut.reset.value = 0
    dut.load.value = 0
    dut.increment.value = 0
    await FallingEdge(dut.clk)

    dut.in_value.value = 0
    dut.reset.value = 1
    dut.load.value = 0
    dut.increment.value = 0
    await FallingEdge(dut.clk)

    assert dut.out.value == 0
