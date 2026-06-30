# ASCEND — top-level Makefile
# Reviewer-facing reproduction harness. Every number is regenerated from the
# PUBLIC benchmark in ./benchmark — no private or NDA-gated data in the loop.

BENCH        := benchmark
PY           := python
OWASP_DIR    := $(BENCH)/_data/owasp-benchmark
SARIF_DIR    := $(BENCH)/_data/sarif
FIXTURES     := examples/conflict-fixtures
SAMPLE_APP   := examples/sample-python-app
RESULTS      := $(BENCH)/results

.PHONY: help install test lint repro eval eval-coverage eval-sync eval-overhead eval-latex clean clean-eval

help:
	@echo "ASCEND — make targets"
	@echo "  install        editable install + public-benchmark requirements"
	@echo "  test           run pytest"
	@echo "  lint           run ruff"
	@echo "  eval           run the whole public benchmark (coverage + sync + overhead)"
	@echo "  eval-coverage  detection coverage on the OWASP Benchmark"
	@echo "  eval-sync      conflict-resolution metrics on public fixtures"
	@echo "  eval-overhead  per-layer scanning overhead on the sample apps"
	@echo "  eval-latex     print LaTeX rows for the paper tables"
	@echo "  repro          install + test + lint + public benchmark + latex (full pass)"
	@echo "  clean          remove caches"

install:
	cd ai-sync && pip install -e ".[dev]"
	$(PY) -m pip install -r $(BENCH)/requirements.txt

test:
	cd ai-sync && pytest -q

lint:
	cd ai-sync && ruff check ascend_sync tests

## Full reproducible pass: install -> test -> lint -> public benchmark -> latex
repro: install test lint eval eval-latex
	@echo
	@echo "==============================================="
	@echo " ASCEND reproduction pass complete."
	@echo " Outputs in $(RESULTS)/ :"
	@echo "   - coverage.json   detection coverage (OWASP Benchmark)"
	@echo "   - sync.json       conflict-resolution metrics (95% CI)"
	@echo "   - overhead.json   per-layer scanning overhead"
	@echo "==============================================="

## Run the whole public benchmark
eval: eval-coverage eval-sync eval-overhead

eval-coverage:
	@echo ">> Detection coverage (OWASP Benchmark). Ensure SARIF exports exist in $(SARIF_DIR)."
	$(PY) $(BENCH)/run_coverage.py --benchmark $(OWASP_DIR) --sarif-dir $(SARIF_DIR) \
		--out $(RESULTS)/coverage.json

eval-sync:
	$(PY) $(BENCH)/run_sync.py --fixtures $(FIXTURES) --tau 0.85 --bootstrap 10000 \
		--out $(RESULTS)/sync.json

eval-overhead:
	$(PY) $(BENCH)/run_overhead.py --app $(SAMPLE_APP) --runs 5 \
		--out $(RESULTS)/overhead.json

eval-latex:
	$(PY) $(BENCH)/gen_latex.py $(RESULTS)/coverage.json $(RESULTS)/sync.json $(RESULTS)/overhead.json

clean-eval:
	rm -rf $(RESULTS)

clean: clean-eval
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type d -name .pytest_cache -prune -exec rm -rf {} +
	find . -type d -name .ruff_cache -prune -exec rm -rf {} +
	rm -rf ai-sync/.coverage ai-sync/htmlcov

# Removed: the old `stats` target that ran a Welch t-test on a synthetic
# schema-demonstration CSV and the field-study reproduction that required
# private per-repository telemetry. Those claims are withdrawn.
