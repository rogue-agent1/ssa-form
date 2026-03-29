#!/usr/bin/env python3
"""SSA Form Converter - Convert basic block code to SSA form."""
import sys, re
from collections import defaultdict

def parse_blocks(text):
    blocks = {}; current = "entry"; blocks[current] = []
    for line in text.strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("#"): continue
        if line.endswith(":"):
            current = line[:-1]; blocks[current] = []
        else:
            blocks[current].append(line)
    return blocks

def get_vars(blocks):
    defs = defaultdict(set); uses = defaultdict(set)
    for label, instrs in blocks.items():
        for instr in instrs:
            m = re.match(r"(\w+)\s*=\s*(.*)", instr)
            if m:
                defs[label].add(m.group(1))
                for v in re.findall(r"[a-zA-Z_]\w*", m.group(2)):
                    uses[label].add(v)
            elif instr.startswith("if ") or instr.startswith("goto "):
                for v in re.findall(r"[a-zA-Z_]\w*", instr):
                    if v not in ("if", "goto", "then"): uses[label].add(v)
    return defs, uses

def to_ssa(blocks):
    counters = defaultdict(int)
    stacks = defaultdict(list)
    result = {}
    def rename(var):
        counters[var] += 1
        name = f"{var}_{counters[var]}"
        stacks[var].append(name)
        return name
    def current(var):
        return stacks[var][-1] if stacks[var] else f"{var}_0"
    for label, instrs in blocks.items():
        new_instrs = []
        for instr in instrs:
            m = re.match(r"(\w+)\s*=\s*(.*)", instr)
            if m:
                var, expr = m.group(1), m.group(2)
                new_expr = re.sub(r"[a-zA-Z_]\w*", lambda m2: current(m2.group()) if m2.group() != var else m2.group(), expr)
                new_var = rename(var)
                new_instrs.append(f"{new_var} = {new_expr}")
            else:
                new_instrs.append(instr)
        result[label] = new_instrs
    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: ssa_form.py <file>"); print("Format: label: / x = expr / if cond goto label"); sys.exit(1)
    with open(sys.argv[1]) as f:
        blocks = parse_blocks(f.read())
    print("=== Original ===")
    for label, instrs in blocks.items():
        print(f"{label}:")
        for i in instrs: print(f"  {i}")
    ssa = to_ssa(blocks)
    print("\n=== SSA Form ===")
    for label, instrs in ssa.items():
        print(f"{label}:")
        for i in instrs: print(f"  {i}")

if __name__ == "__main__":
    main()
