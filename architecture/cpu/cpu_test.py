import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge


@cocotb.test()
async def runs_some_basic_instructions(dut):
    cocotb.start_soon(Clock(dut.clk, 1, units="ns").start())

    # Reset the CPU.
    dut.reset.value = 1
    await FallingEdge(dut.clk)
    print("[SIMULATOR] Reseted")

    dut.inM.value = 0
    # @12345
    dut.instruction.value = 0b0011000000111001
    dut.reset.value = 0
    await FallingEdge(dut.clk)
    print("[SIMULATOR] First instruction executed")

    assert dut.newPC.value == 1
    assert dut.writeM.value == 0
    assert dut.reg_a_in_value.value == 12345

    # D = A
    dut.instruction.value = 0b1110110000010000
    await FallingEdge(dut.clk)
    print("[SIMULATOR] Second instruction executed")

    assert dut.newPC.value == 2
    assert dut.reg_a_value.value == 12345
    assert dut.reg_d_in_value.value == 12345

    # @23456
    dut.instruction.value = 0b0101101110100000
    await FallingEdge(dut.clk)

    assert dut.newPC.value == 3
    assert dut.reg_a_in_value.value == 23456

    # D = A - D
    dut.instruction.value = 0b1110000111010000
    await FallingEdge(dut.clk)

    assert dut.newPC.value == 4
    assert dut.reg_a_value.value == 23456
    assert dut.outM.value == 11111

    # @1000
    dut.instruction.value = 0b0000001111101000
    await FallingEdge(dut.clk)

    assert dut.newPC.value == 5
    assert dut.reg_d_value.value == 11111
    assert dut.reg_a_in_value.value == 1000

    # M = D
    dut.instruction.value = 0b1110001100001000
    await FallingEdge(dut.clk)

    assert dut.newPC.value == 6
    assert dut.writeM.value == 1
    assert dut.addressM.value == 1000
    assert dut.outM.value == 11111
