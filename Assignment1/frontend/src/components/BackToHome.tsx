import { Link } from "react-router-dom"

export default function BackToHome() {
  return (
    <Link
      to="/"
      className="flex items-center gap-1.5 text-sm text-slate-500 transition-colors hover:text-indigo-600 dark:hover:text-indigo-400"
    >
      <svg
        className="h-4 w-4"
        fill="none"
        viewBox="0 0 24 24"
        strokeWidth={2}
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18"
        />
      </svg>
      Portfolio
    </Link>
  )
}
