class Expression:
    def __init__(self, a, operator, b):
        self.a = a
        self.operator = operator["key"]
        self.b = b
        self.value = operator["action"](a.value, b.value)

    def __str__(self):
        lhs = self.a
        if isinstance(lhs, Expression):
            lhs = "(" + str(self.a) + ")"
        rhs = self.b
        if isinstance(rhs, Expression):
            rhs = "(" + str(self.b) + ")"
        return f"{lhs} {self.operator} {rhs}"

    def __repr__(self):
        return str(self)


class Integer:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self)


def train_game(digits, target, operators):
    def try_operator(nums, i, j, operator):
        nums2 = list(nums)
        a = nums[i]
        b = nums[j]
        if "check" in operator:
            if not operator["check"](a.value, b.value):
                return
        new_expr = Expression(a, operator, b)
        nums2[i] = new_expr
        nums2.pop(j)
        find_combo(nums2)

    found = set()

    def find_combo(nums):
        if len(nums) == 0:
            raise ValueError("Missing numbers")
        if len(nums) == 1:
            if nums[0].value == target:
                found.add(str(nums[0]))
            return

        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                for operator in operators:
                    try_operator(nums, i, j, operator)
                    if not operator.get("commutative"):
                        try_operator(nums, j, i, operator)

    find_combo([Integer(n) for n in digits])

    return list(found)


operators = [
    {"key": "+", "action": lambda a, b: a + b, "commutative": True},
    {"key": "-", "action": lambda a, b: a - b},
    {"key": "*", "action": lambda a, b: a * b, "commutative": True},
    {"key": "/", "action": lambda a, b: a / b, "check": lambda a, b: b != 0},
    {
        "key": "^",
        "action": lambda a, b: a**b,
        "check": lambda a, b: abs(b) <= 10
        and not (a == 0 and b <= 0)
        and not (a < 0 and int(b) != b),
    },
]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("nums")
    parser.add_argument("--target", type=int, default=10)
    parser.add_argument("--operators", default="+-*/")
    args = parser.parse_args()

    if len(args.nums) != 4 or not args.nums.isdigit():
        print("enter 4 digits")
        exit(1)

    op_set = [x["key"] for x in operators]

    if any(x not in op_set for x in args.operators):
        print("allowed operators:", "".join(op_set))
        exit(1)

    digits = [int(x) for x in args.nums]
    selected_operators = [x for x in operators if x["key"] in args.operators]

    res = train_game(digits, args.target, selected_operators)
    for r in sorted(res):
        print(r)
