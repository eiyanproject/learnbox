#ifndef BAG_H
#define BAG_H

#include <cstddef>
#include <string>
#include <vector>

std::vector<int> evens_in(const std::vector<int>& values);
int sum(const std::vector<int>& values);
std::vector<int> sorted_copy(std::vector<int> values);
int count_longer_than(const std::vector<std::string>& words, std::size_t n);
bool contains(const std::vector<int>& values, int target);

#endif
