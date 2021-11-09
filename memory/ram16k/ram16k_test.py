import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge
import random


@cocotb.test()
async def can_set_memory(dut):
    cocotb.start_soon(Clock(dut.clk, 1, units="ns").start())

    # Store 0xdead at address 1
    dut.in_value.value = 0xdead
    dut.load.value = 0
    dut.address.value = 1
    await FallingEdge(dut.clk)

    # Load from address 1
    dut.in_value.value = 0
    dut.load.value = 1
    dut.address.value = 1
    await FallingEdge(dut.clk)
    assert dut.out.value == 0xdead

@cocotb.test()
async def can_overwrite_memory(dut):
    cocotb.start_soon(Clock(dut.clk, 1, units="ns").start())

    # Store 0xdead at address 108
    dut.in_value.value = 0xdead
    dut.load.value = 0
    dut.address.value = 108
    await FallingEdge(dut.clk)

    # Store 0xbeef at address 108
    dut.in_value.value = 0xbeef
    dut.load.value = 0
    dut.address.value = 108
    await FallingEdge(dut.clk)

    # Load from address 1
    dut.in_value.value = 0
    dut.load.value = 1
    dut.address.value = 108
    await FallingEdge(dut.clk)
    assert dut.out.value == 0xbeef

@cocotb.test()
async def test_random_addresses(dut):
    cocotb.start_soon(Clock(dut.clk, 1, units="ns").start())

    # address -> data random mapping
    data = {}
    for _ in range(512):
        address = random.randint(0, 16383)
        value = random.randint(0, 0xFFFF)
        data[address] = value

    for address, value in data.items():
        dut.in_value.value = value
        dut.load.value = 0
        dut.address.value = address
        await FallingEdge(dut.clk)

    for address, value in data.items():
        dut.in_value.value = 0
        dut.load.value = 1
        dut.address.value = address
        await FallingEdge(dut.clk)
        assert dut.out.value == value
