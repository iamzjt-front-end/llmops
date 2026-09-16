import type { BaseResponse } from '@/models/base'
import type { ToolInput } from '@/models/api-tool'

export type BuiltinToolCategory = {
  category: string
  icon: string
  name: string
}

export type BuiltinTool = {
  name: string
  label: string
  description: string
  inputs: ToolInput[]
}

export type BuiltinToolProvider = {
  background: string
  category: string
  created_at: number
  description: string
  label: string
  name: string
  tools: BuiltinTool[]
}

export type GetCategoriesResponse = BaseResponse<BuiltinToolCategory[]>

export type GetBuiltinToolsResponse = BaseResponse<BuiltinToolProvider[]>
