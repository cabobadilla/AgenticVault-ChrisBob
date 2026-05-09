const readEnvString = (value: unknown): string | undefined =>
  typeof value === "string" && value.trim() ? value.trim() : undefined

export const workflowId =
  readEnvString(import.meta.env.VITE_CHATKIT_WORKFLOW_ID) ?? ""

export function createClientSecretFetcher(
  workflow: string,
  endpoint = "/api/create-session"
) {
  return async (currentSecret: string | null) => {
    if (currentSecret) return currentSecret

    const body: Record<string, unknown> = {}
    if (workflow) body.workflow = { id: workflow }

    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    })

    const payload = (await response.json().catch(() => ({}))) as {
      client_secret?: string
      error?: string
    }

    if (!response.ok) {
      throw new Error(payload.error ?? "Failed to create session")
    }

    if (!payload.client_secret) {
      throw new Error("Missing client_secret in response")
    }

    return payload.client_secret
  }
}
