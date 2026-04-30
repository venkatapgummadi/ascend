# ASCEND — top-level Makefile
# Reviewer-facing reproduction harness for the IEEE Access submission.

.PHONY: help install test lint eval repro stats clean

help:
	@echo "ASCEND — make targets"
	@echo "  install    install ai-sync in editable mode with dev extras"
	@echo "  test       run pytest"
	@echo "  lint       run ruff"
	@echo "  eval       run conflict-fixtures benchmark"
	@echo "  stats      regenerate paper Table IX from aggregate metrics"
	@echo "  repro      install + test + lint + eval + stats (full pass)"
	@echo "  clean      remove caches"

install:
	cd ai-sync && pip install -e ".[dev]"

test:
	cd ai-sync && pytest -q

lint:
	cd ai-sync && ruff check ascend_sync tests

eval:
	cd ai-sync && PYTHONPATH=. python ../examples/conflict-fixtures/run_fixtures.py

stats:
	cd evaluation && python statistics.py --input aggregate-metrics.csv --output results.json
	@echo "Compare evaluation/results.json against Table IX in the paper."

repro: install test lint eval stats
	@echo
	@echo "==============================================="
	@echo " ASCEND reproduction pass complete."
	@echo " Outputs:"
	@echo "   - pytest:       all tests passed"
	@echo "   - ruff:         clean"
	@echo "   - eval:         conflict-fixtures hit rate (printed above)"
	@echo "   - stats:        evaluation/results.json"
	@echo "==============================================="

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type d -name .pytest_cache -prune -exec rm -rf {} +
	find . -type d -name .ruff_cache -prune -exec rm -rf {} +
	rm -rf ai-sync/.coverage ai-sync/htmlcov
