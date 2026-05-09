import { useMemo, useState } from "react"
import { ChatKit, useChatKit } from "@openai/chatkit-react"
import { createClientSecretFetcher, workflowId } from "../lib/chatkitSession"

export function ChatKitPanel() {
  const [sessionError, setSessionError] = useState<string | null>(null)

  const getClientSecret = useMemo(() => {
    const fetcher = createClientSecretFetcher(workflowId)
    return async (currentSecret: string | null) => {
      try {
        return await fetcher(currentSecret)
      } catch (err) {
        const msg = err instanceof Error ? err.message : "Failed to start chat session"
        setSessionError(msg)
        throw err
      }
    }
  }, [])

  const chatkit = useChatKit({ api: { getClientSecret } })

  return (
    <div className="flex h-[75vh] w-full items-center justify-center rounded-2xl bg-white shadow-sm dark:bg-slate-900">
      {sessionError ? (
        <div className="flex flex-col items-center gap-3 px-6 text-center">
          <p className="text-sm font-medium text-red-500">Chat failed to load</p>
          <p className="max-w-sm text-xs text-slate-400">{sessionError}</p>
        </div>
      ) : (
        <ChatKit control={chatkit.control} className="h-full w-full" />
      )}
    </div>
  )
}
