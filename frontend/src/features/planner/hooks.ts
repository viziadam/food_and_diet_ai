import { useMutation } from '@tanstack/react-query'

import { generateMealPlan } from './api'

export function useGeneratePlan() {
  return useMutation({ mutationFn: generateMealPlan })
}
