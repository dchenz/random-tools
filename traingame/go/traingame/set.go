package traingame

type StringSet struct {
	elements map[string]struct{}
}

func (r *StringSet) Add(value string) {
	r.elements[value] = struct{}{}
}

func (r *StringSet) Remove(value string) {
	delete(r.elements, value)
}

func (r *StringSet) AsArray() []string {
	arr := make([]string, len(r.elements))
	p := 0
	for k := range r.elements {
		arr[p] = k
		p++
	}
	return arr
}

func NewStringSet() *StringSet {
	s := StringSet{
		elements: make(map[string]struct{}),
	}
	return &s
}
