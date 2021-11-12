import assembler
import pytest


def test_parses_a_basic_set_of_instruction():
    assembly = """\
// Load 123 into A
A = 123
// Copy to D
D = A
// Load memory, d and A with (A + 1)
A, D, *A = A + 1
"""
    assembler.parse_and_validate_ast(assembly)


def test_validation_fails_with_using_a_and_memory():
    assembly = """\
    D = A + *A
    """

    with pytest.raises(assembler.ValidationError) as excinfo:
        assembler.parse_and_validate_ast(assembly)

    assert "Can't use both A and *A in ALU operation" in str(excinfo.value)
    assert "D = A + *A" in str(excinfo.value)
    assert "    ^^^^^^" in str(excinfo.value)


def test_validation_fails_with_loading_a_that_does_not_fit():
    assembly = """\
    A = 0xFFFF
    """

    with pytest.raises(assembler.ValidationError) as excinfo:
        assembler.parse_and_validate_ast(assembly)

    assert "Constant is too large (14 bits in immediate)" in str(excinfo.value)
    assert "A = 0xFFFF" in str(excinfo.value)
    assert "    ^^^^^^" in str(excinfo.value)
