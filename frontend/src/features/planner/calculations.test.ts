import { describe, expect, it } from 'vitest'

import { derivePlanSelection, getDefaultSelections } from './calculations'
import type { MealPlanResponse, PlannedMeal } from './types'

const meal = (recipeId: number, cost: number): PlannedMeal => ({
  recipe_id: recipeId,
  name: `Recept ${recipeId}`,
  description: 'Teszt recept',
  meal_type: 'breakfast',
  cuisine: 'hungarian',
  servings: 1,
  prep_minutes: 5,
  cook_minutes: 5,
  nutrition_per_person: {
    calories_kcal: 400 + recipeId,
    protein_g: 20,
    carbs_g: 30,
    fat_g: 10,
  },
  estimated_cost_huf: cost,
  purchase_cost_huf: 500,
  seasonal_ratio: 1,
  ingredients: [
    {
      ingredient_id: recipeId,
      name: `Alapanyag ${recipeId}`,
      quantity_grams: 100,
      display_quantity: '100 g',
      estimated_cost_huf: cost,
      package_size_grams: 500,
      package_price_huf: 500,
      price_store: 'MVP demo',
      price_source: 'Teszt',
      price_checked_at: null,
      seasonal: true,
    },
  ],
  instructions: ['Készítsd el.'],
})

const plan: MealPlanResponse = {
  id: 'test-plan',
  summary: {
    people_count: 1,
    calories_per_person: 401,
    calorie_target_per_person: 1800,
    proportional_total_cost_huf: 100,
    full_purchase_total_cost_huf: 500,
    shopping_total_cost_huf: 500,
    estimated_total_cost_huf: 100,
    budget_huf: 2000,
    budget_difference_huf: 1500,
    protein_per_person_g: 20,
    carbs_per_person_g: 30,
    fat_per_person_g: 10,
    seasonal_ingredient_ratio: 1,
  },
  meals: [meal(1, 100)],
  meal_options: [
    {
      meal_type: 'breakfast',
      recommended_recipe_id: 1,
      options: [meal(1, 100), meal(2, 150)],
    },
  ],
  shopping_list: [],
  notices: [],
}

describe('meal plan calculations', () => {
  it('uses the recommended recipe as the default selection', () => {
    expect(getDefaultSelections(plan)).toEqual({ breakfast: 1 })
  })

  it('recalculates shopping cost after selecting another recipe', () => {
    const result = derivePlanSelection(plan, { breakfast: 2 }, new Set())
    expect(result.selectedMeals[0]?.recipe_id).toBe(2)
    expect(result.summary.shopping_total_cost_huf).toBe(500)
  })

  it('excludes ingredients marked as already available at home', () => {
    const result = derivePlanSelection(plan, { breakfast: 1 }, new Set([1]))
    expect(result.shoppingList[0]?.is_owned).toBe(true)
    expect(result.summary.shopping_total_cost_huf).toBe(0)
  })
})
