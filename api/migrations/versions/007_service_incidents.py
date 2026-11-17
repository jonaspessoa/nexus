"""Track a single open incident per monitored service."""

import sqlalchemy as sa
from alembic import op

revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "service_incidents",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column(
            "service_id", sa.Integer(), sa.ForeignKey("services.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True)),
    )
    op.create_index(
        "uq_service_incidents_open",
        "service_incidents",
        ["service_id"],
        unique=True,
        postgresql_where=sa.text("resolved_at IS NULL"),
    )


def downgrade():
    op.drop_table("service_incidents")
