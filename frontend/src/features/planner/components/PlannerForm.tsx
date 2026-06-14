import { useMemo, useState, type FormEvent } from 'react'

import type {
  Cuisine,
  DietaryPreference,
  Goal,
  MealPlanRequest,
  MealType,
} from '../types'

interface PlannerFormProps {
  onSubmit: (request: MealPlanRequest) => Promise<void>
  isLoading: boolean
}

const goalOptions: Array<{ value: Goal; title: string; description: string }> = [
  { value: 'weight_loss', title: 'Fogyást támogató', description: 'Mérsékelt adagok, könnyebb receptek' },
  { value: 'conscious', title: 'Tudatos étkezés', description: 'Kiegyensúlyozott, változatos napi terv' },
  { value: 'high_protein', title: 'Magasabb fehérje', description: 'Fehérjedúsabb receptválasztás' },
]

const cuisineOptions: Array<{ value: Cuisine; label: string }> = [
  { value: 'mixed', label: 'Vegyes' },
  { value: 'hungarian', label: 'Magyaros' },
  { value: 'italian', label: 'Olasz' },
  { value: 'mediterranean', label: 'Mediterrán' },
]

const mealOptions: Array<{ value: MealType; label: string }> = [
  { value: 'breakfast', label: 'Reggeli' },
  { value: 'lunch', label: 'Ebéd' },
  { value: 'dinner', label: 'Vacsora' },
]

const dietaryOptions: Array<{ value: DietaryPreference; label: string }> = [
  { value: 'vegetarian', label: 'Vegetáriánus' },
  { value: 'gluten_free', label: 'Gluténmentes' },
  { value: 'lactose_free', label: 'Laktózmentes' },
]

const initialState: MealPlanRequest = {
  people_count: 1,
  calorie_target_per_person: 1900,
  daily_budget_huf: 5000,
  goal: 'conscious',
  meal_types: ['breakfast', 'lunch', 'dinner'],
  preferred_cuisines: ['mixed'],
  dietary_preferences: [],
  excluded_ingredients: [],
  max_total_cooking_minutes_per_meal: 60,
}

export function PlannerForm({ onSubmit, isLoading }: PlannerFormProps) {
  const [form, setForm] = useState(initialState)
  const [excludedText, setExcludedText] = useState('')
  const estimatedMeals = form.meal_types.length
  const perPersonBudget = useMemo(
    () => Math.round(form.daily_budget_huf / form.people_count),
    [form.daily_budget_huf, form.people_count],
  )

  const toggleValue = <T extends string>(items: T[], value: T): T[] =>
    items.includes(value) ? items.filter((item) => item !== value) : [...items, value]

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const exclusions = excludedText
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean)
    void onSubmit({ ...form, excluded_ingredients: exclusions })
  }

  return (
    <form className="planner-form" onSubmit={handleSubmit}>
      <fieldset className="form-card form-card-wide">
        <legend>1. Mi a fő célod?</legend>
        <div className="choice-grid choice-grid-goals">
          {goalOptions.map((option) => (
            <label className={`choice-card ${form.goal === option.value ? 'selected' : ''}`} key={option.value}>
              <input
                type="radio"
                name="goal"
                value={option.value}
                checked={form.goal === option.value}
                onChange={() => setForm((current) => ({ ...current, goal: option.value }))}
              />
              <strong>{option.title}</strong>
              <span>{option.description}</span>
            </label>
          ))}
        </div>
      </fieldset>

      <fieldset className="form-card">
        <legend>2. Alapbeállítások</legend>
        <div className="field-grid">
          <label className="field">
            <span>Hány főre?</span>
            <input
              type="number"
              min={1}
              max={10}
              value={form.people_count}
              onChange={(event) => setForm((current) => ({ ...current, people_count: Number(event.target.value) }))}
            />
          </label>
          <label className="field">
            <span>Napi kalóriacél / fő</span>
            <input
              type="number"
              min={1000}
              max={5000}
              step={50}
              value={form.calorie_target_per_person}
              onChange={(event) => setForm((current) => ({ ...current, calorie_target_per_person: Number(event.target.value) }))}
            />
          </label>
          <label className="field">
            <span>Napi keret összesen</span>
            <div className="input-suffix">
              <input
                type="number"
                min={1000}
                max={100000}
                step={250}
                value={form.daily_budget_huf}
                onChange={(event) => setForm((current) => ({ ...current, daily_budget_huf: Number(event.target.value) }))}
              />
              <span>Ft</span>
            </div>
            <small>Körülbelül {perPersonBudget.toLocaleString('hu-HU')} Ft / fő</small>
          </label>
          <label className="field">
            <span>Maximum idő étkezésenként</span>
            <div className="input-suffix">
              <input
                type="number"
                min={5}
                max={240}
                step={5}
                value={form.max_total_cooking_minutes_per_meal}
                onChange={(event) => setForm((current) => ({ ...current, max_total_cooking_minutes_per_meal: Number(event.target.value) }))}
              />
              <span>perc</span>
            </div>
          </label>
        </div>
      </fieldset>

      <fieldset className="form-card">
        <legend>3. Étkezések és ízlés</legend>
        <span className="field-label">Tervezett étkezések</span>
        <div className="chip-group">
          {mealOptions.map((option) => (
            <label className={`chip ${form.meal_types.includes(option.value) ? 'selected' : ''}`} key={option.value}>
              <input
                type="checkbox"
                checked={form.meal_types.includes(option.value)}
                onChange={() => setForm((current) => ({ ...current, meal_types: toggleValue(current.meal_types, option.value) }))}
              />
              {option.label}
            </label>
          ))}
        </div>

        <span className="field-label spaced">Konyhatípus</span>
        <div className="chip-group">
          {cuisineOptions.map((option) => (
            <label className={`chip ${form.preferred_cuisines.includes(option.value) ? 'selected' : ''}`} key={option.value}>
              <input
                type="checkbox"
                checked={form.preferred_cuisines.includes(option.value)}
                onChange={() => {
                  if (option.value === 'mixed') {
                    setForm((current) => ({ ...current, preferred_cuisines: ['mixed'] }))
                    return
                  }
                  setForm((current) => {
                    const withoutMixed = current.preferred_cuisines.filter((item) => item !== 'mixed')
                    const next = toggleValue(withoutMixed, option.value)
                    return { ...current, preferred_cuisines: next.length ? next : ['mixed'] }
                  })
                }}
              />
              {option.label}
            </label>
          ))}
        </div>
      </fieldset>

      <fieldset className="form-card">
        <legend>4. Korlátozások</legend>
        <span className="field-label">Étrendi beállítások</span>
        <div className="chip-group">
          {dietaryOptions.map((option) => (
            <label className={`chip ${form.dietary_preferences.includes(option.value) ? 'selected' : ''}`} key={option.value}>
              <input
                type="checkbox"
                checked={form.dietary_preferences.includes(option.value)}
                onChange={() => setForm((current) => ({ ...current, dietary_preferences: toggleValue(current.dietary_preferences, option.value) }))}
              />
              {option.label}
            </label>
          ))}
        </div>
        <label className="field spaced">
          <span>Nem kedvelt vagy kizárt alapanyagok</span>
          <input
            type="text"
            placeholder="például: gomba, máj, cukkini"
            value={excludedText}
            onChange={(event) => setExcludedText(event.target.value)}
          />
          <small>Az alapanyagokat vesszővel válaszd el.</small>
        </label>
      </fieldset>

      <div className="form-submit-panel">
        <div>
          <strong>{estimatedMeals} étkezés, {form.people_count} főre</strong>
          <span>A rendszer ellenőrzött receptekből számol.</span>
        </div>
        <button className="primary-button" type="submit" disabled={isLoading || !form.meal_types.length}>
          {isLoading ? 'Terv készítése...' : 'Napi étrend létrehozása'}
        </button>
      </div>
    </form>
  )
}
