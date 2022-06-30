package traingame

import (
	"fmt"
	"strconv"
)

type Value interface {
	Value() int
	ToString() string
}

type Expression struct {
	left     Value
	right    Value
	operator string
}

type IntegerValue struct {
	value int
}

func (r *Expression) Value() int {
	leftValue := r.left.Value()
	rightValue := r.right.Value()
	switch r.operator {
	case "+":
		return leftValue + rightValue
	case "-":
		return leftValue - rightValue
	case "*":
		return leftValue * rightValue
	case "/":
		return leftValue / rightValue
	}
	panic("Unknown operator: " + r.operator)
}

func (r *Expression) ToString() string {
	leftStr := r.left.ToString()
	rightStr := r.right.ToString()
	switch r.left.(type) {
	case *Expression:
		leftStr = "(" + leftStr + ")"
	}
	switch r.right.(type) {
	case *Expression:
		rightStr = "(" + rightStr + ")"
	}
	return fmt.Sprintf("%s %s %s", leftStr, r.operator, rightStr)
}

func (r *IntegerValue) Value() int {
	return r.value
}

func (r *IntegerValue) ToString() string {
	return strconv.Itoa(r.value)
}
