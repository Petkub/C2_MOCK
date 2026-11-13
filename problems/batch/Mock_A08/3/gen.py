# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(1701)
MAXN, MAXT = 60000, 100 * 3600 * 1000 - 1
rnd = random.random
tests = []

WORDS = ("hello where are you going now wait for me I am here no yes come back please run fast "
         "the door is open look out behind you what did he say we have to leave tonight okay fine "
         "thank you sorry Mr. Lee it's 5 o'clock (laughs) [music] - hey! who? why... 100% sure, maybe "
         "/ -- 1 2 3 42 --> ~").split()
TRICKY = ["42", "7", "10 9 8 7 6 5 4 3 2 1", "00:00:01,000 --> 00:00:02,000", "-->", "1", "-", "12:00:00,000",
          "two  spaces", "a   b    c", "-  -", "~ music ~"]


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def pick(seq):
    return seq[int(rnd() * len(seq))]


def shuffle(a):
    for i in range(len(a) - 1, 0, -1):
        j = ri(0, i)
        a[i], a[j] = a[j], a[i]


def fmt(t):
    s = t // 1000
    return "%02d:%02d:%02d,%03d" % (s // 3600, s // 60 % 60, s % 60, t % 1000)


def text_line(maxw):
    if rnd() < 0.05:
        return pick(TRICKY)
    sep = "  " if rnd() < 0.1 else " "
    return sep.join(pick(WORDS) for _ in range(ri(1, maxw)))[:40].strip()


POOL = {}
BIGMODE = False


def text(maxw=None):
    """a text from a fixed pool (keeps gen.py fast); shorter texts in the big tests (input size)"""
    if maxw is None:
        maxw = 2 if BIGMODE else 5
    if maxw not in POOL:
        POOL[maxw] = [text_line(maxw) for _ in range(3000)]
    return pick(POOL[maxw])


CHECKED = set()      # texts already checked (only used for lookups, never iterated)


def write(blocks):
    """blocks: list of (start, end, text) in the order of the file"""
    n = len(blocks)
    assert 1 <= n <= MAXN
    out = [str(n) + "\n"]
    for s, e, tx in blocks:
        assert 0 <= s < e <= MAXT
        if tx not in CHECKED:
            assert 1 <= len(tx) <= 40 and tx[0] != " " and tx[-1] != " "
            assert all(32 <= ord(c) <= 126 for c in tx)
            CHECKED.add(tx)
        out.append("%s --> %s %s\n" % (fmt(s), fmt(e), tx))
    tests.append("".join(out))


def add(blocks, order="time"):
    """order "time": the file lists the blocks roughly by start (a block may swap places with a near one);
    "random": any order; "keep": as given"""
    if order == "time":
        key = [s + int(rnd() * 6000) for s, _, _ in blocks]
        idx = sorted(range(len(blocks)), key=lambda i: key[i])
        blocks = [blocks[i] for i in idx]
    elif order == "random":
        blocks = blocks[:]
        shuffle(blocks)
    write(blocks)


def T(h, m, s, ms=0):
    return ((h * 60 + m) * 60 + s) * 1000 + ms


def movie(n, gap=3000, length=2500, overlap=0.1, bg=False):
    """subtitles one after another, some overlapping the next ones, some starting together;
    bg: one more block (background music) from near the start to the end"""
    blocks, t = [], ri(0, 5000)
    for _ in range(n - bg):
        d = ri(length // 3, length * 2)
        e = t + d
        if rnd() < overlap:
            e = t + d * ri(2, 6)
        blocks.append((t, min(e, MAXT), text()))
        if rnd() < 0.15:
            continue                      # the next block starts at the same time
        t += ri(gap // 4, gap * 2)
    assert t < MAXT
    if bg:
        blocks.append((ri(0, 3000), MAXT, "~ music ~"))
    return blocks


# ---- samples
write([
    (T(0, 0, 1, 0), T(0, 0, 4, 0), "Hello."),
    (T(0, 0, 3, 500), T(0, 0, 6, 0), "Who is there?"),
    (T(0, 0, 8, 0), T(0, 0, 9, 0), "(knocking)"),
])
write([
    (T(0, 0, 0, 0), T(0, 1, 0, 0), "[rain]"),
    (T(0, 0, 5, 0), T(0, 0, 9, 0), "Wait for me!"),
    (T(0, 0, 5, 0), T(0, 0, 7, 0), "Run!"),
])
write([
    (T(1, 59, 58, 0), T(2, 0, 2, 0), "New Year!"),
    (T(2, 0, 2, 0), T(2, 0, 5, 0), "2"),
    (T(1, 59, 59, 999), T(2, 0, 0, 1), "3 2 1"),
])
write([
    (T(0, 0, 5, 0), T(0, 0, 30, 0), "- Run!"),
    (T(0, 0, 12, 0), T(0, 0, 15, 0), "(thunder)"),
    (T(0, 0, 10, 0), T(0, 0, 20, 0), "- Where to?"),
])
write([
    (T(0, 0, 0, 0), T(99, 59, 59, 999), "~ music ~"),
    (T(11, 0, 0, 0), T(12, 0, 0, 500), "noon"),
    (T(12, 0, 0, 0), T(12, 0, 1, 0), "12 o'clock"),
])

# ---- hidden: small (brute checks these)
write([(0, 1, "a")])
write([(0, MAXT, "00:00:01,000 --> 00:00:02,000"), (0, MAXT, "-->")])
for n, gap, ln, ov, od in [(12, 500, 3000, 0.3, "time"), (40, 300, 1000, 0.3, "random"),
                           (200, 2000, 6000, 0.3, "time"), (300, 50, 400, 0.5, "random"),
                           (2000, 3000, 2500, 0.1, "time")]:
    add(movie(n, gap, ln, ov, bg=n > 10 and n != 2000), od)
# many equal starts and nested ends
b = []
for k in range(60):
    s = ri(0, 20) * 1000
    b.append((s, s + ri(1, 5) * 1000, text(2)))
add(b, "random")
# the same text in blocks next to each other (still different blocks)
b = []
for k in range(100):
    s = k * 1000 + ri(0, 300)
    b.append((s, s + ri(700, 2500), pick(("(music)", "(music)", "Yes.", "Yes."))))
add(b, "time")


# ---- hidden: big
def long_under_short():
    """one block covering the whole film (first in the file), short blocks with gaps in between"""
    b = [(0, MAXT, "~ soft piano music ~")]
    t = 1000
    for _ in range(MAXN - 1):
        b.append((t, t + ri(500, 1500), text()))
        t += ri(2000, 4000)
    return b


def empty_gaps():
    """short blocks far apart, nothing on screen in between"""
    b, t = [], 0
    for _ in range(MAXN):
        b.append((t, t + ri(1, 1000), text()))
        t += ri(1001, 5000)
    return b


def staircase():
    """block k starts at 5k seconds and most blocks last long: many blocks on screen at once"""
    b = []
    for k in range(MAXN):
        s = k * 5000
        b.append((s, min(MAXT, s + pick((7000, 300000, 1000000, 3000000))), text()))
    return b


def nested():
    """groups with the same start and different ends over background music"""
    b = [(0, MAXT, "~ rain ~")]
    for g in range((MAXN - 1) // 8):
        s = g * 20000
        for _ in range(8):
            b.append((s, s + ri(1, 19999), text()))
    return b


def all_overlap():
    """many blocks on screen at once: each lasts 5 to 37 minutes (about 200 blocks on screen at a time)"""
    b = []
    for _ in range(MAXN):
        d = ri(5 * 60000, 37 * 60000)
        s = ri(0, MAXT - d)
        b.append((s, s + d, text()))
    return b


def late_hours():
    b = movie(MAXN, 5000, 3000, 0.03)
    off = MAXT - max(e for _, e, _ in b)
    return [(s + off, e + off, tx) for s, e, tx in b]


def high_over_low():
    """long blocks late in the file over many short blocks earlier in the file (one block stays on screen
    across many starts and ends of hidden blocks)"""
    top, low, t = [], [], 0
    for _ in range(MAXN // 50):
        top.append((t, t + 200000, text()))
        for _ in range(49):
            s = max(0, t + ri(-20000, 210000))
            low.append((s, s + ri(1, 30000), text()))
        t += 230000
    shuffle(top)
    shuffle(low)
    return low + top


def same_text():
    """neighbouring blocks with the same text"""
    b, t = [], 0
    for _ in range(MAXN):
        b.append((t, t + ri(500, 3000), pick(("(music)", "(music)", "Yes.", "- No!"))))
        t += ri(400, 1500)
    return b


def bg_first(b):
    return b[-1:] + b[:-1]


BIG = [(17010, lambda: add(bg_first(movie(MAXN, 4000, 1500, 0.05, bg=True)), "keep")),
       (17011, lambda: add(long_under_short(), "keep")),
       (17012, lambda: add(empty_gaps())),
       (17013, lambda: add(staircase(), "random")),
       (17014, lambda: add(nested(), "random")),
       (17015, lambda: add(all_overlap(), "random")),
       (17016, lambda: add(late_hours())),
       (17017, lambda: add(movie(MAXN, 4000, 2000, 0.02, bg=True)[::-1], "keep")),
       (17018, lambda: add(long_under_short())),
       (17019, lambda: add(same_text())),
       (17020, lambda: add(movie(MAXN, 3000, 3000, 0.3, bg=True), "random")),
       (17021, lambda: add(high_over_low(), "keep")),
       (17022, lambda: add(nested(), "keep")),
       (17023, lambda: add(movie(MAXN, 2500, 2500, 0.2, bg=True)[::-1])),
       (17024, lambda: add(movie(MAXN, 3000, 2000, 0.1), "random"))]
BIGMODE = True
for seed, make in BIG:
    random.seed(seed)
    make()

os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
