#!/usr/bin/env python3
"""ssa_form - Static Single Assignment form transformation."""
import argparse
from collections import defaultdict

class Instruction:
    def __init__(self, op, dest=None, args=None):
        self.op,self.dest,self.args=op,dest,args or []
    def __repr__(self):
        if self.dest: return f"{self.dest} = {self.op} {' '.join(str(a) for a in self.args)}"
        return f"{self.op} {' '.join(str(a) for a in self.args)}"

class BasicBlock:
    def __init__(self, label): self.label=label;self.instrs=[];self.succs=[];self.preds=[]
    def add(self, instr): self.instrs.append(instr)

class SSAConverter:
    def __init__(self): self.counters=defaultdict(int);self.stacks=defaultdict(list)
    def fresh(self, var):
        self.counters[var]+=1;name=f"{var}.{self.counters[var]}"
        self.stacks[var].append(name);return name
    def current(self, var):
        if self.stacks[var]: return self.stacks[var][-1]
        return self.fresh(var)
    def convert_block(self, block):
        new_instrs=[]
        for instr in block.instrs:
            new_args=[self.current(a) if isinstance(a,str) and not a.startswith('#') else a for a in instr.args]
            new_dest=self.fresh(instr.dest) if instr.dest else None
            new_instrs.append(Instruction(instr.op,new_dest,new_args))
        block.instrs=new_instrs
    def insert_phi(self, block, var, preds):
        args=[]
        for p in preds:
            if self.stacks[var]: args.append(f"{self.stacks[var][-1]}({p.label})")
            else: args.append(f"undef({p.label})")
        dest=self.fresh(var)
        phi=Instruction("phi",dest,args)
        block.instrs.insert(0,phi)

def main():
    p=argparse.ArgumentParser(description="SSA form transformation");args=p.parse_args()
    entry=BasicBlock("entry"); loop=BasicBlock("loop"); exit_=BasicBlock("exit")
    entry.add(Instruction("const","x",["#0"]));entry.add(Instruction("const","n",["#10"]))
    entry.add(Instruction("br",None,["loop"]));entry.succs=[loop];loop.preds=[entry]
    loop.add(Instruction("add","x",["x","#1"]));loop.add(Instruction("sub","n",["n","#1"]))
    loop.add(Instruction("cmp","c",["n","#0"]));loop.add(Instruction("br_if",None,["c","loop","exit"]))
    loop.succs=[loop,exit_];loop.preds.append(loop);exit_.preds=[loop]
    exit_.add(Instruction("ret",None,["x"]))
    blocks=[entry,loop,exit_]
    print("=== Before SSA ===")
    for b in blocks:
        print(f"  {b.label}:");
        for i in b.instrs: print(f"    {i}")
    conv=SSAConverter()
    phi_vars={"x","n"}
    for b in blocks:
        if len(b.preds)>1:
            for v in phi_vars: conv.insert_phi(b,v,b.preds)
        conv.convert_block(b)
    print("\n=== After SSA ===")
    for b in blocks:
        print(f"  {b.label}:");
        for i in b.instrs: print(f"    {i}")

if __name__=="__main__":
    main()
