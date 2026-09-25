#ifndef SHAPES_H
#define SHAPES_H

#include <memory>
#include <numbers>
#include <string>
#include <vector>

class Shape {
public:
    // Not optional: deleting a Circle through a Shape* without this is
    // undefined behaviour, and unique_ptr<Shape> does exactly that.
    virtual ~Shape() = default;

    virtual double area() const = 0;
    virtual std::string name() const = 0;

    // Non-virtual, but calls virtual functions: the derived versions run.
    std::string describe() const { return name() + ": " + std::to_string(area()); }
};

class Circle : public Shape {
public:
    explicit Circle(double radius) : radius_(radius) {}

    double area() const override { return std::numbers::pi * radius_ * radius_; }
    std::string name() const override { return "circle"; }

private:
    double radius_;
};

class Rect : public Shape {
public:
    Rect(double w, double h) : w_(w), h_(h) {}

    double area() const override { return w_ * h_; }
    std::string name() const override { return "rect"; }

private:
    double w_;
    double h_;
};

inline double total_area(const std::vector<std::unique_ptr<Shape>>& shapes) {
    double total = 0;
    for (const auto& shape : shapes) {
        total += shape->area(); // dispatched on the actual type
    }
    return total;
}

inline const Shape* largest(const std::vector<std::unique_ptr<Shape>>& shapes) {
    const Shape* best = nullptr;
    for (const auto& shape : shapes) {
        if (best == nullptr || shape->area() > best->area()) {
            best = shape.get();
        }
    }
    return best;
}

#endif
