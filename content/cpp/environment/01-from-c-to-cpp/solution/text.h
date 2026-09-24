#ifndef TEXT_H
#define TEXT_H

#include <string>
#include <vector>

std::string join(const std::vector<std::string>& parts, const std::string& sep);
int word_count(const std::string& text);
std::string to_upper(std::string text);
std::string longest(const std::vector<std::string>& parts);

#endif
