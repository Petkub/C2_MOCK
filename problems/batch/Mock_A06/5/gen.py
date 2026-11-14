# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# A test is built from pieces: the walk from card 1 (it ends at a card with 0 or loops back into itself),
# trees that hang onto cards of that walk, trees that end at other cards with 0, and loops with tails.
import os, random

random.seed(5122012)
rnd = random.random
MAXN = 200000
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(a):
    n = len(a)
    assert 1 <= n <= MAXN and min(a) >= 0 and max(a) <= n
    tests.append(f"{n}\n" + " ".join(map(str, a)) + "\n")


class Builder:
    def __init__(self, n):
        self.n = n
        self.a = [None] * (n + 1)
        if n == MAXN:               # one shuffled order for every big test, rotated by a random amount
            k = ri(0, n - 2)
            self.pool = BASE[k:] + BASE[:k]
        else:
            self.pool = sorted(range(2, n + 1), key=lambda v: rnd())
        self.forest = []            # cards whose walk ends at a card with 0 (outside the walk from card 1)
        self.looped = []            # cards whose walk runs into a loop (outside the walk from card 1)

    def take(self, k):
        k = min(k, len(self.pool))
        out = self.pool[len(self.pool) - k:]
        del self.pool[len(self.pool) - k:]
        return out

    def path(self, k, close):
        """the walk from card 1 with k cards; close = None: the last card has 0, else it points to path[close]"""
        p = [1] + self.take(k - 1)
        for i in range(len(p) - 1):
            self.a[p[i]] = p[i + 1]
        self.a[p[-1]] = 0 if close is None else p[close]
        self.p = p
        return p

    def tree(self, k, target, width, kind):
        """k new cards hanging onto card target (0: the first new card has 0); parents among the last width cards"""
        nodes = self.take(k)
        for i, v in enumerate(nodes):
            if i == 0:
                self.a[v] = target
            else:
                self.a[v] = nodes[i - 1 - int(rnd() * min(i, width))]
        (self.forest if kind == "f" else self.looped if kind == "l" else []).extend(nodes)
        return nodes

    def loop(self, k):
        nodes = self.take(k)
        for i in range(len(nodes)):
            self.a[nodes[i]] = nodes[(i + 1) % len(nodes)]
        self.looped.extend(nodes)
        return nodes

    def fill(self, targets, width=0):
        """the remaining cards hang onto random cards of targets (or onto one another when width > 0)"""
        rest = self.take(len(self.pool))
        for i, v in enumerate(rest):
            if width and i > 0 and rnd() < 0.7:
                self.a[v] = rest[i - 1 - int(rnd() * min(i, width))]
            else:
                self.a[v] = targets[int(rnd() * len(targets))]

    def done(self):
        assert not self.pool and None not in self.a[1:]
        add(self.a[1:])


BASE = sorted(range(2, MAXN + 1), key=lambda v: rnd())


def rand_graph(n, zero):
    add([0 if rnd() < zero else ri(1, n) for _ in range(n)])


# samples
add([3, 0, 5, 2, 0, 4, 3])
add([2, 3, 4, 2, 6, 0])
add([2, 3, 1, 5, 0])
add([4, 5, 0, 6, 3, 7, 0, 2])
add([5, 7, 0, 7, 9, 2, 3, 8, 0])

# hidden: small (brute checks these)
add([1])
add([0])
add([2, 0, 1])                                          # card 3 hangs onto card 1
add([2, 2])
for zero in (0.05, 0.3):
    rand_graph(60, zero)
b = Builder(150)                                        # walk ends; deep tree onto card 1, a shorter one further on
b.path(20, None)
b.tree(40, 1, 1, "")
b.tree(15, b.p[8], 2, "")
b.tree(10, 0, 3, "f")
b.loop(20)
b.fill(b.looped)
b.done()
b = Builder(200)                                        # walk loops; long tails into the walk and into other loops
b.path(30, 12)
b.tree(50, b.p[5], 1, "")
b.loop(15)
b.tree(40, b.looped[0], 1, "l")
b.tree(25, 0, 2, "f")
b.fill(b.forest + b.p)
b.done()

# hidden: medium
b = Builder(5000)
b.path(1500, None)
b.tree(800, b.p[700], 2, "")
b.tree(700, 0, 2, "f")
b.loop(500)
b.fill(b.looped + b.forest, 4)
b.done()

N = MAXN
# hidden: big, the walk ends at a card with 0
b = Builder(N)                                          # best: the last card points to the deepest other tree
b.path(90000, None)
b.tree(30000, 0, 2, "f")
b.tree(20000, b.p[40000], 2, "")
b.tree(20000, 0, 50, "f")
b.loop(5000)
b.fill(b.forest + b.looped + b.p[1:], 3)
b.done()
b = Builder(N)                                          # best: a deep tree hanging onto the middle of the walk
b.path(80000, None)
b.tree(40000, b.p[ri(30000, 50000)], 2, "")
b.tree(20000, 0, 3, "f")
b.tree(20000, b.p[70000], 1, "")
b.fill(b.forest + b.p[1:], 0)
b.done()
b = Builder(N)                                          # deepest tree hangs onto card 1; no other card with 0
b.path(70000, None)
b.tree(80000, 1, 1, "")
b.tree(30000, b.p[1], 2, "")
b.loop(3000)
b.fill(b.looped + b.p[1:], 5)
b.done()
add(list(range(2, N + 1)) + [0])                        # one walk through every card
b = Builder(N)                                          # no change helps: other cards hang onto card 1 or loop
b.path(100000, None)
b.tree(50000, 1, 1, "")
b.loop(10000)
b.fill(b.looped + [1], 2)
b.done()
b = Builder(N)                                          # deep trees onto the last card and onto the second card
b.path(60000, None)
b.tree(50000, b.p[-1], 1, "")
b.tree(45000, b.p[1], 1, "")
b.tree(40000, 0, 1, "f")
b.fill(b.forest + b.p, 0)
b.done()
b = Builder(N)                                          # short walk, a huge other tree
b.path(3, None)
b.tree(150000, 0, 2, "f")
b.fill(b.forest + b.p, 0)
b.done()
b = Builder(N)                                          # many shallow trees everywhere, a long walk
b.path(100000, None)
for _ in range(200):
    b.tree(300, 0, 40, "f")
b.fill(b.forest + b.p, 0)
b.done()
b = Builder(N)                                          # tree onto the middle and other tree almost equal
b.path(100000, None)
t1 = b.tree(30000, b.p[50000], 1, "")
b.tree(30001, 0, 1, "f")
b.fill(b.p[:50000] + b.forest[:100], 0)
b.done()
b = Builder(N)                                          # trees onto several cards of the walk, the deepest onto card 1
b.path(60000, None)
b.tree(50000, 1, 2, "")
for m in (1, 5000, 20000, 41000, 59999):
    b.tree(ri(8000, 12000), b.p[m], 3, "")
b.tree(5000, 0, 2, "f")
b.fill(b.p + b.forest, 0)
b.done()
b = Builder(N)                                          # bushy trees onto the walk and other trees, a few loops
b.path(50000, None)
b.tree(60000, 1, 8, "")
b.tree(40000, b.p[ri(10000, 40000)], 6, "")
b.tree(30000, 0, 8, "f")
b.loop(2000)
b.fill(b.p + b.forest + b.looped, 20)
b.done()

# hidden: big, the walk loops
b = Builder(N)                                          # long tail and loop, a deep tree ending at 0, longer tails elsewhere
b.path(80000, 30000)
b.tree(25000, 0, 2, "f")
b.loop(20000)
b.tree(40000, b.looped[0], 1, "l")
b.tree(20000, b.p[1000], 1, "")
b.fill(b.forest + b.looped + b.p, 3)
b.done()
b = Builder(N)                                          # the walk loops back to card 1; no card has 0
b.path(120000, 0)
b.loop(30000)
b.fill(b.looped + b.p, 2)
b.done()
b = Builder(N)                                          # card 1 points to itself
b.path(1, 0)
b.tree(100000, 0, 2, "f")
b.loop(40000)
b.fill(b.forest + b.looped + b.p, 4)
b.done()
b = Builder(N)                                          # the last card of the walk points to itself
b.path(100000, 99999)
b.tree(60000, 0, 3, "f")
b.fill(b.forest + b.p, 2)
b.done()
b = Builder(N)                                          # deep trees onto the walk, small trees ending at 0
b.path(70000, 50000)
b.tree(60000, b.p[20000], 1, "")
for _ in range(100):
    b.tree(200, 0, 3, "f")
b.loop(1000)
b.fill(b.looped + b.p, 0)
b.done()
b = Builder(N)                                          # long loop through card 1 and a deep tree ending at 0
b.path(110000, 0)
b.tree(50000, 0, 1, "f")
b.tree(30000, b.p[50], 1, "")
b.fill(b.forest + b.p, 2)
b.done()
b = Builder(N)                                          # the walk loops; other cards in many loops with long tails
b.path(90000, 45000)
for _ in range(50):
    lp = b.loop(100)
    b.tree(1500, lp[0], 1, "l")
b.tree(5000, 0, 2, "f")
b.fill(b.forest + b.looped, 3)
b.done()

# hidden: big random
rand_graph(N, 0.00002)
rand_graph(N, 0.001)

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
