#include "ctest.h"
#include "tally.h"

TEST(a_clear_favourite) {
    ASSERT_STR_EQ("tea", most_common({"tea", "coffee", "tea"}).c_str());
}

TEST(level_words_go_alphabetically) {
    ASSERT_STR_EQ("coffee", most_common({"tea", "coffee"}).c_str());
    ASSERT_STR_EQ("b", most_common({"c", "b", "c", "b", "a"}).c_str());
}

TEST(no_words) {
    ASSERT_STR_EQ("", most_common({}).c_str());
}

TEST(one_word) {
    ASSERT_STR_EQ("zed", most_common({"zed"}).c_str());
}

TEST(case_matters) {
    ASSERT_STR_EQ("tea", most_common({"Tea", "tea", "tea", "Tea", "tea"}).c_str());
}

TEST(a_big_count) {
    std::vector<std::string> words;
    for (int i = 0; i < 500; i++) {
        words.push_back("ana");
        words.push_back("bo");
    }
    words.push_back("bo");
    ASSERT_STR_EQ("bo", most_common(words).c_str());
}

TEST(most_common_leaves_its_input_alone) {
    std::vector<std::string> words = {"b", "a", "b"};
    most_common(words);
    ASSERT_STR_EQ("b", words[0].c_str());
    ASSERT_EQ_INT(3, (int)words.size());
}

TEST(unique_sorted_removes_repeats_and_sorts) {
    auto out = unique_sorted({3, 1, 3, 2, 1});
    ASSERT_EQ_INT(3, (int)out.size());
    ASSERT_EQ_INT(1, out[0]);
    ASSERT_EQ_INT(2, out[1]);
    ASSERT_EQ_INT(3, out[2]);
}

TEST(unique_sorted_of_nothing) {
    ASSERT_TRUE(unique_sorted({}).empty());
}

TEST(unique_sorted_with_negatives) {
    auto out = unique_sorted({0, -5, 7, -5, 0});
    ASSERT_TRUE((out == std::vector<int>{-5, 0, 7}));
}

TEST(unique_sorted_all_the_same) {
    ASSERT_TRUE((unique_sorted({4, 4, 4, 4}) == std::vector<int>{4}));
}

CTEST_MAIN
