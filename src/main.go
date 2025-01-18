package main

import (
	"fmt"
)

type Developer struct {
	Name        string
	Communities []string
	Experiences []string
	Hobbies     []string
	Cats        []struct {
		Name string
		Role string
	}
}

func (d *Developer) Print() {
	fmt.Printf("👋 %s\n\n", d.Name)

	fmt.Println("🏢 Communities:")
	for _, c := range d.Communities {
		fmt.Printf("  %s\n", c)
	}

	fmt.Println("\n💼 Experiences:")
	for _, e := range d.Experiences {
		fmt.Printf("  %s\n", e)
	}

	fmt.Println("\n🎨 Hobbies:")
	for _, h := range d.Hobbies {
		fmt.Printf("  %s\n", h)
	}

	fmt.Println("\n😺 Cats:")
	for _, c := range d.Cats {
		fmt.Printf("  %s: %s\n", c.Name, c.Role)
	}
}

func NewDeveloper() *Developer {
	return &Developer{
		Name: "👵 Misato 👵",
		Communities: []string{
			"SingularitySociety 🚀",
			"WomenWhoGo Tokyo 🦫",
			"42 Tokyo 🎮",
		},
		Experiences: []string{
			"System Development 💻",
			"Infrastructure Management 🛠️",
			"BI & Data Operations 📊",
			"Security Product Support 🔐",
			"Support Center Leadership 🎯",
		},
		Hobbies: []string{
			"Mountain Climbing 🏔️",
			"Knitting 🧶",
			"Piano 🎹",
			"Tennis 🎾",
			"Boy Scouts ⛺",
		},
		Cats: []struct {
			Name string
			Role string
		}{
			{Name: "Nyan1-Go", Role: "Senior Bug Hunter 🐱"},
			{Name: "Nyan2-Go", Role: "Chief Nap Officer 🐱"},
		},
	}
}

func main() {
	developer := NewDeveloper()
	developer.Print()
}
