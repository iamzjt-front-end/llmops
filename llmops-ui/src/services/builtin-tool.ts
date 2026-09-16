import type { GetBuiltinToolsResponse, GetCategoriesResponse } from '@/models/builtin-tool'
import { get } from '@/utils/request'

export const getCategories = () => {
  return get<GetCategoriesResponse>('/builtin-tools/categories')
}

export const getBuiltinTools = () => {
  return get<GetBuiltinToolsResponse>('/builtin-tools')
}
