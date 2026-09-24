/*
 * ctest - a single-header test framework for the learnbox C and C++ lessons.
 *
 * There is no Check, no CUnit, no gtest: one header keeps the container small
 * and means a lesson compiles with nothing but gcc. It writes JUnit XML, which
 * the runner already parses for pytest and JUnit, so C tests come back per
 * test with no new parsing code.
 *
 * Usage:
 *
 *     #include "ctest.h"
 *
 *     TEST(adds_two_numbers) {
 *         ASSERT_EQ_INT(5, add(2, 3));
 *     }
 *
 *     CTEST_MAIN
 *
 * Tests register themselves through a constructor attribute, so there is no
 * list to keep in sync - adding a TEST is the whole of adding a test.
 */
#ifndef LEARNBOX_CTEST_H
#define LEARNBOX_CTEST_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#ifdef __cplusplus
extern "C" {
#endif

#define CT_MAX_TESTS 256
#define CT_MSG_LEN 512

typedef void (*ct_fn)(void);

typedef struct {
    const char *name;
    ct_fn fn;
} ct_case;

/* Defined once by CTEST_MAIN. */
extern ct_case ct_cases[CT_MAX_TESTS];
extern int ct_count;
extern int ct_failed_current;
extern char ct_message[CT_MSG_LEN];

static void ct_register(const char *name, ct_fn fn);

/*
 * A test is a function plus a constructor that registers it before main runs.
 * The constructor attribute is a GCC/Clang extension, which is fine: these
 * lessons are compiled by gcc on Linux and nothing else.
 */
#define TEST(name)                                                          \
    static void ct_test_##name(void);                                       \
    __attribute__((constructor)) static void ct_reg_##name(void) {          \
        ct_register(#name, ct_test_##name);                                 \
    }                                                                       \
    static void ct_test_##name(void)

/* ---------- assertions ---------- */

#define CT_FAIL(...)                                                        \
    do {                                                                    \
        if (!ct_failed_current) {                                           \
            ct_failed_current = 1;                                          \
            snprintf(ct_message, CT_MSG_LEN, __VA_ARGS__);                  \
        }                                                                   \
        return;                                                             \
    } while (0)

#define ASSERT_TRUE(expr)                                                   \
    do {                                                                    \
        if (!(expr)) {                                                      \
            CT_FAIL("%s:%d: expected %s to be true", __FILE__, __LINE__, #expr); \
        }                                                                   \
    } while (0)

#define ASSERT_FALSE(expr)                                                  \
    do {                                                                    \
        if (expr) {                                                         \
            CT_FAIL("%s:%d: expected %s to be false", __FILE__, __LINE__, #expr); \
        }                                                                   \
    } while (0)

#define ASSERT_EQ_INT(expected, actual)                                     \
    do {                                                                    \
        long long ct_e = (long long)(expected), ct_a = (long long)(actual); \
        if (ct_e != ct_a) {                                                 \
            CT_FAIL("%s:%d: expected %lld, got %lld", __FILE__, __LINE__, ct_e, ct_a); \
        }                                                                   \
    } while (0)

#define ASSERT_NEAR(expected, actual, tol)                                  \
    do {                                                                    \
        double ct_e = (double)(expected), ct_a = (double)(actual);           \
        if (fabs(ct_e - ct_a) > (double)(tol)) {                            \
            CT_FAIL("%s:%d: expected %g, got %g", __FILE__, __LINE__, ct_e, ct_a); \
        }                                                                   \
    } while (0)

#define ASSERT_STR_EQ(expected, actual)                                     \
    do {                                                                    \
        const char *ct_e = (expected), *ct_a = (actual);                    \
        if (ct_a == NULL || strcmp(ct_e, ct_a) != 0) {                      \
            CT_FAIL("%s:%d: expected \"%s\", got \"%s\"", __FILE__, __LINE__, \
                    ct_e, ct_a ? ct_a : "(null)");                          \
        }                                                                   \
    } while (0)

#define ASSERT_NULL(ptr)                                                    \
    do {                                                                    \
        if ((ptr) != NULL) {                                                \
            CT_FAIL("%s:%d: expected %s to be NULL", __FILE__, __LINE__, #ptr); \
        }                                                                   \
    } while (0)

#define ASSERT_NOT_NULL(ptr)                                                \
    do {                                                                    \
        if ((ptr) == NULL) {                                                \
            CT_FAIL("%s:%d: expected %s not to be NULL", __FILE__, __LINE__, #ptr); \
        }                                                                   \
    } while (0)

/* ---------- the runner ---------- */

static void ct_register(const char *name, ct_fn fn) {
    if (ct_count < CT_MAX_TESTS) {
        ct_cases[ct_count].name = name;
        ct_cases[ct_count].fn = fn;
        ct_count++;
    }
}

/* XML needs five characters escaped; a failure message can contain any of them. */
static void ct_escape(FILE *out, const char *s) {
    for (; *s; s++) {
        switch (*s) {
            case '&':  fputs("&amp;", out); break;
            case '<':  fputs("&lt;", out); break;
            case '>':  fputs("&gt;", out); break;
            case '"':  fputs("&quot;", out); break;
            case '\'': fputs("&apos;", out); break;
            default:   fputc(*s, out);
        }
    }
}

static int ct_run_all(void) {
    int failures = 0;
    FILE *xml = fopen("TEST-ctest.xml", "w");

    for (int i = 0; i < ct_count; i++) {
        ct_failed_current = 0;
        ct_message[0] = '\0';
        ct_cases[i].fn();
        if (ct_failed_current) {
            failures++;
            printf("FAIL %s\n     %s\n", ct_cases[i].name, ct_message);
        } else {
            printf("ok   %s\n", ct_cases[i].name);
        }
        if (xml) {
            /* Buffered into the file as we go, so a crash still leaves the
               tests that already ran - which is what you want when the bug
               under test is a segfault. */
            fprintf(xml, "  <testcase classname=\"ctest\" name=\"");
            ct_escape(xml, ct_cases[i].name);
            fputs("\"", xml);
            if (ct_failed_current) {
                fputs("><failure message=\"", xml);
                ct_escape(xml, ct_message);
                fputs("\"></failure></testcase>\n", xml);
            } else {
                fputs("/>\n", xml);
            }
        }
    }

    printf("\n%d tests, %d failed\n", ct_count, failures);
    if (xml) {
        fclose(xml);
        /* Rewrite with the wrapper element now that the counts are known. */
        FILE *body = fopen("TEST-ctest.xml", "r");
        FILE *final = fopen("TEST-ctest-final.xml", "w");
        if (body && final) {
            fprintf(final, "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
            fprintf(final, "<testsuite name=\"ctest\" tests=\"%d\" failures=\"%d\">\n",
                    ct_count, failures);
            int c;
            while ((c = fgetc(body)) != EOF) {
                fputc(c, final);
            }
            fputs("</testsuite>\n", final);
        }
        if (body) fclose(body);
        if (final) fclose(final);
        remove("TEST-ctest.xml");
        rename("TEST-ctest-final.xml", "TEST-ctest.xml");
    }
    return failures == 0 ? 0 : 1;
}

#ifdef __cplusplus
}
#endif

/* Placed once, in the test file. */
#define CTEST_MAIN                                                          \
    ct_case ct_cases[CT_MAX_TESTS];                                         \
    int ct_count = 0;                                                       \
    int ct_failed_current = 0;                                              \
    char ct_message[CT_MSG_LEN];                                            \
    int main(void) { return ct_run_all(); }

#endif /* LEARNBOX_CTEST_H */
