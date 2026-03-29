#!/usr/bin/env python3
"""Static Single Assignment (SSA) form converter."""

class SSAConverter:
    def __init__(self):
        self.counters = {}
        self.stacks = {}
        self.ssa_vars = {}

    def fresh(self, var):
        self.counters.setdefault(var, 0)
        self.counters[var] += 1
        name = f"{var}_{self.counters[var]}"
        self.stacks.setdefault(var, []).append(name)
        return name

    def current(self, var):
        if var in self.stacks and self.stacks[var]:
            return self.stacks[var][-1]
        return self.fresh(var)

    def convert_block(self, stmts):
        result = []
        for stmt in stmts:
            if stmt[0] == "assign":
                _, target, expr = stmt
                new_expr = self._rename_expr(expr)
                new_target = self.fresh(target)
                result.append(("assign", new_target, new_expr))
            elif stmt[0] == "return":
                result.append(("return", self._rename_expr(stmt[1])))
            elif stmt[0] == "if":
                cond = self._rename_expr(stmt[1])
                result.append(("if", cond))
        return result

    def _rename_expr(self, expr):
        if isinstance(expr, str):
            if expr.isidentifier() and not expr.startswith('"'):
                return self.current(expr)
            return expr
        if isinstance(expr, (int, float)):
            return expr
        if isinstance(expr, tuple):
            return tuple(self._rename_expr(e) for e in expr)
        return expr

    def insert_phi(self, var, preds):
        sources = []
        for p in preds:
            if var in self.stacks and self.stacks[var]:
                sources.append(self.stacks[var][-1])
            else:
                sources.append(f"{var}_0")
        new = self.fresh(var)
        return ("phi", new, sources)

def test():
    conv = SSAConverter()
    stmts = [
        ("assign", "x", 1),
        ("assign", "y", ("add", "x", 2)),
        ("assign", "x", ("add", "x", "y")),
        ("return", "x"),
    ]
    ssa = conv.convert_block(stmts)
    assert ssa[0] == ("assign", "x_1", 1)
    assert ssa[1][1] == "y_1"
    # expr is renamed: ("add", "x_1", 2)
    assert ssa[1][2][1] == "x_1"
    assert ssa[2][1] == "x_2"
    assert ssa[2][2][1] == "x_1" and ssa[2][2][2] == "y_1"
    assert ssa[3] == ("return", "x_2")
    # Phi
    phi = conv.insert_phi("x", ["block1", "block2"])
    assert phi[0] == "phi"
    assert phi[1] == "x_3"
    assert len(phi[2]) == 2
    print("  ssa_form: ALL TESTS PASSED")

if __name__ == "__main__":
    test()
