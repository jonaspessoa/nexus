import os

from sqlalchemy import create_engine, text

engine = create_engine(os.environ["DATABASE_URL"])
with engine.begin() as connection:
    connection.execute(
        text(
            "INSERT INTO projects (slug, name) VALUES (:slug, :name) "
            "ON CONFLICT (slug) DO NOTHING"
        ),
        {"slug": "portfolio-demo", "name": "Portfólio (demo)"},
    )
