import type {
  DerivedPlanSelection,
  DerivedShoppingListItem,
  MealPlanResponse,
  MealSelectionMap,
  PlanSummary,
  PlannedIngredient,
  PlannedMeal,
} from './types'

interface AggregatedIngredient {
  template: PlannedIngredient
  requiredQuantity: number
  seasonal: boolean
}

const sum = (values: number[]) => values.reduce((total, value) => total + value, 0)

export function getDefaultSelections(plan: MealPlanResponse): MealSelectionMap {
  return Object.fromEntries(
    plan.meal_options.map((group) => [group.meal_type, group.recommended_recipe_id]),
  ) as MealSelectionMap
}

export function derivePlanSelection(
  plan: MealPlanResponse,
  selections: MealSelectionMap,
  ownedIngredientIds: ReadonlySet<number>,
): DerivedPlanSelection {
  const selectedMeals = plan.meal_options.map((group) => {
    const selectedId = selections[group.meal_type] ?? group.recommended_recipe_id
    return (
      group.options.find((meal) => meal.recipe_id === selectedId) ??
      group.options.find((meal) => meal.recipe_id === group.recommended_recipe_id) ??
      group.options[0]
    )
  }).filter((meal): meal is PlannedMeal => Boolean(meal))

  const aggregated = new Map<number, AggregatedIngredient>()
  selectedMeals.forEach((meal) => {
    meal.ingredients.forEach((ingredient) => {
      const existing = aggregated.get(ingredient.ingredient_id)
      if (existing) {
        existing.requiredQuantity += ingredient.quantity_grams
        existing.seasonal = existing.seasonal && ingredient.seasonal
      } else {
        aggregated.set(ingredient.ingredient_id, {
          template: ingredient,
          requiredQuantity: ingredient.quantity_grams,
          seasonal: ingredient.seasonal,
        })
      }
    })
  })

  const shoppingList: DerivedShoppingListItem[] = Array.from(aggregated.values())
    .map(({ template, requiredQuantity, seasonal }) => {
      const packageSize = Math.max(template.package_size_grams, 1)
      const packagePrice = Math.max(template.package_price_huf, 0)
      const packages = Math.ceil(requiredQuantity / packageSize)
      const purchaseQuantity = packages * packageSize
      return {
        ingredient_id: template.ingredient_id,
        name: template.name,
        required_quantity_grams: Math.round(requiredQuantity * 10) / 10,
        package_size_grams: packageSize,
        package_price_huf: packagePrice,
        packages_to_buy: packages,
        purchase_quantity_grams: purchaseQuantity,
        proportional_cost_huf: Math.round(
          (requiredQuantity / packageSize) * packagePrice,
        ),
        purchase_cost_huf: packages * packagePrice,
        leftover_after_plan_grams:
          Math.round((purchaseQuantity - requiredQuantity) * 10) / 10,
        price_store: template.price_store,
        price_source: template.price_source,
        price_checked_at: template.price_checked_at,
        seasonal,
        is_owned: ownedIngredientIds.has(template.ingredient_id),
      }
    })
    .sort((left, right) => left.name.localeCompare(right.name, 'hu'))

  const proportionalTotal = sum(shoppingList.map((item) => item.proportional_cost_huf))
  const fullPurchaseTotal = sum(shoppingList.map((item) => item.purchase_cost_huf))
  const shoppingTotal = sum(
    shoppingList.filter((item) => !item.is_owned).map((item) => item.purchase_cost_huf),
  )
  const seasonalQuantity = sum(
    shoppingList
      .filter((item) => item.seasonal)
      .map((item) => item.required_quantity_grams),
  )
  const totalQuantity = sum(shoppingList.map((item) => item.required_quantity_grams))

  const summary: PlanSummary = {
    ...plan.summary,
    calories_per_person: Math.round(
      sum(selectedMeals.map((meal) => meal.nutrition_per_person.calories_kcal)),
    ),
    proportional_total_cost_huf: proportionalTotal,
    full_purchase_total_cost_huf: fullPurchaseTotal,
    shopping_total_cost_huf: shoppingTotal,
    estimated_total_cost_huf: proportionalTotal,
    budget_difference_huf: plan.summary.budget_huf - shoppingTotal,
    protein_per_person_g:
      Math.round(sum(selectedMeals.map((meal) => meal.nutrition_per_person.protein_g)) * 10) / 10,
    carbs_per_person_g:
      Math.round(sum(selectedMeals.map((meal) => meal.nutrition_per_person.carbs_g)) * 10) / 10,
    fat_per_person_g:
      Math.round(sum(selectedMeals.map((meal) => meal.nutrition_per_person.fat_g)) * 10) / 10,
    seasonal_ingredient_ratio:
      totalQuantity > 0 ? Math.round((seasonalQuantity / totalQuantity) * 100) / 100 : 0,
  }

  return { selectedMeals, shoppingList, summary }
}
