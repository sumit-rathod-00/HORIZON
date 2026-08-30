"""extend vulnerabilities with scan correlation

Revision ID: fab5f84b5376
Revises: 8f2c1a4d6b90
Create Date: 2026-08-30 14:35:37.378644

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fab5f84b5376'
down_revision: Union[str, Sequence[str], None] = '8f2c1a4d6b90'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("vulnerabilities", sa.Column("scan_id", sa.UUID(), nullable=True))
    op.add_column("vulnerabilities", sa.Column("port", sa.Integer(), nullable=True))
    op.add_column("vulnerabilities", sa.Column("protocol", sa.String(length=20), nullable=True))
    op.add_column("vulnerabilities", sa.Column("service", sa.String(length=100), nullable=True))
    op.add_column("vulnerabilities", sa.Column("evidence", sa.Text(), nullable=True))
    op.add_column("vulnerabilities", sa.Column("remediation", sa.Text(), nullable=True))
    op.add_column("vulnerabilities", sa.Column("risk_score", sa.Float(), nullable=True))
    op.add_column("vulnerabilities", sa.Column("risk_factors", sa.Text(), nullable=True))
    op.add_column("vulnerabilities", sa.Column("detection_source", sa.String(length=50), nullable=True))

    op.create_foreign_key(
        "fk_vulnerabilities_scan_id_scans",
        "vulnerabilities",
        "scans",
        ["scan_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_vulnerabilities_scan_id",
        "vulnerabilities",
        ["scan_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_vulnerabilities_scan_id", table_name="vulnerabilities")
    op.drop_constraint("fk_vulnerabilities_scan_id_scans", "vulnerabilities", type_="foreignkey")
    op.drop_column("vulnerabilities", "detection_source")
    op.drop_column("vulnerabilities", "risk_factors")
    op.drop_column("vulnerabilities", "risk_score")
    op.drop_column("vulnerabilities", "remediation")
    op.drop_column("vulnerabilities", "evidence")
    op.drop_column("vulnerabilities", "service")
    op.drop_column("vulnerabilities", "protocol")
    op.drop_column("vulnerabilities", "port")
    op.drop_column("vulnerabilities", "scan_id")
