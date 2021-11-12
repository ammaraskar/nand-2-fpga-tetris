import assembler


def test_load_a_instruction():
    ast = assembler.parse_and_validate_ast('A = 3')
    assembly = assembler.assemble_ast(ast)

    assert assembly == ['0000000000000011']


def test_c_instruction_with_only_alu_output():
    ast = assembler.parse_and_validate_ast('A, *A, D = D; jmp')
    assembly = assembler.assemble_ast(ast)

    #assert assembly == ['0000000000000011']    
