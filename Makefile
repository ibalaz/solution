.PHONY: help install dev test lint format run docker-build docker-run clean

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install dependencies"
	@echo "  dev          - Install development dependencies"
	@echo "  test         - Run tests"
	@echo "  lint         - Run linting (flake8)"  
	@echo "  format       - Format code (black, isort)"
	@echo "  run          - Run the application"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run with Docker Compose"
	@echo "  clean        - Clean up cache files"

# Installation
install:
	pip install -r requirements.txt

dev: install
	pip install black isort flake8 mypy

# Testing
test:
	python -m pytest tests/ -v

test-cov:
	python -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term

# Code quality
lint:
	flake8 src/ tests/
	mypy src/

format:
	black src/ tests/
	isort src/ tests/

format-check:
	black --check src/ tests/
	isort --check-only src/ tests/

# Development
run:
	uvicorn src.tickethub.main:app --reload --host 0.0.0.0 --port 8000

# Docker
docker-build:
	docker build -t tickethub:latest .

docker-run:
	docker-compose up --build

docker-stop:
	docker-compose down

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage

# CI/CD helpers
ci-test: dev lint test-cov

# Production
prod-run:
	uvicorn src.tickethub.main:app --host 0.0.0.0 --port 8000 --workers 4