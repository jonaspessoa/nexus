import os

from sqlalchemy.engine import make_url


def database_url():
    url = make_url(os.environ["DATABASE_URL"])
    if url.drivername in {"postgresql", "postgres"}:
        return url.set(drivername="postgresql+psycopg")
    return url
