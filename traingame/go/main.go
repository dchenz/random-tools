package main

import (
	"flag"
	"fmt"
	"os"
	"strconv"
	"traingame/traingame"
)

func main() {
	digitString := flag.String("digits", "", "Four digits from the train carriage")
	target := flag.Int("target", 10, "The number we're trying to get")
	flag.Parse()

	if len(*digitString) != 4 {
		fmt.Println("Usage: ./prog --digits 1234 --target 10")
		os.Exit(1)
	}

	digits := make([]int, 4)
	for i, v := range *digitString {
		d, e := strconv.Atoi(string(v))
		if e != nil {
			fmt.Println("Usage: ./prog --digits 1234 --target 10")
			os.Exit(1)
		}
		digits[i] = d
	}

	found := traingame.TrainGame(digits, *target)
	for _, v := range found {
		fmt.Println(v)
	}
}
