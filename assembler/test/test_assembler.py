import assembler


def test_load_a_instruction():
    ast = assembler.parse_and_validate_ast('A := 3')
    assert assembler.assemble_ast(ast) == ['0000000000000011']

def test_load_a_instruction_with_largest_num():
    ast = assembler.parse_and_validate_ast('A := 0x7FFF')
    assert assembler.assemble_ast(ast) == ['0111111111111111']

def test_c_instruction_with_single_register_a():
    ast = assembler.parse_and_validate_ast('D = A')
    assert assembler.assemble_ast(ast) == ['1110110000010000']

def test_c_instruction_with_memory():
    ast = assembler.parse_and_validate_ast('A = *A')
    assert assembler.assemble_ast(ast) == ['1111110000100000']

def test_c_instruction_with_single_register_d():
    ast = assembler.parse_and_validate_ast('D, *A = D')
    assert assembler.assemble_ast(ast) == ['1110001100011000']

def test_c_instruction_with_constant_zero():
    ast = assembler.parse_and_validate_ast("D, *A, A = 0")
    assert assembler.assemble_ast(ast) == ['1110101010111000']

def test_c_instruction_with_constant_one():
    ast = assembler.parse_and_validate_ast("A = 1; jeq")
    assert assembler.assemble_ast(ast) == ['1110111111100010']

def test_c_instruction_with_constant_minus_one():
    ast = assembler.parse_and_validate_ast("D = -1; jle")
    assert assembler.assemble_ast(ast) == ['1110111010010110']

def test_c_instruction_with_a_plus_one():
    ast = assembler.parse_and_validate_ast("A, *A = A+1; jge")
    assert assembler.assemble_ast(ast) == ['1110110111101011']

def test_c_instruction_with_memory_plus_one():
    ast = assembler.parse_and_validate_ast("*A + 1; jlt")
    assert assembler.assemble_ast(ast) == ['1111110111000100']

def test_c_instruction_with_d_plus_one():
    ast = assembler.parse_and_validate_ast("D = D + 1; jne")
    assert assembler.assemble_ast(ast) == ['1110011111010101']

def test_c_instruction_with_a_minus_one():
    ast = assembler.parse_and_validate_ast("A = A - 1")
    assert assembler.assemble_ast(ast) == ['1110110010100000']

def test_c_instruction_with_memory_minus_one():
    ast = assembler.parse_and_validate_ast("*A = *A - 1")
    assert assembler.assemble_ast(ast) == ['1111110010001000']

def test_c_instruction_with_d_minus_one():
    ast = assembler.parse_and_validate_ast("D = D - 1")
    assert assembler.assemble_ast(ast) == ['1110001110010000']

