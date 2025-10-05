from logging.config import fileConfig
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from alembic import context

# 👇 Force reading the .env file from the project root
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(dotenv_path, override=True)

# Import Base and models after loading environment variables
from database import Base  # noqa: E402

# Import all models explicitly so Alembic can detect them
# These imports are necessary even if they appear as "unused" in the linter
from models import (  # noqa: F401, E402
    Company,
    Role,
    User,
    Warehouse,
    Employee,
    FaceEncoding,
    AccessLog,
    UserLoginLog,
    PasswordHistory,
    RefreshToken,
)

# Alembic configuration
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata that Alembic will use
target_metadata = Base.metadata

# Override URL with the one from .env
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_DATABASE = os.getenv("DB_DATABASE")

DATABASE_URL = (
    f"mysql+mysqldb://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
)

# Force Alembic to use the URL from .env instead of alembic.ini
config.set_main_option("sqlalchemy.url", DATABASE_URL)
print("🚀🚀 " + DATABASE_URL)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = create_engine(DATABASE_URL)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
