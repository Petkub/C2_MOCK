# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(620512)
MAXN, MAXK = 10 ** 6, 10 ** 18
D = "0123456789"
tests = []


def add(k, s):
    n = len(s)
    assert 1 <= n <= MAXN and 0 <= k <= MAXK
    assert all(c in D for c in s)
    tests.append(f"{n} {k}\n{s}\n")


def runs_inv(runs):
    """number of inversions (pairs i < j with s_i > s_j) of the string made of (digit, length) runs"""
    cnt = [0] * 10
    inv = 0
    for d, l in runs:
        inv += l * sum(cnt[d + 1:])
        cnt[d] += l
    return inv


def runs_str(runs):
    return "".join(str(d) * l for d, l in runs)


def rand_runs(n, maxlen, digits=D):
    runs, left = [], n
    while left:
        l = min(left, random.randint(1, maxlen))
        runs.append((int(random.choice(digits)), l))
        left -= l
    return runs


def rand_str(n, digits=D):
    return "".join(random.choices(digits, k=n))


def est_inv(n):
    """about the number of inversions of a random digit string of length n"""
    return int(0.45 * n * (n - 1) / 2)


# samples
add(3, "43021")
add(100, "3141")
add(10, "22222")
add(0, "987654")
add(15, "902418735160")
# hidden: small and medium (brute checks these)
add(0, "5")
add(MAXK, "10")
add(1, "3210")
add(5, "76543210")
add(7, rand_str(8))
add(12, rand_str(300))
add(5000, rand_str(2000))
r = rand_runs(3000, 30)
add(runs_inv(r) - 1, runs_str(r))
add(40, "9" * 50 + rand_str(1950, "012345678"))
add(MAXK, rand_str(20000, "0123"))
add(123456, rand_str(30000))
# hidden: big (N = 10^6)
N = MAXN
s = rand_str(N)
add(MAXK, s)                                           # everything sorted, far fewer swaps than K
for frac in (0.9, 0.5, 0.3, 0.2):                      # the budget runs out at different points
    add(int(frac * est_inv(N)) + random.randint(0, 10 ** 6), rand_str(N))
add(250000, "9" * 600000 + rand_str(N - 600000, "012345678"))    # small budget, smaller digits far away
add(200000, runs_str(sorted((int(c), 1) for c in rand_str(600000, "56789"))) + rand_str(N - 600000, "01234"))
rev = [(9 - d, N // 10) for d in range(10)]            # 99..988..8...00..0
add(runs_inv(rev) - 1, runs_str(rev))
add(runs_inv(rev) // 3, runs_str(rev))
add(MAXK, "7" * N)                                     # all equal
add(MAXK, runs_str([(d, N // 10) for d in range(10)]))  # already sorted
add(300000, "9" * 700000 + rand_str(N - 700000, "0123"))   # smaller digits just out of reach for a long time
r = rand_runs(N, 50)
add(runs_inv(r) - 1, runs_str(r))
r = rand_runs(N, 80)
add(runs_inv(r), runs_str(r))
r = rand_runs(N, 20)
add(runs_inv(r) + 1, runs_str(r))
per = [(d, 1) for d in range(9, -1, -1)] * (N // 10)    # 9876543210 repeated
add(int(runs_inv(per) * 0.7), runs_str(per))
r = rand_runs(N, 200, "000899999999")
add(12 * 10 ** 10, runs_str(r))
add(N - 2, "1" * (N - 1) + "0")                          # the 0 is one swap out of reach
add(N - 1, "1" * (N - 1) + "0")

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
