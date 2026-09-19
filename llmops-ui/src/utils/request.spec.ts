import { afterEach, describe, expect, it } from 'vitest'

import { ssePost } from '@/utils/request'

const createStreamResponse = (chunks: string[]) => {
  const encoder = new TextEncoder()
  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      chunks.forEach((chunk) => controller.enqueue(encoder.encode(chunk)))
      controller.close()
    },
  })

  return new Response(stream, { status: 200 })
}

describe('ssePost', () => {
  afterEach(() => {
    Object.defineProperty(globalThis, 'fetch', {
      configurable: true,
      value: globalThis.fetch,
      writable: true,
    })
  })

  it('parses streamed events across chunk boundaries and waits for stream completion', async () => {
    const events: Array<{ event: string; data: Record<string, any> }> = []
    const response = createStreamResponse([
      'event: agent_message\ndata: {"answer":"你',
      '好"}\n\nevent: agent_end\r\ndata: {"answer":"你好"}\r\n\r\n',
    ])
    const fetchMock = () => Promise.resolve(response)
    Object.defineProperty(globalThis, 'fetch', {
      configurable: true,
      value: fetchMock,
      writable: true,
    })

    await ssePost('/apps/app-id/debug', { body: { query: '你好' } }, (event) => {
      events.push(event)
    })

    expect(events).toEqual([
      { event: 'agent_message', data: { answer: '你好' } },
      { event: 'agent_end', data: { answer: '你好' } },
    ])
  })

  it('rejects when the response is not usable', async () => {
    Object.defineProperty(globalThis, 'fetch', {
      configurable: true,
      value: () => Promise.resolve(new Response(null, { status: 500 })),
      writable: true,
    })

    await expect(
      ssePost('/apps/app-id/debug', { body: { query: '你好' } }, () => undefined),
    ).rejects.toThrow('网络请求失败')
  })
})
