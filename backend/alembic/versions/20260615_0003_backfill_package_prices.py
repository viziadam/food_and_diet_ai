from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260615_0003"
down_revision: str | None = "20260615_0002"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

PACKAGE_DATA: dict[str, tuple[float, int]] = {
    "zabpehely": (500, 210),
    "tej": (1000, 480),
    "gorog-joghurt": (400, 480),
    "alma": (1000, 700),
    "banan": (1000, 850),
    "tojas": (500, 525),
    "paradicsom": (1000, 950),
    "paprika": (1000, 1100),
    "csirkemell": (1000, 2550),
    "rizs": (1000, 650),
    "voroshagyma": (1000, 450),
    "tejfol": (330, 314),
    "teljes-kiorlesu-teszta": (500, 410),
    "passata": (500, 390),
    "olivaolaj": (500, 950),
    "voroslencse": (500, 475),
    "sargarepa": (1000, 450),
    "burgonya": (2500, 1250),
    "cukkini": (1000, 900),
    "kuszkusz": (500, 440),
    "csicseriborso": (400, 288),
    "feta": (200, 360),
    "turo": (250, 275),
    "tortilla": (320, 320),
    "salata": (150, 225),
    "mozzarella": (125, 275),
    "gomba": (500, 600),
}


def upgrade() -> None:
    ingredients = sa.table(
        "ingredients",
        sa.column("slug", sa.String()),
        sa.column("price_per_100g_huf", sa.Float()),
        sa.column("package_size_grams", sa.Float()),
        sa.column("package_price_huf", sa.Integer()),
        sa.column("price_store", sa.String()),
        sa.column("price_source", sa.String()),
    )

    for slug, (package_size, package_price) in PACKAGE_DATA.items():
        op.execute(
            ingredients.update()
            .where(ingredients.c.slug == slug)
            .values(
                package_size_grams=package_size,
                package_price_huf=package_price,
                price_per_100g_huf=round(package_price / package_size * 100, 2),
                price_store="MVP demo",
                price_source="Kézi mintaadat, production előtt frissítendő",
            )
        )


def downgrade() -> None:
    pass
