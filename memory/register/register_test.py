import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge
import random


@cocotb.test()
async def can_set_register(dut):
    cocotb.start_soon(Clock(dut.clk, 1, units="ns").start())

    # Store 0xdead
    dut.in_value.value = 0xdead
    dut.load.value = 1
    await FallingEdge(dut.clk)

    await RisingEdge(dut.clk)
    assert dut.out.value == 0xdead
    

@cocotb.test()
async def can_overwrite_register(dut):
    cocotb.start_soon(Clock(dut.clk, 1, units="ns").start())

    # Store 0xcafe
    dut.in_value.value = 0xcafe
    dut.load.value = 1
    await FallingEdge(dut.clk)

    # Store 0xbeef
    await RisingEdge(dut.clk)
    assert dut.out.value == 0xcafe

    dut.in_value.value = 0xbeef
    dut.load.value = 1
    await FallingEdge(dut.clk)

    await RisingEdge(dut.clk)
    assert dut.out.value == 0xbeef

    dut.in_value.value = 0
    dut.load.value = 0
    await FallingEdge(dut.clk)
    assert dut.out.value == 0xbeef

@cocotb.test()
async def test_random_values(dut):
    cocotb.start_soon(Clock(dut.clk, 1, units="ns").start())

    # Random data values
    random_values = [random.randint(0, 0xFFFF) for _ in range(512)]

    for i, data in enumerate(random_values):
        dut.in_value.value = data
        dut.load.value = 1
        await FallingEdge(dut.clk)

        await RisingEdge(dut.clk)
        assert dut.out.value == data
        dut.in_value.value = 0
        dut.load.value = 0


@cocotb.test()
async def test_latches_on_positive_edge(dut):
    cocotb.start_soon(Clock(dut.clk, 1, units="ns").start())

    dut.in_value.value = 0
    dut.load.value = 0

    await FallingEdge(dut.clk)
    await FallingEdge(dut.clk)

    await RisingEdge(dut.clk)
    dut.in_value.value = 101
    dut.load.value = 1
    await FallingEdge(dut.clk)
    await RisingEdge(dut.clk)

    assert dut.out.value == 101
