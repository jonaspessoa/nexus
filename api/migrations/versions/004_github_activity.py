"""Keep the last successful GitHub activity snapshot."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "github_activity",
        sa.Column("repository", sa.Text(), primary_key=True),
        sa.Column("items", JSONB(), nullable=False),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade():
    op.drop_table("github_activity")
