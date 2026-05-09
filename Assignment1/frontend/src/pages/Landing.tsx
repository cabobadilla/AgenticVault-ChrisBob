import { Link } from "react-router-dom"

interface Project {
  id: string
  week: number
  title: string
  description: string
  tags: string[]
  path: string
}

const PROJECTS: Project[] = [
  {
    id: "chatkit-agent",
    week: 1,
    title: "Customer Service Agent",
    description:
      "AI-powered customer service chatbot built with OpenAI ChatKit and Agent Builder. Handles common queries with a managed workflow.",
    tags: ["ChatKit", "Agent Builder", "FastAPI"],
    path: "/projects/chatkit-agent",
  },
]

export default function Landing() {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <header className="border-b border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
        <div className="mx-auto max-w-5xl px-6 py-10">
          <p className="text-xs font-semibold uppercase tracking-widest text-indigo-600 dark:text-indigo-400">
            AI Bootcamp · Maven
          </p>
          <h1 className="mt-2 text-4xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
            Portfolio
          </h1>
          <p className="mt-2 text-slate-500 dark:text-slate-400">
            Christian Bobadilla — Weekly Assignments
          </p>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-6 py-12">
        <h2 className="mb-6 text-xs font-semibold uppercase tracking-widest text-slate-400">
          Assignments
        </h2>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {PROJECTS.map((p) => (
            <Link
              key={p.id}
              to={p.path}
              className="group flex flex-col rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-all hover:border-indigo-300 hover:shadow-md dark:border-slate-700 dark:bg-slate-900 dark:hover:border-indigo-500"
            >
              <span className="text-xs font-medium text-slate-400">
                Week {p.week}
              </span>
              <h3 className="mt-1 text-lg font-semibold text-slate-900 transition-colors group-hover:text-indigo-600 dark:text-slate-100 dark:group-hover:text-indigo-400">
                {p.week}. {p.title}
              </h3>
              <p className="mt-2 flex-1 text-sm leading-relaxed text-slate-500 dark:text-slate-400">
                {p.description}
              </p>
              <div className="mt-4 flex flex-wrap gap-2">
                {p.tags.map((tag) => (
                  <span
                    key={tag}
                    className="rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs font-medium text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </Link>
          ))}
        </div>
      </main>

      <footer className="mx-auto max-w-5xl border-t border-slate-100 px-6 py-8 dark:border-slate-800">
        <p className="text-xs text-slate-400">
          Built with OpenAI ChatKit · FastAPI · React
        </p>
      </footer>
    </div>
  )
}
