# Linux / macOS, inside this set folder (Mock_A01 ...):
#   make      judge the whole set (problem folders 1 ... 6)
#   make 3    judge problem 3 only
#   make progress   show solved problems
PYTHON ?= python3
JUDGE  := $(PYTHON) ../Judge/judge.py

all:
	@$(JUDGE)

1 2 3 4 5 6:
	@$(JUDGE) $@

progress:
	@$(JUDGE) --progress

.PHONY: all progress 1 2 3 4 5 6
