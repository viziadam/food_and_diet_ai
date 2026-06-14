// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { PlannerForm } from './PlannerForm'

describe('PlannerForm', () => {
  it('submits the default plan request', async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined)
    render(<PlannerForm onSubmit={onSubmit} isLoading={false} />)

    fireEvent.click(screen.getByRole('button', { name: 'Napi étrend létrehozása' }))

    expect(onSubmit).toHaveBeenCalledOnce()
    expect(onSubmit.mock.calls[0]?.[0]).toMatchObject({
      people_count: 1,
      goal: 'conscious',
      meal_types: ['breakfast', 'lunch', 'dinner'],
    })
  })
})
