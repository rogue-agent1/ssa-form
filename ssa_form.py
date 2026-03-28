#!/usr/bin/env python3
"""SSA (Static Single Assignment) form converter."""
class Instruction:
    def __init__(self,op,dest=None,args=None):
        self.op=op;self.dest=dest;self.args=args or []
    def __repr__(self):
        if self.dest: return f"{self.dest} = {self.op} {', '.join(str(a) for a in self.args)}"
        return f"{self.op} {', '.join(str(a) for a in self.args)}"
def to_ssa(instructions):
    versions={};ssa=[]
    def get_version(var):
        return f"{var}_{versions.get(var,0)}"
    def new_version(var):
        versions[var]=versions.get(var,0)+1
        return f"{var}_{versions[var]}"
    for inst in instructions:
        new_args=[get_version(a) if isinstance(a,str) and a.isalpha() else a for a in inst.args]
        new_dest=new_version(inst.dest) if inst.dest else None
        ssa.append(Instruction(inst.op,new_dest,new_args))
    return ssa
def from_ssa(instructions):
    result=[]
    for inst in instructions:
        dest=inst.dest.rsplit("_",1)[0] if inst.dest else None
        args=[a.rsplit("_",1)[0] if isinstance(a,str) and "_" in a else a for a in inst.args]
        result.append(Instruction(inst.op,dest,args))
    return result
if __name__=="__main__":
    code=[Instruction("assign","x",[1]),Instruction("add","y",["x",2]),
        Instruction("assign","x",[3]),Instruction("add","z",["x","y"])]
    ssa=to_ssa(code)
    for i in ssa: print(i)
    assert "x_1" in str(ssa[0]) and "x_2" in str(ssa[2])
    back=from_ssa(ssa)
    print("\nBack from SSA:")
    for i in back: print(i)
    print("SSA form OK")
