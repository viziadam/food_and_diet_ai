export type Goal = 'weight_loss' | 'conscious' | 'high_protein'
export type MealType = 'breakfast' | 'lunch' | 'dinner' | 'snack'
export type Cuisine = 'hungarian' | 'italian' | 'mediterranean' | 'mixed'
export type DietaryPreference = 'vegetarian' | 'lactose_free' | 'gluten_free'

export interface MealPlanRequest {
  people_count: number
  calorie_target_per_person: number
  daily_budget_huf: number
  goal: Goal
  meal_types: MealType[]
  preferred_cuisines: Cuisine[]
  dietary_preferences: DietaryPreference[]
  excluded_ingredients: string[]
  max_total_cooking_minutes_per_meal: number
}

export interface MacroSummary {
  calories_kcal: number
  protein_g: number
  carbs_g: number
  fat_g: number
}

export interface PlannedIngredient {
  name: string
  quantity_grams: number
  display_quantity: string
  estimated_cost_huf: number
  seasonal: boolean
}

export interface PlannedMeal {
  recipe_id: number
  name: string
  description: string
  meal_type: MealType
  cuisine: Cuisine
  servings: number
  prep_minutes: number
  cook_minutes: number
  nutrition_per_person: MacroSummary
  estimated_cost_huf: number
  seasonal_ratio: number
  ingredients: PlannedIngredient[]
  instructions: string[]
}

export interface ShoppingListItem {
  name: string
  quantity_grams: number
  estimated_cost_huf: number
  seasonal: boolean
}

export interface MealPlanResponse {
  id: string
  summary: {
    people_count: number
    calories_per_person: number
    calorie_target_per_person: number
    estimated_total_cost_huf: number
    budget_huf: number
    budget_difference_huf: number
    protein_per_person_g: number
    carbs_per_person_g: number
    fat_per_person_g: number
    seasonal_ingredient_ratio: number
  }
  meals: PlannedMeal[]
  shopping_list: ShoppingListItem[]
  notices: string[]
}
