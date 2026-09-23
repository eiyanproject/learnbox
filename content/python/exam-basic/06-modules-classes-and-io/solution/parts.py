class Shape:
    created = 0

    def __init__(self, name):
        self.name = name
        Shape.created += 1

    def area(self):
        raise NotImplementedError


class Rect(Shape):
    def __init__(self, w, h):
        super().__init__("rect")
        self.w = w
        self.h = h

    def area(self):
        return self.w * self.h


def save_lines(path, lines):
    with open(path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(f"{line}\n")


def load_lines(path):
    with open(path, encoding="utf-8") as f:
        return [line.rstrip("\n") for line in f]


def render(name, score):
    return f"{name:<10}{score:>6.1f}"
