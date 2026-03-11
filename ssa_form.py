#!/usr/bin/env python3
"""Static Single Assignment — convert imperative code to SSA form with φ-functions."""
import sys

class Instruction:
    def __init__(self, op, dest=None, args=None):
        self.op, self.dest, self.args = op, dest, args or []
    def __repr__(self):
        if self.op == 'phi': return f"{self.dest} = φ({', '.join(self.args)})"
        if self.op == 'assign': return f"{self.dest} = {self.args[0]}"
        if self.op == 'binop': return f"{self.dest} = {self.args[0]} {self.args[1]} {self.args[2]}"
        return f"{self.op}({', '.join(map(str, self.args))})"

class BasicBlock:
    def __init__(self, label):
        self.label, self.instrs = label, []
        self.preds, self.succs = [], []
    def add(self, instr): self.instrs.append(instr)

def to_ssa(blocks):
    versions = {}; result_blocks = []
    def ver(name):
        v = versions.get(name, 0); return f"{name}_{v}"
    def bump(name):
        versions[name] = versions.get(name, 0) + 1; return ver(name)
    for block in blocks:
        new_block = BasicBlock(block.label)
        for instr in block.instrs:
            if instr.op == 'assign':
                dest = bump(instr.dest)
                new_block.add(Instruction('assign', dest, instr.args))
            elif instr.op == 'binop':
                a1 = ver(instr.args[0]) if not instr.args[0].isdigit() else instr.args[0]
                a2 = ver(instr.args[2]) if not instr.args[2].isdigit() else instr.args[2]
                dest = bump(instr.dest)
                new_block.add(Instruction('binop', dest, [a1, instr.args[1], a2]))
            elif instr.op == 'phi':
                sources = [ver(a) for a in instr.args]
                dest = bump(instr.dest)
                new_block.add(Instruction('phi', dest, sources))
        result_blocks.append(new_block)
    return result_blocks

if __name__ == "__main__":
    b1 = BasicBlock("entry")
    b1.add(Instruction('assign', 'x', ['1']))
    b1.add(Instruction('assign', 'y', ['2']))
    b2 = BasicBlock("loop")
    b2.add(Instruction('phi', 'x', ['x', 'x']))
    b2.add(Instruction('binop', 'x', ['x', '+', 'y']))
    b2.add(Instruction('binop', 'y', ['y', '*', '2']))
    for block in to_ssa([b1, b2]):
        print(f"{block.label}:")
        for i in block.instrs: print(f"  {i}")
