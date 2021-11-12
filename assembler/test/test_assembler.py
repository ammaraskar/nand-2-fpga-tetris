import assembler


def test_load_a_instruction():
    ast = assembler.parse_and_validate_ast('A = 3')
    assembly = assembler.assemble_ast(ast)

    assert assembly == ['0000000000000011']


def test_c_instruction_with_single_register_a():
    ast = assembler.parse_and_validate_ast('D = A')
    assert assembler.assemble_ast(ast) == ['1110110000010000']

def test_c_instruction_with_memory():
    ast = assembler.parse_and_validate_ast('A = *A')
    assert assembler.assemble_ast(ast) == ['1111110000100000']    

def test_c_instruction_with_single_register_d():
    ast = assembler.parse_and_validate_ast('D, *A = D')
    assert assembler.assemble_ast(ast) == ['1110001100011000']
