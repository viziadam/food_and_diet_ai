import { useState } from 'react'

import { PlannerForm } from './features/planner/components/PlannerForm'
import { PlanView } from './features/planner/components/PlanView'
import { useGeneratePlan } from './features/planner/hooks'
import type { MealPlanRequest } from './features/planner/types'

function App() {
  const [resultAnchor, setResultAnchor] = useState<HTMLDivElement | null>(null)
  const generatePlan = useGeneratePlan()

  const handleSubmit = async (request: MealPlanRequest) => {
    await generatePlan.mutateAsync(request)
    window.setTimeout(() => resultAnchor?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 50)
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#top" aria-label="ÉtrendTerv kezdőlap">
          <span className="brand-mark">ET</span>
          <span>
            <strong>ÉtrendTerv</strong>
            <small>Magyar alapanyagokra tervezve</small>
          </span>
        </a>
        <a className="topbar-link" href="#planner">Új terv</a>
      </header>

      <main id="top">
        <section className="hero section-frame">
          <div className="hero-copy">
            <p className="eyebrow">Tudatos étkezés, valós keretek között</p>
            <h1>Az étrended igazodjon hozzád, ne fordítva.</h1>
            <p className="hero-lead">
              Állíts össze egy személyre szabott napi tervet magyar alapanyagokból,
              szezonális választásokkal, becsült költséggel és használható bevásárlólistával.
            </p>
            <div className="hero-points" aria-label="Fő előnyök">
              <span>Célhoz igazított adagok</span>
              <span>Átlátható költségbecslés</span>
              <span>Mobilon is kényelmes</span>
            </div>
          </div>
          <aside className="hero-panel" aria-label="Minta napi összesítés">
            <span className="hero-panel-label">Minta napi terv</span>
            <strong>1 846 kcal</strong>
            <div className="macro-row"><span>Fehérje</span><b>112 g</b></div>
            <div className="macro-row"><span>Becsült költség</span><b>4 380 Ft</b></div>
            <div className="macro-row"><span>Szezonális arány</span><b>74%</b></div>
          </aside>
        </section>

        <section className="trust-strip" aria-label="A tervező működése">
          <div><b>1.</b><span>Add meg a céljaidat</span></div>
          <div><b>2.</b><span>A rendszer ellenőrzött recepteket választ</span></div>
          <div><b>3.</b><span>Megkapod az étrendet és a listát</span></div>
        </section>

        <section id="planner" className="planner-section section-frame">
          <div className="section-heading">
            <p className="eyebrow">Első napi terved</p>
            <h2>Mondd el, mire van szükséged</h2>
            <p>A számítások személyenkénti célértékkel, a költségek a teljes háztartásra készülnek.</p>
          </div>
          <PlannerForm onSubmit={handleSubmit} isLoading={generatePlan.isPending} />
          {generatePlan.isError && (
            <div className="error-banner" role="alert">
              {generatePlan.error instanceof Error
                ? generatePlan.error.message
                : 'Nem sikerült létrehozni a tervet.'}
            </div>
          )}
        </section>

        <div ref={setResultAnchor}>
          {generatePlan.data && <PlanView plan={generatePlan.data} />}
        </div>
      </main>

      <footer className="footer section-frame">
        <strong>ÉtrendTerv MVP</strong>
        <p>A megjelenített árak és tápértékek becslések. Nem minősül egészségügyi tanácsadásnak.</p>
      </footer>
    </div>
  )
}

export default App
