from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20260615_0002"
down_revision: str | None = "20260614_0001"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("ingredients") as batch_op:
        batch_op.add_column(
            sa.Column(
                "package_size_grams",
                sa.Float(),
                nullable=False,
                server_default="100",
            )
        )

        batch_op.add_column(
            sa.Column(
                "package_price_huf",
                sa.Integer(),
                nullable=False,
                server_default="0",
            )
        )

        batch_op.add_column(
            sa.Column(
                "price_store",
                sa.String(length=100),
                nullable=False,
                server_default="MVP demo",
            )
        )

        batch_op.add_column(
            sa.Column(
                "price_source",
                sa.String(length=255),
                nullable=False,
                server_default="Kézi mintaadat",
            )
        )

        batch_op.add_column(
            sa.Column(
                "price_checked_at",
                sa.Date(),
                nullable=True,
            )
        )


def downgrade() -> None:
    with op.batch_alter_table("ingredients") as batch_op:
        batch_op.drop_column("price_checked_at")
        batch_op.drop_column("price_source")
        batch_op.drop_column("price_store")
        batch_op.drop_column("package_price_huf")
        batch_op.drop_column("package_size_grams")