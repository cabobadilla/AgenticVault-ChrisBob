import { ChatKitPanel } from "../components/ChatKitPanel"
import BackToHome from "../components/BackToHome"
import FeedbackForm from "../components/FeedbackForm"

export default function ChatKitAgent() {
  return (
    <div className="min-h-screen bg-slate-100 dark:bg-slate-950">
      <header className="border-b border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
        <div className="mx-auto flex max-w-5xl items-center gap-4 px-6 py-4">
          <BackToHome />
          <div className="h-5 w-px bg-slate-200 dark:bg-slate-700" />
          <div>
            <p className="text-xs text-slate-400">Assignment 1</p>
            <h1 className="text-base font-semibold text-slate-900 dark:text-slate-100">
              Customer Service Agent
            </h1>
          </div>
        </div>
      </header>

      <main className="mx-auto flex max-w-5xl flex-col gap-8 px-6 py-8">
        <ChatKitPanel />
        <FeedbackForm project="chatkit-agent" />
      </main>
    </div>
  )
}
