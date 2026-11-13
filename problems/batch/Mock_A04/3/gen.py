# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import os, random

random.seed(240401)
MAXT, MAXL = 100000, 1000000
LOW = "abcdefghijklmnopqrstuvwxyz"
DIG = "0123456789"
UP = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALLOWED = set(LOW + DIG + UP + "<>/")
tests = []
rnd = random.random


def ri(a, b):
    return a + int(rnd() * (b - a + 1))


def add(docs):
    assert 1 <= len(docs) <= MAXT
    assert sum(len(d) for d in docs) <= MAXL
    for d in docs:
        assert len(d) >= 1 and set(d) <= ALLOWED
    tests.append(str(len(docs)) + "\n" + "\n".join(docs) + "\n")


def name(maxlen):
    k = ri(1, maxlen)
    return random.choice(LOW) + "".join(random.choice(LOW + DIG) for _ in range(k - 1))


def text(k, chars=LOW + DIG + UP + "/"):
    m = len(chars)
    return "".join([chars[int(rnd() * m)] for _ in range(k)])


def valid(L, pool, p_text=0.2, p_single=0.1, drift=0.5, maxtext=5):
    """a valid document of about L characters; drift = probability of opening rather than closing"""
    parts, st, n = [], [], 0
    while n < L:
        r = rnd()
        if r < p_text:
            x = text(ri(1, maxtext))
        elif r < p_text + p_single:
            x = "<" + random.choice(pool) + "/>"
        elif st and (rnd() > drift or n > L - 20 * len(st)):
            x = "</" + st.pop() + ">"
        else:
            nm = random.choice(pool)
            st.append(nm)
            x = "<" + nm + ">"
        parts.append(x)
        n += len(x)
    while st:
        parts.append("</" + st.pop() + ">")
    return parts, n


def doc(parts):
    return "".join(parts)


def pool_of(k, maxlen):
    return sorted(set(name(maxlen) for _ in range(k)))


def mutate(parts, kind):
    """break a valid token list near its end (the error is the first one only if every earlier token stays valid)"""
    closers = [i for i, x in enumerate(parts) if x.startswith("</")]
    if not closers:
        return parts + [">"]
    i = closers[-1 - ri(0, min(5, len(closers) - 1))]
    if kind == "wrong":
        nm = parts[i][2:-1]
        parts[i] = "</" + (nm[:-1] + ("b" if nm[-1] != "b" else "c") if rnd() < 0.5 else nm + "x") + ">"
    elif kind == "extra":
        parts.append("</" + parts[i][2:-1] + ">")
    elif kind == "open":
        del parts[i]
    elif kind == "stray":
        parts.insert(i, ">")
    elif kind == "bad":
        parts[i] = random.choice(["<" + parts[i][2:-1].upper() + ">", "</>", "<>", "<" + parts[i][2:],
                                  "<9" + parts[i][2:], "</" + parts[i][2:-1] + "/>", "<//" + parts[i][2:],
                                  "<" + parts[i][2:-1] + "Q>", "</" + parts[i][2:-1] + "R>"])
    return parts


def single_at_deepest(parts):
    """put a single tag right after the first opening tag of greatest depth (so a single tag holds the maximum)"""
    d, best, at = 0, 0, 0
    for i, x in enumerate(parts):
        if x.startswith("</"):
            d -= 1
        elif x.startswith("<") and not x.endswith("/>"):
            d += 1
            if d > best:
                best, at = d, i
    return parts[:at + 1] + ["<s/>"] + parts[at + 1:]


BAD_K = 0


def bad_name(parts):
    """replace a closing tag near the end by a tag whose name breaks the name rules"""
    closers = [i for i, x in enumerate(parts) if x.startswith("</")]
    i = closers[-1 - ri(0, min(5, len(closers) - 1))]
    nm = parts[i][2:-1]
    global BAD_K
    BAD_K += 1
    # even: an upper-case letter inside the name; odd: the name starts with a digit
    variants = ["<" + nm[0] + "K" + nm[1:] + ">", "<" + str(ri(0, 9)) + nm + ">", "<" + nm + "Q/>",
                "</" + str(ri(0, 9)) + nm + ">", "</" + nm + "Z>", "<" + str(ri(0, 9)) + nm + "/>"]
    parts[i] = variants[BAD_K % len(variants)]
    return parts


def mixed(n, pool, drift=0.6, p_text=0.2, maxtext=5):
    """n documents; every detail of the rules decides at least one of them, and every document that ends
    with a non-empty list is followed by a valid one. Document 2 (valid, few text runs) takes 70% of the length."""
    half = (L - 200) * 7 // 10
    rest = (L - 200 - half) // (n - 1)
    kinds = ["stray", "single", "bad", "extra", "bad", "wrong", "open2", "single"]
    docs = []
    for j in range(n):
        k = kinds[j % len(kinds)]
        parts = valid((half if j == 1 else rest) - 60, pool, 0.03 if j == 1 else p_text, 0.0 if k == "single" else 0.1, drift, maxtext)[0]
        if k == "single":
            parts = single_at_deepest(parts)
        elif k == "bad":
            parts = bad_name(parts)
        elif k == "open2":
            parts = ["<r>", "<s>"] + parts
        else:
            parts = mutate(parts, k)
        docs.append(doc(parts))
    return docs


def small_random(T, maxparts):
    docs = []
    for _ in range(T):
        parts, st = [], []
        for _ in range(ri(1, maxparts)):
            r = rnd()
            if r < 0.3:
                x = random.choice(["a", "b", "ab", "a1", "b2c"])
                st.append(x)
                parts.append("<" + x + ">")
            elif r < 0.6 and st:
                x = st.pop() if rnd() < 0.85 else random.choice(["a", "b", "ab"])
                parts.append("</" + x + ">")
            elif r < 0.7:
                parts.append("<" + random.choice(["a", "b", "c2"]) + "/>")
            elif r < 0.85:
                parts.append(text(ri(1, 3), "xY9/"))
            elif r < 0.95:
                parts.append(text(ri(1, 4), "<>/aB1"))
            else:
                parts.append(random.choice(["<A>", "<1a>", "<aB>", "</bA>", "<a1C/>", "</>", "<>", "<a//>", "</a/>", "<a", ">", "<a<b>"]))
        docs.append(doc(parts) or "x")
    return docs


# samples
add(["<p><b>c</b><br/></p>", "<p><i>x</p></i>", "ab</p>"])
add(["<a><b/></a><c>", "x>y", "<list><item>1</item>"])
add(["<x/><y/>", "<Tr>", "a<b>", "<a></a/>", "<i><></i>"])
add(["<a><a><a/></a></a>", "<td>5/2</td><td/>"])
add(["noTags/at/all", "<x></x></x>", "<u><v><w></v>", "<h><p>1</p><p>2"])
# hidden: small (brute checks these)
for T, mp in [(500, 3), (2000, 6), (2000, 12), (1000, 30)]:
    add(small_random(T, mp))
pl = pool_of(6, 3)
add([doc(mutate(valid(ri(20, 200), pl)[0], k)) for k in ["wrong", "extra", "open", "stray", "bad"] * 200])
add([doc(valid(ri(10, 300), pl, drift=0.6)[0]) for _ in range(600)])

# hidden: big
BIG = []


def big(seed, make):
    BIG.append((seed, make))


def deep(k, nm, single=False):
    mid = "<" + nm + "/>" if single else "x"
    return ["<" + nm + ">"] * k + [mid] + ["</" + nm + ">"] * k


L = MAXL - 100
P8 = pool_of(8, 3)
big(1, lambda: [doc(deep(L // 7, "a"))])                                   # deepest, valid
big(2, lambda: [doc(deep(L // 7 - 1, "a", True))])                         # deepest point is a single tag
big(3, lambda: [doc(["<a></a>"] * (L // 7))])                              # flat, many tags
big(4, lambda: [doc(deep(L // 9, "a", True) + [">"])])                    # stray > at the end
big(5, lambda: mixed(5, pool_of(30, 4)))
big(6, lambda: mixed(7, pool_of(30, 6), drift=0.7, p_text=0.05))
big(7, lambda: [doc(mutate(valid(L, pool_of(50, 5), drift=0.6)[0], "wrong"))])
big(8, lambda: [doc(mutate(valid(L, pool_of(50, 5), drift=0.65)[0], "extra"))])
big(9, lambda: mixed(14, pool_of(10, 3)))
big(10, lambda: [doc(["<r>", "<s>"] + valid(L - 10, pool_of(10, 3), drift=0.6)[0])])  # two tags stay open
big(11, lambda: [doc(mutate(valid(L, pool_of(20, 4), drift=0.6)[0], "stray"))])
big(12, lambda: [doc(mutate(valid(L, pool_of(20, 4), drift=0.6)[0], "bad"))])
big(13, lambda: [doc(valid(L - 1000, pool_of(20, 4), drift=0.6)[0] + ["<abc"])])  # the last < has no >
big(14, lambda: [doc(deep(L // 2004, "q" * 1000)[:-1] + ["</" + "q" * 999 + "r>"])])  # long names, differ at the end
big(15, lambda: [doc(deep(L // 9 - 1, "ab")[:-1] + ["</a>"])])           # a prefix of the open name
big(16, lambda: mixed(6, pool_of(300, 8), p_text=0.45, maxtext=12))
big(17, lambda: [text(L)])                                                 # no tag at all
big(18, lambda: budget(MAXT, lambda: doc(valid(ri(1, 12), P8, drift=0.6)[0])))  # many short documents
big(19, lambda: budget(MAXT, lambda: doc(mutate(valid(ri(30, 70), P8, drift=0.6)[0], random.choice(["wrong", "extra", "open", "stray", "bad"])))))
big(20, lambda: mixed(9, pool_of(15, 4), drift=0.7))
big(21, lambda: [doc(deep(L // 14, "b") + ["<b>"] + deep(L // 14 - 1, "b"))])  # the first tag closes, a later one stays open


def budget(T, make):
    """up to T documents made by make() while the total length stays within MAXL"""
    docs, tot = [], 0
    while len(docs) < T:
        d = make()
        if tot + len(d) > MAXL:
            break
        docs.append(d)
        tot += len(d)
    return docs
big(22, lambda: [doc(["<a>"] * (L // 3 // 2) + ["</a>"] * (L // 3 // 4))])  # only the outer half closes
big(23, lambda: mixed(7, pool_of(40, 5), drift=0.65))
big(24, lambda: mixed(21, pool_of(12, 4), drift=0.6, p_text=0.3))


def cap(docs):
    """trim the last document parts so the total length fits"""
    tot = sum(len(d) for d in docs)
    assert tot <= MAXL, tot
    return docs


for seed, make in BIG:
    random.seed(241000 + seed)
    add(cap(make()))

for t in tests:
    assert t.endswith("\n") and " " not in t
os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
