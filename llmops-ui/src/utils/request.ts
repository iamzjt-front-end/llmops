import { Message } from '@arco-design/web-vue'
import { apiPrefix, httpCode } from '@/config'

// 1.超时时间为100s
const TIME_OUT = 100000

// 2.基础的配置
const baseFetchOptions = {
  method: 'GET',
  mode: 'cors',
  credentials: 'include',
  headers: new Headers({
    'Content-Type': 'application/json',
  }),
  redirect: 'follow',
}

// 3.fetch参数类型
type FetchOptionType = Omit<RequestInit, 'body'> & {
  params?: Record<string, any>
  body?: BodyInit | Record<string, any> | null
}

// 4.封装基础的fetch请求
const baseFetch = <T>(url: string, fetchOptions: FetchOptionType): Promise<T> => {
  // 5.将所有的配置信息合并起来
  const options: typeof baseFetchOptions & FetchOptionType = Object.assign(
    {},
    baseFetchOptions,
    fetchOptions,
  )

  // 6.组装url
  let urlWithPrefix = `${apiPrefix}${url.startsWith('/') ? url : `/${url}`}`

  // 7.解构出对应的请求方法、params、body参数
  const { method, params, body } = options

  // 8.如果请求是GET方法，并且传递了params参数
  if (method === 'GET' && params) {
    const paramsArray: string[] = []
    Object.keys(params).forEach((key) => {
      paramsArray.push(`${key}=${encodeURIComponent(params[key])}`)
    })
    if (urlWithPrefix.search(/\?/) === -1) {
      urlWithPrefix += `?${paramsArray.join('&')}`
    } else {
      urlWithPrefix += `&${paramsArray.join('&')}`
    }

    delete options.params
  }

  // 9.处理post传递的数据
  if (body) {
    options.body = JSON.stringify(body)
  }

  // 10.同时发起两个Promise(或者是说两个操作，看谁先返回，就先结束)
  return Promise.race([
    // 11.使用定时器来检测是否超时
    new Promise((resolve, reject) => {
      setTimeout(() => {
        reject('接口已超时')
      }, TIME_OUT)
    }),
    // 12.发起一个正常请求
    new Promise((resolve, reject) => {
      globalThis
        .fetch(urlWithPrefix, options as RequestInit)
        .then(async (res) => {
          const json = await res.json()
          if (json.code === httpCode.success) {
            resolve(json)
          } else {
            Message.error(json.message)
            reject(new Error(json.message))
          }
        })
        .catch((err) => {
          Message.error(err.message)
          reject(err)
        })
    }),
  ]) as Promise<T>
}

export const request = <T>(url: string, options = {}) => {
  return baseFetch<T>(url, options)
}

export const get = <T>(url: string, options = {}) => {
  return request<T>(url, Object.assign({}, options, { method: 'GET' }))
}

export const post = <T>(url: string, options = {}) => {
  return request<T>(url, Object.assign({}, options, { method: 'POST' }))
}

// 封装基于 POST 的 SSE 流式事件请求。Promise 会在服务端流结束后才 resolve。
export const ssePost = async (
  url: string,
  fetchOptions: FetchOptionType,
  onData: (data: { event: string; data: Record<string, any> }) => void,
): Promise<void> => {
  const options = Object.assign({}, baseFetchOptions, { method: 'POST' }, fetchOptions)
  const urlWithPrefix = `${apiPrefix}${url.startsWith('/') ? url : `/${url}`}`

  const { body } = fetchOptions
  if (body) options.body = JSON.stringify(body)

  let response: Response
  try {
    response = await globalThis.fetch(urlWithPrefix, options as RequestInit)
  } catch (error) {
    Message.error('网络请求失败')
    throw error
  }

  if (!response.ok || !response.body) {
    const error = new Error('网络请求失败')
    Message.error(error.message)
    throw error
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''

  const parseBlock = (block: string) => {
    let event = 'message'
    const dataLines: string[] = []

    for (const rawLine of block.split(/\r?\n/)) {
      if (rawLine.startsWith('event:')) {
        event = rawLine.slice(6).trim()
      } else if (rawLine.startsWith('data:')) {
        dataLines.push(rawLine.slice(5).trimStart())
      }
    }

    if (!dataLines.length) return
    const data = JSON.parse(dataLines.join('\n'))
    onData({ event, data })
  }

  return new Promise<void>((resolve, reject) => {
    const read = (): void => {
      reader
        .read()
        .then((result) => {
          buffer += decoder.decode(result.value, { stream: true })
          const blocks = buffer.split(/\r?\n\r?\n/)
          buffer = blocks.pop() ?? ''

          try {
            blocks.forEach(parseBlock)
          } catch (error) {
            reader.cancel().catch(() => undefined)
            Message.error('流式响应解析失败')
            reject(error)
            return
          }

          if (result.done) {
            resolve()
            return
          }
          read()
        })
        .catch((error) => {
          Message.error('网络请求失败')
          reject(error)
        })
    }

    read()
  })
}
