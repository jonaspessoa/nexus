"""Keep the pull request URL with the task."""

import sqlalchemy as sa
from alembic import op

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("tasks", sa.Column("pull_request_url", sa.String(255)))


def downgrade():
    op.drop_column("tasks", "pull_request_url")
