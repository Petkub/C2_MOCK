# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# Integers only: every random value comes from getrandbits / randrange (no floating point).
import os, random

r = random.Random(31203)
MAXN = 500000
tests = []

# a byte b (0..255) becomes a teacher if b < t0, a red student if b < t0 + t1, else a blue student
TABLES = {}


def seg(n, t0, t1):
    """n people at random; teacher with chance t0/256, red with chance t1/256, blue otherwise"""
    key = (t0, t1)
    if key not in TABLES:
        TABLES[key] = bytes(48 if b < t0 else 49 if b < t0 + t1 else 50 for b in range(256))
    raw = r.getrandbits(8 * n).to_bytes(n, "little") if n else b""
    return raw.translate(TABLES[key]).decode()


def rep(s, k):
    return s * k


def add(s):
    n = len(s)
    assert 1 <= n <= MAXN
    assert set(s) <= set("012")
    tests.append("%d\n%s\n" % (n, " ".join(s)))


# samples
add("20102")
add("220112")
add("102002")
add("0102011")
add("201102101011")

# hidden: small (brute runs BFS on N <= 9)
add("0")
add("1")
add("21")
add("000")
add("2121")
add("200001")
add("021021021")
add(seg(9, 100, 78))
add(seg(300, 85, 85))
add(seg(2000, 30, 113))
add(seg(1500, 128, 64) + seg(1500, 128, 0) + seg(1500, 128, 128))

# hidden: big (every big test has at least 100 000 teachers)
add(seg(MAXN, 86, 85))                                            # uniform mix
add(seg(MAXN, 128, 64))                                           # many teachers
add(seg(MAXN, 210, 23))                                           # mostly teachers
add(seg(MAXN // 2, 64, 0) + seg(MAXN // 2, 64, 192))              # blues + teachers, then reds + teachers
add(seg(200000, 0, 0) + seg(100000, 256, 0) + seg(200000, 0, 256))  # 200 000 blues, teachers, 200 000 reds
add(seg(150000, 0, 256) + seg(200000, 256, 0) + seg(150000, 0, 0))  # already in order
add(seg(MAXN // 4, 60, 190) + seg(MAXN // 2, 60, 6) + seg(MAXN // 4, 60, 190))
add(seg(MAXN // 4, 60, 6) + seg(MAXN // 2, 60, 190) + seg(MAXN // 4, 60, 6))
add(seg(MAXN // 3, 96, 150) + seg(MAXN // 3, 96, 80) + seg(MAXN - 2 * (MAXN // 3), 96, 10))
add(rep("201", MAXN // 3) + "02")                                 # periodic
add(rep("2001", MAXN // 4))                                       # teachers with equal choices
add(rep("1020", MAXN // 4))
add(seg(MAXN, 100, 140))
add(seg(MAXN, 100, 16))
add("".join(seg(10000, 77, (i * 37) % 179) for i in range(MAXN // 10000)))   # many blocks
add("2" * 250000 + "0" * 100000 + "1" * 150000)                  # huge answer
add(seg(MAXN, 140, 58))

for t in tests:
    if len(t) > 100000:
        assert t.count("0") >= 100000
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open("tests/%02d.in" % i, "w") as f:
        f.write(t)
