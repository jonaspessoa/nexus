"""Store services and their investigation tasks."""

import sqlalchemy as sa
from alembic import op

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "services",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.UniqueConstraint("project_id", "url", name="uq_services_project_url"),
        sa.UniqueConstraint("project_id", "id", name="uq_services_project_id"),
    )
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("service_id", sa.Integer()),
        sa.Column("title", sa.String(120), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="todo"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["project_id", "service_id"], ["services.project_id", "services.id"],
            name="fk_tasks_service_project",
        ),
        sa.CheckConstraint("status IN ('todo', 'in_progress', 'done')", name="ck_tasks_status"),
        sa.CheckConstraint("length(btrim(title)) > 0", name="ck_tasks_title"),
    )
    op.create_index("ix_tasks_project_id", "tasks", ["project_id"])


def downgrade():
    op.drop_table("tasks")
    op.drop_table("services")
