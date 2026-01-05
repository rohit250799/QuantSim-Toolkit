SEEDER := scripts/seed_benchmark.py

.PHONY: setup analyze test lint clean

setup:
	@echo ">>> Setting up environment"
	pip install --upgrade uv
	uv sync
	@$(MAKE) hydrate

hydrate:
	@echo ">>> Hydrating local database from CSV source..."
	# We use 'uv run' to ensure we use the correct virtual environment
	# We call the specific seeder functions to build the initial state
	uv run python3 -c "\
	from src.logic.seeder import seed_database; \
	seed_database('NIFTY50', 'NIFTY50_id.csv'); \
	seed_database('TCS', 'TCS_id.csv'); \
    seed_database('ITC', 'ITC_id.csv') \   
	seed_database('RELIANCE', 'RELIANCE_id.csv')"
	@echo ">>> Environment and Database ready."


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