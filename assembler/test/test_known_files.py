import assembler
import pytest

import os
import sys
from pathlib import Path


TEST_DIR = Path(__file__).resolve().parent


@pytest.mark.parametrize("test_file", ["Add", "Max"])
def test_against_known_file(test_file):
    source_file = TEST_DIR / 'test_files' / (test_file + '.asm')
    expected_assembly = TEST_DIR / 'test_files' / (test_file + '.hack')

    with source_file.open() as f:
        source = f.read()

    with expected_assembly.open() as f:
        expected = f.read().splitlines()

    ast = assembler.parse_and_validate_ast(source)
    assert assembler.assemble_ast(ast) == expected
