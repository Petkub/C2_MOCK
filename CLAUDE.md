# C2_MOCK: POSN Camp 2 Practice Judge

A terminal judge that students run on their own machines to practice for the POSN Computer Olympiad (Camp 2, no subtasks). Since v7.0 the sets come in tracks: Track A = 12 exam-level sets x 6 problems
(`Mock_A01` ... `Mock_A12`, set names A1 ... A12, `--set A3`); Track B = 8 harder
sets x 6 beyond the syllabus (`Mock_B01` ... `Mock_B08`, B1 ... B8, no target scores, progress counted apart). Set keys are strings ("A01"); `judge.py` helpers `set_key` / `set_label` / `set_index` / `track_of` parse them.
**7.2 is the first release students get** (no student has an older package, so there is no code for older layouts;
plan `C2_MOCK_SRC/plans/V7_LAYOUT.md`, teacher's override 2026-11-20: no migration). The student package has **one
folder per problem**, the same layout as C2_PRACTICE 4.0.0: `Mock_A01/3/A01-3.cpp` (the student's code) and
`Mock_A01/3/3_<English_Title>.pdf` (that problem's PDF); the whole set stays in `Mock_A01/Mock_A01.pdf`. Folder and
code-file names never change; the PDF's name follows the English title (letters, digits and `_` only, at most 60
characters). **`tools/layout.py` is the one place for these names** (build tools, and `C2_MOCK_SRC`'s build);
`core/judge.py` and `core/updater.py` hold the same rules for the students' side, and the regression test
(`test_layout`) compares them. Change a name in all three.
Sibling repo `C1_MOCK` is the Camp 1 judge (same structure); fix shared bugs in both.
Today it judges batch problems (`judge.py`). We are adding interactive and communication problems,
and it updates itself from this GitHub repo so bugs can be fixed without re-sending zip files.

## Hard constraints (never break these)

1. **Python 3.7+ standard library only.** No pip packages. Students have Python and g++, nothing else.
2. **Student machines run Windows, macOS and Linux.** Every change must work on all three.
   Use `os.name == "nt"` guards like `judge.py` does. Never assume `/tmp`, `fork`, `resource`, or bash.
3. **Never touch student code.** The updater writes only files listed in `manifest.json`: inside `Judge/`,
   plus the managed package files students do not edit (PDFs, Makefile, judge.bat, READMEs, `.vscode/`) and
   missing code files `Mock_<set>/<n>/<set>-<n>.cpp` (empty, create-only). It must never read, move, delete or
   overwrite an existing student `.cpp` or `progress.json`, and never touch a file it did not ship. One exception
   (approved by the teacher 2026-11-13, v6.1; the rules of C2_PRACTICE's V4_LAYOUT section 3): when a release
   after 7.2 moves or replaces problems, the manifest's `moves` let a student's written file follow its problem
   once (`follow_moves` in `updater.py`): by English title to `Mock_<set>/<n>/<set>-<n>.cpp` (also into another
   set); a replaced problem's file to `Mock_<set>/old/<n>_<OldTitle>.cpp`; never over written code (on a clash the
   incoming file goes to `Mock_<set>/old/<name>_moved.cpp` and the judge prints it); empty starters stay; nothing
   deleted; every move printed once (`show_moves` in `judge.py`), the second run is quiet.
4. **Never delete files the updater does not own.** No "wipe and reinstall" step, ever.
5. **Fail safe.** If the network is down, slow (>2 s), or a hash does not match, keep the current
   version and continue silently. A broken update must never stop a student from judging.
6. **Do not change the existing look.** New commands reuse `Style`, `box`, `rule`, `bar`, `compile_source`
   and the scoring functions from `judge.py` so everything feels the same (verdict table, score bar).
7. **Output is English, ASCII-safe.** Keep the `--ascii` and `--no-color` fallbacks working.

## Repo layout

```
C2_MOCK/
  CLAUDE.md
  core/                         # what students get inside Judge/
    judge.py                    # batch judge (existing, keep working)
    interactive_judge.py        # interactive problems (prototype exists)
    communication_judge.py      # TODO: IOI-style manager + stub
    updater.py                  # self-update from GitHub (manifest + SHA-256), see below
    include/bits/stdc++.h       # macOS fallback header
  problems/
    batch/Mock_K/N/*.in|out, gen.py, manifest.json   # see "Compact test data" below
    batch/problems.json         # problem bank: id -> title, tier, dir (Mock_K/N), samples, subtasks, optional ml (MB)
    batch/sets.json             # set key ("A01") -> list of problem ids (6) and its "track" ("A" / "B")
    interactive/<name>/{problem.json, interactor.cpp, tests/NN.in}
    communication/<name>/{problem.json, manager.cpp, stub/, tests/}
  student/                      # student-side files outside Judge/ (copied by build_dist.py)
    README.txt, Progress.md, .vscode/
    Mock_A01/Mock_A01.pdf                           # the whole set with its cover
    Mock_A01/3/3_<Title>.pdf                        # one problem; all PDFs are written by C2_MOCK_SRC build.py all
    set_files/{Makefile, judge.bat}                 # in every set folder (a Makefile_<n> is used for a set of n != 6
                                                    # problems): whole set, `make 3` / `judge 3`, `make progress`
                                                    # (a problem folder gets no Makefile / judge.bat)
    set_files/template.cpp                          # (empty) -> Mock_A01/3/A01-3.cpp
  samples/                      # known-verdict programs used as regression tests
    batch/towers_ok.cpp, towers_smallhi.cpp, towers_slow.cpp, towers_crash.cpp, towers_syntax.cpp
    interactive/guess_ok.cpp, guess_noflush.cpp, guess_linear.cpp, guess_crash.cpp
    expected.json               # {"batch/towers_ok.cpp": {"problem": "3-2", "verdict": "AC", "score": 100}, ...}
                                # verdict: AC/WA/TLE/RE/MLE/CE (first failing test); "score" optional (runs all tests)
  tools/
    layout.py                   # the names of the student package (code_path, pdf_path, old_name): the one place
    build_manifest.py           # writes manifest.json (VERSION + SHA-256 of every file in Judge/); --check for CI
    moves/problems_<v>.json     # problems.json of release <v> (from 7.2 on; none yet), see "Self-update"
    update_problem_manifest.py  # refreshes problems/batch/Mock_K/N/manifest.json after adding tests; --check --all in CI
    build_dist.py               # builds the student zip (C2_Mock_Test/ layout with Judge/ and one folder per problem)
  tests/
    run_regression.py           # runs every sample, compares verdicts with expected.json
  .github/workflows/ci.yml      # matrix: windows-latest, macos-latest, ubuntu-latest
  VERSION                       # e.g. 1.0; bump it with every change students should get
  manifest.json                 # generated by build_manifest.py, committed, served by GitHub raw; do not edit by hand
```

Student-side layout (what `build_dist.py` produces): `C2_Mock_Test/Judge/` = `core/` + `problems/`,
and `C2_Mock_Test/Mock_A01/3/` = one problem: the student's `A01-3.cpp` (empty at first), `3_<Title>.pdf` and
nothing else (teacher's decision 2026-11-20: no `Makefile` / `judge.bat` in a problem folder; the updater refuses
such a path); the set folder also holds `Mock_A01.pdf`, `Makefile`, `judge.bat` (and `old/` after an update that
replaced a problem the student had written). The repo layout is **not** the student layout.
The judge finds the problem from the code file's name (`A01-3.cpp`, also `a1-3.cpp`: `problem_of_name`) or from its
folder (`Mock_A01/3/`: `problem_of_folder`), the name first; both must keep working. Inside a problem folder, no
arguments = that problem; inside a set folder, no arguments = the whole set and `3` = problem 3. A file that is not a
`.cpp` (Ctrl+Shift+B on `Progress.md`) shows the progress dashboard. Binaries are compiled in `Judge/.build/<new
folder>` (`make_build_dir`; removed after the run; the system temp folder when `Judge/` is not writable), never in a
set or problem folder (`test_judging` checks that nothing is left behind and that `Judge/.build/` is empty).
The progress tracker is keyed by problem id (`Judge/progress.json`), so a score stays with its problem when the
problem moves.
`judge.py` finds batch data in the first existing of `Judge/problems/batch/` (student package),
`../problems/batch/` (repo, run from `core/`) and `Judge/tests/` (older zips, JSON files next to judge.py).

## Compact test data and progress (C2 only)

- Each problem folder has `gen.py` and a per-problem `manifest.json` (not the updater's `manifest.json`).
  Tests with `"in_file": false` are not shipped: `judge.py` rebuilds them with `gen.py` the first time the
  problem is judged and checks their SHA-256. `"out_file": false` outputs are compared by hash only.
- Judging in the repo (`python3 core/judge.py ...`) writes those big inputs into `problems/batch/` and a
  `core/progress.json`. Never commit them; `build_dist.py` leaves them out, and the regression tests run inside
  a temporary built package so they never create them.
- `Judge/progress.json` is the student's own history (best score per problem). Never ship or overwrite it.

## Judging rules (batch)

- Compile: `g++ -O2 -std=c++17 -Wall -Wno-sign-compare -Wno-char-subscripts` (Windows: `-static`).
- Stack: 256 MB on every platform (recursion of depth 10^6 runs; regression test `towers_deep.cpp`). Linux:
  `raise_stack_limit` raises the judge's soft RLIMIT_STACK (inherited by the program; capped by the hard limit,
  normally unlimited). macOS: the hard limit is 64 MB, so `-Wl,-stack_size,0x10000000` is linked in (dropped if
  the linker rejects it; then 64 MB). Windows: `-Wl,--stack,268435456`.
- Time = wall-clock time of the run (`perf_counter`, includes process start); a slow but finished run is measured
  once more. Memory is not capped while the program runs: the peak is checked after it (below), so a 400 MB
  program gets MLE, it is not killed at 256 MB.
  Warnings are shown after "Compiled" (a count in set mode); they do not change the verdict.
- Limits: time `--tl` (default 1 s, hard kill at 2x+0.5 s), memory `--ml` (default 256 MB, the statements;
  `"ml"` in `problems.json` per problem). Memory = the program's peak resident size, read every millisecond while
  it runs (`/proc/<pid>/status VmHWM` on Linux, `proc_pid_rusage` on macOS, `GetProcessMemoryInfo` after exit on
  Windows); `ru_maxrss` of the child (`exited_peak`) only as a last check after the exit, because it includes the
  judge's own Python image before exec: used when it is clearly above the judge's own peak and above the readings
  (a program can grow after the last reading). On macOS the reading is `max(ri_phys_footprint,
  ri_lifetime_max_phys_footprint)`; never compare it with `ri_resident_size`, which counts shared pages too (that
  check threw away nearly every reading and made a 200 MB program AC now and then on CI).
  Verdicts in order: MLE, TLE (killed), WA (output over 64 MB), RE (exit code != 0), TLE (slow), AC/WA.
- Score: every C2_MOCK problem has `"scoring": "all"` in `problems.json` (100 only when every test passes, else 0,
  like the real exam); the result still shows `passed/total tests`. Without the field: share of tests passed.
- The last 8 KB of the program's stderr are kept; after an RE the last 5 lines are shown (exception text, assert).
- Samples for the regression suite: `*_mle.cpp`, `*_throw.cpp`, `*_warn.cpp` next to the AC/WA/TLE/RE/CE ones.

## Interactive protocol (already implemented, keep compatible)

- Interactor is called as `interactor <input-file> <output-file>` and talks to the student on stdin/stdout.
- Exit code: `0` OK, `1` Wrong Answer, `2` Presentation Error (treated as WA), `3` judge failure.
  One line on stderr is the message shown to the student. This matches testlib.
- The judge relays the pipes and records the conversation, so failures show a `you` / `judge` transcript.
- A student program that hangs while the judge waits gets a flush hint
  (`cin.tie(0); ios::sync_with_stdio(0);` disables the automatic flush; the course template has it).
- Times are wall-clock on the student's machine: fine for practice, not for ranking.

## Communication problems (next, design before coding)

Manager process + one or more student processes linked by pipes, with a stub/grader header the
student includes. Reuse the pipe relay and transcript code from `interactive_judge.py`.
Propose the design and wait for approval before writing it.

## Self-update (implemented: `core/updater.py`, hooks in `judge.py`)

- Hosting is GitHub raw: `https://raw.githubusercontent.com/Petkub/C2_MOCK/main/` is the one
  constant (`BASE_URL` in `updater.py`; `REPO` differs between C1_MOCK and C2_MOCK). HTTPS only; the env var
  `JUDGE_UPDATE_URL` may point at `http://127.0.0.1:PORT/` for tests. `JUDGE_NO_UPDATE=1` disables checks
  (set by the regression tests and by the judge when it restarts after an update).
- `judge.py` is the entry point students already have (Makefile, judge.bat, VS Code tasks), so there is no
  separate launcher: `judge.py` imports `updater.py`, calls `updater.check()` at start-up (at most once every 10 minutes,
  stamp file `Judge/.update_check`), and after an update re-runs itself with the same arguments.
- `check()`: fetch `manifest.json` (2 s timeout) -> compare hashes (files whose hash equals the installed
  `Judge/manifest.json` entry are trusted without re-reading; `--update` re-hashes everything) -> download the
  changed files into `Judge/.update_tmp/` -> verify every SHA-256, `compile()` every `.py`, run the new
  `judge.py --help` -> only then `os.replace` them in (data first, `judge.py` last), old files to `Judge/.backup/`
  -> write the new `Judge/manifest.json`. Any failure: remove the temp folder, keep the current version, silent.
- Paths: only `Judge/`-relative, no absolute, no `..`, no `\`, no leading `.`, never `manifest.json` /
  `progress.json`. Outside `Judge/` only two kinds, each matched by a strict regex in `updater.py`:
  *managed* files students do not edit (`Mock_<S>/Mock_<S>.pdf`, `Mock_<S>/<n>/<n>_<Title>.pdf`, `Makefile` and
  `judge.bat` of a set folder only, `README.txt`, `Guide.pdf`, `Progress.md`, `.vscode/*.json`)
  are replaced when their hash changes (old copy in `Judge/.backup/_package/`);
  *create-only* files (`Mock_<S>/<n>/<S>-<n>.cpp`, S = `[AB][0-9]{2}`, n = 1..9: the set and the number in the name
  must agree with the folders, `SET_FILE`) are added only when missing. A `.cpp` can never be managed. Nothing is
  ever deleted.
- Retired PDFs: a problem PDF is named after its English title, so a re-titled problem gets a new PDF name and
  the new manifest no longer lists the old one. The updater moves the old PDF to `Judge/.backup/_package/` only when
  its bytes are exactly what it installed (the hash in the installed `Judge/manifest.json`) and the new manifest
  manages another PDF in the same problem folder (`plan_retired`, `retire`). No list of old names is needed; a file
  with other bytes stays.
- Versions: `check()` installs a release only when its `version` is **strictly newer** (`version_key`: numbers,
  4.10 > 4.9, 4.1 = 4.1.0). An older release never replaces a newer package (e.g. a build from a branch: before this
  rule a 4.0.0 on GitHub turned such a package back, retiring its PDFs), the same version is left alone, and a forced
  check of the same version only repairs missing or damaged files whose hash in the release is the installed one
  (`installed_view`). So every release must bump `VERSION`. Regression: `test_versions` (newer / same / older), and
  `test_future_update` serves `next_version(VERSION)`.
- Only an installed package updates (`Judge/judge.py` and `Judge/manifest.json` exist); `core/` in the repo never.
- `--update` forces a check and prints the result; `--no-update` skips it; the header box shows `Judge vX.Y`
  (from `Judge/manifest.json`). Recovery when `judge.py` itself is broken: `python3 ../Judge/updater.py`.
- Manifest format (version in `tools/build_manifest.py`): `version`, `sources` (Judge/ prefix -> repo folder),
  `files` (Judge/ path -> sha256), `managed` and `create_only` (package path -> [sha256, repo path]), `bundles`,
  `moves`. It is one plain view: no legacy or bootstrap views (every installed updater reads it as it is).
- Speed: GitHub raw answers one file in about 0.3 s, so an updater that fetches files one
  by one needs minutes for a new set of problems (v3.0 of C1_PRACTICE: ~1,950 files, ~11 minutes, and one slow
  request aborted all of it). The updater therefore downloads in parallel (`WORKERS`), retries each file (`TRIES`),
  fetches one `bundles/<folder>.zip` per problem folder when it needs many of its files (every member is still
  checked against its own sha256 in `files`), and prints "Downloading ..." for big updates.
  `build_manifest.py` writes the bundles (deterministic zips, rewritten only when their content changes) and
  `manifest.json` lists them under `bundles`. Commit `bundles/` with the manifest.
- Moves (releases after 7.2 move, replace and re-title problems): `moves` is {sha256 of an earlier release's
  `problems.json`: [[from, to], ...]}, built by `build_manifest.py` from `tools/moves/problems_<v>.json` (exact bytes of
  release `<v>`; none exist yet). The same English title = the same problem (`RENAMED` in `build_manifest.py` maps an
  old title to a new one; without it a re-title counts as a replacement); a problem that is no longer in the sets
  goes to `Mock_<set>/old/<n>_<OldTitle>.cpp`. After an update, `follow_moves` finds the hash of the `problems.json`
  it replaced (in `Judge/.backup/`), applies the pairs once (`Judge/.moves_done`) under the rules of hard constraint
  3, and puts an empty starter back where a file moved away. Ids in `problems.json` stay with their problems, so the
  tracker's scores follow. Regression: `test_future_update` (a fake 7.3 over local HTTP: re-titled, replaced and
  moved problems inside a set and across sets, a clash, files the updater did not ship, tracker scores kept, a quiet
  second run).
- There is no legacy manifest, no bootstrap view and no code for layouts before 7.2 (`Mock_K/N.cpp`): they were
  removed with 7.2 because no student ever had those packages. Do not add them back.

## Releasing a change to students

1. Make the change, add a sample/test, run `python3 tests/run_regression.py`.
2. If the release moves, replaces or re-titles problems: first save the released `problems.json` (exact bytes, e.g.
   `git show v7.2:problems/batch/problems.json`) as `tools/moves/problems_<released version>.json`, and put re-titled
   problems in `RENAMED` in `tools/build_manifest.py`.
3. Bump `VERSION`, run `python3 tools/build_manifest.py`, commit both with the change, push.
   CI fails if `manifest.json` is stale. Students get the new files on their next judge run (GitHub raw caches
   for up to 5 minutes; a forced `--update` adds `?t=<time>` to every URL to skip that cache).
   `build_manifest.py` stops with "missing student/Mock_.../<n>_<Title>.pdf" when a problem PDF is not there: run
   `C2_MOCK_SRC`'s `build.py all` first.
4. For new students: `python3 tools/build_dist.py` and publish `dist/C2_Mock_Test.zip` (GitHub Release).

## Commands

```
python3 tests/run_regression.py          # must pass before every commit
python3 tools/build_manifest.py          # after changing anything under core/, problems/ or student/ (and bump VERSION)
python3 tools/build_manifest.py --check  # CI: fails if manifest.json is stale
python3 tools/update_problem_manifest.py Mock_K/N   # after adding NN.in/NN.out to a problem (--check --all in CI)
python3 tools/build_dist.py              # build dist/C2_Mock_Test/ + dist/C2_Mock_Test.zip (--out DIR, --no-zip)
python3 core/judge.py samples/batch/towers_ok.cpp A7-3     # judge one file from the repo (creates big tests, see above)
python3 core/interactive_judge.py guess samples/interactive/guess_ok.cpp
```
In a student package (`dist/C2_Mock_Test/`):
```
python3 ../../Judge/judge.py             # in a problem folder (Mock_A03/5): that problem (no `make` / `judge` there)
python3 ../Judge/judge.py                # in a set folder: the whole set; also `make`, `judge`
python3 ../Judge/judge.py 5              # in a set folder: problem 5; also `make 5`, `judge 5`
python3 <path>/Judge/judge.py FILE.cpp   # anywhere: the problem from the file's name or folder (Ctrl+Shift+B does this)
python3 <path>/Judge/judge.py FILE.cpp K-P   # name the problem yourself (A3-5)
python3 ../Judge/judge.py --list         # sets with their folders and code names
python3 ../Judge/judge.py --progress     # the tracker (--progress A3: one set)
```

## Working rules for Claude Code

- Before changing `judge.py`, run the regression tests; after changing it, run them again.
- Add a sample program + expected verdict for every new behaviour or bug fix.
- Keep functions small and readable, in the same style as `judge.py`. No new dependencies.
- If a change cannot be verified on Windows locally, say so and rely on the CI matrix.
- Ask before: changing the manifest format, the exit-code protocol, or the safety rules of the updater.
