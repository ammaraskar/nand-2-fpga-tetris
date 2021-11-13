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
%import common.CNAME -> NAME

%import common.WS
%ignore WS
%ignore COMMENT

// A type instructions
HEX_NUMBER: "0" "x" HEXDIGIT+
number: HEX_NUMBER -> hex_number
      | INT        -> decimal_number

// We use a := here to disambiguate between A=0 etc C-type instructions.
a_type_instruction: "A" ":=" number     -> a_const
                  | "A" ":=" ("@" NAME) -> a_label

// C type instructions

LOCATION: "A" | "D" | "*A"
BINARY_OPERATOR: "+" | "-" | "&" | "|"
UNARY_OPERATOR: "~" | "-"

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

label: NAME ":"

// Line either has an instruction or a label.
line: instruction
    | label

start: [line NEWLINE]*
""", propagate_positions=True, maybe_placeholders=True)


class ASTValidator(Transformer):
    def __init__(self):
        # Used to make sure every instruction label used in `A :=` is defined.
        self.instruction_labels = set()
        self.used_instruction_labels = []

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

    def a_label(self, items):
        (label, ) = items
        self.used_instruction_labels.append(label)

    def label(self, items):
        (label_name, ) = items
        self.instruction_labels.add(label_name)


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
        validator = ASTValidator()
        validator.transform(parsed)

        # Check for any missing labels.
        for label in validator.used_instruction_labels:
            if label in validator.instruction_labels:
                continue
            error = ValueError("Label {} used but never defined".format(label))
            raise VisitError('a_label', label, error)
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


@dataclass
class TypeAInstructionPlaceholder:
    """Used for when we do `A := @symbol` on an unresolved symbol. """
    label_name: str


class Assembler(Transformer):
    def __init__(self):
        super().__init__(self)
        self.instruction_labels = {}
        self.instruction_index = 0

    def NEWLINE(self, _):
        # Ignore new lines.
        raise lark.visitors.Discard()

    # Take the integer value of numbers.
    def decimal_number(self, items):
        (n, ) = items
        return int(n)
    def hex_number(self, items):
        (n, ) = items
        return int(n, 16)

    def instruction(self, items):
        # Increment the instruction index used to keep track of label values.
        self.instruction_index += 1
        (instr, ) = items
        return instr

    def label(self, items):
        (label_name, ) = items
        self.instruction_labels[label_name] = self.instruction_index
        return None

    def line(self, items):
        (line, ) = items
        # Discard because we don't actually want labels in the final transformation.
        # Instead, label information should be retrieved from
        # `assembler.instruction_labels`.
        if line is None:
            raise lark.visitors.Discard()
        return line

    def start(self, items):
        # Collect all instructions into a list.
        return list(items)

    def a_const(self, items):
        (constant, ) = items
        return '0' + format(constant, '015b')

    def a_label(self, items):
        (label, ) = items
        if label in self.instruction_labels:
            return self.a_const((self.instruction_labels[label], ))
        return TypeAInstructionPlaceholder(label_name=label)

    def a_type_instruction(self, items):
        (instr, ) = items
        return instr

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
        # same as the value (-x - 1)
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

    def single_register_operation(self, items):
        # Compute ~register or -register.
        # ~register is just done with ~(x & 0xFFFF) = ~x
        #
        # -register is computed with ~(x - 1)
        # This once again rlies on the fact that in two's complement negating
        # x is the same as (-x - 1)
        #   -x = ~(x - 1)
        #   -x = -(x - 1) - 1
        #   -x = -x + 1 - 1
        #   -x = -x
        (operator, register, ) = items

        control_bits = ALUControlBits.make_empty_alu_bits()
        instr = InstructionC(load_y_from_memory=False, alu_control_bits=control_bits)

        control_bits.negate_output = True
        if operator == '-':
            control_bits.perform_addition = True
        else:
            control_bits.perform_addition = False

        if register == '*A':
            instr.load_y_from_memory = True

        if register == 'A' or register == '*A':
            control_bits.zero_x = True
            control_bits.negate_x = True
        else:
            control_bits.zero_y = True
            control_bits.negate_y = True

        return instr

    def register_operation(self, items):
        # Handles operations between two different registers.
        (reg1, operator, reg2) = items

        control_bits = ALUControlBits.make_empty_alu_bits()
        instr = InstructionC(load_y_from_memory=False, alu_control_bits=control_bits)

        # Make sure it's reg2 that is register A or *A consistently for operators
        # that are commutative. 
        if operator != '-' and (reg1 == 'A' or reg1 == '*A'):
            reg1, reg2 = reg2, reg1

        # Set the memory load bit depending on whether we're using *A
        if '*A' in (reg1, reg2):
            instr.load_y_from_memory = True

        if operator == '+':
            # We use the adder circuit for +
            control_bits.perform_addition = True
        elif operator == '-':
            # Subtraction is implemented in a little funny way.using again, the
            # property that negation of x in two's complement is (-x - 1):
            #   y - x = ~(x + ~y)
            #         = ~(x - y - 1)
            #         = -(x - y - 1) - 1
            #         = -x + y + 1 - 1
            #         = y - x
            control_bits.perform_addition = True
            control_bits.negate_output = True
            # Here order actually matters.
            a_on_left = (reg1 == 'A' or reg1 == '*A')
            if a_on_left:
                control_bits.negate_y = True
            else:
                control_bits.negate_x = True
        elif operator == '&':
            # Simply use the AND circuit in the ALU.
            control_bits.perform_addition = False
        elif operator == '|':
            # We implement or using De Morgan's law
            # (x or y) = not(not x and not y)
            control_bits.negate_x = True
            control_bits.negate_y = True
            control_bits.perform_addition = False
            control_bits.negate_output = True

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
    assembler = Assembler()
    machine_code = assembler.transform(ast)

    # Perform a second pass over the list of machine code, substituting in any
    # undefined instruction labels for their real values.
    for i, instruction in enumerate(machine_code):
        if not isinstance(instruction, TypeAInstructionPlaceholder):
            continue
        symbol = assembler.instruction_labels[instruction.label_name]
        machine_code[i] = assembler.a_const((symbol, ))

    return machine_code
