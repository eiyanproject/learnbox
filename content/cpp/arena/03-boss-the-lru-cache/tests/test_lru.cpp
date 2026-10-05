#include "ctest.h"
#include "lru.h"

using Keys = std::vector<std::string>;

TEST(starts_empty) {
    LruCache cache(3);
    ASSERT_EQ_INT(0, (int)cache.size());
    ASSERT_TRUE(cache.keys().empty());
    ASSERT_FALSE(cache.contains("a"));
    ASSERT_FALSE(cache.get("a").has_value());
}

TEST(put_then_get) {
    LruCache cache(3);
    cache.put("a", 1);
    cache.put("b", 2);
    ASSERT_EQ_INT(2, (int)cache.size());
    ASSERT_TRUE(cache.get("a") == std::optional<int>(1));
    ASSERT_TRUE(cache.get("b") == std::optional<int>(2));
}

TEST(keys_run_from_most_recent_to_least) {
    LruCache cache(3);
    cache.put("a", 1);
    cache.put("b", 2);
    cache.put("c", 3);
    ASSERT_TRUE((cache.keys() == Keys{"c", "b", "a"}));
}

TEST(the_least_recent_is_evicted) {
    LruCache cache(2);
    cache.put("a", 1);
    cache.put("b", 2);
    cache.put("c", 3);
    ASSERT_EQ_INT(2, (int)cache.size());
    ASSERT_FALSE(cache.contains("a"));
    ASSERT_FALSE(cache.get("a").has_value());
    ASSERT_TRUE((cache.keys() == Keys{"c", "b"}));
}

TEST(get_counts_as_a_use) {
    LruCache cache(2);
    cache.put("a", 1);
    cache.put("b", 2);
    ASSERT_TRUE(cache.get("a") == std::optional<int>(1));
    cache.put("c", 3);
    ASSERT_TRUE(cache.contains("a"));
    ASSERT_FALSE(cache.contains("b"));
    ASSERT_TRUE((cache.keys() == Keys{"c", "a"}));
}

TEST(a_miss_changes_nothing) {
    LruCache cache(2);
    cache.put("a", 1);
    cache.put("b", 2);
    ASSERT_FALSE(cache.get("zzz").has_value());
    ASSERT_TRUE((cache.keys() == Keys{"b", "a"}));
    ASSERT_EQ_INT(2, (int)cache.size());
}

TEST(contains_does_not_count_as_a_use) {
    LruCache cache(2);
    cache.put("a", 1);
    cache.put("b", 2);
    ASSERT_TRUE(cache.contains("a"));
    cache.put("c", 3);
    ASSERT_FALSE(cache.contains("a"));
    ASSERT_TRUE(cache.contains("b"));
}

TEST(put_on_an_existing_key_replaces_and_refreshes) {
    LruCache cache(2);
    cache.put("a", 1);
    cache.put("b", 2);
    cache.put("a", 10);
    ASSERT_EQ_INT(2, (int)cache.size());
    ASSERT_TRUE((cache.keys() == Keys{"a", "b"}));
    cache.put("c", 3);
    ASSERT_FALSE(cache.contains("b"));
    ASSERT_TRUE(cache.get("a") == std::optional<int>(10));
}

TEST(capacity_one) {
    LruCache cache(1);
    cache.put("a", 1);
    cache.put("b", 2);
    ASSERT_EQ_INT(1, (int)cache.size());
    ASSERT_FALSE(cache.contains("a"));
    ASSERT_TRUE(cache.get("b") == std::optional<int>(2));
    cache.put("b", 3);
    ASSERT_EQ_INT(1, (int)cache.size());
    ASSERT_TRUE(cache.get("b") == std::optional<int>(3));
}

TEST(capacity_zero_stores_nothing) {
    LruCache cache(0);
    cache.put("a", 1);
    ASSERT_EQ_INT(0, (int)cache.size());
    ASSERT_FALSE(cache.contains("a"));
    ASSERT_FALSE(cache.get("a").has_value());
}

TEST(zero_is_a_value_not_a_miss) {
    LruCache cache(2);
    cache.put("zero", 0);
    auto got = cache.get("zero");
    ASSERT_TRUE(got.has_value());
    ASSERT_EQ_INT(0, *got);
}

TEST(two_caches_do_not_share) {
    LruCache a(2);
    LruCache b(2);
    a.put("x", 1);
    ASSERT_FALSE(b.contains("x"));
    ASSERT_EQ_INT(0, (int)b.size());
}

TEST(a_long_run_keeps_exactly_the_newest) {
    LruCache cache(50);
    for (int i = 0; i < 5000; i++) {
        cache.put("k" + std::to_string(i), i);
    }
    ASSERT_EQ_INT(50, (int)cache.size());
    ASSERT_FALSE(cache.contains("k4949"));
    ASSERT_TRUE(cache.contains("k4950"));
    ASSERT_TRUE(cache.get("k4999") == std::optional<int>(4999));
    auto keys = cache.keys();
    ASSERT_TRUE(keys.front() == "k4999");
    ASSERT_TRUE(keys.back() == "k4950");
}

CTEST_MAIN
