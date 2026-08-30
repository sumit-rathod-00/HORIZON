"""add persistent scan results

Revision ID: 8f2c1a4d6b90
Revises: 6869f479daa9
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8f2c1a4d6b90"
down_revision: Union[str, Sequence[str], None] = "6869f479daa9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("scans", sa.Column("raw_output", sa.Text(), nullable=True))
    op.create_table(
        "scan_results",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("scan_id", sa.UUID(), nullable=False),
        sa.Column("asset_id", sa.UUID(), nullable=False),
        sa.Column("port", sa.Integer(), nullable=False),
        sa.Column("protocol", sa.String(length=20), nullable=False),
        sa.Column("state", sa.String(length=30), nullable=False),
        sa.Column("service", sa.String(length=100), nullable=True),
        sa.Column("product", sa.String(length=200), nullable=True),
        sa.Column("version", sa.String(length=200), nullable=True),
        sa.Column("hostname", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["scan_id"], ["scans.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_scan_results_scan_id", "scan_results", ["scan_id"], unique=False)
    op.create_index("ix_scan_results_asset_id", "scan_results", ["asset_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_scan_results_asset_id", table_name="scan_results")
    op.drop_index("ix_scan_results_scan_id", table_name="scan_results")
    op.drop_table("scan_results")
    op.drop_column("scans", "raw_output")
