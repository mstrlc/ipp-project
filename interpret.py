import argparse
import re
import sys
import os
from enum import Enum
import xml.etree.ElementTree as etree
import typing

###

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

###

class Prog:
    def __init__(self, input_file):
        self.gf = {}    # global frame
        self.tf = None    # temporary frame
        self.lf = []  # local frame
        self.instructions = []
        self.current_instruction = 0
        self.stack = []
        self.labels = []
        self.callstack = []
        self.input = input_file
        
    def run(self, instructions):
        self.instructions = instructions
        
        self.get_labels(self.instructions)
        
        self.current_instruction = 0
        while(self.current_instruction < len(instructions)):
            instructions[self.current_instruction].execute(self)
            self.current_instruction += 1
            
    def get_labels(self, instructions):
        for i in range(len(instructions)):
            if(instructions[i].opcode == 'LABEL'):
                if(instructions[i].args[0].data in self.labels):
                    print("Error: Label already defined", file=sys.stderr)
                    exit(Errors.SEMANTIC_CHECKS.value)
                self.labels.append(instructions[i].args[0].data)
                
    def find_label_index(self, label):
        for i in range(len(self.instructions)):
            if(self.instructions[i].opcode == 'LABEL' and self.instructions[i].args[0].data == label):
                return i
        return -1
                    
    def get_symb(self, symb):
        # todo frames
        # todo def check
        if(isinstance(symb, Var)):
            return self.read_var(symb)
        elif(isinstance(symb, Const)):
            return symb
        else:
            print("Wrong argument", file=sys.stderr)
            exit(Errors.WRONG_OPERAND_TYPE.value)
    
    def define_var(self, var):
        if(var.frame == 'GF'):
            self.gf[var.name] = Const(None)
        elif(var.frame == 'TF'):
            if(self.tf is not None):
                self.tf[var.name] = Const(None)
            else:
                print("Error: Frame not defined", file=sys.stderr)
                exit(Errors.NONEXISTENT_FRAME.value)
        elif(var.frame == 'LF'):
            if(self.lf[-1] is not None):
                self.lf[-1][var.name] = Const(None)
            else:
                print("Error: Frame not defined", file=sys.stderr)
                exit(Errors.NONEXISTENT_FRAME.value)
                
    def is_var_defined(self, var):
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
            if(self.lf[-1] is not None):
                if(var.name in self.lf[-1]):
                    return True
                else:
                    return False
        return False
        
    def read_from_var(self, var):
        if(var.frame == 'GF'):
            return self.gf[var.name].data
        elif(var.frame == 'TF'):
            if(self.tf is not None):
                return self.tf[var.name].data
            else:
                print("Error: Variable not defined", file=sys.stderr)
                exit(Errors.NONEXISTENT_VARIABLE.value)
        elif(var.frame == 'LF'):
            if(self.lf[-1] is not None):
                return self.lf[-1][var.name].data
            else:
                print("Error: Variable not defined", file=sys.stderr)
                exit(Errors.NONEXISTENT_VARIABLE.value)
    
    def read_var(self, var):
        if(var.frame == 'GF'):
            if(self.is_var_defined(var)):
                return self.gf[var.name]
            else:
                print("Error: Variable not defined", file=sys.stderr)
                exit(Errors.NONEXISTENT_VARIABLE.value)
        elif(var.frame == 'TF'):
            if(self.tf is not None):
                if(self.is_var_defined(var)):
                    return self.tf[var.name]
                else:
                    print("Error: Variable not defined", file=sys.stderr)
                    exit(Errors.NONEXISTENT_VARIABLE.value)
            else:
                print("Error: Frame not defined", file=sys.stderr)
                exit(Errors.NONEXISTENT_FRAME.value)
        elif(var.frame == 'LF'):
            if(self.lf[-1] is not None):
                if(self.is_var_defined(var)):
                    return self.lf[-1][var.name]
                else:
                    print("Error: Variable not defined", file=sys.stderr)
                    exit(Errors.NONEXISTENT_VARIABLE.value)
            else:
                print("Error: Frame not defined", file=sys.stderr)
                exit(Errors.NONEXISTENT_FRAME.value)
    
    def write_to_var(self, var, data):
        if(var.frame == 'GF'):
            if(self.is_var_defined(var)):
                self.gf[var.name] = data
            else:
                print("Error: Variable not defined", file=sys.stderr)
                exit(Errors.NONEXISTENT_VARIABLE.value)
        elif(var.frame == 'TF'):
            if(self.tf is not None):
                if(self.is_var_defined(var)):
                    self.tf[var.name] = data
                else:
                    print("Error: Variable not defined", file=sys.stderr)
                    exit(Errors.NONEXISTENT_VARIABLE.value)
        elif(var.frame == 'LF'):
            if(self.lf[-1] is not None):
                if(self.is_var_defined(var)):
                    self.lf[-1][var.name] = data
                else:
                    print("Error: Variable not defined", file=sys.stderr)
                    exit(Errors.NONEXISTENT_VARIABLE.value)

###
     
class Arg:
    def __init__(self):
        pass
    
class Symb(Arg):
    def __init__(self, data):
        self.data = data
            
class Var(Symb):
    def __init__(self, frame, name, data):
        self.frame = frame
        self.name = name
        self.data : Const = data
                
class Const(Symb):
    def __init__(self, data):
        self.data = data
        
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
        
class Label(Arg):
    def __init__(self, name):
        self.data = name
        
class Type(Arg):
    def __init__(self, type):
        self.data = type

###

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

###

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
            print("Temporary frame is empty", file=sys.stderr)
            exit(Errors.NONEXISTENT_FRAME.value)

class POPFRAME(Instruction):
    def execute(self, program):
        try:
            program.tf = program.lf.pop()
        except(IndexError):
            print("Local frame is empty", file=sys.stderr)
            exit(Errors.NONEXISTENT_FRAME.value)
        
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
            print("Wrong label", file=sys.stderr)
            exit(Errors.SEMANTIC_CHECKS.value)

class RETURN(Instruction):
    def execute(self, program):
        try:
            index = program.callstack.pop()
            program.current_instruction = index
        except(IndexError):
            print("Callstack is empty", file=sys.stderr)
            exit(Errors.MISSING_VALUE.value)
            
class PUSHS(Instruction):
    def execute(self, program):
        symb1 = self.get_arg1()
        
        operand1 = program.get_symb(symb1)
                    
        program.stack.append(operand1)


class POPS(Instruction):
    def execute(self, program):
        var = self.get_arg1()
        
        try:
            operand1 = program.stack.pop()
        except(IndexError):
            print("Stack is empty", file=sys.stderr)
            exit(Errors.MISSING_VALUE.value)
            
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
            print("Wrong operands", file=sys.stderr)
            exit(Errors.WRONG_OPERAND_TYPE.value)
        
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
            print("Wrong operands", file=sys.stderr)
            exit(Errors.WRONG_OPERAND_TYPE.value)

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
            print("Wrong operands", file=sys.stderr)
            exit(Errors.WRONG_OPERAND_TYPE.value)


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
            print("Division by zero", file=sys.stderr)
            exit(Errors.WRONG_OPERANT_VALUE.value)

        if(isinstance(operand1, Int) and isinstance(operand2, Int)):
            program.write_to_var(var, Int(val1 // val2))
        else:
            print("Wrong operands", file=sys.stderr)
            exit(Errors.WRONG_OPERAND_TYPE.value)


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
            print("Wrong operands", file=sys.stderr)
            exit(Errors.WRONG_OPERAND_TYPE.value)
                            
        if((isinstance(operand1, Int) and isinstance(operand2, Int)) or
           (isinstance(operand1, String) and isinstance(operand2, String))):
            program.write_to_var(var, Bool(bool(val1 < val2)))
        elif(isinstance(operand1, Bool) and isinstance(operand2, Bool)):
            val1, val2 = int(val1), int(val2)
            program.write_to_var(var, Bool(bool(val1 < val2)))
        else:
            print("Wrong operands", file=sys.stderr)
            exit(Errors.WRONG_OPERAND_TYPE.value)

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
            print("Wrong operands", file=sys.stderr)
            exit(Errors.WRONG_OPERAND_TYPE.value)
                            
        if((isinstance(operand1, Int) and isinstance(operand2, Int)) or
           (isinstance(operand1, String) and isinstance(operand2, String))):
            program.write_to_var(var, Bool(bool(val1 > val2)))
        elif(isinstance(operand1, Bool) and isinstance(operand2, Bool)):
            val1, val2 = int(val1), int(val2)
            program.write_to_var(var, Bool(bool(val1 > val2)))
        else:
            print("Wrong operands", file=sys.stderr)
            exit(Errors.WRONG_OPERAND_TYPE.value)

class EQ(Instruction):
    def execute(self, program):
        var = self.get_arg1()
        symb1 = self.get_arg2()
        symb2 = self.get_arg3()
        
        operand1 = program.get_symb(symb1)     
        operand2 = program.get_symb(symb2)   

        val1 = operand1.data
        val2 = operand2.data
                    
        if((isinstance(operand1, Int) and isinstance(operand2, Int)) or
           (isinstance(operand1, String) and isinstance(operand2, String))):
            program.write_to_var(var, Bool(bool(val1 == val2)))
        elif(isinstance(operand1, Bool) and isinstance(operand2, Bool)):
            val1, val2 = int(val1), int(val2)
            program.write_to_var(var, Bool(bool(val1 == val2)))
        elif(isinstance(operand1, Nil) or isinstance(operand2, Nil)):
            program.write_to_var(var, Bool(bool(val1 == val2)))
        else:
            print("Wrong operands", file=sys.stderr)
            exit(Errors.WRONG_OPERAND_TYPE.value)

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
            print("Wrong operands", file=sys.stderr)
            exit(Errors.WRONG_OPERAND_TYPE.value)

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
            print("Wrong operands", file=sys.stderr)
            exit(Errors.WRONG_OPERAND_TYPE.value)

class NOT(Instruction):
    def execute(self, program):
        var = self.get_arg1()
        symb1 = self.get_arg2()
        
        operand1 = program.get_symb(symb1)     

        val1 = operand1.data
        
        if(isinstance(operand1, Bool)):
            program.write_to_var(var, Bool(bool(not val1)))
        else:
            print("Wrong operands", file=sys.stderr)
            exit(Errors.WRONG_OPERAND_TYPE.value)

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
                print("Invalid ASCII code", file=sys.stderr)
                exit(Errors.WRONG_STRING.value)
            program.write_to_var(var, String(char))
        else:
            print("Wrong operands", file=sys.stderr)
            exit(Errors.WRONG_OPERAND_TYPE.value)

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
                print("Wrong index", file=sys.stderr)
                exit(Errors.WRONG_STRING.value)
            program.write_to_var(var, Int(ord(val1[val2])))
        else:
            print("Wrong operands", file=sys.stderr)
            exit(Errors.WRONG_OPERAND_TYPE.value)

class READ(Instruction):
    def execute(self, program):
        var = self.get_arg1()
        var_type = self.get_arg2()
        
        if(isinstance(var_type, Var)):
            val_type = program.read_var(var_type)
        elif(isinstance(var_type, Type)):
            val_type = var_type
        else:
            print("Wrong argument", file=sys.stderr)
            exit(Errors.UNEXPECTED_XML_STRUCT.value)
        
        if(not isinstance(val_type, Type)):
            print("Wrong argument", file=sys.stderr)
            exit(Errors.UNEXPECTED_XML_STRUCT.value)
        
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
            string = string_escape(read)
            val = String(str(string))
            program.write_to_var(var, val)
        else:
            print("Wrong type", file=sys.stderr)
            exit(Errors.WRONG_OPERAND_TYPE.value)

class WRITE(Instruction):
    def execute(self, program):
        symb1 = self.get_arg1()
        
        operand1 = program.get_symb(symb1)     

        val1 = operand1.data
        
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
            print("Wrong operands", file=sys.stderr)
            exit(Errors.WRONG_OPERAND_TYPE.value)


class STRLEN(Instruction):
    def execute(self, program):
        var = self.get_arg1()
        symb1 = self.get_arg2()
        
        operand1 = program.get_symb(symb1)     

        val1 = operand1.data
        
        if(isinstance(operand1, String)):
            program.write_to_var(var, Int(int(len(val1))))
        else:
            print("Wrong operands", file=sys.stderr)
            exit(Errors.WRONG_OPERAND_TYPE.value)

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
                print("Wrong index", file=sys.stderr)
                exit(Errors.WRONG_STRING.value)
            program.write_to_var(var, String(str(val1[val2:val2+1])))
        else:
            print("Wrong operands", file=sys.stderr)
            exit(Errors.WRONG_OPERAND_TYPE.value)

class SETCHAR(Instruction):
    def execute(self, program):
        var = self.get_arg1()
        symb1 = self.get_arg2()
        symb2 = self.get_arg3()
        
        operand0 = program.read_var(var)
        
        operand1 = program.get_symb(symb1)     
        operand2 = program.get_symb(symb2)   

        val1 = operand1.data
        val2 = operand2.data

        string = program.read_var(var).data
        
        if(isinstance(operand0, String) and isinstance(operand1, Int) and isinstance(operand2, String)):
            if(val1 < 0 or val1 >= len(string)):
                print("Wrong index", file=sys.stderr)
                exit(Errors.WRONG_STRING.value)
            program.write_to_var(var, String(string[0:val1] + val2[0] + string[val1+1:]))
        else:
            print("Wrong operands", file=sys.stderr)
            exit(Errors.WRONG_OPERAND_TYPE.value)

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
        else:
            print("Wrong operands", file=sys.stderr)
            exit(Errors.WRONG_OPERAND_TYPE.value)

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
                print("Wrong label", file=sys.stderr)
                exit(Errors.SEMANTIC_CHECKS.value)
        else:
            print("Wrong argument", file=sys.stderr)
            exit(Errors.WRONG_OPERAND_TYPE.value)

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
            print("Wrong operands", file=sys.stderr)
            exit(Errors.WRONG_OPERAND_TYPE.value)
        
        if(isinstance(label, Label)):
            if(type(operand1) == type(operand2)):
                if(val1 == val2):
                    index = program.find_label_index(label.data)
                    if(index != -1):
                        program.current_instruction = index
                    else:
                        print("Wrong label", file=sys.stderr)
                        exit(Errors.SEMANTIC_CHECKS.value)
            else:
                print("Wrong operands", file=sys.stderr)
                exit(Errors.WRONG_OPERAND_TYPE.value)
        else:
            print("Wrong argument", file=sys.stderr)
            exit(Errors.WRONG_OPERAND_TYPE.value)

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
            print("Wrong operands", file=sys.stderr)
            exit(Errors.WRONG_OPERAND_TYPE.value)
        
        if(isinstance(label, Label)):
            if(type(operand1) == type(operand2)):
                if(val1 != val2):
                    index = program.find_label_index(label.data)
                    if(index != -1):
                        program.current_instruction = index
                    else:
                        print("Wrong label", file=sys.stderr)
                        exit(Errors.SEMANTIC_CHECKS.value)
            else:
                print("Wrong operands", file=sys.stderr)
                exit(Errors.WRONG_OPERAND_TYPE.value)
        else:
            print("Wrong argument", file=sys.stderr)
            exit(Errors.WRONG_OPERAND_TYPE.value)

class EXIT(Instruction):
    def execute(self, program: Prog):
        symb1 = self.get_arg1()
        
        operand1 = program.get_symb(symb1)     

        val1 = operand1.data
        
        if(isinstance(operand1, Int)):
            if(val1 < 0 or val1 > 49):
                print("Wrong exit code", file=sys.stderr)
                exit(Errors.WRONG_OPERANT_VALUE.value)
            else:
                exit(val1)
        else:
            print("Wrong argument", file=sys.stderr)
            exit(Errors.WRONG_OPERAND_TYPE.value)

class DPRINT(Instruction):
    pass

class BREAK(Instruction):
    pass

###

class CmdArgs:
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
                print("Cannot open source file", file=sys.stderr)
                exit(Errors.INPUT_OPEN.value)
                
            try:
                self.input_file = open(self._input_filename, 'r')
            except(IOError, FileNotFoundError):
                print("Cannot open input file", file=sys.stderr)
                exit(Errors.INPUT_OPEN.value)

        # Source from file, input from stdin
        elif(args.source is None and args.input is not None):
            self._source_filename = sys.stdin
            self._input_filename = args.input
            
            self.source_file = sys.stdin
            
            try:
                self.input_file = open(self._input_filename, 'r')
            except(IOError, FileNotFoundError):
                print("Cannot open input file", file=sys.stderr)
                exit(Errors.INPUT_OPEN.value)

        # Source from stdin, input from file
        elif(args.source is not None and args.input is None):
            self._source_filename = args.source
            self._input_filename = sys.stdin
            
            try:
                self.source_file = open(self._source_filename, 'r')
            except(IOError, FileNotFoundError):
                print("Cannot open source file", file=sys.stderr)
                exit(Errors.INPUT_OPEN.value)
                
            self.input_file = sys.stdin

        # Missing parameter
        elif(args.source is None and args.input is None):
            print("Missing parameter --source or --input", file=sys.stderr)
            exit(Errors.MISSING_PARAMETER.value)
        
###

class Xml:
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
            print("Wrong XML format", file=sys.stderr)
            exit(Errors.WRONG_XML_FORMAT.value)
                        
    def parser(self):
        instructions = {}
        
        tag = self.xml_root.tag
        if(tag != 'program'):
            print("Unexpected XML structure", file=sys.stderr)
            exit(Errors.WRONG_XML_FORMAT.value)
        
        lang = self.xml_root.attrib.get('language')
        if(lang != 'IPPcode23'):
            print("Wrong language", file=sys.stderr)
            exit(Errors.UNEXPECTED_XML_STRUCT.value)
        
        for instruction in self.xml_root:
            tag = instruction.tag
            if(tag != 'instruction'):
                print("Unexpected XML structure", file=sys.stderr)
                exit(Errors.UNEXPECTED_XML_STRUCT.value)
                
            order = instruction.attrib.get('order').strip()
            if(order is None):
                print("Unexpected XML structure", file=sys.stderr)
                exit(Errors.WRONG_XML_FORMAT.value)
            elif(int(order) < 1):
                print("Wrong order", file=sys.stderr)
                exit(Errors.UNEXPECTED_XML_STRUCT.value)                
            order = int(order)
            
            opcode = instruction.attrib.get('opcode').upper()
            if(opcode is None):
                print("Unexpected XML structure", file=sys.stderr)
                exit(Errors.WRONG_XML_FORMAT.value)
                
            if (opcode not in Opcodes):
                print("Unknown opcode", file=sys.stderr)
                exit(Errors.UNKNOWN_OPCODE.value)
            
            expected_args = ExpectedArgs[opcode]
            args_dict = {}
            
            for arg in instruction:
                
                arg_order = arg.tag
                if(arg_order not in ['arg1', 'arg2', 'arg3']):
                    print("Unexpected XML structure", file=sys.stderr)
                    exit(Errors.UNEXPECTED_XML_STRUCT.value)
                
                arg_type = arg.attrib.get('type')

                if(arg.text is not None):
                    arg.text = arg.text.strip()
                
                if(arg_type is None):
                    print("Unexpected XML structure", file=sys.stderr)
                    exit(Errors.UNEXPECTED_XML_STRUCT.value)
                
                elif(arg_type == 'var'):
                    var_frame = arg.text.split('@')[0]
                    var_name = arg.text.split('@')[1]
                    if(var_frame not in ['GF', 'LF', 'TF']):
                        print("Unexpected XML structure", file=sys.stderr)
                        exit(Errors.SEMANTIC_CHECKS.value)                        
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
                    string = string_escape(arg.text)
                    argument = String(str(string))
                    
                elif(arg_type == 'nil'):
                    argument = Nil()
                    
                elif(arg_type == 'label'):
                    argument = Label(arg.text)
                
                # Check if argument is already in dictionary
                if(arg_order in args_dict):
                    print("Unexpected XML structure", file=sys.stderr)
                    exit(Errors.UNEXPECTED_XML_STRUCT.value)
                    
                args_dict[arg_order] = argument
                 
            args = []
            if('arg1' in args_dict):
                args.append(args_dict['arg1'])
                if('arg2' in args_dict):
                    args.append(args_dict['arg2'])
                    if('arg3' in args_dict):
                        args.append(args_dict['arg3'])
                
            if(len(args) != len(ExpectedArgs[opcode])):
                print("Wrong number of arguments", file=sys.stderr)
                exit(Errors.UNEXPECTED_XML_STRUCT.value)
                
            if(len(args) == 1):
                if(not isinstance(args[0], expected_args[0])):
                    print("Wrong operand type", file=sys.stderr)
                    exit(Errors.OTHER_LEX_SYNT.value)
            elif(len(args) == 2):
                if(not isinstance(args[0], expected_args[0]) or
                   not isinstance(args[1], expected_args[1])):
                    print("Wrong operand type", file=sys.stderr)
                    exit(Errors.OTHER_LEX_SYNT.value)
            elif(len(args) == 3):
                if(not isinstance(args[0], expected_args[0]) or
                   not isinstance(args[1], expected_args[1]) or
                   not isinstance(args[2], expected_args[2])):
                    print("Wrong operand type", file=sys.stderr)
                    exit(Errors.OTHER_LEX_SYNT.value)

            # Check if order is already in dictionary
            if(order in instructions):
                print("Unexpected XML structure", file=sys.stderr)
                exit(Errors.UNEXPECTED_XML_STRUCT.value)
            instructions[order] = eval(opcode)(opcode, args, None)
            
        # array to list
        instructions = [instructions[i] for i in sorted(instructions.keys())]
        self._instructions = instructions
        
    def get_instructions(self):
        return self._instructions
    
###

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
    
###
    
if __name__ == '__main__':
    cmd_args = CmdArgs()
    
    xml = Xml(cmd_args.source_file)
    xml.parser()
    
    program = Prog(cmd_args.input_file)
    
    instructions = xml.get_instructions()
    
    program.run(instructions)
    
    pass
    # cmd_args.end()
