"""Store the outcome of each scheduled HTTP check."""

import sqlalchemy as sa
from alembic import op

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "service_checks",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column(
            "service_id", sa.Integer(), sa.ForeignKey("services.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "checked_at", sa.DateTime(timezone=True), server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("outcome", sa.String(16), nullable=False),
        sa.Column("http_status", sa.Integer()),
        sa.Column("latency_ms", sa.Integer()),
        sa.CheckConstraint("outcome IN ('up', 'down', 'blocked')", name="ck_service_checks_outcome"),
        sa.CheckConstraint(
            "http_status IS NULL OR http_status BETWEEN 100 AND 599",
            name="ck_service_checks_http_status",
        ),
        sa.CheckConstraint("latency_ms IS NULL OR latency_ms >= 0", name="ck_service_checks_latency"),
    )
    op.create_index("ix_service_checks_history", "service_checks", ["service_id", "checked_at", "id"])


def downgrade():
    op.drop_table("service_checks")
