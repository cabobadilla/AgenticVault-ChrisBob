import { useState } from "react"

interface Props {
  project: string
}

type Status = "idle" | "loading" | "done" | "error"

export default function FeedbackForm({ project }: Props) {
  const [rating, setRating] = useState<number | null>(null)
  const [comment, setComment] = useState("")
  const [status, setStatus] = useState<Status>("idle")

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!comment.trim()) return
    setStatus("loading")
    try {
      const res = await fetch("/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ project, comment: comment.trim(), rating }),
      })
      if (!res.ok) throw new Error()
      setStatus("done")
    } catch {
      setStatus("error")
    }
  }

  if (status === "done") {
    return (
      <div className="rounded-2xl border border-green-200 bg-green-50 p-6 text-center dark:border-green-800 dark:bg-green-900/20">
        <p className="font-medium text-green-700 dark:text-green-300">
          Thank you for your feedback!
        </p>
      </div>
    )
  }

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
      <h2 className="text-base font-semibold text-slate-900 dark:text-slate-100">
        Leave Feedback
      </h2>
      <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
        What do you think about this project?
      </p>

      <form onSubmit={handleSubmit} className="mt-4 flex flex-col gap-4">
        <div className="flex gap-1">
          {[1, 2, 3, 4, 5].map((star) => (
            <button
              key={star}
              type="button"
              onClick={() => setRating(star === rating ? null : star)}
              className={`text-2xl leading-none transition-transform hover:scale-110 ${
                rating !== null && star <= rating
                  ? "text-amber-400"
                  : "text-slate-300 dark:text-slate-600"
              }`}
            >
              ★
            </button>
          ))}
        </div>

        <textarea
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="Share your thoughts…"
          rows={3}
          maxLength={1000}
          className="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:border-indigo-400 focus:outline-none dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100 dark:placeholder-slate-500"
        />

        {status === "error" && (
          <p className="text-sm text-red-500">
            Something went wrong. Please try again.
          </p>
        )}

        <button
          type="submit"
          disabled={!comment.trim() || status === "loading"}
          className="self-start rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-700 disabled:opacity-50"
        >
          {status === "loading" ? "Sending…" : "Submit Feedback"}
        </button>
      </form>
    </section>
  )
}
