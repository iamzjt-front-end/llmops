<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Message, Modal } from '@arco-design/web-vue'
import type { FormInstance, ValidatedError } from '@arco-design/web-vue'
import type {
  ApiToolHeader,
  ApiToolProvider,
  CreateApiToolProviderRequest,
} from '@/models/api-tool'
import { typeMap } from '@/config'
import {
  createApiToolProvider,
  deleteApiToolProvider,
  getApiToolProvider,
  getApiToolProvidersWithPage,
  updateApiToolProvider,
  validateOpenAPISchema,
} from '@/services/api-tool'
import { useAccountStore } from '@/stores/account'

type AvailableTool = {
  name: string
  description: string
  method: string
  path: string
}

type SubmitData = {
  values: Record<string, unknown>
  errors: Record<string, ValidatedError> | undefined
}

const props = defineProps<{
  createType: string
}>()
const emit = defineEmits<{
  'update-create-type': [value: string]
}>()

const route = useRoute()
const accountStore = useAccountStore()
const providers = ref<ApiToolProvider[]>([])
const paginator = reactive({
  currentPage: 1,
  pageSize: 20,
  totalPage: 1,
  totalRecord: 0,
})
const form = reactive<CreateApiToolProviderRequest>({
  icon: '',
  name: '',
  openapi_schema: '',
  headers: [],
})
const formRef = ref<FormInstance>()
const selectedProviderId = ref('')
const editingProviderId = ref('')
const loading = ref(false)
const detailLoading = ref(false)
const submitLoading = ref(false)
const schemaValidating = ref(false)

const getSearchWord = () => {
  const value = route.query.search_word
  return Array.isArray(value) ? value[0] ?? '' : value ?? ''
}

const selectedProvider = computed(
  () => providers.value.find((provider) => provider.id === selectedProviderId.value) ?? null,
)
const formVisible = computed(() => props.createType === 'tool' || Boolean(editingProviderId.value))
const hasMore = computed(() => paginator.currentPage <= paginator.totalPage)
const formatTime = (timestamp: number) => {
  const date = new Date(timestamp * 1000)
  const pad = (value: number) => String(value).padStart(2, '0')
  return `${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}

const availableTools = computed<AvailableTool[]>(() => {
  try {
    const schema = JSON.parse(form.openapi_schema) as Record<string, unknown>
    if (!schema.paths || typeof schema.paths !== 'object') return []

    return Object.entries(schema.paths as Record<string, unknown>).flatMap(([path, pathConfig]) => {
      if (!pathConfig || typeof pathConfig !== 'object') return []
      return Object.entries(pathConfig as Record<string, unknown>).flatMap(
        ([method, operation]) => {
          if (!['get', 'post'].includes(method.toLowerCase())) return []
          if (!operation || typeof operation !== 'object') return []

          const operationData = operation as Record<string, unknown>
          if (typeof operationData.operationId !== 'string') return []
          return [
            {
              name: operationData.operationId,
              description:
                typeof operationData.description === 'string'
                  ? operationData.description
                  : typeof operationData.summary === 'string'
                    ? operationData.summary
                    : '',
              method: method.toUpperCase(),
              path,
            },
          ]
        },
      )
    })
  } catch {
    return []
  }
})

const resetPaginator = () => {
  paginator.currentPage = 1
  paginator.pageSize = 20
  paginator.totalPage = 1
  paginator.totalRecord = 0
}

const loadProviders = async (initial = false) => {
  if (loading.value || (!initial && !hasMore.value)) return
  if (initial) resetPaginator()

  loading.value = true
  try {
    const response = await getApiToolProvidersWithPage(
      paginator.currentPage,
      paginator.pageSize,
      getSearchWord(),
    )
    const { list, paginator: responsePaginator } = response.data
    providers.value = initial ? list : [...providers.value, ...list]
    paginator.currentPage = responsePaginator.current_page + 1
    paginator.pageSize = responsePaginator.page_size
    paginator.totalPage = responsePaginator.total_page
    paginator.totalRecord = responsePaginator.total_record
  } finally {
    loading.value = false
  }
}

const initialize = async () => {
  selectedProviderId.value = ''
  await loadProviders(true)
}

const handleScroll = (event: Event) => {
  const element = event.target as HTMLElement
  if (element.scrollTop + element.clientHeight >= element.scrollHeight - 10) {
    void loadProviders()
  }
}

const resetForm = () => {
  formRef.value?.resetFields()
  Object.assign(form, {
    icon: '',
    name: '',
    openapi_schema: '',
    headers: [] as ApiToolHeader[],
  })
}

const closeForm = () => {
  resetForm()
  editingProviderId.value = ''
  emit('update-create-type', '')
}

const openEditForm = async () => {
  if (!selectedProvider.value) return
  detailLoading.value = true
  try {
    const response = await getApiToolProvider(selectedProvider.value.id)
    const detail = response.data
    resetForm()
    Object.assign(form, {
      icon: detail.icon,
      name: detail.name,
      openapi_schema: detail.openapi_schema,
      headers: detail.headers.map((header) => ({ ...header })),
    })
    editingProviderId.value = detail.id
  } finally {
    detailLoading.value = false
  }
}

const validateSchema = async () => {
  if (!form.openapi_schema.trim()) return
  schemaValidating.value = true
  try {
    await validateOpenAPISchema(form.openapi_schema)
    Message.success('OpenAPI Schema 校验通过')
  } finally {
    schemaValidating.value = false
  }
}

const handleSubmit = async ({ errors }: SubmitData) => {
  if (errors) return

  submitLoading.value = true
  try {
    const request: CreateApiToolProviderRequest = {
      ...form,
      headers: form.headers.map((header) => ({ ...header })),
    }
    const response = editingProviderId.value
      ? await updateApiToolProvider(editingProviderId.value, request)
      : await createApiToolProvider(request)
    Message.success(response.message)
    closeForm()
    selectedProviderId.value = ''
    await initialize()
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = () => {
  if (!editingProviderId.value) return
  const providerId = editingProviderId.value
  Modal.warning({
    title: '删除这个插件？',
    content: '删除操作不可撤销，AI 应用将无法再访问该插件。',
    hideCancel: false,
    onOk: async () => {
      const response = await deleteApiToolProvider(providerId)
      Message.success(response.message)
      closeForm()
      selectedProviderId.value = ''
      await initialize()
    },
  })
}

watch(
  () => route.query.search_word,
  () => void initialize(),
)

watch(
  () => props.createType,
  (value) => {
    if (value === 'tool') {
      editingProviderId.value = ''
      resetForm()
    }
  },
)

onMounted(() => void initialize())
</script>

<template>
  <div class="scrollbar-w-none h-full overflow-y-auto" @scroll="handleScroll">
    <a-spin :loading="loading && providers.length === 0" class="block min-h-full w-full">
      <a-row :gutter="[20, 20]">
        <a-col v-for="provider in providers" :key="provider.id" :span="6">
          <a-card
            hoverable
            class="h-full cursor-pointer rounded-lg"
            @click="selectedProviderId = provider.id"
          >
            <div class="mb-3 flex items-center gap-3">
              <a-avatar :size="40" shape="square" :image-url="provider.icon" />
              <div class="min-w-0">
                <div class="truncate text-base font-bold text-gray-900">{{ provider.name }}</div>
                <div class="truncate text-xs text-gray-500">{{ provider.tools.length }} 个工具</div>
              </div>
            </div>
            <div class="mb-2 line-clamp-4 h-[72px] leading-[18px] text-gray-500">
              {{ provider.description }}
            </div>
            <div class="flex items-center gap-1.5">
              <a-avatar :size="18" class="bg-blue-700"><icon-user /></a-avatar>
              <div class="text-xs text-gray-400">
                {{ accountStore.account.name }} · 编辑时间 {{ formatTime(provider.created_at) }}
              </div>
            </div>
          </a-card>
        </a-col>

        <a-col v-if="!loading && providers.length === 0" :span="24">
          <a-empty
            description="没有匹配的自定义插件"
            class="flex h-[400px] flex-col items-center justify-center"
          />
        </a-col>
      </a-row>

      <div v-if="providers.length" class="flex h-14 items-center justify-center text-gray-400">
        <a-space v-if="loading"><a-spin />正在加载</a-space>
        <span v-else-if="hasMore">继续向下滚动加载</span>
        <span v-else>共 {{ paginator.totalRecord }} 个插件，已全部加载</span>
      </div>
    </a-spin>

    <a-drawer
      :visible="Boolean(selectedProvider)"
      :width="380"
      :footer="false"
      title="工具详情"
      :drawer-style="{ background: '#f9fafb' }"
      @cancel="selectedProviderId = ''"
    >
      <div v-if="selectedProvider">
        <div class="mb-3 flex items-center gap-3">
          <a-avatar :size="40" shape="square" :image-url="selectedProvider.icon" />
          <div class="min-w-0">
            <div class="truncate text-base font-bold text-gray-900">
              {{ selectedProvider.name }}
            </div>
            <div class="text-xs text-gray-500">包含 {{ selectedProvider.tools.length }} 个工具</div>
          </div>
        </div>
        <p class="mb-4 leading-[18px] text-gray-500">{{ selectedProvider.description }}</p>
        <a-button
          :loading="detailLoading"
          type="dashed"
          long
          class="mb-2 rounded-lg"
          @click="openEditForm"
        >
          <template #icon><icon-settings /></template>
          编辑插件
        </a-button>
        <hr class="my-4" />
        <div class="flex flex-col gap-2">
          <a-card v-for="tool in selectedProvider.tools" :key="tool.id" class="rounded-xl">
            <div class="mb-2 font-bold text-gray-900">{{ tool.name }}</div>
            <div class="text-xs text-gray-500">{{ tool.description }}</div>
            <template v-if="tool.inputs.length">
              <div class="my-4 flex items-center gap-2">
                <span class="text-xs font-bold text-gray-500">参数</span>
                <hr class="flex-1" />
              </div>
              <div class="flex flex-col gap-4">
                <div v-for="input in tool.inputs" :key="input.name" class="flex flex-col gap-2">
                  <div class="flex items-center gap-2 text-xs">
                    <span class="font-bold text-gray-900">{{ input.name }}</span>
                    <span class="text-gray-500">{{ typeMap[input.type] ?? input.type }}</span>
                    <span v-if="input.required" class="text-red-700">必填</span>
                  </div>
                  <div class="text-xs text-gray-500">{{ input.description }}</div>
                </div>
              </div>
            </template>
          </a-card>
        </div>
      </div>
    </a-drawer>

    <a-modal
      :width="680"
      :visible="formVisible"
      hide-title
      :footer="false"
      modal-class="rounded-xl"
      @cancel="closeForm"
    >
      <div class="flex items-center justify-between">
        <div class="text-lg font-bold text-gray-700">
          {{ editingProviderId ? '更新' : '新建' }}插件
        </div>
        <a-button type="text" class="!text-gray-700" size="small" @click="closeForm">
          <template #icon><icon-close /></template>
        </a-button>
      </div>

      <a-form ref="formRef" :model="form" layout="vertical" class="pt-6" @submit="handleSubmit">
        <a-form-item
          field="icon"
          label="插件图标 URL"
          asterisk-position="end"
          :rules="[
            { required: true, message: '插件图标不能为空' },
            { type: 'url', message: '请输入有效的图片 URL' },
          ]"
        >
          <div class="flex w-full items-center gap-3">
            <a-avatar v-if="form.icon" :size="40" shape="square" :image-url="form.icon" />
            <a-input v-model="form.icon" placeholder="https://example.com/icon.png" />
          </div>
        </a-form-item>
        <a-form-item
          field="name"
          label="插件名称"
          asterisk-position="end"
          :rules="[{ required: true, message: '插件名称不能为空' }]"
        >
          <a-input
            v-model="form.name"
            placeholder="请输入含义清晰的插件名称"
            show-word-limit
            :max-length="30"
          />
        </a-form-item>
        <a-form-item
          field="openapi_schema"
          label="OpenAPI Schema"
          asterisk-position="end"
          :rules="[{ required: true, message: 'OpenAPI Schema 不能为空' }]"
        >
          <a-textarea
            v-model="form.openapi_schema"
            :loading="schemaValidating"
            :auto-size="{ minRows: 5, maxRows: 9 }"
            placeholder="在此输入 JSON 格式的 OpenAPI Schema"
            @blur="validateSchema"
          />
        </a-form-item>
        <a-form-item label="可用工具">
          <div class="w-full overflow-x-auto rounded-lg border border-gray-200">
            <table class="w-full text-left text-xs font-normal leading-[18px] text-gray-700">
              <thead class="text-gray-500">
                <tr class="border-b border-gray-200">
                  <th class="p-2 pl-3 font-medium">名称</th>
                  <th class="w-[236px] p-2 pl-3 font-medium">描述</th>
                  <th class="p-2 pl-3 font-medium">方法</th>
                  <th class="p-2 pl-3 font-medium">路径</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="tool in availableTools"
                  :key="`${tool.method}-${tool.path}`"
                  class="border-b border-gray-200 last:border-0"
                >
                  <td class="p-2 pl-3">{{ tool.name }}</td>
                  <td class="w-[236px] p-2 pl-3">{{ tool.description }}</td>
                  <td class="p-2 pl-3">{{ tool.method }}</td>
                  <td class="p-2 pl-3">{{ tool.path }}</td>
                </tr>
                <tr v-if="availableTools.length === 0">
                  <td colspan="4" class="p-4 text-center text-gray-400">
                    输入有效的 OpenAPI Schema 后会在这里显示工具
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </a-form-item>
        <a-form-item label="Headers">
          <div class="w-full overflow-x-auto rounded-lg border border-gray-200">
            <table class="mb-3 w-full text-xs font-normal leading-[18px] text-gray-700">
              <thead class="text-gray-500">
                <tr class="border-b border-gray-200">
                  <th class="p-2 pl-3 font-medium">Key</th>
                  <th class="p-2 pl-3 font-medium">Value</th>
                  <th class="w-[50px] p-2 pl-3 font-medium">操作</th>
                </tr>
              </thead>
              <tbody v-if="form.headers.length" class="border-b border-gray-200">
                <tr
                  v-for="(header, index) in form.headers"
                  :key="index"
                  class="border-b border-gray-200 last:border-0"
                >
                  <td class="p-2 pl-3">
                    <a-input v-model="header.key" placeholder="请求头键名" />
                  </td>
                  <td class="p-2 pl-3">
                    <a-input v-model="header.value" placeholder="请求头键值" />
                  </td>
                  <td class="p-2 pl-3">
                    <a-button
                      size="mini"
                      type="text"
                      class="!text-gray-700"
                      @click="form.headers.splice(index, 1)"
                    >
                      <template #icon><icon-delete /></template>
                    </a-button>
                  </td>
                </tr>
              </tbody>
            </table>
            <a-button
              size="mini"
              class="mb-3 ml-3 rounded !text-gray-700"
              @click="form.headers.push({ key: '', value: '' })"
            >
              <template #icon><icon-plus /></template>
              增加请求头
            </a-button>
          </div>
        </a-form-item>

        <div class="flex items-center justify-between">
          <a-button v-if="editingProviderId" class="rounded-lg !text-red-700" @click="handleDelete">
            删除
          </a-button>
          <span v-else />
          <a-space :size="16">
            <a-button class="rounded-lg" @click="closeForm">取消</a-button>
            <a-button :loading="submitLoading" type="primary" html-type="submit" class="rounded-lg">
              保存
            </a-button>
          </a-space>
        </div>
      </a-form>
    </a-modal>
  </div>
</template>
