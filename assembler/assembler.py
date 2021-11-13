import lark
from lark import Lark, Transformer
from lark.exceptions import VisitError
from dataclasses import dataclass


parser = Lark(r"""
%import common.DIGIT -> DIGIT
%import common.HEXDIGIT -> HEXDIGIT
%import common.INT -> INT
%import common.NEWLINE -> NEWLINE
%import common.CPP_COMMENT -> COMMENT

%import common.WS
%ignore WS
%ignore COMMENT

// A type instructions
HEX_NUMBER: "0" "x" HEXDIGIT+
number: HEX_NUMBER -> hex_number
      | INT        -> decimal_number

// We use a := here to disambiguate between A=0 etc C-type instructions.
a_type_instruction: "A" ":=" number

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
""", propagate_positions=True, maybe_placeholders=True)


class ASTValidator(Transformer):
    def validate_number(self, n):
        """Check if the number, as a short can be represented in 14 bits. """
        # Check the length of the binary representation of n.
        bitstring = bin(n)[2:]

        if len(bitstring) > 15:
            raise ValueError(
                "Constant ({}) cannot fit in 15-bit immediate".format(bitstring))

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

    def assignment(self, items):
        used_locations = set()
        for item in items:
            if item in used_locations:
                raise ValueError("Duplicate assignment target, {} already used".format(item))
            used_locations.add(item)


class ValidationError(Exception):
    def __init__(self, message, line, lineno, col_start, col_end):
        self.message = message
        self.line = line
        self.lineno = lineno
        self.col_start = col_start
        self.col_end = col_end

    def __str__(self):
        message =  '{} at line {} col {}:{}\n'.format(
            self.message, self.lineno, self.col_start, self.col_end)
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
        error = ValidationError(
            str(e.orig_exc), line, e.obj.line, e.obj.column, e.obj.end_column)
        # Raise from None so we avoid chaining the real error.
        raise error from None
    return parsed


@dataclass
class ALUControlBits:
    zero_x: bool
    negate_x: bool
    zero_y: bool
    negate_y: bool
    perform_addition: bool
    negate_output: bool

    @classmethod
    def make_empty_alu_bits(cls):
        return cls(zero_x=False, negate_x=False, zero_y=False, negate_y=False,
            perform_addition=False, negate_output=False)

    def get_bits(self):
        """Returns a bitstring of the control bits such as '000010'
        """
        bits = [self.zero_x, self.negate_x, self.zero_y, self.negate_y,
                self.perform_addition, self.negate_output]
        return ''.join(str(int(x)) for x in bits)


@dataclass
class InstructionC:
    load_y_from_memory: bool
    alu_control_bits: ALUControlBits

    def get_bits(self):
        """Gets bits 12 to 6 for a C-type instruction representing whether to
        load from memory and the ALU's control bits"""
        bits = '1' if self.load_y_from_memory else '0'
        bits += self.alu_control_bits.get_bits()
        return bits

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

    JUMP_TYPES = {
        'no_jump': '000',
        'jgt': '001',
        'jeq': '010',
        'jge': '011',
        'jlt': '100',
        'jne': '101',
        'jle': '110',
        'jmp': '111',
    }

    def JUMP(self, items):
        return Assembler.JUMP_TYPES[items]

    def assignment(self, items):
        load_a = 'A' in items
        load_d = 'D' in items
        load_a_star = '*A' in items

        load_bits = (load_a, load_d, load_a_star)
        return ''.join(str(int(x)) for x in load_bits)

    def single_register(self, items):
        (register, ) = items

        control_bits = ALUControlBits.make_empty_alu_bits()
        instr = InstructionC(load_y_from_memory=False, alu_control_bits=control_bits)

        # Perform (x & ~0) or (y & ~0) which simplify to
        # = (x & 0xFFFF), (y & 0xFFFF)
        # = x, y
        # respectively to just get the register values out of the ALU.
        # ALU input x is connected to register D.
        # ALU input y is connected to register A and memory.
        control_bits.perform_addition = False

        if register == 'A':
            instr.load_y_from_memory = False
            control_bits.zero_x = True
            control_bits.negate_x = True
        elif register == '*A':
            instr.load_y_from_memory = True
            control_bits.zero_x = True
            control_bits.negate_x = True
        else:
            control_bits.zero_y = True
            control_bits.negate_y = True

        return instr

    def zero_const(self, _):
        # Generate a zero out of the ALU by zero-ing out both inputs and
        # performing a x+y. (x & y could also be used here but this is what
        # the book uses so...)
        control_bits = ALUControlBits.make_empty_alu_bits()
        instr = InstructionC(load_y_from_memory=False, alu_control_bits=control_bits)

        control_bits.zero_x = True
        control_bits.zero_y = True
        control_bits.perform_addition = True

        return instr

    def one_const(self, _):
        # Generate a one out of the ALU in a rather fun way. We load in
        # 0xFFFF and 0xFFFF (all ones) into both ALU inputs. Now if we add
        # these we get 0xFFFE (1111...1110, all ones except the last bit).
        # Now, performing the negation of this gives us a 1 :)
        control_bits = ALUControlBits.make_empty_alu_bits()
        instr = InstructionC(load_y_from_memory=False, alu_control_bits=control_bits)

        control_bits.zero_x = True
        control_bits.negate_x = True
        control_bits.zero_y = True
        control_bits.negate_y = True
        control_bits.perform_addition = True
        control_bits.negate_output = True

        return instr

    def minus_one_const(self, _):
        # Generating a minus one is pretty easy. Just set one ALU inputs to
        # 0xFFFF, the other to 0 and then add them together.
        control_bits = ALUControlBits.make_empty_alu_bits()
        instr = InstructionC(load_y_from_memory=False, alu_control_bits=control_bits)

        control_bits.zero_x = True
        control_bits.negate_x = True
        control_bits.zero_y = True
        control_bits.perform_addition = True

        return instr

    def minus_one(self, items):
        # Perform register-1
        (register, ) = items      

        control_bits = ALUControlBits.make_empty_alu_bits()
        instr = InstructionC(load_y_from_memory=False, alu_control_bits=control_bits)

        # Subtracting 1 is simple, add -1 (0xFFFF in two's complement) to the
        # desired register.
        control_bits.perform_addition = True
        if register == 'A':
            instr.load_y_from_memory = False
            control_bits.zero_x = True
            control_bits.negate_x = True
        elif register == '*A':
            instr.load_y_from_memory = True
            control_bits.zero_x = True
            control_bits.negate_x = True
        else:
            control_bits.zero_y = True
            control_bits.negate_y = True
        return instr  

    def plus_one(self, items):
        # Perform register+1
        (register, ) = items

        control_bits = ALUControlBits.make_empty_alu_bits()
        instr = InstructionC(load_y_from_memory=False, alu_control_bits=control_bits)
        # We do this by taking the input register, negating it, adding -1/0xFFFF
        # and then negating the output. For example where x = 1:
        #   = ~(1111111111111110 + 1111111111111111)
        #   = ~(1111111111111110 + 1111111111111111)
        #   = ~(1111111111111101)
        #   =   0000000000000010 = 2
        # This works because in two's complement, negating a number x is the
        # same as (-x - 1)
        #   x + 1 = ~(~x + 0xFFFF)    <- Express ~x as -x - 1
        #   x + 1 = ~(-x - 1 - 1)     <- Simplify (- 1 - 1)
        #   x + 1 = ~(-x - 2)         <- Express ~(-x - 2) as -(-x - 2) - 1
        #   x + 1 = -(-x - 2) - 1
        #   x + 1 = x + 2 - 1
        #   x + 1 = x + 1
        control_bits.negate_output = True
        control_bits.perform_addition = True

        control_bits.negate_x = True
        control_bits.negate_y = True

        if register == 'A':
            instr.load_y_from_memory = False
            control_bits.zero_x = True
        elif register == '*A':
            instr.load_y_from_memory = True
            control_bits.zero_x = True
        else:
            control_bits.zero_y = True

        return instr

    def c_type_instruction(self, items):
        if items[0] is not None:
            assignment = items[0]
        else:
            # Assign nothing by default.
            assignment = '000'

        # Memory input and ALU bits given by middle part.
        instr = items[1]

        if items[2] is not None:
            jump = items[2]
        else:
            # Do not perform any jump by default.
            jump = Assembler.JUMP_TYPES['no_jump']

        return '111' + instr.get_bits() + assignment + jump


def assemble_ast(ast):
    machine_code = Assembler().transform(ast)
    return machine_code
