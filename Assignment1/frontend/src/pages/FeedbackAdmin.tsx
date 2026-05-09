import { useEffect, useState } from "react"
import BackToHome from "../components/BackToHome"

interface FeedbackEntry {
  id: number
  project: string
  comment: string
  rating: number | null
  created_at: string
}

export default function FeedbackAdmin() {
  const [entries, setEntries] = useState<FeedbackEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [project, setProject] = useState("")

  useEffect(() => {
    const url = project
      ? `/api/admin/feedback?project=${encodeURIComponent(project)}`
      : "/api/admin/feedback"
    fetch(url)
      .then((r) => r.json())
      .then((data) => setEntries(data.feedback ?? []))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [project])

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <header className="border-b border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
        <div className="mx-auto flex max-w-4xl items-center gap-4 px-6 py-4">
          <BackToHome />
          <div className="h-5 w-px bg-slate-200 dark:bg-slate-700" />
          <h1 className="text-base font-semibold text-slate-900 dark:text-slate-100">
            Feedback Admin
          </h1>
          <span className="ml-auto rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs font-medium text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300">
            {entries.length} entries
          </span>
        </div>
      </header>

      <main className="mx-auto max-w-4xl px-6 py-8">
        <div className="mb-6">
          <select
            value={project}
            onChange={(e) => {
              setLoading(true)
              setProject(e.target.value)
            }}
            className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 focus:border-indigo-400 focus:outline-none dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300"
          >
            <option value="">All projects</option>
            <option value="chatkit-agent">chatkit-agent</option>
          </select>
        </div>

        {loading ? (
          <p className="text-sm text-slate-400">Loading…</p>
        ) : entries.length === 0 ? (
          <p className="text-sm text-slate-400">No feedback yet.</p>
        ) : (
          <div className="flex flex-col gap-3">
            {entries.map((e) => (
              <div
                key={e.id}
                className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-900"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-full bg-indigo-50 px-2 py-0.5 text-xs font-medium text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300">
                    {e.project}
                  </span>
                  {e.rating && (
                    <span className="text-sm text-amber-400">
                      {"★".repeat(e.rating)}
                      {"☆".repeat(5 - e.rating)}
                    </span>
                  )}
                  <span className="ml-auto text-xs text-slate-400">
                    {new Date(e.created_at).toLocaleString()}
                  </span>
                </div>
                <p className="mt-2 text-sm text-slate-700 dark:text-slate-300">
                  {e.comment}
                </p>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
