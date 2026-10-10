# C2_MOCK — POSN Camp 2 Practice Judge (teacher's guide)

This repo is the source of the judge that students run on their own computers for the Camp 2 mock exams
(4 sets × 5 problems, no subtasks). Students never clone it: they download `C2_Mock_Test.zip` once from
[Releases](https://github.com/Petkub/C2_MOCK/releases/latest), and from then on their judge **updates itself from
this repo** every time you push to `main`.

The Camp 1 judge lives in [C1_MOCK](https://github.com/Petkub/C1_MOCK) and works the same way. This README is
the same guide with the Camp 2 differences: **compact test data** (big tests are rebuilt on the student's computer
by `gen.py`) and **progress tracking** (`Judge/progress.json`). `CLAUDE.md` has the rules for working on the code
with Claude Code.

---

## 1. What is where

```
core/                  what students get inside Judge/   (judge.py, updater.py, include/, README.txt, CHANGELOG.txt)
problems/batch/        test data: Mock_K/N/01.in, 01.out, ..., gen.py, manifest.json (the problem's own test list)
                       + problems.json (problem bank) + sets.json (sets)
student/               the rest of the student package: README.txt, Progress.md, .vscode/, Mock_K/Mock_K.pdf,
                       set_files/ (Makefile, judge.bat, template.cpp -> 1.cpp ... 5.cpp)
samples/               known-verdict programs used by the tests (expected.json says which verdict each must get)
tests/run_regression.py          the test suite: run before every push
tools/build_manifest.py          writes manifest.json (hashes of everything students get)
tools/update_problem_manifest.py refreshes a problem's own manifest.json after adding/changing tests
tools/build_dist.py              builds dist/C2_Mock_Test.zip for new students
VERSION                          the version students see ("Judge v1.3")
manifest.json                    generated, served to students by GitHub; never edit by hand
```

What a student has: `C2_Mock_Test/Judge/` (= `core/` + `problems/` + `manifest.json`), `C2_Mock_Test/Mock_K/1.cpp ... 5.cpp`
(their code, which the updater never touches) and `Judge/progress.json` (their best scores, never touched either).

**Two manifests, do not mix them up.** `manifest.json` at the repo root lists every file of `Judge/` for the
updater. `problems/batch/Mock_K/N/manifest.json` lists that problem's tests with the SHA-256 of each input and
output, and whether the files are shipped (`in_file`/`out_file` true) or rebuilt by `gen.py` on the student's
computer (false). The judge refuses a test that is not in it.

## 2. One-time setup on a new computer

```bash
git clone https://github.com/Petkub/C2_MOCK.git
cd C2_MOCK
python3 tests/run_regression.py        # needs python3 and g++; ~40 s; must end with "All regression tests passed."
```
Optional: `gh auth login` (GitHub CLI) if you want to publish releases from the terminal.

## 3. The release routine (every change students should get)

```bash
cd ~/stupidGrader/C2_MOCK            # or wherever your clone is
# ... make the change (see section 4) ...
python3 tests/run_regression.py       # 1. tests pass
cat VERSION                           # 2. bump the version: one higher than this
echo 1.4 > VERSION
python3 tools/build_manifest.py       # 3. rebuild manifest.json (ALWAYS after the change, never before)
git add -A
git commit -m "Mock_2/3: add test 29"  # 4. commit ...
git push                              #    ... and push
```
Then check that CI is green: <https://github.com/Petkub/C2_MOCK/actions> (it runs the tests on Windows, macOS,
Linux and Python 3.7, and fails if either kind of manifest is stale).

Students receive it automatically: their judge checks GitHub at most every 10 minutes, GitHub caches files for
up to 5 minutes, so everyone who is judging gets the new version within ~15 minutes; a student who opens the judge
later gets it on that first run. To see it immediately on any installed copy:
`python3 ../Judge/judge.py --update` (inside a `Mock_K` folder).

Add one line to `core/CHANGELOG.txt` for each version; students can read it.

## 4. Common changes

### 4a. Add a test to a problem
1. Find the folder: `problems/batch/Mock_K/N/`. Tests are `01.in/01.out`, `02.in/02.out`, ... Tests `01..05`
   are the samples printed in the PDF; a new test goes at the end as a hidden test.
2. Write the input, e.g. `29.in`. Create the output **with the official solution**, never by hand:
   `g++ -O2 -std=c++17 -o sol solution.cpp && ./sol < 29.in > 29.out`
3. `python3 tools/update_problem_manifest.py Mock_K/N` — adds the test to the problem's own `manifest.json`
   as a shipped test. (For a big test you would rather have `gen.py` produce, add it to `gen.py` instead and set
   `"in_file": false` by hand; the hash must be of the file `gen.py` writes.)
4. Release (section 3). The test suite fails if a problem manifest does not match the files on disk.

### 4b. Fix a bug in the judge
1. Edit `core/judge.py` (or `core/updater.py`).
2. Add a sample program that shows the bug under `samples/batch/` and its expected verdict in
   `samples/expected.json`, so the bug cannot come back.
3. Run the tests, release. If it cannot be tested on Linux (a Windows-only problem), rely on CI's Windows job.

### 4c. Add a new mock set (e.g. set 5)
1. Test data: `problems/batch/Mock_5/1/ ... Mock_5/5/` with `NN.in`/`NN.out` (and `gen.py` if big inputs are
   generated), then `python3 tools/update_problem_manifest.py --all`.
2. `problems/batch/problems.json`: one entry per new problem (`"en"`, `"title"`, `"tier"`, `"dir": "Mock_5/1"`,
   `"samples"`), with new ids.
3. `problems/batch/sets.json`: append `{"set": 5, ..., "problems": [ids in order]}`.
4. `student/Mock_5/Mock_5.pdf` (the statement).
5. Release. Existing students get the test data, `Mock_5/Mock_5.pdf`, `Makefile`, `judge.bat`, and the
   updater **creates** `Mock_5/1.cpp ... 5.cpp` (templates are only ever created, never overwritten).

### 4d. Change something students see outside Judge/ (README, Makefile, judge.bat, template, Progress.md)
Edit it under `student/` and release. These are *managed* files: the updater replaces them on every student's
computer when they change (the old copy goes to `Judge/.backup/_package/`), because students do not edit them.
The only files that are never replaced are the `Mock_K/N.cpp` templates (created once, then the student's own)
and `Judge/progress.json`.

### 4e. A new zip for new students
```bash
python3 tools/build_dist.py                                   # -> dist/C2_Mock_Test.zip (big tests and progress.json left out)
gh release create v1.4 dist/C2_Mock_Test.zip --title "C2_Mock_Test v1.4"
```
The link <https://github.com/Petkub/C2_MOCK/releases/latest/download/C2_Mock_Test.zip> always gives the newest
release. You only need a new release for new students (or new sets); existing students update themselves.

## 5. How the self-update works (so you can trust it)

- `Judge/updater.py` fetches `manifest.json` from `raw.githubusercontent.com/Petkub/C2_MOCK/main/`, compares the
  SHA-256 of every file in `Judge/`, downloads the changed ones to a temp folder, verifies each hash, compiles
  the new `.py` files and test-runs the new `judge.py --help`, and only then swaps them in. The old file is kept
  in `Judge/.backup/`.
- Outside `Judge/` it only replaces the managed files above and creates missing `Mock_K/N.cpp` templates; it
  never deletes anything and never touches an existing `Mock_K/N.cpp` or `Judge/progress.json`. Big tests that `gen.py` rebuilt on the student's computer are not in
  the manifest and are left alone.
- No network, a slow network (> 2 s), a bad hash, a strange path: it keeps the current version and says nothing.
  A failed update never stops a student from judging.
- Students with a zip from **before** the updater existed (before v1.2) must download the zip once; nothing can
  reach them otherwise. That zip also fixes the Windows bug where big tests failed their checksum.

## 6. Checking a student's problem report

- "The judge says I have the old version": ask them to run `python3 ../Judge/judge.py --update`. Its message says
  why it cannot update (e.g. a school firewall, or a macOS Python without certificates:
  `CERTIFICATE_VERIFY_FAILED` → run "Install Certificates.command" from the Python folder).
- "Could not rebuild test(s) ... on this computer": their `gen.py` output does not match the hash. Ask for their
  Python version and OS; a judge older than v1.2 on Windows always fails this way (update fixes it).
- "My correct code gets Runtime Error / Wrong Answer": ask for the problem, the test number and the line printed
  under *First failure* (e.g. `your program crashed (signal 11 SIGSEGV: invalid memory access)`). Then run their
  file here: `python3 core/judge.py their.cpp K-N` (that creates the big tests under `problems/batch/` and a
  `core/progress.json`; neither is shipped, `progress.json` is ignored by git, and the big inputs show up
  as untracked in `git status`: do not `git add` them). The judge compiles with `-O2`, which
  exposes uninitialised variables and out-of-bounds reads that pass on the student's own compile.
- Progress: `python3 ../Judge/judge.py --progress` inside a student's `Mock_K` shows what they have solved;
  the file is `Judge/progress.json`.

## 7. Things that go wrong, and the fix

| Symptom | Fix |
|---|---|
| CI red: "manifest.json is stale" | `python3 tools/build_manifest.py`, commit, push. |
| CI red: "problem manifests match the test files" | `python3 tools/update_problem_manifest.py --all`, commit, push. |
| A pushed version is broken | `git revert HEAD`, bump `VERSION`, rebuild the manifest, push. Students roll forward to the fixed version; their `Judge/.backup/` also still has the previous files. |
| `build_dist.py` refuses to overwrite | it only replaces a `dist/C2_Mock_Test` folder it made itself, so a student folder is never wiped; delete `dist/` by hand if you are sure. |
| Students on Windows see `?` boxes | they can use `--ascii`; the judge output must stay ASCII-safe. |

## 8. Never

- Edit either `manifest.json` by hand, or commit without rebuilding them.
- Commit the big inputs that judging in the repo generated (untracked `NN.in` files in `git status`), or
  `core/progress.json`.
- Delete or rename a test that students already have (the updater never deletes; add a new one instead).
- Type an expected output by hand.
- Change the judge's exit codes, the manifest format or the updater's safety rules without updating the tests.
