# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
# A tree is kept as kids[box] = list of its items, an artifact is -1 and a box is its id (box 0 is the outermost).
import os, random, re
from itertools import accumulate, chain
from operator import sub

random.seed(93141)
rnd = random.random
MAXL, MAXQ, MAXK, MAXP, MAXC = 5 * 10 ** 5, 2 * 10 ** 5, 5 * 10 ** 5, 10 ** 9, 10 ** 9
tests = []


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def check_record(s):
    assert 2 <= len(s) <= MAXL and s[0] == '[' and s[-1] == ']'
    assert re.fullmatch(r'[\[\],0-9]*', s)
    # what may follow: '[' -> '[' ']' digit; ']' -> ',' ']'; ',' -> '[' digit; digit -> ',' ']' digit
    assert not re.search(r'\]\[|\][0-9]|\[,|,,|,\]|[0-9]\[', s)
    assert not re.search(r'(?<![0-9])0[0-9]', s)
    assert all(x == '1000000000' for x in re.findall(r'[0-9]{10,}', s))
    b = s.encode().translate(bytes.maketrans(b'[]', b'\x02\x00'), b',0123456789')
    # depth after the i-th bracket = 2 * (opening brackets so far) - (i + 1): >= 1 before the last one, 0 at the end
    assert len(b) % 2 == 0 and sum(b) == len(b)
    assert min(map(sub, accumulate(b[:-1]), range(1, len(b)))) >= 1


def add(s, queries):
    check_record(s)
    assert 1 <= len(queries) <= MAXQ and min(map(len, queries)) >= 1
    ps = list(chain.from_iterable(queries))
    assert len(ps) <= MAXK and min(ps) >= 1 and max(ps) <= MAXP
    lines = [s, str(len(queries))] + ["%d %s" % (len(q), " ".join(map(str, q))) for q in queries]
    t = "\n".join(lines) + "\n"
    assert len(t) <= 3 * 10 ** 6
    tests.append(t)


def code_small():
    return ri(0, 9)


def code_mid():
    return ri(0, 999)


def code_big():
    x = rnd()
    if x < 0.05:
        return MAXC
    if x < 0.1:
        return 0
    return ri(1, MAXC)


def code_mix():
    return ri(0, 99) if rnd() < 0.6 else code_big()


def rand_tree(target, p_open, p_close, codes, maxd=10 ** 9):
    """random record of length <= target: at each step open a box, close the current one, or put an artifact"""
    out, kids, st, length = ['['], [[]], [0], 1
    while True:
        d = len(st)
        if length + d + 12 > target:
            break
        top = kids[st[-1]]
        sep = ',' if top else ''
        r = rnd()
        if r < p_open and d < maxd:
            nid = len(kids)
            kids.append([])
            top.append(nid)
            st.append(nid)
            out.append(sep + '[')
            length += len(sep) + 1
        elif r < p_open + p_close and d > 1:
            st.pop()
            out.append(']')
            length += 1
        else:
            x = sep + str(codes())
            top.append(-1)
            out.append(x)
            length += len(x)
    out.append(']' * len(st))
    return ''.join(out), kids


def walk_query(kids, max_len, p_stop, p_bad):
    """random descent from the outermost box; sometimes a step that does not exist"""
    q, cur = [], 0
    while len(q) < max_len:
        if cur < 0:                                    # holding an artifact: one more step makes it NONE
            if rnd() < p_bad:
                q.append(ri(1, 3))
            break
        items = kids[cur]
        if rnd() < p_bad or not items:
            x = rnd()
            if x < 0.5:
                q.append(len(items) + 1)
            elif x < 0.8:
                q.append(len(items) + ri(1, 1000))
            else:
                q.append(ri(len(items) + 1, MAXP))
            break
        i = ri(1, len(items))
        if rnd() < 0.5:
            i = len(items) - int(rnd() * min(len(items), 5))      # often near the end of the box
        q.append(i)
        cur = items[i - 1]
        if rnd() < p_stop:
            break
    if not q:
        q.append(1)
    return q


def walk_queries(kids, nq, budget, max_len, p_stop, p_bad):
    qs, used = [], 0
    while len(qs) < nq and used + max_len <= budget:
        q = walk_query(kids, max_len, p_stop, p_bad)
        qs.append(q)
        used += len(q)
    return qs


# ---------------------------------------------------------------- samples
add("[5,[],[12,[0]]]", [[1], [3, 2, 1], [2, 1], [1, 1]])
add("[[3,1],[[4],1,5],9]", [[2, 1], [2, 1, 1], [4], [1]])
add("[[],[[]],[7]]", [[2], [2, 1], [3, 1], [1, 1]])
add("[1,[2,[3]],[[4]]]", [[2, 2, 1], [3, 1], [2, 3], [3, 1, 1]])
add("[[0,[]],1000000000]", [[2], [1, 1], [1, 2], [1]])

# ---------------------------------------------------------------- small hidden (brute checks these)
add("[]", [[1], [1, 1], [MAXP]])
add("[0]", [[1], [2], [1, 1]])
add("[[[[[]]]]]", [[1], [1, 1], [1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1, 1], [1, 2]])
for target, po, pc, codes in ((60, 0.3, 0.25, code_small), (300, 0.3, 0.3, code_mix),
                              (3000, 0.35, 0.3, code_big), (20000, 0.4, 0.38, code_mid),
                              (100000, 0.45, 0.45, code_small), (200000, 0.5, 0.42, code_mix)):
    s, kids = rand_tree(target, po, pc, codes)
    add(s, walk_queries(kids, min(2000, 10 * target // 60), 20000, 200, 0.2, 0.15))
s = '[' * 50000 + ']' * 50000                                   # deep, brute size
add(s, [[1] * ri(1, 49999) for _ in range(5)] + [[1] * 49999, [1] * 50000, [1] * 49998 + [2]])

# ---------------------------------------------------------------- big
D = MAXL // 2
qs = [[1] * (D - 1)]
used = D - 1
while used + 300 < MAXK and len(qs) < MAXQ:
    q = [1] * (ri(1, 200) if rnd() < 0.05 else ri(1, 4))         # mostly short: each ends on a huge box
    if rnd() < 0.3:
        q[-1] = 2
    qs.append(q)
    used += len(q)
add('[' * D + ']' * D, qs)                                      # one chain of empty boxes, the deepest record

codes, ln = [], 2
while True:
    c = code_small() if rnd() < 0.9 else code_mix()
    if ln + len(str(c)) + 3 > MAXL:
        break
    codes.append(c)
    ln += len(str(c)) + 3
D = len(codes) + 1
s = ''.join('[%d,' % c for c in codes) + '[]' + ']' * len(codes)    # [c,[c,[c,...[]...]]]
qs, used = [], 0
while used + 300 <= MAXK and len(qs) < MAXQ:                   # two very long commands, then mostly short ones
    n = min(ri(D // 2, D + 1), 150000) if len(qs) < 2 else ri(1, 300) if rnd() < 0.01 else ri(1, 3)
    q = [2] * n
    if rnd() < 0.2:
        q[-1] = 1
    elif rnd() < 0.4:
        q[-1] = 3
    qs.append(q)
    used += n
add(s, qs)

codes = codes[:-1]
s = '[' * len(codes) + '[[]' + ''.join(',%d]' % c for c in codes) + ']'   # [[[...[[]],c],c],c]
qs, used = [], 0
while used + 300 <= MAXK and len(qs) < MAXQ:
    n = min(ri(len(codes) // 2, len(codes) + 2), 150000) if len(qs) < 2 else ri(1, 300) if rnd() < 0.01 else ri(1, 3)
    q = [1] * n
    if rnd() < 0.6:
        q[-1] = 2
    qs.append(q)
    used += n
add(s, qs)


def wide(items, depth_before, nq):
    """a box of the given items, at depth depth_before (inside boxes with nothing else); queries pick near its end"""
    w = len(items)
    s = '[' * depth_before + '[' + ','.join(items) + ']' + ']' * depth_before
    head = [1] * depth_before
    qs = []
    for _ in range(nq):
        x = rnd()
        if x < 0.85:
            p = w - int(rnd() * rnd() * w)
        elif x < 0.95:
            p = w + ri(1, 3)
        else:
            p = ri(1, MAXP)
        qs.append(head + [p])
    return s, qs


s, qs = wide([str(code_small()) for _ in range(MAXL // 2 - 1)], 0, MAXQ)
add(s, qs)                                                       # 5 * 10^5 one-digit artifacts in the outermost box
s, qs = wide([str(code_big()) for _ in range(45000)], 0, MAXQ)
add(s, qs)
s, qs = wide(['[]'] * (MAXL // 3 - 1), 0, MAXQ // 2)
qs += [q + [1] for q in qs]
add(s, qs)                                                       # empty boxes only
items, ln = [], 0
while ln < MAXL - 40:
    x = rnd()
    items.append('[]' if x < 0.4 else '[%d]' % code_small() if x < 0.6 else str(code_mid()))
    ln += len(items[-1]) + 1
s, qs = wide(items, 2, MAXQ // 4)
qs += [q + [1] for q in qs]
add(s, qs)                                                       # a wide box at depth 2, mixed items

# random records
for po, pc, codes, maxd, plen, pstop in ((0.45, 0.45, code_small, 10 ** 9, 60, 0.05),
                                         (0.35, 0.25, code_mix, 40, 40, 0.1),
                                         (0.70, 0.29, code_small, 10 ** 9, 3000, 0.0)):
    s, kids = rand_tree(MAXL, po, pc, codes, maxd)
    add(s, walk_queries(kids, MAXQ, MAXK, plen, pstop, 0.1))

# a comb: every level holds some empty boxes and artifacts, then the next level, then more artifacts
levels, ln = [], 2
while True:
    e, a, b = ri(0, 4), ri(0, 2), ri(0, 2)
    pre = '[' + ''.join('[],' if rnd() < 0.6 else '%d,' % code_small() for _ in range(e + a))
    post = ''.join(',%d' % code_mid() for _ in range(b)) + ']'
    if ln + len(pre) + len(post) > MAXL:
        break
    levels.append((pre, post, e + a + 1, e + a + b + 1))
    ln += len(pre) + len(post)
s = ''.join(x[0] for x in levels) + '[]' + ''.join(x[1] for x in reversed(levels))
qs, used = [], 0
while len(qs) < MAXQ and used + len(levels) + 2 < MAXK:
    j = ri(0, len(levels) - 1) if rnd() < 0.0005 else ri(0, min(len(levels) - 1, 30))
    q = [levels[i][2] for i in range(j)]
    x = rnd()
    q.append(ri(1, levels[j][3]) if x < 0.8 else levels[j][3] + 1 if x < 0.9 else levels[j][2])
    if rnd() < 0.3:
        q.append(1)
    qs.append(q)
    used += len(q)
add(s, qs)

# deep chain where every box also holds a run of empty boxes before the next level: [[],[],...,[[],...]]
reps = [ri(0, 1) if rnd() < 0.9 else ri(2, 6) for _ in range(MAXL // 3)]
ln = 0
for i, r in enumerate(reps):
    ln += 3 * r + 2
    if ln > MAXL - 2:
        reps = reps[:i]
        break
s = ''.join('[' + '[],' * r for r in reps) + '[]' + ']' * len(reps)
qs, used = [], 0
while len(qs) < MAXQ and used + len(reps) + 2 < MAXK:
    j = ri(0, len(reps)) if rnd() < 0.0005 else ri(0, min(len(reps), 50))
    q = [reps[i] + 1 for i in range(j)]
    if j < len(reps):
        q.append(ri(1, reps[j] + 2))
    if rnd() < 0.4:
        q.append(1)
    qs.append(q)
    used += len(q)
add(s, qs)

# every box: an empty box, then the next box: [[],[[],[[],...[]...]]]
D = (MAXL - 2) // 5
s = '[[],' * D + '[]' + ']' * D
qs, used = [], 0
while len(qs) < MAXQ and used + D + 2 < MAXK:
    n = ri(D // 2, D) if len(qs) < 2 else ri(0, 200) if rnd() < 0.01 else ri(0, 3)
    q = [2] * n + [ri(1, 3) if rnd() < 0.2 else ri(2, 3)]
    if rnd() < 0.3:
        q.append(1)
    qs.append(q)
    used += len(q)
add(s, qs)

# a full tree: T(i+1) = [T(i),[],T(i),code], with the same T(i) twice
t, lv = '[7]', 0
while 2 * len(t) + 20 <= MAXL:
    t = '[' + t + ',[],' + t + ',' + str(code_big()) + ']'
    lv += 1
qs, used = [], 0
while used + lv + 2 <= MAXK and len(qs) < MAXQ:
    q = [1 if rnd() < 0.5 else 3 for _ in range(ri(0, lv))]
    x = rnd()
    q.append(ri(1, 2) if x < 0.4 else 4 if x < 0.7 else ri(1, 6))
    if rnd() < 0.2:
        q.append(1)
    qs.append(q)
    used += len(q)
add(t, qs)

# many empty boxes and artifacts in a wide box at the bottom of a chain of 1000 boxes
items = ['[]' if rnd() < 0.7 else str(code_mix()) for _ in range(125000)]
s = '[' * 1000 + ','.join(items) + ']' * 1000
qs, used = [], 0
for _ in range(300):                                             # long commands to late items of the wide box
    q = [1] * 999 + [125001 - int(rnd() * rnd() * 125001)] + ([1] if rnd() < 0.5 else [])
    qs.append(q)
    used += len(q)
while used + 5 <= MAXK and len(qs) < MAXQ:                       # short commands: each ends on a box of almost all S
    q = [1] * ri(0, 3) + [ri(1, 2)]
    qs.append(q)
    used += len(q)
random.shuffle(qs)
add(s, qs)

# many chains side by side: [[[[...]]],[[[...]]],...]
parts, ln = [], 2
while True:
    d = ri(1, 3000)
    if ln + 2 * d + 1 > MAXL:
        break
    parts.append(d)
    ln += 2 * d + 1
s = '[' + ','.join('[' * d + ']' * d for d in parts) + ']'
qs, used = [], 0
while len(qs) < MAXQ and used + 3001 < MAXK:
    i = ri(1, len(parts) + 1)
    n = ri(0, parts[i - 1]) if i <= len(parts) and rnd() < 0.001 else ri(0, 3)
    qs.append([i] + [1] * n)
    used += n + 1
add(s, qs)

for t in tests:
    assert t.endswith("\n") and "  " not in t and " \n" not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
