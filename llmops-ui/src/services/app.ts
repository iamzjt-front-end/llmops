import { ssePost } from '@/utils/request'

export type DebugStreamEvent = { event: string; data: Record<string, any> }

export const debugApp = (
  app_id: string,
  query: string,
  onData: (event_response: DebugStreamEvent) => void,
) => {
  return ssePost(
    `/apps/${app_id}/debug`,
    {
      body: { query },
    },
    onData,
  )
}
