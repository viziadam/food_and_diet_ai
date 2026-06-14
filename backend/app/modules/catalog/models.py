from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import JSON, Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    category: Mapped[str] = mapped_column(String(60))

    kcal_per_100g: Mapped[float] = mapped_column(Float)
    protein_per_100g: Mapped[float] = mapped_column(Float)
    carbs_per_100g: Mapped[float] = mapped_column(Float)
    fat_per_100g: Mapped[float] = mapped_column(Float)

    price_per_100g_huf: Mapped[float] = mapped_column(Float)
    package_size_grams: Mapped[float] = mapped_column(Float, default=100.0)
    package_price_huf: Mapped[int] = mapped_column(Integer, default=0)
    price_store: Mapped[str] = mapped_column(String(100), default="MVP demo")
    price_source: Mapped[str] = mapped_column(String(255), default="Kézi mintaadat")
    price_checked_at: Mapped[date | None] = mapped_column(Date, nullable=True)

    seasonal_months: Mapped[list[int]] = mapped_column(JSON, default=list)
    allergens: Mapped[list[str]] = mapped_column(JSON, default=list)

    recipe_links: Mapped[list[RecipeIngredient]] = relationship(back_populates="ingredient")


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text)
    meal_type: Mapped[str] = mapped_column(String(30), index=True)
    cuisine: Mapped[str] = mapped_column(String(40), index=True)
    default_servings: Mapped[int] = mapped_column(Integer, default=2)
    prep_minutes: Mapped[int] = mapped_column(Integer)
    cook_minutes: Mapped[int] = mapped_column(Integer)
    instructions: Mapped[list[str]] = mapped_column(JSON, default=list)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    ingredients: Mapped[list[RecipeIngredient]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"))
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"))
    quantity_grams: Mapped[float] = mapped_column(Float)
    display_quantity: Mapped[str] = mapped_column(String(80))

    recipe: Mapped[Recipe] = relationship(back_populates="ingredients")
    ingredient: Mapped[Ingredient] = relationship(
        back_populates="recipe_links", lazy="joined"
    )


class MealPlanRecord(Base):
    __tablename__ = "meal_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    request_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON)
    result_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
