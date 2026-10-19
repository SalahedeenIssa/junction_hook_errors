/* Exhaustive search for the minimum weight elements of a coset seed + span(F_1, ..., F_m) over GF(2).
 *
 * Input (stdin):  m seed F_1 ... F_m, as unsigned 64-bit integers (bit q = data qubit q).
 * Output (stdout): the minimum weight w and the number of minimum weight elements, then those elements.
 *
 * With F_i the stabilizers of the triangular color code and seed any logical operator, the output is every
 * minimum weight logical operator. The 2^m elements are visited in Gray-code order, so each step is one XOR.
 * Used by jhe/logicals.py for d = 7 (m = 18) and d = 9 (m = 30). */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

int main(void) {
    int m;
    unsigned long long seed, F[64];
    if (scanf("%d %llu", &m, &seed) != 2 || m < 1 || m > 63) return 1;
    for (int i = 0; i < m; i++)
        if (scanf("%llu", &F[i]) != 1) return 1;
    unsigned long long cur = seed;
    int best = __builtin_popcountll(cur);
    size_t cap = 1 << 20, cnt = 0;
    unsigned long long *out = malloc(cap * sizeof *out);
    if (!out) return 1;
    out[cnt++] = cur;
    unsigned long long N = 1ULL << m;
    for (unsigned long long k = 1; k < N; k++) {
        cur ^= F[__builtin_ctzll(k)];
        int w = __builtin_popcountll(cur);
        if (w < best) { best = w; cnt = 0; }
        if (w == best) {
            if (cnt == cap) {
                cap *= 2;
                out = realloc(out, cap * sizeof *out);
                if (!out) return 1;
            }
            out[cnt++] = cur;
        }
    }
    printf("%d %zu\n", best, cnt);
    for (size_t i = 0; i < cnt; i++) printf("%llu\n", out[i]);
    free(out);
    return 0;
}
