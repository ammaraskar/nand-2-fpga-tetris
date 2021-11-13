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
