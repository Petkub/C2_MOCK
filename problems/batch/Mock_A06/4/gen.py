# Writes tests/NN.in for this problem. Samples first (01..05), then hidden tests.
import itertools, os, random

random.seed(1302002)
MAXN, MAXK, MAXL = 1000000, 50, 250
tests = []


def add(text, words):
    assert 1 <= len(text) <= MAXN and set(text) <= set("abcdefghijklmnopqrstuvwxyz ")
    assert text[0] != " " and text[-1] != " "
    assert 1 <= len(words) <= MAXK and sum(map(len, words)) <= MAXL
    for w in words:
        assert len(w) >= 1 and set(w) <= set("abcdefghijklmnopqrstuvwxyz?")
    tests.append("\n".join([text, str(len(words))] + words) + "\n")


def fix_ends(t):
    t = list(t)
    if t[0] == " ":
        t[0] = "a"
    if t[-1] == " ":
        t[-1] = "a"
    return "".join(t)


def rtext(n, alpha, space=0.0):
    return fix_ends("".join(" " if random.random() < space else random.choice(alpha) for _ in range(n)))


def words_text(n, vocab):
    """words from a vocabulary separated by single spaces, exactly n characters"""
    out = []
    size = 0
    while size < n:
        w = random.choice(vocab)
        out.append(w)
        size += len(w) + 1
    return fix_ends(" ".join(out)[:n])


def from_text(t, cnt, lo, hi, wild=0.0):
    """keywords cut out of the text (so they occur), some letters turned into '?'"""
    ws = []
    for _ in range(cnt):
        L = random.randint(lo, hi)
        s = random.randint(0, len(t) - L)
        w = "".join("?" if (c == " " or random.random() < wild) else c for c in t[s:s + L])
        ws.append(w)
    return ws


def rword(L, alpha):
    return "".join(random.choice(alpha) for _ in range(L))


def cap(ws):
    """keep the keywords while the total length stays within MAXL"""
    out, tot = [], 0
    for w in ws:
        if len(out) < MAXK and tot + len(w) <= MAXL:
            out.append(w)
            tot += len(w)
    return out


def pat(alpha, L, q):
    """a random keyword of length L with q question marks"""
    w = [random.choice(alpha) for _ in range(L)]
    for p in random.sample(range(L), q):
        w[p] = "?"
    return "".join(w)


VOCAB = ["the", "cat", "sat", "on", "a", "mat", "and", "dog", "ran", "to", "school", "rain", "is", "not", "in",
         "spain", "banana", "band", "ana", "can", "cannot", "see", "sea", "is", "it", "at", "tea", "eat"]

# samples
add("banana bandana", ["ana", "b?n"])
add("to be or not to be", ["o?b", "not", "zz"])
add("hello world", ["abc"])
add("mississippi", ["ss", "i?p", "si"])
add("the cat sat on the mat", ["at", "c?t", "?he"])
# hidden: small (brute checks these)
add("a", ["a"])
add("a", ["b", "?", "aa"])
add("ab cd ef", ["??", "b?c"])
t = rtext(2000, "abcd", 0.05); add(t, cap(from_text(t, 10, 3, 12, 0.2) + [rword(4, "abcd") for _ in range(10)]))
t = words_text(3000, VOCAB); add(t, cap(from_text(t, 20, 2, 10, 0.1) + ["cat", "is", "s?a", "zz", "an?"]))
t = "ab" * 1000 + "c"; add(t, ["ab", "ba", "c"])
add("abcdef xabcdef", ["abc", "def", "bcde", "f?x"])
t = rtext(2500, "ab", 0.02); add(t, cap(from_text(t, 30, 3, 12, 0.15)))
t = rtext(3000, "abc"); add(t, cap([pat("abc", random.randint(2, 6), random.randint(0, 2)) for _ in range(30)]))
t = rtext(1500, "ab"); add(t, cap(["a" * 30 + "b"] + from_text(t, 15, 5, 40, 0.5)))
# hidden: big
N = MAXN
L26 = "abcdefghijklmnopqrstuvwxyz"


# v7.1: ten weak max tests were replaced by tests with both about 10^5..4*10^5 highlighted runs and
# 3*10^7..4*10^7 occurrences, so that inserting the brackets one by one (string::insert, O(N * runs)) and storing
# every occurrence then sorting them (also over 256 MB) both fail. The old tests keep their random draws (skip),
# the new ones use their own generator, so the other tests stay the same.
rk = random.Random(71064)


def skip(*a):
    pass


def blocks(n, letter, lo, hi, gaps, inner="", p_inner=0.0):
    """blocks of `letter` (sometimes an `inner` letter) of length lo..hi, each followed by one gap from `gaps`"""
    out, size = [], 0
    while size < n:
        b = "".join(rk.choice(inner) if rk.random() < p_inner else letter for _ in range(rk.randint(lo, hi)))
        b += rk.choice(gaps)
        out.append(b)
        size += len(b)
    t = "".join(out)[:n]
    return t if t[-1] == letter else t[:-1] + letter


def ablock_words(n, lo, hi, other, p_other):
    """words of mostly 'a' (length lo..hi) separated by single spaces, exactly n characters"""
    out, size = [], 0
    while size <= n:
        w = "".join(rk.choice(other) if rk.random() < p_other else "a" for _ in range(rk.randint(lo, hi)))
        out.append(w)
        size += len(w) + 1
    return fix_ends(" ".join(out)[:n])


def fill(ws, pool):
    """the keywords ws, then copies of the short keywords in pool up to 50 keywords"""
    ws = list(ws)
    while len(ws) < MAXK and sum(map(len, ws)) + max(map(len, pool)) <= MAXL:
        ws.append(rk.choice(pool))
    return ws


def sprinkle(t, ch, rate):
    return fix_ends("".join(ch if random.random() < rate else c for c in t))


add("a" * N, cap(["a" * (m - 1) + "b" for m in range(5, 25)]))                                  # nothing found
add("a" * N, ["a" * 120 + "?", "a" * 120 + "?b"])                                              # everything
add(fix_ends(("ab " * N)[:N]), ["ab"])                                                       # many runs
add(fix_ends(("ab " * N)[:N]), ["ab", "b?a"])                                                # one run
add(("abcd" * N)[:N], ["ab", "cd"])                                                          # touching runs
add(fix_ends(("abc " * N)[:N]), ["ab", "c", "bc"])                                            # touching, many runs
t = rtext(N, L26, 0.15); skip(t, cap([pat(L26, 3, 1) for _ in range(50)]))
add(blocks(N, "a", 1, 7, "b"), fill(["aa", "aaa", "aaaa"], ["a"]))                              # 200000 runs
# v6.0.2: this test was replaced; its random draws stay so that the later tests stay the same
t = rtext(N, L26, 0.0); cap([pat(L26, 2, 0) for _ in range(50)])
# every keyword occurs at every position: about 5 * 10^7 occurrences in all
ws = []
for L in range(1, 6):
    pats = ["".join(p) for p in itertools.product("a?", repeat=L)]
    ws += [pats[(3 * i + L) % len(pats)] for i in range(10)]
add("a" * N, ws)
t = rtext(N, "ab", 0.0); skip(t, cap([pat("ab", random.randint(7, 9), random.randint(0, 1)) for _ in range(30)]))
add(blocks(N, "a", 1, 6, ["c", "c", "c", "bc"]), fill(["aab", "a?b", "aa"], ["a"]))                 # aab beats a later a
t = rtext(N, "ab", 0.08); skip(t, cap([pat("ab", random.randint(3, 10), 1) for _ in range(35)]))
add(ablock_words(N, 1, 7, "b", 0.05), fill(["ab", "ba", "aba", "aa"], ["a"]))             # words, spaces
t = rtext(N, "abcd", 0.1); skip(t, cap([pat("abcd", random.randint(4, 6), random.randint(0, 2)) for _ in range(50)]))
add(blocks(N, "z", 1, 6, ["x", "x", "yx"]), fill(["zzy", "zz", "zzz"], ["z"]))
t = words_text(N, VOCAB); add(t, ["school", "spain", "cannot", "banana", "tea", "s?a"])
t = words_text(N, VOCAB); skip(t, ["a?c", "e?t", "n?s", "t?c", "n?n"])
t = fix_ends("".join("a" if rk.random() < 0.74 else rk.choice("bcdefghij") for _ in range(N)))
add(t, fill(["ja", "aa", "aaa", "aaaa"], ["a"]))                                          # random gap letters
t = words_text(N, ["x", "y", "z", "xy", "yz", "zx", "xyz"]); skip(t, cap(from_text(t, 30, 6, 9, 0.1)))
add(blocks(N, "a", 1, 7, "cd", "b", 0.1), fill(["ab", "ba", "aab", "bb"], ["a"]))     # b inside blocks
t = sprinkle("a" * N, "b", 0.003)
add(t, cap(["a" * m for m in (30, 60, 90)] + ["a" * 40 + "?" + "a" * 20]))                     # long matches, gaps
t = sprinkle(("aab" * N)[:N], "c", 0.01)
skip(t, cap(["aab" * 15 + "aac"] * 4 + ["aac", "caa"]))
add(blocks(N, "a", 1, 5, "c", "b", 0.12), fill(["a?b", "b?a", "a?a?b", "aa"], ["a"]))         # ? inside
t = sprinkle(rtext(N, "a", 0.0), "b", 0.05); skip(t, cap(["a" * 30 + "?" * 10] * 5 + ["b?b", "ab"]))
add(ablock_words(N, 1, 7, "a", 0.0), fill(["aa", "aaa", "aaaaa"], ["a"]))                       # a-words, spaces
t = rtext(N, L26, 0.05); skip(t, cap(from_text(t, 40, 3, 3, 0.0) + [pat(L26, 2, 1) for _ in range(6)]))
add(blocks(N, "a", 1, 3, "b"), fill(["aa"], ["a"]))                                             # 333000 runs
t = rtext(N, "ab", 0.0); skip(t, cap(from_text(t, 30, 3, 12, 0.0)))
add(blocks(N, "q", 1, 6, ["s", "s", "rs"], "r", 0.05), fill(["qqr", "rq", "qq", "qrq"], ["q"]))
t = words_text(N, ["ab", "ba", "abc", "cab", "bca", "cc", "a", "b", "c", "abcab"])                # many runs, mixed lengths
add(t, cap(["ab", "c?b", "?ca", "abca", "b?b", "cab?", "a?c?b"]))

os.makedirs("tests", exist_ok=True)
for i, t in enumerate(tests, 1):
    with open(f"tests/{i:02d}.in", "w") as f:
        f.write(t)
