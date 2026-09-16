<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const getSearchWord = () => {
  const value = route.query.search_word
  return Array.isArray(value) ? value[0] ?? '' : value ?? ''
}

const createType = ref(route.query.create === 'tool' ? 'tool' : '')
const searchWord = ref(getSearchWord())

const search = (value: string) => {
  void router.push({
    path: route.path,
    query: value ? { search_word: value } : {},
  })
}

const updateCreateType = (value: string) => {
  createType.value = value
  if (!value && route.query.create) {
    const query = { ...route.query }
    delete query.create
    void router.replace({ path: route.path, query })
  }
}

watch(
  () => route.query.search_word,
  () => {
    searchWord.value = getSearchWord()
  },
)

watch(
  () => route.query.create,
  (value) => {
    createType.value = value === 'tool' ? 'tool' : ''
  },
)
</script>

<template>
  <div class="flex h-full flex-col overflow-hidden px-6">
    <div class="sticky top-0 z-20 bg-gray-50 pt-6">
      <div class="mb-6 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <a-avatar :size="32" class="bg-blue-700"><icon-user :size="18" /></a-avatar>
          <div class="text-lg font-medium text-gray-900">个人空间</div>
        </div>
        <a-button v-if="route.path.startsWith('/space/apps')" type="primary" class="rounded-lg">
          创建 AI 应用
        </a-button>
        <a-button
          v-else-if="route.path.startsWith('/space/tools')"
          type="primary"
          class="rounded-lg"
          @click="createType = 'tool'"
        >
          创建自定义插件
        </a-button>
        <a-button
          v-else-if="route.path.startsWith('/space/workflows')"
          type="primary"
          class="rounded-lg"
        >
          创建工作流
        </a-button>
        <a-button v-else type="primary" class="rounded-lg">创建知识库</a-button>
      </div>

      <div class="mb-6 flex items-center justify-between">
        <nav class="flex items-center gap-2">
          <router-link
            v-for="item in [
              { path: '/space/apps', label: 'AI应用' },
              { path: '/space/tools', label: '插件' },
              { path: '/space/workflows', label: '工作流' },
              { path: '/space/datasets', label: '知识库' },
            ]"
            :key="item.path"
            :to="item.path"
            class="h-8 rounded-lg px-3 leading-8 text-gray-700 transition-all hover:bg-gray-200"
            active-class="bg-gray-100"
          >
            {{ item.label }}
          </router-link>
        </nav>
        <a-input-search
          v-model="searchWord"
          placeholder="输入关键词进行搜索"
          class="w-[240px] rounded-lg border-gray-300 bg-white"
          @search="search"
        />
      </div>
    </div>

    <router-view :create-type="createType" @update-create-type="updateCreateType" />
  </div>
</template>
