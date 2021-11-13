import assembler
import pytest


def test_parses_a_basic_set_of_instruction():
    assembly = """\
// Load 123 into A
A := 123
// Copy to D
D = A
// Load memory, d and A with (A + 1)
A, D, *A = A + 1
D; jmp
"""
    assembler.parse_and_validate_ast(assembly)


def test_validation_fails_with_duplicate_assignment():
    assembly = "D, D, A = A"

    with pytest.raises(assembler.ValidationError) as excinfo:
        assembler.parse_and_validate_ast(assembly)

    assert "Duplicate assignment target, D already used" in str(excinfo.value)
    assert "D, D, A = A" in str(excinfo.value)
    assert "^^^^^^^^^" in str(excinfo.value)


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
    A := 0xFFFF
    """

    with pytest.raises(assembler.ValidationError) as excinfo:
        assembler.parse_and_validate_ast(assembly)

    assert "cannot fit in 15-bit immediate" in str(excinfo.value)
    assert "A := 0xFFFF" in str(excinfo.value)
    assert "     ^^^^^^" in str(excinfo.value)


def test_validation_fails_when_instruction_label_is_not_defined():
    assembly = """\
    A := 0
    A := @missing_label
    """

    with pytest.raises(assembler.ValidationError) as excinfo:
        assembler.parse_and_validate_ast(assembly)

    assert "Label missing_label used but never defined" in str(excinfo.value)
    assert "A := @missing_label" in str(excinfo.value)
    assert "      ^^^^^^^^^^^^^" in str(excinfo.value)
