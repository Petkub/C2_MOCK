# Linux / macOS, inside this Mock folder:
#   make      judge the whole set (1.cpp ... 5.cpp)
#   make 3    judge problem 3 only
#   make progress   show solved problems
PYTHON ?= python3
JUDGE  := $(PYTHON) ../Judge/judge.py

all:
	@$(JUDGE)

1 2 3 4 5:
	@$(JUDGE) $@.cpp

progress:
	@$(JUDGE) --progress

.PHONY: all progress 1 2 3 4 5
