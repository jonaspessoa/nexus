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
    connection.execute(
        text(
            "INSERT INTO services (project_id, name, url) "
            "SELECT id, :name, :url FROM projects WHERE slug = :slug "
            "ON CONFLICT (project_id, url) DO NOTHING"
        ),
        {
            "slug": "portfolio-demo",
            "name": "Site do portfólio",
            "url": "https://jonaspessoa.github.io/",
        },
    )
