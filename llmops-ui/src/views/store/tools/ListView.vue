<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import type { BuiltinToolCategory, BuiltinToolProvider } from '@/models/builtin-tool'
import { apiPrefix, typeMap } from '@/config'
import { getBuiltinTools, getCategories } from '@/services/builtin-tool'

const router = useRouter()
const categories = ref<BuiltinToolCategory[]>([])
const providers = ref<BuiltinToolProvider[]>([])
const loading = ref(false)
const category = ref('all')
const searchWord = ref('')
const selectedProviderName = ref('')

const filteredProviders = computed(() => {
  const keyword = searchWord.value.trim().toLocaleLowerCase()
  return providers.value.filter((provider) => {
    const matchesCategory = category.value === 'all' || provider.category === category.value
    const searchableText =
      `${provider.label} ${provider.name} ${provider.description}`.toLocaleLowerCase()
    return matchesCategory && (!keyword || searchableText.includes(keyword))
  })
})

const selectedProvider = computed(
  () => providers.value.find((provider) => provider.name === selectedProviderName.value) ?? null,
)

const formatTime = (timestamp: number) => {
  const date = new Date(timestamp * 1000)
  const pad = (value: number) => String(value).padStart(2, '0')
  return `${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}

const openCreatePage = () => {
  void router.push({ name: 'space-tools-list', query: { create: 'tool' } })
}

onMounted(async () => {
  loading.value = true
  try {
    const [categoryResponse, providerResponse] = await Promise.all([
      getCategories(),
      getBuiltinTools(),
    ])
    categories.value = categoryResponse.data
    providers.value = providerResponse.data
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <a-spin :loading="loading" class="block h-full w-full overflow-y-auto">
    <div class="flex min-h-full flex-col p-6">
      <div class="mb-6 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <a-avatar :size="32" class="bg-blue-700"><icon-common :size="18" /></a-avatar>
          <h1 class="text-lg font-medium text-gray-900">插件广场</h1>
        </div>
        <a-button type="primary" class="rounded-lg" @click="openCreatePage">
          创建自定义插件
        </a-button>
      </div>

      <div class="mb-6 flex items-start justify-between gap-6">
        <div class="flex flex-wrap items-center gap-2">
          <a-button
            :type="category === 'all' ? 'secondary' : 'text'"
            class="rounded-lg !text-gray-700"
            @click="category = 'all'"
          >
            全部
          </a-button>
          <a-button
            v-for="item in categories"
            :key="item.category"
            :type="category === item.category ? 'secondary' : 'text'"
            class="rounded-lg !text-gray-700"
            @click="category = item.category"
          >
            {{ item.name }}
          </a-button>
        </div>
        <a-input-search
          v-model="searchWord"
          allow-clear
          placeholder="请输入插件名称"
          class="w-[240px] flex-shrink-0 rounded-lg border-gray-300 bg-white"
        />
      </div>

      <a-row :gutter="[20, 20]" class="flex-1">
        <a-col v-for="provider in filteredProviders" :key="provider.name" :span="6">
          <a-card
            hoverable
            class="h-full cursor-pointer rounded-lg"
            @click="selectedProviderName = provider.name"
          >
            <div class="mb-3 flex items-center gap-3">
              <a-avatar :size="40" shape="square" :style="{ backgroundColor: provider.background }">
                <img
                  :src="`${apiPrefix}/builtin-tools/${provider.name}/icon`"
                  :alt="provider.label"
                />
              </a-avatar>
              <div class="min-w-0">
                <div class="truncate text-base font-bold text-gray-900">{{ provider.label }}</div>
                <div class="truncate text-xs text-gray-500">
                  提供商 {{ provider.name }} · {{ provider.tools.length }} 个工具
                </div>
              </div>
            </div>
            <div class="mb-2 line-clamp-4 h-[72px] leading-[18px] text-gray-500">
              {{ provider.description }}
            </div>
            <div class="flex items-center gap-1.5">
              <a-avatar :size="18" class="bg-blue-700"><icon-user /></a-avatar>
              <div class="text-xs text-gray-400">
                LLMOps · 发布时间 {{ formatTime(provider.created_at) }}
              </div>
            </div>
          </a-card>
        </a-col>
        <a-col v-if="!loading && filteredProviders.length === 0" :span="24">
          <a-empty
            description="没有匹配的内置插件"
            class="flex h-[400px] flex-col items-center justify-center"
          />
        </a-col>
      </a-row>
    </div>

    <a-drawer
      :visible="Boolean(selectedProvider)"
      :width="380"
      :footer="false"
      title="工具详情"
      :drawer-style="{ background: '#f9fafb' }"
      @cancel="selectedProviderName = ''"
    >
      <div v-if="selectedProvider">
        <div class="mb-3 flex items-center gap-3">
          <a-avatar
            :size="40"
            shape="square"
            :style="{ backgroundColor: selectedProvider.background }"
          >
            <img
              :src="`${apiPrefix}/builtin-tools/${selectedProvider.name}/icon`"
              :alt="selectedProvider.label"
            />
          </a-avatar>
          <div>
            <div class="text-base font-bold text-gray-900">{{ selectedProvider.label }}</div>
            <div class="text-xs text-gray-500">
              提供商 {{ selectedProvider.name }} · {{ selectedProvider.tools.length }} 个工具
            </div>
          </div>
        </div>
        <p class="leading-[18px] text-gray-500">{{ selectedProvider.description }}</p>
        <hr class="my-4" />
        <div class="mb-2 text-xs text-gray-500">
          包含 {{ selectedProvider.tools.length }} 个工具
        </div>
        <div class="flex flex-col gap-2">
          <a-card v-for="tool in selectedProvider.tools" :key="tool.name" class="rounded-xl">
            <div class="mb-2 font-bold text-gray-900">{{ tool.label }}</div>
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
  </a-spin>
</template>
