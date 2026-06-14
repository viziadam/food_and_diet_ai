"""Initial meal-planning schema.

Revision ID: 20260614_0001
Revises:
Create Date: 2026-06-14
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260614_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ingredients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("category", sa.String(length=60), nullable=False),
        sa.Column("kcal_per_100g", sa.Float(), nullable=False),
        sa.Column("protein_per_100g", sa.Float(), nullable=False),
        sa.Column("carbs_per_100g", sa.Float(), nullable=False),
        sa.Column("fat_per_100g", sa.Float(), nullable=False),
        sa.Column("price_per_100g_huf", sa.Float(), nullable=False),
        sa.Column("seasonal_months", sa.JSON(), nullable=False),
        sa.Column("allergens", sa.JSON(), nullable=False),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_ingredients_slug", "ingredients", ["slug"])
    op.create_table(
        "recipes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("meal_type", sa.String(length=30), nullable=False),
        sa.Column("cuisine", sa.String(length=40), nullable=False),
        sa.Column("default_servings", sa.Integer(), nullable=False),
        sa.Column("prep_minutes", sa.Integer(), nullable=False),
        sa.Column("cook_minutes", sa.Integer(), nullable=False),
        sa.Column("instructions", sa.JSON(), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_recipes_slug", "recipes", ["slug"])
    op.create_index("ix_recipes_meal_type", "recipes", ["meal_type"])
    op.create_index("ix_recipes_cuisine", "recipes", ["cuisine"])
    op.create_table(
        "meal_plans",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("request_snapshot", sa.JSON(), nullable=False),
        sa.Column("result_snapshot", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "recipe_ingredients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("recipe_id", sa.Integer(), sa.ForeignKey("recipes.id", ondelete="CASCADE")),
        sa.Column("ingredient_id", sa.Integer(), sa.ForeignKey("ingredients.id")),
        sa.Column("quantity_grams", sa.Float(), nullable=False),
        sa.Column("display_quantity", sa.String(length=80), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("recipe_ingredients")
    op.drop_table("meal_plans")
    op.drop_index("ix_recipes_cuisine", table_name="recipes")
    op.drop_index("ix_recipes_meal_type", table_name="recipes")
    op.drop_index("ix_recipes_slug", table_name="recipes")
    op.drop_table("recipes")
    op.drop_index("ix_ingredients_slug", table_name="ingredients")
    op.drop_table("ingredients")
