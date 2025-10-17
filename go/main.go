package main

import (
	"fmt"
	"reflect"
)

func initiate() {
	
	log_path := "logs/"

	typeofvar := reflect.TypeOf(log_path).Kind()

	fmt.Println(typeofvar)
}

func main() {
	initiate()
}