import random, os, math
random.seed(2617)
os.makedirs("tests", exist_ok=True)
cases = []
cases.append((2, [3, 5, 4, 8, 7, 6, 9]))
cases.append((0, [1, 1, 2, 2, 2, 1]))
cases.append((10, [-5, 5, -5, 5]))
cases.append((0, [42]))
cases.append((3, [10, 1, 2, 3, 4, 20, 21, 22, 23]))
for _ in range(6):
    n = random.randint(1, 15); cases.append((random.randint(0, 6), [random.randint(-6, 6) for _ in range(n)]))
B = 10**9
N = 100000
def rnd(n, K, lo, hi): return (K, [random.randint(lo, hi) for _ in range(n)])
def walk(n, K, step, start=0):
    t = [start]
    for _ in range(n - 1): t.append(max(-B, min(B, t[-1] + random.randint(-step, step))))
    return (K, t)
cases.append(rnd(3000, 100, -1000, 1000))
cases.append(rnd(N, B, -B, B))
cases.append(walk(N, 3000, 10))
cases.append(walk(N, 0, 1))
cases.append((2 * B, [random.choice([-B, B]) for _ in range(N)]))   # difference 2*10^9: whole array
cases.append((2 * B - 1, [-B] + [0] * (N - 2) + [B]))
cases.append((5, [i // 3 for i in range(N)]))                        # slow ramp
cases.append((10**6, [int(10**8 * math.sin(i / 5000)) for i in range(N)]))
for K, step in ((800, 5), (1500, 10), (160, 1), (3000, 20), (450, 3)):
    cases.append(walk(N, K, step))
cases.append((1, [0, 1] * (N // 2)))                                 # answer N, start 1
cases.append((3, [5] * 10 + [0, 9] * 50 + [5] * 10))                 # two equal best windows: take the left one
cases.append((N // 4, list(range(N))))                    # every window of length N/4+1 works
cases.append((N // 3, list(range(N, 0, -1))))
cases.append(walk(N, 20000, 300))
for K, step in ((150, 1), (240, 2), (4000, 25), (30000, 200)):     # long windows everywhere (sum of window lengths ~10^9+)
    cases.append(walk(N, K, step))
cases.append((N // 5, [i % (N // 2) for i in range(N)]))            # sawtooth
cases.append((N // 6, [(i * 7) % N if i % 1000 else i for i in range(N)][:0] + list(range(0, 2 * N, 2))))                          # long windows everywhere, answer in the middle
for _ in range(3):                                          # medium random data: resetting the window on violation is wrong
    cases.append((random.randint(3, 8), [random.randint(0, 10) for _ in range(random.randint(2000, 5000))]))
# ---- legacy strengthening (2026-10): the brute force that stops once the best can no longer be beaten scored 95%,
# because long windows were either the whole array or started near day 1. The new big tests have stable windows
# of about N/2 days everywhere and the (slightly longer) best one starting after day 0.4 N, so that brute does
# ~2 * 10^9 steps. The cases above are still generated so the unchanged tests keep their bytes; `override`
# replaces some of them, `extra` adds tests at the end. All new data comes from R, not from `random`.
R = random.Random(26172)
rr = R.random
def late(A, step, tail, s, sign=1, rand=False, jitter=0, n=N):
    """days rise (sign 1) or fall (-1) by `step` per day (random in [0, 2 step] if rand), the last `tail` days s times
    slower; K = (A - 1) * step, so windows are about A days long and the longest ones lie in the slow tail"""
    t = []; x = 0.0
    for i in range(n):
        t.append(int(x))
        st = step if i < n - tail else step * s
        x += (rr() * 2 * st) if rand else st
    if jitter:
        t = [v + int(rr() * (2 * jitter + 1)) - jitter for v in t]
    shift = -(max(t) + min(t)) // 2
    return (int(round((A - 1) * step)), [sign * (v + shift) for v in t])
override = {
    13: late(50000, 20000, 55000, 0.9),                          # values from -10^9 to 10^9: max - min near 2 * 10^9
    14: late(50000, 10, 52000, 0.92, rand=True),
    18: late(48000, 1 / 3, 55000, 0.9),                          # slow ramp (steps of 1 every 3 days)
    19: (lambda K, t: (K, [v + abs(i % 4000 - 2000) - 1000 for i, v in enumerate(t)]))(*late(50000, 1000, 54000, 0.9)),   # wavy ramp
    20: late(50000, 5, 55000, 0.9, rand=True),
    21: late(52000, 10, 56000, 0.93, sign=-1, rand=True),
    22: late(45000, 1, 54000, 0.85, rand=True),
    23: late(50000, 20, 55000, 0.9, rand=True, jitter=15),
    24: late(53000, 3, 56000, 0.95, sign=-1, rand=True),
    29: late(50000, 300, 55000, 0.9, rand=True),
    30: late(49000, 2, 54000, 0.9, rand=True),
    31: late(50000, 25, 55000, 0.9, sign=-1),
    32: late(51000, 200, 55000, 0.92, rand=True, jitter=100),
    33: late(50000, 7, 56000, 0.88, rand=True),
    34: late(47000, 100, 53000, 0.9, sign=-1, rand=True, jitter=40),
    27: (N // 2 - 1, list(range(N))),                            # every window of N/2 days works: take day 1
    35: late(50000, 2, 60000, 0.9),          # exact slopes: every window inside the tail has the same length: take the first
}
extra = [
    late(50000, 9000, 58000, 0.9, sign=-1),                      # large values, falling
    late(52000, 50, 57000, 0.94, rand=True),
]
for i, (K, t) in enumerate(cases + extra, 1):
    if i in override:
        K, t = override[i]
    assert 1 <= len(t) <= N and 0 <= K <= 2 * B and -B <= min(t) and max(t) <= B
    open(f"tests/{i:02d}.in", "w").write(f"{len(t)} {K}\n" + " ".join(map(str, t)) + "\n")
assert len(cases) + len(extra) <= 40
print(len(cases) + len(extra), "tests")
