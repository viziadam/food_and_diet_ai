import { useMemo, useState } from 'react'

import { derivePlanSelection, getDefaultSelections } from '../calculations'
import type {
  DerivedShoppingListItem,
  MealPlanResponse,
  MealType,
  PlannedMeal,
  PlanSummary,
} from '../types'

interface PlanViewProps {
  plan: MealPlanResponse
}

const mealLabels: Record<MealType, string> = {
  breakfast: 'Reggeli',
  lunch: 'Ebéd',
  dinner: 'Vacsora',
  snack: 'Kisétkezés',
}

const cuisineLabels: Record<string, string> = {
  hungarian: 'Magyaros',
  italian: 'Olasz',
  mediterranean: 'Mediterrán',
  mixed: 'Vegyes',
}

const currency = (value: number) => `${value.toLocaleString('hu-HU')} Ft`

function SummaryCards({ summary }: { summary: PlanSummary }) {
  const budgetClass = summary.budget_difference_huf >= 0 ? 'positive' : 'negative'
  return (
    <div className="cost-summary-grid">
      <div className="summary-card featured">
        <span>Napi energia / fő</span>
        <strong>{summary.calories_per_person.toLocaleString('hu-HU')} kcal</strong>
        <small>Cél: {summary.calorie_target_per_person.toLocaleString('hu-HU')} kcal</small>
      </div>
      <div className="summary-card">
        <span>Felhasznált mennyiség értéke</span>
        <strong>{currency(summary.proportional_total_cost_huf)}</strong>
        <small>Csak a receptekhez felhasznált rész</small>
      </div>
      <div className="summary-card">
        <span>Teljes csomagok ára</span>
        <strong>{currency(summary.full_purchase_total_cost_huf)}</strong>
        <small>Ha semmi nincs otthon</small>
      </div>
      <div className="summary-card">
        <span>Tényleges bevásárlás</span>
        <strong>{currency(summary.shopping_total_cost_huf)}</strong>
        <small className={budgetClass}>
          {summary.budget_difference_huf >= 0
            ? `${currency(summary.budget_difference_huf)} marad a keretből`
            : `${currency(Math.abs(summary.budget_difference_huf))} keret felett`}
        </small>
      </div>
    </div>
  )
}

function MealOptionCard({
  meal,
  selected,
  recommended,
  onSelect,
}: {
  meal: PlannedMeal
  selected: boolean
  recommended: boolean
  onSelect: () => void
}) {
  const [expanded, setExpanded] = useState(false)
  const totalMinutes = meal.prep_minutes + meal.cook_minutes

  return (
    <article className={`meal-option-card ${selected ? 'selected' : ''}`}>
      <div className="option-topline">
        <span className="cuisine-badge">{cuisineLabels[meal.cuisine] ?? meal.cuisine}</span>
        {recommended && <span className="recommended-badge">Ajánlott</span>}
      </div>
      <h4>{meal.name}</h4>
      <p>{meal.description}</p>
      <div className="meal-metrics">
        <div><span>Energia / fő</span><strong>{meal.nutrition_per_person.calories_kcal} kcal</strong></div>
        <div><span>Idő</span><strong>{totalMinutes} perc</strong></div>
        <div><span>Arányos ár</span><strong>{currency(meal.estimated_cost_huf)}</strong></div>
        <div><span>Csomagár</span><strong>{currency(meal.purchase_cost_huf)}</strong></div>
      </div>
      <button
        className={`option-select-button ${selected ? 'selected' : ''}`}
        type="button"
        onClick={onSelect}
        aria-pressed={selected}
      >
        {selected ? 'Kiválasztva' : 'Ezt választom'}
      </button>
      <button className="text-button option-details-button" type="button" onClick={() => setExpanded((value) => !value)}>
        {expanded ? 'Részletek bezárása' : 'Hozzávalók és elkészítés'}
      </button>
      {expanded && (
        <div className="meal-details compact-details">
          <div>
            <h5>Hozzávalók</h5>
            <ul className="ingredient-list">
              {meal.ingredients.map((ingredient) => (
                <li key={ingredient.ingredient_id}>
                  <span>{ingredient.name}{ingredient.seasonal ? <small>Szezonális</small> : null}</span>
                  <b>{ingredient.quantity_grams.toLocaleString('hu-HU')} g</b>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h5>Elkészítés</h5>
            <ol className="instruction-list">
              {meal.instructions.map((instruction) => <li key={instruction}>{instruction}</li>)}
            </ol>
          </div>
        </div>
      )}
    </article>
  )
}

function ShoppingList({
  items,
  summary,
  onToggleOwned,
}: {
  items: DerivedShoppingListItem[]
  summary: PlanSummary
  onToggleOwned: (ingredientId: number) => void
}) {
  return (
    <section className="shopping-workspace">
      <div className="shopping-workspace-header">
        <div>
          <p className="eyebrow">Interaktív lista</p>
          <h3>Bevásárlólista</h3>
          <p>Jelöld be, ami már otthon van. Ezek a tételek nem számítanak bele a tényleges bevásárlásba.</p>
        </div>
        <strong>{currency(summary.shopping_total_cost_huf)}</strong>
      </div>
      <div className="shopping-table">
        {items.map((item) => (
          <label className={`shopping-row ${item.is_owned ? 'owned' : ''}`} key={item.ingredient_id}>
            <input
              type="checkbox"
              checked={item.is_owned}
              onChange={() => onToggleOwned(item.ingredient_id)}
            />
            <span className="shopping-checkmark" aria-hidden="true" />
            <span className="shopping-main">
              <strong>{item.name}</strong>
              <small>
                Kell: {item.required_quantity_grams.toLocaleString('hu-HU')} g · {item.packages_to_buy} × {item.package_size_grams.toLocaleString('hu-HU')} g
              </small>
              <small>
                Maradék: {item.leftover_after_plan_grams.toLocaleString('hu-HU')} g · {item.price_store}
              </small>
            </span>
            <span className="shopping-price">
              <b>{item.is_owned ? '0 Ft' : currency(item.purchase_cost_huf)}</b>
              <small>arányos: {currency(item.proportional_cost_huf)}</small>
            </span>
          </label>
        ))}
      </div>
    </section>
  )
}

export function PlanView({ plan }: PlanViewProps) {
  const [selectedRecipeIds, setSelectedRecipeIds] = useState(() => getDefaultSelections(plan))
  const [ownedIngredientIds, setOwnedIngredientIds] = useState<Set<number>>(() => new Set())
  const derived = useMemo(
    () => derivePlanSelection(plan, selectedRecipeIds, ownedIngredientIds),
    [ownedIngredientIds, plan, selectedRecipeIds],
  )

  const selectMeal = (mealType: MealType, recipeId: number) => {
    setSelectedRecipeIds((current) => ({ ...current, [mealType]: recipeId }))
  }

  const toggleOwned = (ingredientId: number) => {
    setOwnedIngredientIds((current) => {
      const next = new Set(current)
      if (next.has(ingredientId)) next.delete(ingredientId)
      else next.add(ingredientId)
      return next
    })
  }

  return (
    <section className="results-section section-frame" aria-live="polite">
      <div className="section-heading result-heading">
        <div>
          <p className="eyebrow">Elkészült a napi terved</p>
          <h2>Válassz három lehetőség közül</h2>
          <p>A tápértékek, a három költségnézet és a bevásárlólista azonnal frissül.</p>
        </div>
        <span className="plan-id">Terv: {plan.id.slice(0, 8)}</span>
      </div>

      <SummaryCards summary={derived.summary} />

      <div className="meal-choice-list">
        {plan.meal_options.map((group) => (
          <section className="meal-choice-group" key={group.meal_type}>
            <div className="meal-choice-heading">
              <span className="meal-type">{mealLabels[group.meal_type]}</span>
              <h3>Válassz egy receptet</h3>
              <p>{group.options.length} megfelelő lehetőség a beállításaid alapján.</p>
            </div>
            <div className="meal-option-grid">
              {group.options.map((meal) => (
                <MealOptionCard
                  key={meal.recipe_id}
                  meal={meal}
                  selected={selectedRecipeIds[group.meal_type] === meal.recipe_id}
                  recommended={group.recommended_recipe_id === meal.recipe_id}
                  onSelect={() => selectMeal(group.meal_type, meal.recipe_id)}
                />
              ))}
            </div>
          </section>
        ))}
      </div>

      <ShoppingList
        items={derived.shoppingList}
        summary={derived.summary}
        onToggleOwned={toggleOwned}
      />

      <div className="notice-box">
        {plan.notices.map((notice) => <p key={notice}>{notice}</p>)}
      </div>
    </section>
  )
}
