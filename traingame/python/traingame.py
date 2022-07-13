from abc import ABC, abstractmethod
from fractions import Fraction


class Operator(ABC):
    def __init__(self, symbol, commutative, priority):
        self.symbol = symbol
        self.commutative = commutative
        self.priority = priority

    @abstractmethod
    def action(self, a, b):
        pass

    def check(self, a, b):
        return True

    def __str__(self):
        return str(self.symbol)

    def __repr__(self):
        return str(self)


class Add(Operator):
    def __init__(self):
        super().__init__("+", True, 10)

    def action(self, a, b):
        return a + b


class Subtract(Operator):
    def __init__(self):
        super().__init__("-", False, 10)

    def action(self, a, b):
        return a - b


class Multiply(Operator):
    def __init__(self):
        super().__init__("*", True, 5)

    def action(self, a, b):
        return a * b


class Divide(Operator):
    def __init__(self):
        super().__init__("/", False, 5)

    def action(self, a, b):
        return a / b

    def check(self, a, b):
        return b != 0


class Power(Operator):
    def __init__(self):
        super().__init__("^", False, 1)

    def action(self, a, b):
        return a**b

    def check(self, a, b):
        return abs(b) <= 10 and not (a == 0 and b <= 0) and not (a < 0 and int(b) != b)

    def __str__(self):
        return "**"


class Value:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self)


class Expression(Value):
    def __init__(self, lhs, op, rhs):
        super().__init__(op.action(lhs.value, rhs.value))
        self.op = op
        self.lhs = lhs
        self.rhs = rhs

    def __str__(self):
        lhs = self.lhs
        if isinstance(lhs, Expression):
            if lhs.op.priority > self.op.priority or (
                lhs.op.symbol == "^" and self.op.symbol == "^"
            ):
                lhs = "(" + str(self.lhs) + ")"
        rhs = self.rhs
        if isinstance(rhs, Expression):
            if rhs.op.priority >= self.op.priority:
                rhs = "(" + str(self.rhs) + ")"
        return f"{lhs} {self.op} {rhs}"


def train_game(digits, target, ops):
    def try_operator(values, i, j, op):
        values2 = list(values)
        a = values[i]
        b = values[j]
        if not op.check(a.value, b.value):
            return
        new_expr = Expression(a, op, b)
        values2[i] = new_expr
        values2.pop(j)
        find_combo(values2)

    found = set()

    def find_combo(values):
        if len(values) == 0:
            raise ValueError("Missing numbers")
        if len(values) == 1:
            if values[0].value == target:
                found.add(str(values[0]))
            return

        for i in range(len(values)):
            for j in range(i + 1, len(values)):
                for op in ops:
                    try_operator(values, i, j, op)
                    if not op.commutative:
                        try_operator(values, j, i, op)

    find_combo([Value(Fraction(n)) for n in digits])

    return list(found)


operators = [Add(), Subtract(), Multiply(), Divide(), Power()]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("values")
    parser.add_argument("--target", type=int, default=10)
    parser.add_argument("--operators", default="+-*/")
    args = parser.parse_args()

    if len(args.values) != 4 or not args.values.isdigit():
        print("enter 4 digits")
        exit(1)

    op_set = [x.symbol for x in operators]

    if any(x not in op_set for x in args.operators):
        print("allowed operators:", "".join(op_set))
        exit(1)

    digits = [int(x) for x in args.values]
    selected_ops = [x for x in operators if x.symbol in args.operators]

    res = train_game(digits, args.target, selected_ops)
    for r in sorted(res):
        print(r)
