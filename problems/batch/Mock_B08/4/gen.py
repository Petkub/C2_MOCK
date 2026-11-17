# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# The cheapest set of passes for a start s is a shared route from s to some node z (a room, or a pass already
# bought), then two separate routes from z to A and to B. The big tests make z land strictly inside the graph:
# at a hub room far from s, A and B (kills "A then B / B then A / separately"), and right after a shared pass that
# opens one room near A and another near B (kills "split only at rooms"). Every big test has a large strongly
# connected part, so one Dijkstra per start explores most of the graph. Some tests have answers above 2^31.
import os, random

random.seed(20211217)
rnd = random.random
MAXN, MAXK, MAXL, MAXP = 60000, 60000, 120000, 10 ** 9
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(n, a, b, passes, mix=False):
    """passes: list of (c, p, rooms); mix: shuffle the order of the passes"""
    k = len(passes)
    assert 2 <= n <= MAXN and 1 <= k <= MAXK
    assert 1 <= a <= n and 1 <= b <= n and a != b
    if mix:
        keys = [rnd() for _ in passes]
        passes = [passes[i] for i in sorted(range(k), key=keys.__getitem__)]
    lines = ["%d %d %d %d" % (n, k, a, b)]
    total = 0
    for c, p, rooms in passes:
        m = len(rooms)
        assert 1 <= c <= n and 1 <= p <= MAXP and 1 <= min(rooms) and max(rooms) <= n
        assert m == 1 or (m == 2 and rooms[0] != rooms[1]) or len(set(rooms)) == m
        total += m
        lines.append("%d %d %d %s" % (c, p, m, " ".join(map(str, rooms))))
    assert total <= MAXL
    tests.append("\n".join(lines) + "\n")


def rooms_from(pool, m):
    """m distinct rooms taken at random from the list pool (m <= len(pool))"""
    w = len(pool)
    if m == 1:
        return [pool[int(rnd() * w)]]
    if m == 2 and w >= 2:
        x, y = pool[int(rnd() * w)], pool[int(rnd() * w)]
        while y == x:
            y = pool[int(rnd() * w)]
        return [x, y]
    got, seen = [], set()
    while len(got) < m:
        r = pool[int(rnd() * len(pool))]
        if r not in seen:
            seen.add(r)
            got.append(r)
    return got


def sizes(k, total, cap, big=0):
    """k list sizes in [1, cap] adding up to total (at most k * cap); big > 0: a few lists get big sizes"""
    assert k <= total <= k * cap
    ms = [1] * k
    left = total - k
    if big:
        for _ in range(big):
            i = int(rnd() * k)
            take = min(left, ri(1, max(1, left // big)), cap - ms[i])
            ms[i] += take
            left -= take
    while left > 0:
        i = int(rnd() * k)
        if ms[i] < cap:
            ms[i] += 1
            left -= 1
    return ms


def random_passes(n, k, total, plo, phi, sellers=None, pool=None, big=0):
    sellers = sellers or list(range(1, n + 1))
    pool = pool or list(range(1, n + 1))
    return [(sellers[int(rnd() * len(sellers))], ri(plo, phi), rooms_from(pool, m))
            for m in sizes(k, total, max(1, len(pool) // 2) if len(pool) > 20 else len(pool), big)]


def ring(rooms, plo, phi):
    """a cheap cycle: the pass sold in rooms[i] opens rooms[i + 1]"""
    return [(rooms[i], ri(plo, phi), [rooms[(i + 1) % len(rooms)]]) for i in range(len(rooms))]


def shuffled(xs):
    keys = [rnd() for _ in xs]
    return [xs[i] for i in sorted(range(len(xs)), key=lambda i: keys[i])]


def random_test(n, k, total, plo, phi, big=0):
    a, b = rooms_from(list(range(1, n + 1)), 2)
    add(n, a, b, random_passes(n, k, total, plo, phi, big=big))   # already in random order


def split_test(n, k, total, hubs, hub_price, single_price):
    """Region RA (holds A) and region RB (holds B) are cheap cycles. Hub passes, sold anywhere, open one room
    of RA and one of RB; single passes open one room of only one region. The rest is an expensive random graph."""
    rooms = shuffled(list(range(1, n + 1)))
    q = n // 10
    ra, rb = rooms[:q], rooms[q:2 * q]
    a, b = ra[0], rb[0]
    passes = ring(ra, 1, 50) + ring(rb, 1, 50)
    for _ in range(hubs):
        passes.append((ri(1, n), ri(*hub_price), [ra[int(rnd() * q)], rb[int(rnd() * q)]]))
        reg = ra if rnd() < 0.5 else rb
        passes.append((ri(1, n), ri(*single_price), [reg[int(rnd() * q)]]))
    rest = k - len(passes)
    used = sum(len(p[2]) for p in passes)
    passes += random_passes(n, rest, total - used, 10 ** 8, MAXP, sellers=rooms[2 * q:])
    add(n, a, b, passes, True)


def hub_room_test(n, k, total, hubs):
    """A few hub rooms z sell one cheap pass towards A and another towards B; everything else is expensive,
    so most starts pay once to reach a hub and then split there."""
    rooms = shuffled(list(range(1, n + 1)))
    a, b = rooms[0], rooms[1]
    near_a, near_b = rooms[2:2 + 50], rooms[52:102]
    zs = rooms[102:102 + hubs]
    passes = [(x, ri(1, 1000), [a]) for x in near_a] + [(x, ri(1, 1000), [b]) for x in near_b]
    for z in zs:
        passes.append((z, ri(10 ** 5, 10 ** 6), [near_a[int(rnd() * 50)]]))
        passes.append((z, ri(10 ** 5, 10 ** 6), [near_b[int(rnd() * 50)]]))
    # cheap passes into the hubs from everywhere, expensive passes between the other rooms
    for _ in range(k // 4):
        passes.append((ri(1, n), ri(10 ** 7, 10 ** 8), [zs[int(rnd() * hubs)]]))
    rest = k - len(passes)
    used = sum(len(p[2]) for p in passes)
    passes += random_passes(n, rest, total - used, 5 * 10 ** 8, MAXP, pool=rooms[102:])
    add(n, a, b, passes, True)


def chain_test(n, total, price):
    """a long cycle through every room (answers up to n * price); each pass also opens a few random rooms"""
    rooms = shuffled(list(range(1, n + 1)))
    passes = ring(rooms, price[0], price[1])
    for _ in range(total - n):
        c, p, rs = passes[int(rnd() * n)]
        r = ri(1, n)
        if r not in rs:
            rs.append(r)
    a, b = rooms[n // 3], rooms[2 * n // 3]
    add(n, a, b, passes, True)


# samples
add(6, 1, 6, [(3, 4, [2]), (2, 7, [6]), (3, 5, [4, 5]), (5, 2, [1]), (1, 9, [3])])
add(5, 1, 3, [(5, 10, [3, 2]), (1, 26, [2]), (1, 14, [5, 4]), (5, 5, [4]), (3, 14, [1, 2, 4]), (1, 10, [3, 4])])
add(7, 7, 1, [(3, 2, [1, 2, 6]), (4, 18, [5]), (1, 15, [7]), (5, 17, [5, 7]), (3, 15, [6]), (2, 23, [5, 4, 7]),
              (7, 15, [3, 5, 2]), (1, 13, [4])])
add(8, 1, 2, [(8, 13, [8]), (6, 13, [3, 4]), (6, 1, [2, 7]), (7, 4, [6, 7]), (5, 9, [1]), (7, 28, [2, 4]),
              (5, 28, [2, 3, 4]), (2, 2, [5])])
add(4, 2, 4, [(1, 10 ** 9, [3]), (3, 10 ** 9, [4]), (4, 999999999, [2]), (2, 1, [1])])

# hidden: small (brute checks these)
add(2, 1, 2, [(1, 5, [2])])
add(3, 3, 1, [(2, 4, [1, 3]), (1, 1, [2]), (3, 2, [2])])
for t in range(6):
    n = ri(3, 8)
    k = ri(4, 13)
    if t % 2 == 0:
        random_test(n, k, ri(k, min(n * k, 3 * k)), 1, 30)
    else:      # few price levels, many ties; passes that open both targets
        a, b = rooms_from(list(range(1, n + 1)), 2)
        ps = random_passes(n, k - 2, ri(k - 2, 2 * k), 1, 4)
        ps += [(ri(1, n), ri(3, 8), [a, b]), (ri(1, n), ri(3, 8), rooms_from(list(range(1, n + 1)), 3))]
        add(n, a, b, ps, True)
# hidden: medium
random_test(2000, 2000, 4000, 1, 10 ** 6)

# hidden: big
N, K, L = MAXN, MAXK, MAXL
random_test(N, K, L, 1, MAXP)
random_test(N, K, L, MAXP - 1000, MAXP)                                   # answers above 2^31
random_test(N, K, L, 1, 100)                                              # many ties
random_test(N, K, L, 1, MAXP, big=5)                                      # a few passes open thousands of rooms
split_test(N, K, L, 300, (10 ** 6, 2 * 10 ** 6), (6 * 10 ** 5, 2 * 10 ** 6))
split_test(N, K, L, 3000, (10 ** 5, 10 ** 6), (10 ** 5, 10 ** 6))
split_test(N, K, L, 30, (10 ** 7, 10 ** 8), (6 * 10 ** 6, 10 ** 8))
hub_room_test(N, K, L, 5)
hub_room_test(N, K, L, 200)
chain_test(N, L, (1, 1000))
chain_test(N, N + 3000, (MAXP - 10 ** 6, MAXP))                          # long expensive routes
# one room sells 30 000 passes that open two rooms each; 30 000 other rooms sell a pass back to it
rooms = shuffled(list(range(1, N + 1)))
star = [(rooms[0], ri(1, MAXP), [rooms[2 * i + 1], rooms[2 * i + 2]]) for i in range(K // 2 - 1)]
star.append((rooms[0], ri(1, MAXP), [rooms[N - 1]]))
star += [(r, ri(1, MAXP), [rooms[0]]) for r in rooms[1:K // 2 + 1]]
add(N, rooms[5], rooms[7], star, True)
# B can be opened only by passes sold in ten rooms that nobody can open: almost every answer is -1.
# The other rooms form one long cycle, so every start still reaches almost every room.
rooms = shuffled(list(range(1, N + 1)))
a, b, lock = rooms[0], rooms[1], rooms[2:12]
free = [rooms[0]] + rooms[12:N - 9]                   # the last 9 rooms stay closed and sell nothing
ps = ring(free, 1, MAXP)
for _ in range(L - len(free) - 20):
    c, p, rs = ps[int(rnd() * len(free))]
    r = free[int(rnd() * len(free))]
    if r not in rs:
        rs.append(r)
ps += [(x, ri(1, MAXP), [b]) for x in lock] + [(x, ri(1, MAXP), [free[ri(1, 5000)]]) for x in lock]
add(N, a, b, ps, True)
# targets that sit next to each other in the room numbering
random_test(N, K, L, 1, 10 ** 6)
split_test(N, K, L, 1000, (10 ** 3, 10 ** 4), (10 ** 3, 10 ** 4))
hub_room_test(N, K, L, 30)

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
