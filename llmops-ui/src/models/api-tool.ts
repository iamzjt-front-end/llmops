import type { BasePaginatorResponse, BaseResponse } from '@/models/base'

export type ToolInput = {
  name: string
  description: string
  required: boolean
  type: string
}

export type ApiTool = {
  id: string
  name: string
  description: string
  inputs: ToolInput[]
}

export type ApiToolHeader = {
  key: string
  value: string
}

export type ApiToolProvider = {
  id: string
  name: string
  icon: string
  description: string
  headers: ApiToolHeader[]
  tools: ApiTool[]
  created_at: number
}

export type ApiToolProviderDetail = Omit<ApiToolProvider, 'description' | 'tools'> & {
  openapi_schema: string
}

export type GetApiToolProvidersWithPageResponse = BasePaginatorResponse<ApiToolProvider>

export type CreateApiToolProviderRequest = {
  name: string
  icon: string
  openapi_schema: string
  headers: ApiToolHeader[]
}

export type UpdateApiToolProviderRequest = CreateApiToolProviderRequest

export type GetApiToolProviderResponse = BaseResponse<ApiToolProviderDetail>
