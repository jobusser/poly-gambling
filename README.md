# poly-gambling

btc_bot/
├── config/
│   └── settings.yaml          # thresholds, symbols, fee rates
├── ingestion/
│   ├── candle_fetcher.py       # CandleFetcher — ccxt wrapper
│   ├── normaliser.py           # Normaliser — validate & align
│   └── scheduler.py            # run_loop() — APScheduler entry
├── features/
│   ├── engineer.py             # FeatureEngineer — RSI, EMA, etc.
│   └── cache.py                # FeatureCache — read/write SQLite
├── strategy/
│   ├── base_model.py           # ABC: predict(df) → float
│   ├── logistic_model.py       # first concrete model
│   ├── signal_generator.py     # SignalGenerator — prob → action
│   └── position_sizer.py       # PositionSizer — Kelly / fixed
├── execution/
│   ├── paper_broker.py         # PaperBroker — virtual orders
│   └── performance.py          # PerformanceTracker — metrics
├── backtest/
│   └── engine.py               # Backtester — replay loop
├── storage/
│   └── db.py                   # init_db(), write_candle(), etc.
├── tests/
└── main.py  