#include "ctest.h"
#include "shapes.h"

#include <memory>
#include <numbers>
#include <type_traits>
#include <vector>

TEST(circle_area) {
    ASSERT_NEAR(std::numbers::pi * 4, Circle(2).area(), 0.0001);
}

TEST(rect_area) {
    ASSERT_NEAR(12.0, Rect(3, 4).area(), 0.0001);
}

TEST(names_come_from_the_derived_classes) {
    ASSERT_STR_EQ("circle", Circle(1).name().c_str());
    ASSERT_STR_EQ("rect", Rect(1, 1).name().c_str());
}

TEST(a_base_pointer_dispatches_to_the_derived_type) {
    std::unique_ptr<Shape> s = std::make_unique<Rect>(3, 4);
    ASSERT_NEAR(12.0, s->area(), 0.0001);
    ASSERT_STR_EQ("rect", s->name().c_str());
}

TEST(describe_calls_the_overridden_functions) {
    std::unique_ptr<Shape> s = std::make_unique<Rect>(2, 2);
    ASSERT_EQ_INT(0, (int)s->describe().rfind("rect: ", 0));
}

TEST(total_area_sums_through_base_pointers) {
    std::vector<std::unique_ptr<Shape>> shapes;
    shapes.push_back(std::make_unique<Rect>(2, 3));
    shapes.push_back(std::make_unique<Rect>(1, 4));
    ASSERT_NEAR(10.0, total_area(shapes), 0.0001);
}

TEST(total_area_mixes_types) {
    std::vector<std::unique_ptr<Shape>> shapes;
    shapes.push_back(std::make_unique<Rect>(2, 2));
    shapes.push_back(std::make_unique<Circle>(1));
    ASSERT_NEAR(4.0 + std::numbers::pi, total_area(shapes), 0.0001);
}

TEST(total_area_of_nothing) {
    std::vector<std::unique_ptr<Shape>> shapes;
    ASSERT_NEAR(0.0, total_area(shapes), 0.0001);
}

TEST(largest_finds_the_biggest) {
    std::vector<std::unique_ptr<Shape>> shapes;
    shapes.push_back(std::make_unique<Rect>(1, 1));
    shapes.push_back(std::make_unique<Rect>(5, 5));
    shapes.push_back(std::make_unique<Rect>(2, 2));
    ASSERT_NEAR(25.0, largest(shapes)->area(), 0.0001);
}

TEST(largest_of_nothing_is_null) {
    std::vector<std::unique_ptr<Shape>> shapes;
    ASSERT_NULL((void *)largest(shapes));
}

TEST(the_destructor_is_virtual) {
    /* If it were not, this delete would destroy only the base part. */
    ASSERT_TRUE(std::has_virtual_destructor<Shape>::value);
}

TEST(shape_cannot_be_instantiated) {
    ASSERT_TRUE(std::is_abstract<Shape>::value);
}

CTEST_MAIN
