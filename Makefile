.PHONY: install lint test run docker-up docker-down eval index clean help

PYTHON := python3
UV := uv
SRC := src
export PYTHONPATH := $(CURDIR)
TESTS := tests
COVERAGE_MIN := 80

help:
	@echo "Available targets:"
	@echo "  install      Install all dependencies with uv"
	@echo "  lint         Run ruff + mypy"
	@echo "  test         Run pytest with coverage"
	@echo "  run          Start FastAPI dev server"
	@echo "  docker-up    Start full local stack (API + ChromaDB + Prometheus + Grafana + Jaeger)"
	@echo "  docker-down  Stop all containers"
	@echo "  eval         Run RAGAS evaluation suite"
	@echo "  index        Index sample documents"
	@echo "  clean        Remove build artifacts and caches"

install:
	$(UV) sync

lint:
	$(UV) run ruff check $(SRC) $(TESTS)
	$(UV) run ruff format --check $(SRC) $(TESTS)
	$(UV) run mypy $(SRC)

format:
	$(UV) run ruff format $(SRC) $(TESTS)
	$(UV) run ruff check --fix $(SRC) $(TESTS)

test:
	$(UV) run pytest $(TESTS)/unit $(TESTS)/integration \
		--cov=$(SRC) \
		--cov-report=term-missing \
		--cov-fail-under=$(COVERAGE_MIN) \
		-v

test-unit:
	$(UV) run pytest $(TESTS)/unit -v

test-integration:
	$(UV) run pytest $(TESTS)/integration -v

run:
	$(UV) run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

docker-up:
	docker compose up --build -d
	@echo "Services starting..."
	@echo "  API:        http://localhost:8000"
	@echo "  API docs:   http://localhost:8000/docs"
	@echo "  Prometheus: http://localhost:9090"
	@echo "  Grafana:    http://localhost:3000"
	@echo "  Jaeger:     http://localhost:16686"

docker-down:
	docker compose down

eval:
	$(UV) run pytest $(TESTS)/evaluation -v --tb=short

index:
	$(UV) run python -m scripts.index_samples

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; true
	find . -type f -name "*.pyc" -delete 2>/dev/null; true
	rm -rf .coverage htmlcov .mypy_cache .ruff_cache dist .pytest_cache
