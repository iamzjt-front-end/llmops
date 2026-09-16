import type {
  CreateApiToolProviderRequest,
  GetApiToolProviderResponse,
  GetApiToolProvidersWithPageResponse,
  UpdateApiToolProviderRequest,
} from '@/models/api-tool'
import type { BaseResponse } from '@/models/base'
import { get, post } from '@/utils/request'

type MessageResponse = BaseResponse<Record<string, never>>

export const getApiToolProvidersWithPage = (currentPage = 1, pageSize = 20, searchWord = '') => {
  return get<GetApiToolProvidersWithPageResponse>('/api-tools', {
    params: {
      current_page: currentPage,
      page_size: pageSize,
      search_word: searchWord,
    },
  })
}

export const validateOpenAPISchema = (openapiSchema: string) => {
  return post<MessageResponse>('/api-tools/validate-openapi-schema', {
    body: { openapi_schema: openapiSchema },
  })
}

export const createApiToolProvider = (request: CreateApiToolProviderRequest) => {
  return post<MessageResponse>('/api-tools', { body: request })
}

export const updateApiToolProvider = (
  providerId: string,
  request: UpdateApiToolProviderRequest,
) => {
  return post<MessageResponse>(`/api-tools/${providerId}`, { body: request })
}

export const deleteApiToolProvider = (providerId: string) => {
  return post<MessageResponse>(`/api-tools/${providerId}/delete`)
}

export const getApiToolProvider = (providerId: string) => {
  return get<GetApiToolProviderResponse>(`/api-tools/${providerId}`)
}
