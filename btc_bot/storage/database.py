from pathlib import Path
import yaml
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session

from btc_bot.storage.models import Base


def _load_config() -> dict:
    config_path = Path(__file__).parent.parent / "config" / "settings.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


def get_db_url(env: str | None = None) -> str:
    config = _load_config()
    env = env or config["database"]["env"]
    filename = config["database"][env]
    db_path = Path(__file__).parent / filename
    return f"sqlite:///{db_path}"


def get_engine(env: str | None = None) -> Engine:
    return create_engine(
        get_db_url(env),
        connect_args={"check_same_thread": False},
    )


def get_session_factory(env: str | None = None):
    return sessionmaker(bind=get_engine(env))


def get_session(env: str | None = None) -> Session:
    return get_session_factory(env)()


def setup_db(env: str | None = None) -> None:
    """Create all tables. Use `alembic upgrade head` for production migrations."""
    Base.metadata.create_all(get_engine(env))
