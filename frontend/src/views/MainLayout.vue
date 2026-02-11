<script setup lang="ts">
import { useAuthStore } from '../stores/auth'
import { useRouter, useRoute } from 'vue-router'
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { Menu as IconMenu, List, Refresh, SwitchButton, Setting, Fold, Expand } from '@element-plus/icons-vue'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const isCollapse = ref(false)
const isMobile = ref(false)

const activeMenu = computed(() => route.path)

const handleLogout = () => {
  authStore.logout()
}

const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}

const checkMobile = () => {
  const isMobileView = window.innerWidth <= 768
  if (isMobileView !== isMobile.value) {
    isMobile.value = isMobileView
    if (isMobileView) {
      isCollapse.value = true
    }
  }
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapse ? '64px' : '240px'" class="aside transition-all">
      <div class="logo">
        <h3 v-if="!isCollapse">仓库管理系统</h3>
        <h3 v-else>WMS</h3>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="el-menu-vertical"
        router
        :collapse="isCollapse"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/">
          <el-icon><IconMenu /></el-icon>
          <template #title>仓库总览</template>
        </el-menu-item>
        <el-menu-item index="/inventory">
          <el-icon><List /></el-icon>
          <template #title>备品查询</template>
        </el-menu-item>
        <el-menu-item index="/transactions">
          <el-icon><Refresh /></el-icon>
          <template #title>出入库管理</template>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <template #title>系统设置</template>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-button link @click="toggleSidebar" class="toggle-btn">
            <el-icon :size="20">
              <Expand v-if="isCollapse" />
              <Fold v-else />
            </el-icon>
          </el-button>
        </div>
        <div class="header-content">
          <span class="username" v-if="!isMobile">欢迎您, 用户</span>
          <el-button type="danger" link @click="handleLogout">
            <el-icon><SwitchButton /></el-icon> <span v-if="!isMobile">退出登录</span>
          </el-button>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.layout-container {
  height: 100vh;
}
.aside {
  background-color: #304156;
  color: white;
  transition: width 0.3s;
  overflow: hidden;
}
.transition-all {
  transition: all 0.3s;
}
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #263445;
  white-space: nowrap;
  overflow: hidden;
}
.el-menu-vertical {
  border-right: none;
}
.header {
  background-color: #fff;
  border-bottom: 1px solid #dcdfe6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}
.header-left {
  display: flex;
  align-items: center;
}
.toggle-btn {
  font-size: 20px;
  cursor: pointer;
}
.header-content {
  display: flex;
  align-items: center;
  gap: 15px;
}
.username {
  font-size: 14px;
  color: #606266;
}

@media (max-width: 768px) {
  .header {
    padding: 0 10px;
  }
}
</style>
