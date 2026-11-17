from alembic import context
from sqlalchemy import create_engine
from db_config import database_url

url = database_url()

if context.is_offline_mode():
    context.configure(url=url, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    with create_engine(url).connect() as connection:
        context.configure(connection=connection)
        with context.begin_transaction():
            context.run_migrations()
