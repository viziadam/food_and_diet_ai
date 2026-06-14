import { useState } from 'react'

import type { MealPlanResponse, MealType, PlannedMeal } from '../types'

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

function MealCard({ meal }: { meal: PlannedMeal }) {
  const [expanded, setExpanded] = useState(false)
  const totalMinutes = meal.prep_minutes + meal.cook_minutes

  return (
    <article className="meal-card">
      <div className="meal-card-header">
        <div>
          <span className="meal-type">{mealLabels[meal.meal_type]}</span>
          <h3>{meal.name}</h3>
          <p>{meal.description}</p>
        </div>
        <span className="cuisine-badge">{cuisineLabels[meal.cuisine] ?? meal.cuisine}</span>
      </div>

      <div className="meal-metrics">
        <div><span>Adag</span><strong>{meal.servings} fő</strong></div>
        <div><span>Energia / fő</span><strong>{meal.nutrition_per_person.calories_kcal} kcal</strong></div>
        <div><span>Idő</span><strong>{totalMinutes} perc</strong></div>
        <div><span>Becsült ár</span><strong>{meal.estimated_cost_huf.toLocaleString('hu-HU')} Ft</strong></div>
      </div>

      <button className="text-button" type="button" onClick={() => setExpanded((value) => !value)}>
        {expanded ? 'Részletek bezárása' : 'Hozzávalók és elkészítés'}
      </button>

      {expanded && (
        <div className="meal-details">
          <div>
            <h4>Hozzávalók</h4>
            <ul className="ingredient-list">
              {meal.ingredients.map((ingredient) => (
                <li key={ingredient.name}>
                  <span>{ingredient.name}{ingredient.seasonal ? <small>Szezonális</small> : null}</span>
                  <b>{ingredient.quantity_grams.toLocaleString('hu-HU')} g</b>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h4>Elkészítés</h4>
            <ol className="instruction-list">
              {meal.instructions.map((instruction) => <li key={instruction}>{instruction}</li>)}
            </ol>
          </div>
        </div>
      )}
    </article>
  )
}

export function PlanView({ plan }: PlanViewProps) {
  const seasonalPercent = Math.round(plan.summary.seasonal_ingredient_ratio * 100)
  const budgetClass = plan.summary.budget_difference_huf >= 0 ? 'positive' : 'negative'

  return (
    <section className="results-section section-frame" aria-live="polite">
      <div className="section-heading result-heading">
        <div>
          <p className="eyebrow">Elkészült a napi terved</p>
          <h2>Kiegyensúlyozott terv, átlátható számokkal</h2>
        </div>
        <span className="plan-id">Terv: {plan.id.slice(0, 8)}</span>
      </div>

      <div className="summary-grid">
        <div className="summary-card featured">
          <span>Napi energia / fő</span>
          <strong>{plan.summary.calories_per_person.toLocaleString('hu-HU')} kcal</strong>
          <small>Cél: {plan.summary.calorie_target_per_person.toLocaleString('hu-HU')} kcal</small>
        </div>
        <div className="summary-card">
          <span>Becsült napi költség</span>
          <strong>{plan.summary.estimated_total_cost_huf.toLocaleString('hu-HU')} Ft</strong>
          <small className={budgetClass}>
            {plan.summary.budget_difference_huf >= 0
              ? `${plan.summary.budget_difference_huf.toLocaleString('hu-HU')} Ft marad a keretből`
              : `${Math.abs(plan.summary.budget_difference_huf).toLocaleString('hu-HU')} Ft-tal keret felett`}
          </small>
        </div>
        <div className="summary-card">
          <span>Fehérje / fő</span>
          <strong>{plan.summary.protein_per_person_g} g</strong>
          <small>Szénhidrát: {plan.summary.carbs_per_person_g} g</small>
        </div>
        <div className="summary-card">
          <span>Szezonális alapanyag</span>
          <strong>{seasonalPercent}%</strong>
          <small>A teljes felhasznált mennyiségből</small>
        </div>
      </div>

      <div className="result-layout">
        <div className="meal-list">
          {plan.meals.map((meal) => <MealCard meal={meal} key={`${meal.meal_type}-${meal.recipe_id}`} />)}
        </div>

        <aside className="shopping-card">
          <div className="shopping-header">
            <div>
              <span className="meal-type">Összesítve</span>
              <h3>Bevásárlólista</h3>
            </div>
            <strong>{plan.shopping_list.length} tétel</strong>
          </div>
          <ul className="shopping-list">
            {plan.shopping_list.map((item) => (
              <li key={item.name}>
                <div>
                  <strong>{item.name}</strong>
                  <span>{item.quantity_grams.toLocaleString('hu-HU')} g</span>
                </div>
                <b>{item.estimated_cost_huf.toLocaleString('hu-HU')} Ft</b>
              </li>
            ))}
          </ul>
          <div className="shopping-total">
            <span>Becsült összesen</span>
            <strong>{plan.summary.estimated_total_cost_huf.toLocaleString('hu-HU')} Ft</strong>
          </div>
        </aside>
      </div>

      <div className="notice-box">
        {plan.notices.map((notice) => <p key={notice}>{notice}</p>)}
      </div>
    </section>
  )
}
