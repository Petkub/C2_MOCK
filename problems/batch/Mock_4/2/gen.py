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
for i, (K, t) in enumerate(cases, 1):
    assert 1 <= len(t) <= N and 0 <= K <= 2 * B and all(abs(x) <= B for x in t)
    open(f"tests/{i:02d}.in", "w").write(f"{len(t)} {K}\n" + " ".join(map(str, t)) + "\n")
print(len(cases), "tests")
