import type { MealPlanRequest, MealPlanResponse } from './types'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1'

interface ApiErrorPayload {
  message?: string
  detail?: string | Array<{ msg?: string }>
}

export async function generateMealPlan(request: MealPlanRequest): Promise<MealPlanResponse> {
  const response = await fetch(`${API_URL}/plans/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    const payload = (await response.json().catch(() => ({}))) as ApiErrorPayload
    const validationMessage = Array.isArray(payload.detail)
      ? payload.detail.map((item) => item.msg).filter(Boolean).join(' ')
      : payload.detail
    throw new Error(payload.message ?? validationMessage ?? 'A tervezés nem sikerült.')
  }

  return response.json() as Promise<MealPlanResponse>
}
