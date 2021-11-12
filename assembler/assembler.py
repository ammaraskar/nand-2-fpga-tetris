import lark
from lark import Lark, Transformer
from lark.exceptions import VisitError


parser = Lark(r"""
%import common.DIGIT -> DIGIT
%import common.HEXDIGIT -> HEXDIGIT
%import common.NEWLINE -> NEWLINE
%import common.CPP_COMMENT -> COMMENT

%import common.WS
%ignore WS
%ignore COMMENT

// A type instructions

DEC_NUMBER: DIGIT+
HEX_NUMBER: "0" "x" HEXDIGIT+
number: DEC_NUMBER  -> decimal_number
      | HEX_NUMBER  -> hex_number

a_type_instruction: "A" "=" number

// C type instructions

LOCATION: "A" | "D" | "*A"
BINARY_OPERATOR: "+" | "-" | "&" | "|"
UNARY_OPERATOR: "!" | "-"

computed_value: LOCATION                          -> single_register
              | LOCATION BINARY_OPERATOR LOCATION -> register_operation
              | UNARY_OPERATOR LOCATION           -> single_register_operation
              | LOCATION "+" "1"                  -> plus_one
              | LOCATION "-" "1"                  -> minus_one
              | "0"                               -> zero_const
              | "1"                               -> one_const
              | "-1"                              -> minus_one_const

assignment: LOCATION ("," LOCATION)* "="

JUMP: "jgt" | "jeq" | "jge" | "jlt" | "jne" | "jle" | "jmp"

// An optional assignment, followed by an ALU value, and then an optional jump
c_type_instruction: [assignment] computed_value [";" JUMP]

instruction: a_type_instruction
           | c_type_instruction

start: [instruction NEWLINE]*
""", propagate_positions=True)


class ASTValidator(Transformer):
    def validate_number(self, n):
        if n < -(2**14):
            raise ValueError("Constant is too small (15 bits in immediate)")
        if n > (2**14) - 1:
            raise ValueError("Constant is too large (15 bits in immediate)")

    def decimal_number(self, n):
        (n, ) = n
        n = int(n)
        self.validate_number(n)

    def hex_number(self, n):
        (n, ) = n
        n = int(n, 16)
        self.validate_number(n)

    def register_operation(self, items):
        (location_a, _, location_b) = items
        if 'A' in (location_a, location_b) and '*A' in (location_a, location_b):
            raise ValueError("Can't use both A and *A in ALU operation")


class ValidationError(Exception):
    def __init__(self, message, line, lineno, col_start, col_end):
        self.message = message
        self.line = line
        self.lineno = lineno
        self.col_start = col_start
        self.col_end = col_end

    def __str__(self):
        message =  '{} at line {} col {}:{}\n'.format(self.message, self.lineno, self.col_start, self.col_end)
        message += self.line + '\n'
        message += (' ' * (self.col_start - 1))
        message += ('^' * (self.col_end - self.col_start))
        return message


def parse_and_validate_ast(assembly):
    # Add a newline at the end if the input doesn't end in one.
    if not assembly.endswith('\n'):
        assembly += '\n'

    # Create a raw parse tree.
    parsed = parser.parse(assembly)
    # Run the validator on it.
    try:
        ASTValidator().transform(parsed)
    except VisitError as e:
        # Grab the line the error occured on.
        line = assembly.split('\n')[e.obj.line - 1]
        error = ValidationError(str(e.orig_exc), line, e.obj.line, e.obj.column, e.obj.end_column)
        # Raise from None so we avoid chaining the real error.
        raise error from None
    return parsed


class Assembler(Transformer):
    # Ignore new lines.
    def NEWLINE(self, _):
        raise lark.visitors.Discard()

    # Take the integer value of numbers.
    def decimal_number(self, items):
        (n, ) = items
        return int(n)

    def hex_number(self, items):
        (n, ) = items
        return int(n, 16)

    def a_type_instruction(self, items):
        (constant, ) = items
        return '0' + format(constant, '015b')

    def instruction(self, items):
        (instr, ) = items
        return instr

    def start(self, items):
        return list(items)


def assemble_ast(ast):
    machine_code = Assembler().transform(ast)
    return machine_code
