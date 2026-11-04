# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1102)
MAXN, MAXK, MAXW, MAXF, MAXE = 200000, 100, 10 ** 6, 10 ** 6, 10 ** 9
tests = []
rnd = random.random


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(w, trucks):
    n, k = len(w), len(trucks)
    assert 1 <= n <= MAXN and 1 <= k <= MAXK
    assert all(1 <= x <= MAXW for x in w)
    for c, f, e in trucks:
        assert 1 <= c <= n and 1 <= f <= MAXF and 0 <= e <= MAXE
    lines = [f"{n} {k}", " ".join(map(str, w))] + [f"{c} {f} {e}" for c, f, e in trucks]
    tests.append("\n".join(lines) + "\n")


def caps(n, k, lo, hi):
    """k capacities, each between lo and hi times n / k (at least 1, at most n)"""
    return [max(1, min(n, int(n / k * (lo + (hi - lo) * rnd())))) for _ in range(k)]


def weights(n, kind):
    if kind == "rand":
        return [ri(1, MAXW) for _ in range(n)]
    if kind == "max":
        return [MAXW] * n
    if kind == "small":
        return [ri(1, 10) for _ in range(n)]
    if kind == "blocks":      # long runs of heavy and light crates
        w = []
        while len(w) < n:
            v = MAXW if rnd() < 0.5 else ri(1, 100)
            w += [max(1, min(MAXW, v - ri(0, 50))) for _ in range(ri(1, max(1, n // 40)))]
        return w[:n]
    if kind == "inc":
        return sorted(ri(1, MAXW) for _ in range(n))
    if kind == "dec":
        return sorted((ri(1, MAXW) for _ in range(n)), reverse=True)
    raise ValueError(kind)


def trucks_from(cs, fkind, ekind):
    k = len(cs)
    if fkind == "rand":
        fs = [ri(1, MAXF) for _ in range(k)]
    elif fkind == "alt":       # cheap and expensive trucks alternate
        fs = [ri(1, 1000) if j % 2 else ri(MAXF - 1000, MAXF) for j in range(k)]
    elif fkind == "dec":       # later trucks are cheaper
        fs = sorted((ri(1, MAXF) for _ in range(k)), reverse=True)
    elif fkind == "inc":
        fs = sorted(ri(1, MAXF) for _ in range(k))
    elif fkind == "max":
        fs = [MAXF] * k
    elif fkind == "small":
        fs = [ri(1, 5) for _ in range(k)]
    elif fkind == "close":     # nearly equal prices: the fees decide
        base = ri(MAXF // 2, MAXF - 100)
        fs = [base + ri(0, 100) for _ in range(k)]
    else:
        raise ValueError(fkind)
    if ekind == "rand":
        es = [ri(0, MAXE) for _ in range(k)]
    elif ekind == "zero":
        es = [0] * k
    elif ekind == "max":
        es = [MAXE] * k
    elif ekind == "mix":
        es = [0 if rnd() < 0.3 else ri(0, MAXE) for _ in range(k)]
    elif ekind == "small":
        es = [ri(0, 20) for _ in range(k)]
    else:
        raise ValueError(ekind)
    return list(zip(cs, fs, es))


def rand_case(n, k, lo, hi, wk="rand", fk="rand", ek="rand"):
    add(weights(n, wk), trucks_from(caps(n, k, lo, hi), fk, ek))


# samples
add([4, 1, 3, 5, 2, 2], [(4, 4, 2), (2, 1, 0), (2, 2, 2)])
add([2, 7, 7, 2], [(3, 1, 50), (2, 2, 1), (2, 2, 1)])
add([1, 1, 1, 1, 1], [(2, 1, 0), (2, 1, 0)])
add([10], [(1, 5, 0), (1, 1, 100), (1, 3, 0)])
add([3, 8, 1, 6, 2, 9, 4, 4], [(3, 2, 5), (4, 3, 0), (2, 1, 9), (3, 2, 1)])
# hidden: small and medium (brute checks these)
for n, k in ((1, 1), (7, 5), (30, 8), (60, 12)):
    w = [ri(1, 20) for _ in range(n)]
    add(w, [(ri(1, n), ri(1, 10), ri(0, 60)) for _ in range(k)] if n > 1 else [(1, 7, 3)])
add(weights(300, "rand"), trucks_from(caps(300, 20, 0.6, 2.0), "rand", "rand"))
add(weights(2000, "blocks"), trucks_from(caps(2000, 100, 0.5, 2.5), "alt", "mix"))
add(weights(2000, "small"), trucks_from(caps(2000, 60, 0.8, 1.6), "small", "max"))
add(weights(1500, "max"), trucks_from(caps(1500, 100, 1.0, 1.6), "max", "max"))
# hidden: big
N = MAXN
rand_case(N, 100, 0.5, 2.5)
rand_case(N, 100, 0.8, 1.6, "blocks", "alt", "mix")
rand_case(N, 100, 1.0, 1.3, "rand", "close", "rand")
rand_case(N, 100, 0.2, 4.0, "inc", "dec", "small")
rand_case(N, 100, 0.5, 3.0, "dec", "inc", "zero")
rand_case(N, 100, 1.0, 2.0, "max", "max", "max")
rand_case(N, 100, 0.9, 1.5, "small", "small", "max")
rand_case(N, 50, 0.5, 2.5, "blocks", "rand", "mix")
add(weights(N, "rand"), trucks_from([N] * 100, "rand", "rand"))          # every truck could take everything
add(weights(N, "blocks"), trucks_from([ri(1, N) for _ in range(100)], "alt", "zero"))
add(weights(N, "max"), trucks_from([N // 2 + 1, N // 2 + 1], "rand", "rand"))
add(weights(N, "rand"), trucks_from([N], "rand", "max"))
cs = [N // 100] * 100                                                       # exactly enough room
add(weights(N, "rand"), trucks_from(cs, "rand", "rand"))
cs = [N // 100] * 100
cs[ri(0, 99)] -= 1                                                          # one crate too many
add(weights(N, "blocks"), trucks_from(cs, "alt", "rand"))
cs = [ri(1, 10) for _ in range(90)] + [ri(N // 8, N // 4) for _ in range(10)]
random.shuffle(cs)
add(weights(N, "rand"), trucks_from(cs, "rand", "mix"))
rand_case(N, 100, 0.95, 1.1, "blocks", "dec", "small")
rand_case(N, 100, 1.5, 3.0, "rand", "alt", "max")
rand_case(N, 100, 0.5, 2.0, "dec", "close", "small")

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
