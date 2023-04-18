# IPP 2022/23
# Project 2 - Interpret of IPPcode23 XML representation
# Author: Matyas Strelec (xstrel03)

# ------------------–------------------–------------------–------------------–------------------ #

import argparse
import sys
import xml.etree.ElementTree as etree
from enum import Enum

# ------------------–------------------–------------------–------------------–------------------ #

# Main program class
class Prog:
    def __init__(self, input_file):
        self.gf = {}            # Global frame
        self.tf = None          # Temporary frame
        self.lf = []            # Local frame
        self.instructions = []
        self.current_instruction = 0
        self.stack = []         # Data stack
        self.labels = []
        self.callstack = []     # Call stack (for CALL and RETURN)
        self.input = input_file # Input file (for READ)

    # Start interpreting the program
    def run(self, instructions):
        self.instructions = instructions

        # Find all labels to prevent redefinition
        self._get_labels(self.instructions)

        self.current_instruction = 0
        while(self.current_instruction < len(instructions)):
            instructions[self.current_instruction].execute(self)
            self.current_instruction += 1

    # Get all labels from the program
    def _get_labels(self, instructions):
        for i in range(len(instructions)):
            if(instructions[i].opcode == 'LABEL'):
                if(instructions[i].args[0].data in self.labels):
                    Helper.error_exit("Label already defined", Errors.SEMANTIC_CHECKS.value, self)
                self.labels.append(instructions[i].args[0].data)

    # Find label index in the program for jumps and calls
    def find_label_index(self, label):
        for i in range(len(self.instructions)):
            if(self.instructions[i].opcode == 'LABEL' and self.instructions[i].args[0].data == label):
                return i
        return -1

    # Return value of variable or constant
    def get_symb(self, symb):
        # Find variable data in frames
        if(isinstance(symb, Var)):
            return self.read_var_obj(symb)
        # Get data from constant
        elif(isinstance(symb, Const)):
            return symb
        else:
            Helper.error_exit("Wrong argument type", Errors.WRONG_OPERAND_TYPE.value, self)

    # Define empty variable and check if it is not already defined
    def define_var(self, var):
        if(self._is_var_defined(var)):
            Helper.error_exit("Variable already defined", Errors.SEMANTIC_CHECKS.value, self)
        if(var.frame == 'GF'):
            self.gf[var.name] = Const(None)
        elif(var.frame == 'TF'):
            if(self.tf is not None):
                self.tf[var.name] = Const(None)
            else:
                Helper.error_exit("Frame not defined", Errors.NONEXISTENT_FRAME.value, self)
        elif(var.frame == 'LF'):
            if(len(self.lf) > 0):
                self.lf[-1][var.name] = Const(None)
            else:
                Helper.error_exit("Frame not defined", Errors.NONEXISTENT_FRAME.value, self)
        else:
            Helper.error_exit("Frame not defined", Errors.NONEXISTENT_FRAME.value, self)

    # Check if variable is defined in given frame
    def _is_var_defined(self, var):
        if(var.frame == 'GF'):
            if(var.name in self.gf):
                return True
            else:
                return False
        elif(var.frame == 'TF'):
            if(self.tf is not None):
                if(var.name in self.tf):
                    return True
                else:
                    return False
        elif(var.frame == 'LF'):
            if(len(self.lf) > 0):
                if(var.name in self.lf[-1]):
                    return True
                else:
                    return False
        return False

    # Read variable data from frame
    def read_from_var(self, var):
        if(var.frame == 'GF'):
            return self.gf[var.name].data
        elif(var.frame == 'TF'):
            if(self.tf is not None):
                return self.tf[var.name].data
            else:
                Helper.error_exit("Variable not defined", Errors.NONEXISTENT_VARIABLE.value, self)
        elif(var.frame == 'LF'):
            if(len(self.lf) > 0):
                return self.lf[-1][var.name].data
            else:
                Helper.error_exit("Variable not defined", Errors.NONEXISTENT_VARIABLE.value, self)
            Helper.error_exit("Variable not defined", Errors.NONEXISTENT_VARIABLE.value, self)
        else:
            Helper.error_exit("Frame not defined", Errors.NONEXISTENT_FRAME.value, self)

    # Read variable (the object) from frame
    def read_var_obj(self, var):
        if(var.frame == 'GF'):
            if(self._is_var_defined(var)):
                return self.gf[var.name]
            else:
                Helper.error_exit("Variable not defined", Errors.NONEXISTENT_VARIABLE.value, self)
        elif(var.frame == 'TF'):
            if(self.tf is not None):
                if(self._is_var_defined(var)):
                    return self.tf[var.name]
                else:
                    Helper.error_exit("Variable not defined", Errors.NONEXISTENT_VARIABLE.value, self)
            else:
                Helper.error_exit("Frame not defined", Errors.NONEXISTENT_FRAME.value, self)
        elif(var.frame == 'LF'):
            if(len(self.lf) > 0):
                if(self._is_var_defined(var)):
                    return self.lf[-1][var.name]
                else:
                    Helper.error_exit("Variable not defined", Errors.NONEXISTENT_VARIABLE.value, self)
            else:
                Helper.error_exit("Frame not defined", Errors.NONEXISTENT_FRAME.value, self)
        else:
            Helper.error_exit("Frame not defined", Errors.NONEXISTENT_FRAME.value, self)

    # Write data to variable
    def write_to_var(self, var, data):
        if(var.frame == 'GF'):
            if(self._is_var_defined(var)):
                self.gf[var.name] = data
                return
            else:
                Helper.error_exit("Variable not defined", Errors.NONEXISTENT_VARIABLE.value, self)
        elif(var.frame == 'TF'):
            if(self.tf is not None):
                if(self._is_var_defined(var)):
                    self.tf[var.name] = data
                    return
                else:
                    Helper.error_exit("Variable not defined", Errors.NONEXISTENT_VARIABLE.value, self)
            else:
                Helper.error_exit("Frame not defined", Errors.NONEXISTENT_FRAME.value, self)
        elif(var.frame == 'LF'):
            if(len(self.lf) > 0):
                if(self._is_var_defined(var)):
                    self.lf[-1][var.name] = data
                    return
                else:
                    Helper.error_exit("Frame not defined", Errors.NONEXISTENT_FRAME.value, self)
            else:
                Helper.error_exit("Frame not defined", Errors.NONEXISTENT_FRAME.value, self)
        else:
            Helper.error_exit("Variable not defined", Errors.NONEXISTENT_VARIABLE.value, self)


# ------------------–------------------–------------------–------------------–------------------ #

# Arguments
class Arg:
    def __init__(self):
        pass

# Symbol (variable or constant)
class Symb(Arg):
    def __init__(self, data):
        self.data = data

# Variable, is in given frame, has name, and data
class Var(Symb):
    def __init__(self, frame, name, data):
        self.frame = frame
        self.name = name
        self.data : Const = data

# Constant, only has data
class Const(Symb):
    def __init__(self, data):
        self.data = data

# Constants of different types
class Int(Const):
    def __init__(self, data: int):
        self.data = data

class String(Const):
    def __init__(self, data: str):
        self.data = data

class Bool(Const):
    def __init__(self, data: bool):
        self.data = data

class Nil(Const):
    def __init__(self):
        self.data = 'nil'

# Label is a special type, only has name
class Label(Arg):
    def __init__(self, name):
        self.data = name

# Type is a special type, only has type
class Type(String):
    def __init__(self, type):
        self.data = type

# ------------------–------------------–------------------–------------------–------------------ #

class Instruction:
    def __init__(self, opcode, args, program: Prog):
        self.opcode = opcode
        self.args = args
        self.program = program

    def get_arg1(self):
        return self.args[0]

    def get_arg2(self):
        return self.args[1]

    def get_arg3(self):
        return self.args[2]

    def execute(self, program: Prog):
        pass


class MOVE(Instruction):
    def execute(self, program):
        var = self.get_arg1()
        symb = self.get_arg2()

        val = program.get_symb(symb)

        program.write_to_var(var, val)

class CREATEFRAME(Instruction):
    def execute(self, program):
        program.tf = {}

class PUSHFRAME(Instruction):
    def execute(self, program):
        if(program.tf is not None):
            program.lf.append(program.tf)
            program.tf = None
        else:
            Helper.error_exit("Temporary frame is empty", Errors.NONEXISTENT_FRAME.value, program)

class POPFRAME(Instruction):
    def execute(self, program):
        if(len(program.lf) > 0):
            program.tf = program.lf.pop()
        else:
            Helper.error_exit("Local frame is empty", Errors.NONEXISTENT_FRAME.value, program)

class DEFVAR(Instruction):
    def execute(self, program):
        var = self.get_arg1()
        program.define_var(var)

class CALL(Instruction):
    def execute(self, program):
        label = self.get_arg1()

        index = program.find_label_index(label.data)
        if(index != -1):
            program.callstack.append(program.current_instruction)
            program.current_instruction = index
        else:
            Helper.error_exit("Label not found", Errors.SEMANTIC_CHECKS.value, program)

class RETURN(Instruction):
    def execute(self, program):
        if(len(program.callstack) > 0):
            index = program.callstack.pop()
            program.current_instruction = index
        else:
            Helper.error_exit("Empty callstack", Errors.MISSING_VALUE.value, program)

class PUSHS(Instruction):
    def execute(self, program):
        symb1 = self.get_arg1()

        operand1 = program.get_symb(symb1)

        program.stack.append(operand1)


class POPS(Instruction):
    def execute(self, program):
        var = self.get_arg1()

        if(len(program.stack) > 0):
            operand1 = program.stack.pop()
        else:
            Helper.error_exit("Empty stack", Errors.MISSING_VALUE.value, program)

        program.write_to_var(var, operand1)

class ADD(Instruction):
    def execute(self, program):
        var = self.get_arg1()
        symb1 = self.get_arg2()
        symb2 = self.get_arg3()

        operand1 = program.get_symb(symb1)
        operand2 = program.get_symb(symb2)

        val1 = operand1.data
        val2 = operand2.data

        if(isinstance(operand1, Int) and isinstance(operand2, Int)):
            program.write_to_var(var, Int(val1 + val2))
        else:
            Helper.error_exit("Wrong operands", Errors.WRONG_OPERAND_TYPE.value, program)

class SUB(Instruction):
    def execute(self, program):
        var = self.get_arg1()
        symb1 = self.get_arg2()
        symb2 = self.get_arg3()

        operand1 = program.get_symb(symb1)
        operand2 = program.get_symb(symb2)

        val1 = operand1.data
        val2 = operand2.data

        if(isinstance(operand1, Int) and isinstance(operand2, Int)):
            program.write_to_var(var, Int(val1 - val2))
        else:
            Helper.error_exit("Wrong operands", Errors.WRONG_OPERAND_TYPE.value, program)

class MUL(Instruction):
    def execute(self, program):
        var = self.get_arg1()
        symb1 = self.get_arg2()
        symb2 = self.get_arg3()

        operand1 = program.get_symb(symb1)
        operand2 = program.get_symb(symb2)

        val1 = operand1.data
        val2 = operand2.data

        if(isinstance(operand1, Int) and isinstance(operand2, Int)):
            program.write_to_var(var, Int(val1 * val2))
        else:
            Helper.error_exit("Wrong operands", Errors.WRONG_OPERAND_TYPE.value, program)


class IDIV(Instruction):
    def execute(self, program):
        var = self.get_arg1()
        symb1 = self.get_arg2()
        symb2 = self.get_arg3()

        operand1 = program.get_symb(symb1)
        operand2 = program.get_symb(symb2)

        val1 = operand1.data
        val2 = operand2.data

        if(isinstance(operand2, Int) and val2 == 0):
            Helper.error_exit("Division by zero", Errors.WRONG_OPERANT_VALUE.value, program)

        if(isinstance(operand1, Int) and isinstance(operand2, Int)):
            program.write_to_var(var, Int(val1 // val2))
        else:
            Helper.error_exit("Wrong operands", Errors.WRONG_OPERAND_TYPE.value, program)


class LT(Instruction):
    def execute(self, program):
        var = self.get_arg1()
        symb1 = self.get_arg2()
        symb2 = self.get_arg3()

        operand1 = program.get_symb(symb1)
        operand2 = program.get_symb(symb2)

        val1 = operand1.data
        val2 = operand2.data

        if(isinstance(operand1, Nil) or isinstance(operand2, Nil)):
            Helper.error_exit("Wrong operands", Errors.WRONG_OPERAND_TYPE.value, program)

        if((isinstance(operand1, Int) and isinstance(operand2, Int)) or
           (isinstance(operand1, String) and isinstance(operand2, String))):
            program.write_to_var(var, Bool(bool(val1 < val2)))
        elif(isinstance(operand1, Bool) and isinstance(operand2, Bool)):
            val1, val2 = int(val1), int(val2)
            program.write_to_var(var, Bool(bool(val1 < val2)))
        else:
            Helper.error_exit("Wrong operands", Errors.WRONG_OPERAND_TYPE.value, program)

class GT(Instruction):
    def execute(self, program):
        var = self.get_arg1()
        symb1 = self.get_arg2()
        symb2 = self.get_arg3()

        operand1 = program.get_symb(symb1)
        operand2 = program.get_symb(symb2)

        val1 = operand1.data
        val2 = operand2.data

        if(isinstance(operand1, Nil) or isinstance(operand2, Nil)):
            Helper.error_exit("Wrong operands", Errors.WRONG_OPERAND_TYPE.value, program)

        if((isinstance(operand1, Int) and isinstance(operand2, Int)) or
           (isinstance(operand1, String) and isinstance(operand2, String))):
            program.write_to_var(var, Bool(bool(val1 > val2)))
        elif(isinstance(operand1, Bool) and isinstance(operand2, Bool)):
            val1, val2 = int(val1), int(val2)
            program.write_to_var(var, Bool(bool(val1 > val2)))
        else:
            Helper.error_exit("Wrong operands", Errors.WRONG_OPERAND_TYPE.value, program)

class EQ(Instruction):
    def execute(self, program):
        var = self.get_arg1()
        symb1 = self.get_arg2()
        symb2 = self.get_arg3()

        operand1 = program.get_symb(symb1)
        operand2 = program.get_symb(symb2)

        val1 = operand1.data
        val2 = operand2.data

        if(isinstance(operand1, Nil) or isinstance(operand2, Nil)):
            if(isinstance(operand1, Nil) and isinstance(operand2, Nil)):
                program.write_to_var(var, Bool(True))
            else:
                program.write_to_var(var, Bool(False))
        elif((isinstance(operand1, Int) and isinstance(operand2, Int)) or
           (isinstance(operand1, String) and isinstance(operand2, String))):
            program.write_to_var(var, Bool(bool(val1 == val2)))
        elif(isinstance(operand1, Bool) and isinstance(operand2, Bool)):
            val1, val2 = int(val1), int(val2)
            program.write_to_var(var, Bool(bool(val1 == val2)))
        else:
            Helper.error_exit("Wrong operands", Errors.WRONG_OPERAND_TYPE.value, program)

class AND(Instruction):
    def execute(self, program):
        var = self.get_arg1()
        symb1 = self.get_arg2()
        symb2 = self.get_arg3()

        operand1 = program.get_symb(symb1)
        operand2 = program.get_symb(symb2)

        val1 = operand1.data
        val2 = operand2.data

        if(isinstance(operand1, Bool) and isinstance(operand2, Bool)):
            program.write_to_var(var, Bool(bool(val1 and val2)))
        else:
            Helper.error_exit("Wrong operands", Errors.WRONG_OPERAND_TYPE.value, program)

class OR(Instruction):
    def execute(self, program):
        var = self.get_arg1()
        symb1 = self.get_arg2()
        symb2 = self.get_arg3()

        operand1 = program.get_symb(symb1)
        operand2 = program.get_symb(symb2)

        val1 = operand1.data
        val2 = operand2.data

        if(isinstance(operand1, Bool) and isinstance(operand2, Bool)):
            program.write_to_var(var, Bool(bool(val1 or val2)))
        else:
            Helper.error_exit("Wrong operands", Errors.WRONG_OPERAND_TYPE.value, program)

class NOT(Instruction):
    def execute(self, program):
        var = self.get_arg1()
        symb1 = self.get_arg2()

        operand1 = program.get_symb(symb1)

        val1 = operand1.data

        if(isinstance(operand1, Bool)):
            program.write_to_var(var, Bool(bool(not val1)))
        else:
            Helper.error_exit("Wrong operands", Errors.WRONG_OPERAND_TYPE.value, program)

class INT2CHAR(Instruction):
    def execute(self, program):
        var = self.get_arg1()
        symb1 = self.get_arg2()

        operand1 = program.get_symb(symb1)

        val1 = operand1.data

        if(isinstance(operand1, Int)):
            try:
                char = chr(val1)
            except(ValueError):
                Helper.error_exit("Invalid ASCII code", Errors.WRONG_STRING.value, program)
            program.write_to_var(var, String(char))
        else:
            Helper.error_exit("Wrong operands", Errors.WRONG_OPERAND_TYPE.value, program)

class STRI2INT(Instruction):
    def execute(self, program):
        var = self.get_arg1()
        symb1 = self.get_arg2()
        symb2 = self.get_arg3()

        operand1 = program.get_symb(symb1)
        operand2 = program.get_symb(symb2)

        val1 = operand1.data
        val2 = operand2.data

        if(isinstance(operand1, String) and isinstance(operand2, Int)):
            if(val2 < 0 or val2 >= len(val1)):
                Helper.error_exit("Invalid index or character", Errors.WRONG_STRING.value, program)
            program.write_to_var(var, Int(ord(val1[val2])))
        else:
            Helper.error_exit("Wrong operands", Errors.WRONG_OPERAND_TYPE.value, program)

class READ(Instruction):
    def execute(self, program):
        var = self.get_arg1()
        var_type = self.get_arg2()

        if(isinstance(var_type, Var)):
            val_type = program.read_var_obj(var_type)
        elif(isinstance(var_type, Type)):
            val_type = var_type
        else:
            Helper.error_exit("Wrong argument", Errors.UNEXPECTED_XML_STRUCT.value, program)

        if(not isinstance(val_type, Type)):
            Helper.error_exit("Wrong argument", Errors.UNEXPECTED_XML_STRUCT.value, program)

        read = program.input.readline()

        if (val_type.data == 'int'):
            try:
                val = Int(int(read))
            except:
                val = Nil()
            program.write_to_var(var, val)
        elif (val_type.data == 'bool'):
            read = read.lower().strip()
            if(read == 'true'):
                val = Bool(bool(read))
            elif(read == 'false'):
                val = Bool(bool(read))
            else:
                val = Nil()
            program.write_to_var(var, val)
        elif (val_type.data == 'string'):
            string = read.strip()
            string = Helper.string_escape(string)
            val = String(str(string))
            program.write_to_var(var, val)
        else:
            Helper.error_exit("Wrong type", Errors.WRONG_OPERAND_TYPE.value, program)

class WRITE(Instruction):
    def execute(self, program):
        symb1 = self.get_arg1()

        operand1 = program.get_symb(symb1)

        val1 = operand1.data

        if not (val1 == None or val1 == "None" or val1 == ''):
            if(isinstance(operand1, Nil)):
                val1 = ''
            elif(isinstance(operand1, Bool)):
                if(val1 == True):
                    val1 = 'true'
                elif(val1 == False):
                    val1 = 'false'
            print(val1, end='')

class CONCAT(Instruction):
    def execute(self, program):
        var = self.get_arg1()
        symb1 = self.get_arg2()
        symb2 = self.get_arg3()

        operand1 = program.get_symb(symb1)
        operand2 = program.get_symb(symb2)

        val1 = operand1.data
        val2 = operand2.data

        if(isinstance(operand1, String) and isinstance(operand2, String)):
            program.write_to_var(var, String(str(val1 + val2)))
        else:
            Helper.error_exit("Wrong operands", Errors.WRONG_OPERAND_TYPE.value, program)


class STRLEN(Instruction):
    def execute(self, program):
        var = self.get_arg1()
        symb1 = self.get_arg2()

        operand1 = program.get_symb(symb1)

        val1 = operand1.data

        if(isinstance(operand1, String)):
            program.write_to_var(var, Int(int(len(val1))))
        else:
            Helper.error_exit("Wrong operands", Errors.WRONG_OPERAND_TYPE.value, program)


class GETCHAR(Instruction):
    def execute(self, program):
        var = self.get_arg1()
        symb1 = self.get_arg2()
        symb2 = self.get_arg3()

        operand1 = program.get_symb(symb1)
        operand2 = program.get_symb(symb2)

        val1 = operand1.data
        val2 = operand2.data

        if(isinstance(operand1, String) and isinstance(operand2, Int)):
            if(val2 < 0 or val2 >= len(val1)):
                Helper.error_exit("Wrong index", Errors.WRONG_STRING.value, program)
            program.write_to_var(var, String(str(val1[val2:val2+1])))
        else:
            Helper.error_exit("Wrong operands", Errors.WRONG_OPERAND_TYPE.value, program)


class SETCHAR(Instruction):
    def execute(self, program):
        var = self.get_arg1()
        symb1 = self.get_arg2()
        symb2 = self.get_arg3()

        operand0 = program.read_var_obj(var)

        operand1 = program.get_symb(symb1)
        operand2 = program.get_symb(symb2)

        val1 = operand1.data
        val2 = operand2.data

        string = program.read_var_obj(var).data

        if(isinstance(operand0, String) and isinstance(operand1, Int) and isinstance(operand2, String)):
            if(val1 < 0 or val1 >= len(string)):
                Helper.error_exit("Wrong index", Errors.WRONG_STRING.value, program)
            program.write_to_var(var, String(string[0:val1] + val2[0] + string[val1+1:]))
        else:
            Helper.error_exit("Wrong operands", Errors.WRONG_OPERAND_TYPE.value, program)


class TYPE(Instruction):
    def execute(self, program: Prog):
        var = self.get_arg1()
        symb1 = self.get_arg2()

        operand1 = program.get_symb(symb1)

        if(isinstance(operand1, Int)):
            program.write_to_var(var, Type('int'))
        elif(isinstance(operand1, String)):
            program.write_to_var(var, Type('string'))
        elif(isinstance(operand1, Bool)):
            program.write_to_var(var, Type('bool'))
        elif(isinstance(operand1, Nil)):
            program.write_to_var(var, Type('nil'))
        elif(isinstance(operand1, Const)):
            if(operand1.data == None):
                program.write_to_var(var, Type(""))
        else:
            Helper.error_exit("Wrong operands", Errors.WRONG_OPERAND_TYPE.value, program)


class LABEL(Instruction):
    def execute(self, program):
        pass

class JUMP(Instruction):
    def execute(self, program):
        label = self.get_arg1()

        if(isinstance(label, Label)):
            index = program.find_label_index(label.data)
            if(index != -1):
                program.current_instruction = index
            else:
                Helper.error_exit("Wrong label", Errors.SEMANTIC_CHECKS.value, program)
        else:
            Helper.error_exit("Wrong argument", Errors.WRONG_OPERAND_TYPE.value, program)

class JUMPIFEQ(Instruction):
    def execute(self, program):
        label = self.get_arg1()
        symb1 = self.get_arg2()
        symb2 = self.get_arg3()

        operand1 = program.get_symb(symb1)
        operand2 = program.get_symb(symb2)

        val1 = operand1.data
        val2 = operand2.data

        if(isinstance(operand1, Nil) or isinstance(operand2, Nil)):
            if(isinstance(operand1, Nil) and isinstance(operand2, Nil)):
                index = program.find_label_index(label.data)
                if(index != -1):
                    program.current_instruction = index
                else:
                    Helper.error_exit("Wrong label", Errors.SEMANTIC_CHECKS.value, program)
            Helper.error_exit("Wrong operands", Errors.WRONG_OPERAND_TYPE.value, program)

        if(isinstance(label, Label)):
            if(issubclass(type(operand1), type(operand2)) or issubclass(type(operand2), type(operand1))):
                if(val1 == val2):
                    index = program.find_label_index(label.data)
                    if(index != -1):
                        program.current_instruction = index
                    else:
                        Helper.error_exit("Wrong label", Errors.SEMANTIC_CHECKS.value, program)
            else:
                Helper.error_exit("Wrong operands", Errors.WRONG_OPERAND_TYPE.value, program)
        else:
            Helper.error_exit("Wrong operands", Errors.WRONG_OPERAND_TYPE.value, program)

class JUMPIFNEQ(Instruction):
    def execute(self, program):
        label = self.get_arg1()
        symb1 = self.get_arg2()
        symb2 = self.get_arg3()

        operand1 = program.get_symb(symb1)
        operand2 = program.get_symb(symb2)

        val1 = operand1.data
        val2 = operand2.data

        if(isinstance(operand1, Nil) or isinstance(operand2, Nil)):
            if(not(isinstance(operand1, Nil) and isinstance(operand2, Nil))):
                index = program.find_label_index(label.data)
                if(index != -1):
                    program.current_instruction = index
                else:
                    Helper.error_exit("Wrong label", Errors.SEMANTIC_CHECKS.value, program)
            else:
                Helper.error_exit("Wrong operands", Errors.WRONG_OPERAND_TYPE.value, program)

        if(isinstance(label, Label)):
            if(type(operand1) == type(operand2)):
                if(val1 != val2):
                    index = program.find_label_index(label.data)
                    if(index != -1):
                        program.current_instruction = index
                    else:
                        Helper.error_exit("Wrong label", Errors.SEMANTIC_CHECKS.value, program)
            else:
                Helper.error_exit("Wrong operands", Errors.WRONG_OPERAND_TYPE.value, program)
        else:
            Helper.error_exit("Wrong operands", Errors.WRONG_OPERAND_TYPE.value, program)

class EXIT(Instruction):
    def execute(self, program: Prog):
        symb1 = self.get_arg1()

        operand1 = program.get_symb(symb1)

        val1 = operand1.data

        if(isinstance(operand1, Int)):
            if(val1 < 0 or val1 > 49):
                Helper.error_exit("Wrong exit code", Errors.WRONG_OPERANT_VALUE.value, program)
            else:
                sys.exit(val1)
        else:
            Helper.error_exit("Wrong operands", Errors.WRONG_OPERAND_TYPE.value, program)

class DPRINT(Instruction):
    def execute(self, program):
        symb1 = self.get_arg1()

        operand1 = program.get_symb(symb1)

        val1 = operand1.data

        if not (val1 == None or val1 == "None" or val1 == ''):
            if(isinstance(operand1, Nil)):
                val1 = ''
            elif(isinstance(operand1, Bool)):
                if(val1 == True):
                    val1 = 'true'
                elif(val1 == False):
                    val1 = 'false'
            print(sys.argv, file=sys.stderr)
            print(val1, end='', file=sys.stderr)

class BREAK(Instruction):
    def execute(self, program):
        print("BREAK: .\nCalled from "+str(program.instructions[program.current_instruction].opcode)+"("+str(program.current_instruction)+").", file=sys.stderr)
    pass

# ------------------–------------------–------------------–------------------–------------------ #

# Get input files, parse and check them
class InputFiles:
    def __init__(self):
        self.source_file = None
        self.input_file = None

        self._source_filename = None
        self._input_filename = None

        prog = 'interpret.py'
        desc = "Script reads the XML representation of the program and will interrpret it and generate an output."

        parser = argparse.ArgumentParser(prog=prog, description=desc)

        parser.add_argument('--source', help='Source file with XML representation of IPPcode23 source code', required=False)
        parser.add_argument('--input', help='File with inputs for interpretation', required=False)

        args = parser.parse_args()

        # Source from file, input from file
        if(args.source is not None and args.input is not None):
            self._source_filename = args.source
            self._input_filename = args.input

            try:
                self.source_file = open(self._source_filename, 'r')
            except(IOError, FileNotFoundError):
                Helper.error_exit("Cannot open source file", Errors.INPUT_OPEN.value, None)

            try:
                self.input_file = open(self._input_filename, 'r')
            except(IOError, FileNotFoundError):
                Helper.error_exit("Cannot open source file", Errors.INPUT_OPEN.value, None)

        # Source from file, input from stdin
        elif(args.source is None and args.input is not None):
            self._source_filename = sys.stdin
            self._input_filename = args.input

            self.source_file = sys.stdin

            try:
                self.input_file = open(self._input_filename, 'r')
            except(IOError, FileNotFoundError):
                Helper.error_exit("Cannot open source file", Errors.INPUT_OPEN.value, None)

        # Source from stdin, input from file
        elif(args.source is not None and args.input is None):
            self._source_filename = args.source
            self._input_filename = sys.stdin

            try:
                self.source_file = open(self._source_filename, 'r')
            except(IOError, FileNotFoundError):
                Helper.error_exit("Cannot open source file", Errors.INPUT_OPEN.value, None)

            self.input_file = sys.stdin

        # Missing parameter
        elif(args.source is None and args.input is None):
            Helper.error_exit("Missing parameter --source or --input", Errors.MISSING_PARAMETER.value, None)

# ------------------–------------------–------------------–------------------–------------------ #

# Class for XML parsing
class Xml:
    # Input file is XML representation of IPPcode23 source code
    def __init__(self, input_file):
        self.xml_root = None
        self._header = None
        self._instructions = None
        self.input_file = input_file

        self._get_root()

    def _get_root(self):
        try:
            self.xml_root = etree.parse(self.input_file).getroot()
        except(etree.ParseError):
            Helper.error_exit("Wrong XML format", Errors.WRONG_XML_FORMAT.value, None)

    # Parse XML to instructions
    def parser(self):
        instructions = {}

        tag = self.xml_root.tag
        if(tag != 'program'):
            Helper.error_exit("Unexpected XML structure", Errors.WRONG_XML_FORMAT.value, None)

        lang = self.xml_root.attrib.get('language')
        if(lang != 'IPPcode23'):
            Helper.error_exit("Wrong language", Errors.UNEXPECTED_XML_STRUCT.value, None)

        for instruction in self.xml_root:
            tag = instruction.tag
            if(tag != 'instruction'):
                Helper.error_exit("Unexpected XML structure", Errors.UNEXPECTED_XML_STRUCT.value, None)

            order = instruction.attrib.get('order').strip()
            if(order is None):
                Helper.error_exit("Unexpected XML structure", Errors.UNEXPECTED_XML_STRUCT.value, None)
            elif(int(order) < 1):
                Helper.error_exit("Wrong order", Errors.UNEXPECTED_XML_STRUCT.value, None)
            order = int(order)

            opcode = instruction.attrib.get('opcode').upper()
            if(opcode is None):
                Helper.error_exit("Unexpected XML structure", Errors.UNEXPECTED_XML_STRUCT.value, None)

            if (opcode not in Helper.Opcodes):
                Helper.error_exit("Unknown opcode", Errors.WRONG_OPCODE.value, None)

            expected_args = Helper.ExpectedArgs[opcode]
            args_dict = {}

            for arg in instruction:

                arg_order = arg.tag
                if(arg_order not in ['arg1', 'arg2', 'arg3']):
                    Helper.error_exit("Unexpected XML structure", Errors.UNEXPECTED_XML_STRUCT.value, None)

                arg_type = arg.attrib.get('type')

                if(arg.text is not None):
                    arg.text = arg.text.strip()

                if(arg_type is None):
                    Helper.error_exit("Unexpected XML structure", Errors.UNEXPECTED_XML_STRUCT.value, None)

                elif(arg_type == 'var'):
                    var_frame = arg.text.split('@')[0]
                    var_name = arg.text.split('@')[1]
                    if(var_frame not in ['GF', 'LF', 'TF']):
                        Helper.error_exit("Unexpected XML structure", Errors.SEMANTIC_CHECKS.value, None)

                    argument = Var(var_frame, var_name, None)

                elif(arg_type == 'label'):
                    argument = Label(arg.text)

                elif(arg_type == 'type'):
                    argument = Type(arg.text)

                elif(arg_type == 'int'):
                    argument = Int(int(arg.text))

                elif(arg_type == 'bool'):
                    if(arg.text.lower() == 'true'):
                        argument = Bool(True)
                    if(arg.text.lower() == 'false'):
                        argument = Bool(False)

                elif(arg_type == 'string'):
                    string = Helper.string_escape(arg.text)
                    argument = String(str(string))

                elif(arg_type == 'nil'):
                    argument = Nil()

                elif(arg_type == 'label'):
                    argument = Label(arg.text)

                # Check if argument is already in dictionary
                if(arg_order in args_dict):
                    Helper.error_exit("Unexpected XML structure", Errors.UNEXPECTED_XML_STRUCT.value, None)

                args_dict[arg_order] = argument

            args = []
            if('arg1' in args_dict):
                args.append(args_dict['arg1'])
                if('arg2' in args_dict):
                    args.append(args_dict['arg2'])
                    if('arg3' in args_dict):
                        args.append(args_dict['arg3'])

            if(len(args) != len(Helper.ExpectedArgs[opcode])):
                Helper.error_exit("Wrong number of arguments", Errors.UNEXPECTED_XML_STRUCT.value, None)

            if(len(args) == 1):
                if(not isinstance(args[0], expected_args[0])):
                    Helper.error_exit("Wrong operand type", Errors.OTHER_LEX_SYNT.value, None)
            elif(len(args) == 2):
                if(not isinstance(args[0], expected_args[0]) or
                   not isinstance(args[1], expected_args[1])):
                    Helper.error_exit("Wrong operand type", Errors.OTHER_LEX_SYNT.value, None)
            elif(len(args) == 3):
                if(not isinstance(args[0], expected_args[0]) or
                   not isinstance(args[1], expected_args[1]) or
                   not isinstance(args[2], expected_args[2])):
                    Helper.error_exit("Wrong operand type", Errors.OTHER_LEX_SYNT.value, None)

            # Check if order is already in dictionary
            if(order in instructions):
                Helper.error_exit("Unexpected XML structure", Errors.UNEXPECTED_XML_STRUCT.value, None)
            instructions[order] = eval(opcode)(opcode, args, None)

        # array to list
        instructions = [instructions[i] for i in sorted(instructions.keys())]

        instructions.append(EXIT('EXIT', [Int(0)], None))

        self._instructions = instructions

    def get_instructions(self):
        return self._instructions

# ------------------–------------------–------------------–------------------–------------------ #

# Helper class with static methods useful everywhere
class Helper:
    @staticmethod
    def string_escape(string):
        if(string is not None):
            index = 0
            while(string.find('\\') != -1):
                index = str.find(string, '\\', index)
                if(string[index+1].isdigit() and
                string[index+2].isdigit() and
                string[index+3].isdigit()):
                    string = string[:index] + chr(int(string[index+1:index+4])) + string[index+4:]
                else:
                    index += 1
        return string

    @staticmethod
    def error_exit(error, code, prog):
        if(prog is not None):
            print("ERROR "+str(code)+": "+str(error)+".\nCalled from "+str(prog.instructions[prog.current_instruction].opcode)+"("+str(prog.current_instruction)+").", file=sys.stderr)
        else:
            print("ERROR "+str(code)+": "+str(error), file=sys.stderr)
        sys.exit(code)

    Opcodes = [
        "MOVE",
        "CREATEFRAME",
        "PUSHFRAME",
        "POPFRAME",
        "DEFVAR",
        "CALL",
        "RETURN",
        "PUSHS",
        "POPS",
        "ADD",
        "SUB",
        "MUL",
        "IDIV",
        "LT",
        "GT",
        "EQ",
        "AND",
        "OR",
        "NOT",
        "INT2CHAR",
        "STRI2INT",
        "READ",
        "WRITE",
        "CONCAT",
        "STRLEN",
        "GETCHAR",
        "SETCHAR",
        "TYPE",
        "LABEL",
        "JUMP",
        "JUMPIFEQ",
        "JUMPIFNEQ",
        "EXIT",
        "DPRINT",
        "BREAK"
    ]

    ExpectedArgs = {
        "MOVE":[Var, Symb],
        "CREATEFRAME":[],
        "PUSHFRAME":[],
        "POPFRAME":[],
        "DEFVAR":[Var],
        "CALL":[Label],
        "RETURN":[],
        "PUSHS":[Symb],
        "POPS":[Var],
        "ADD":[Var, Symb, Symb],
        "SUB":[Var, Symb, Symb],
        "MUL":[Var, Symb, Symb],
        "IDIV":[Var, Symb, Symb],
        "LT":[Var, Symb, Symb],
        "GT":[Var, Symb, Symb],
        "EQ":[Var, Symb, Symb],
        "AND":[Var, Symb, Symb],
        "OR":[Var, Symb, Symb],
        "NOT":[Var, Symb],
        "INT2CHAR":[Var, Symb],
        "STRI2INT":[Var, Symb, Symb],
        "READ":[Var, Arg],
        "WRITE":[Symb],
        "CONCAT":[Var, Symb, Symb],
        "STRLEN":[Var, Symb],
        "GETCHAR":[Var, Symb, Symb],
        "SETCHAR":[Var, Symb, Symb],
        "TYPE":[Var, Symb],
        "LABEL":[Label],
        "JUMP":[Label],
        "JUMPIFEQ":[Label, Symb, Symb],
        "JUMPIFNEQ":[Label, Symb, Symb],
        "EXIT":[Symb],
        "DPRINT":[Symb],
        "BREAK":[]
    }

# ------------------–------------------–------------------–------------------–------------------ #

class Errors(Enum):
    # Program
    MISSING_PARAMETER = 10
    INPUT_OPEN = 11
    OUTPUT_OPEN = 12
    # Parser
    WRONG_MISSING_HEADER = 21
    WRONG_OPCODE = 22
    OTHER_LEX_SYNT = 23
    # Interpret
    WRONG_XML_FORMAT = 31
    UNEXPECTED_XML_STRUCT = 32
    #
    SEMANTIC_CHECKS = 52
    WRONG_OPERAND_TYPE = 53
    NONEXISTENT_VARIABLE = 54
    NONEXISTENT_FRAME = 55
    MISSING_VALUE = 56
    WRONG_OPERANT_VALUE = 57
    WRONG_STRING = 58
    # Other
    INTERNAL = 99

# ------------------–------------------–------------------–------------------–------------------ #

# Main function
if __name__ == '__main__':

    # Get command line arguments = inputs and check them
    inputs = InputFiles()

    # Parse XML file
    xml = Xml(inputs.source_file)
    xml.parser()

    # Get instructions from XML
    instructions = xml.get_instructions()

    # Initialize program
    program = Prog(inputs.input_file)

    # Run program
    program.run(instructions)
