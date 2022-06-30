package traingame

import "sort"

func TrainGame(digits []int, target int) []string {

	found := NewStringSet()

	digitValues := make([]Value, len(digits))
	for i, v := range digits {
		digitValues[i] = &IntegerValue{
			value: v,
		}
	}

	findCombo(digitValues, target, found)
	foundUnique := found.AsArray()
	sort.Strings(foundUnique)

	return foundUnique
}

func findCombo(nums []Value, target int, found *StringSet) {
	if len(nums) == 0 {
		panic("Missing digits")
	}
	if len(nums) == 1 && nums[0].Value() == target {
		found.Add(nums[0].ToString())
		return
	}

	tryOperator := func(lo int, hi int, operator string) {
		left := nums[lo]
		right := nums[hi]
		if operator == "/" && right.Value() == 0 {
			return
		}
		nums2 := make([]Value, len(nums)-1)
		p := 0
		for i, v := range nums {
			if i == lo {
				nums2[p] = &Expression{
					left:     left,
					right:    right,
					operator: operator,
				}
				p++
			} else if i != hi {
				nums2[p] = v
				p++
			}
		}
		findCombo(nums2, target, found)
	}

	for i := 0; i < len(nums); i++ {
		for j := i + 1; j < len(nums); j++ {
			tryOperator(i, j, "+")
			tryOperator(i, j, "-")
			tryOperator(j, i, "-")
			tryOperator(i, j, "*")
			tryOperator(i, j, "/")
			tryOperator(j, i, "/")
		}
	}
}
