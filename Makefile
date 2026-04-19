.PHONY: install db-init db-migrate db-reset run run-sim lint clean

install:
	pip install -r requirements.txt

# Create the dev database and run all migrations
db-init:
	alembic upgrade head

# Generate a new migration after changing storage/models.py
# Usage: make db-migrate msg="add foo column"
db-migrate:
	alembic revision --autogenerate -m "$(msg)"

# Apply pending migrations
db-upgrade:
	alembic upgrade head

# Roll back the last migration
db-downgrade:
	alembic downgrade -1

# Wipe the dev database and recreate it from scratch
db-reset:
	rm -f btc_bot/storage/dev.db
	alembic upgrade head

# Run a backtest against the dev database
run:
	python -m btc_bot.main

# Run a backtest against the sim database (paper trading — never delete)
run-sim:
	python -m btc_bot.main --env sim

lint:
	python -m py_compile btc_bot/storage/models.py \
		btc_bot/storage/database.py \
		btc_bot/ingestion/candle_fetcher.py \
		btc_bot/strategy/base_model.py \
		btc_bot/strategy/random_model.py \
		btc_bot/strategy/moving_average.py \
		btc_bot/strategy/signal_generator.py \
		btc_bot/strategy/position_sizer.py \
		btc_bot/execution/paper_broker.py \
		btc_bot/execution/performance.py \
		btc_bot/main.py
	@echo "Syntax OK"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
