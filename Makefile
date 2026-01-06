SEEDER := scripts/seed_benchmark.py

.PHONY: setup analyze test lint clean

setup:
	@echo ">>> Setting up environment"
	pip install --upgrade uv
	uv sync
	@$(MAKE) hydrate

hydrate:
	@echo ">>> Hydrating database from golden CSV samples..."
	uv run python3 -m scripts.hydrate_db
	@echo ">>> Database hydration complete."

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
	@echo ">>> Removing temporary artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache test-results *.db
	@echo ">>> Done."

validate:
	@echo "Running data validation..."
	uv run python3 -m src.main validate $(ARGS)

download:
	@echo "Running data download..."
	uv run python3 -m src.main download $(ARGS)

help:
	@echo "Running help command..."
	uv run python3 -m src.main $(ARGS) -h

securityCheck:
	@echo "Running security checks..."
	uv run bandit -c .bandit.yaml -r . -lll