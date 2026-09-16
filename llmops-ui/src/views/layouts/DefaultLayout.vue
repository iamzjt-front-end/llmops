<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import IconApp from '@/components/icons/IconApp.vue'
import IconAppFull from '@/components/icons/IconAppFull.vue'
import IconHome from '@/components/icons/IconHome.vue'
import IconHomeFull from '@/components/icons/IconHomeFull.vue'
import IconOpenApi from '@/components/icons/IconOpenApi.vue'
import IconOpenApiFull from '@/components/icons/IconOpenApiFull.vue'
import IconSpace from '@/components/icons/IconSpace.vue'
import IconSpaceFull from '@/components/icons/IconSpaceFull.vue'
import IconTool from '@/components/icons/IconTool.vue'
import IconToolFull from '@/components/icons/IconToolFull.vue'
import { useAccountStore } from '@/stores/account'

const route = useRoute()
const accountStore = useAccountStore()
const avatarText = computed(() => accountStore.account.name.trim().slice(0, 1) || 'U')
</script>

<template>
  <a-layout has-sider class="h-full">
    <a-layout-sider :width="240" class="min-h-screen bg-gray-50 p-2 shadow-none">
      <div class="flex h-full flex-col justify-between rounded-lg bg-white px-2 py-4">
        <div>
          <router-link
            to="/home"
            class="mb-5 flex h-9 items-center gap-2 rounded-lg px-2 text-lg font-bold text-blue-700 transition-all hover:bg-blue-50"
          >
            <icon-app-full />
            LLMOps
          </router-link>
          <a-button type="primary" long class="mb-4 rounded-lg">
            <template #icon><icon-plus /></template>
            创建 AI 应用
          </a-button>

          <nav class="flex flex-col gap-2">
            <router-link
              to="/home"
              class="flex h-8 items-center gap-2 rounded-lg px-2 leading-8 text-gray-700 transition-all hover:bg-gray-200 hover:text-gray-900"
              active-class="bg-gray-100"
            >
              <icon-home-full v-if="route.path.startsWith('/home')" />
              <icon-home v-else />
              主页
            </router-link>
            <router-link
              to="/space/apps"
              class="flex h-8 items-center gap-2 rounded-lg px-2 leading-8 text-gray-700 transition-all hover:bg-gray-200 hover:text-gray-900"
              :class="{ 'bg-gray-100': route.path.startsWith('/space') }"
            >
              <icon-space-full v-if="route.path.startsWith('/space')" />
              <icon-space v-else />
              个人空间
            </router-link>
            <div class="px-2 text-sm text-gray-500">探索</div>
            <router-link
              to="/store/apps"
              class="flex h-8 items-center gap-2 rounded-lg px-2 leading-8 text-gray-700 transition-all hover:bg-gray-200 hover:text-gray-900"
              active-class="bg-gray-100"
            >
              <icon-app-full v-if="route.path.startsWith('/store/apps')" />
              <icon-app v-else />
              应用广场
            </router-link>
            <router-link
              to="/store/tools"
              class="flex h-8 items-center gap-2 rounded-lg px-2 leading-8 text-gray-700 transition-all hover:bg-gray-200 hover:text-gray-900"
              active-class="bg-gray-100"
            >
              <icon-tool-full v-if="route.path.startsWith('/store/tools')" />
              <icon-tool v-else />
              插件广场
            </router-link>
            <router-link
              to="/open"
              class="flex h-8 items-center gap-2 rounded-lg px-2 leading-8 text-gray-700 transition-all hover:bg-gray-200 hover:text-gray-900"
              active-class="bg-gray-100"
            >
              <icon-open-api-full v-if="route.path.startsWith('/open')" />
              <icon-open-api v-else />
              开放 API
            </router-link>
          </nav>
        </div>

        <a-dropdown position="tl">
          <div
            class="flex cursor-pointer items-center gap-2 rounded-lg p-2 transition-all hover:bg-gray-100"
          >
            <a-avatar :size="32" class="bg-blue-700 text-sm">{{ avatarText }}</a-avatar>
            <div class="min-w-0 flex flex-col">
              <div class="truncate text-sm text-gray-900">{{ accountStore.account.name }}</div>
              <div class="truncate text-xs text-gray-500">{{ accountStore.account.email }}</div>
            </div>
          </div>
          <template #content>
            <a-doption>
              <template #icon><icon-settings /></template>
              账号设置
            </a-doption>
            <a-doption>
              <template #icon><icon-poweroff /></template>
              退出登录
            </a-doption>
          </template>
        </a-dropdown>
      </div>
    </a-layout-sider>
    <a-layout-content class="h-screen min-w-0 overflow-hidden">
      <router-view />
    </a-layout-content>
  </a-layout>
</template>
