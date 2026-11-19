#!/usr/bin/env python3
"""
Names of the student package (v7.2: one folder per problem; the same layout as C2_PRACTICE 4.0.0). The one place
the layout is written down for the build tools; Judge/judge.py and Judge/updater.py hold the same rules for the
students' side (the regression test compares them).

  Mock_A01/                              set folder: "Mock_" + sets.json "set" (A01 ... A12, B01 ... B08)
    Mock_A01.pdf                         the whole set with its cover (timed practice like the real exam)
    Makefile, judge.bat
    3/                                   problem 3 (1 ... 6)
      A01-3.cpp                          the student's code (create-only: empty at first, never replaced)
      3_Boxes_Within_Boxes.pdf           the statement of this problem alone (managed: replaced when it changes)
      Makefile, judge.bat                judge this problem from its own folder

A folder name never changes when a problem is replaced or re-titled; the PDF's name follows the English title.
"""
import re

TITLE_MAX = 60          # characters of the title kept in a PDF's file name


def set_dir(s):
    """Folder of a set (s: an entry of sets.json): Mock_A01."""
    return f"Mock_{s['set']}"


def prefix(s):
    """First part of a code file's name: the set, "A01"."""
    return str(s["set"])


def slot(s, i):
    """Folder of problem i (1-based) inside its set folder."""
    return str(i)


def code_name(s, i):
    return f"{prefix(s)}-{slot(s, i)}.cpp"


def code_path(s, i):
    """Package path of problem i's code file: Mock_A01/3/A01-3.cpp."""
    return f"{set_dir(s)}/{slot(s, i)}/{code_name(s, i)}"


def title_slug(title):
    """An English title as part of a file name: ASCII letters, digits and "_" only; spaces become "_", every
    other character is dropped; at most TITLE_MAX characters (the same rule as C2_PRACTICE)."""
    out = re.sub(r"[^A-Za-z0-9_]", "", re.sub(r"\s+", "_", title.strip()))
    out = re.sub(r"_+", "_", out).strip("_")[:TITLE_MAX].rstrip("_")
    if not out:
        raise ValueError(f"title gives an empty file name: {title!r}")
    return out


def pdf_name(s, i, title):
    """File name of problem i's own PDF: 3_Boxes_Within_Boxes.pdf."""
    return f"{slot(s, i)}_{title_slug(title)}.pdf"


def pdf_path(s, i, title):
    return f"{set_dir(s)}/{slot(s, i)}/{pdf_name(s, i, title)}"


def old_name(i, title):
    """Where the written file of a replaced problem goes inside Mock_Axx/old/: 3_BoxesWithinBoxes.cpp."""
    words = "".join(c if c.isalnum() and c.isascii() else " " for c in title).split()
    return f"{i}_{''.join(w[:1].upper() + w[1:] for w in words)}.cpp"


def entry_set(e):
    """The sets.json-like view of a problems.json entry ("dir": "Mock_A01/3"), also of an earlier release."""
    return {"set": e["dir"].split("/")[0][len("Mock_"):]}


def entry_code_path(e):
    """Package path of the code file of a problems.json entry."""
    return code_path(entry_set(e), int(e["dir"].split("/")[1]))
