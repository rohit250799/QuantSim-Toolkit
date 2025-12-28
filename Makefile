.PHONY: setup analyze test lint clean

setup:
	@echo ">>> Setting up environment"
	pip install --upgrade uv
	uv sync

# Usage:
# make analyze ARGS="--ticker TCS --start 2024-01-01 --end 2024-12-31"

analyze:
	@echo ">>> Running QuantSim Toolkit"
	uv run python -m src.main analyze $(ARGS)

test:
	@echo ">>> Running tests"
	mkdir -p test-results
	uv run pytest tests/ -v 

lint:
	@echo ">>> Running type checks"
	uv run mypy . \
		--strict \
		--warn-unused-configs \
		--warn-redundant-casts

clean:
	rm -rf .pytest_cache .mypy_cache test-results

# Usage:
# make validate ARGS="-tname TCS"

validate:
	@echo "Running data validation..."
	uv run python3 -m src.main validate $(ARGS)

# Usage:
# make download ARGS="-symbol NMDC -sdate 2025-09-01 -edate 2025-09-23"

download:
	@echo "Running data download..."
	uv run python3 -m src.main download $(ARGS)

help:
	@echo "Running help command..."
	uv run python3 -m src.main $(ARGS) -h

securityCheck:
	@echo "Running security checks..."
	uv run bandit -c .bandit.yaml -r . -lll