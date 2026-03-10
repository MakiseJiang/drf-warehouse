<script setup lang="ts">
defineOptions({ name: 'WarehouseInventory' })

import { ref, onMounted } from 'vue'
import http from '../http'
import { ElMessage } from 'element-plus'

interface Material {
  id: number
  name: string
  model_number: string
  usage: string
  warehouse: string
  shelf: string
  quantity: number
  threshold: number
}

const materials = ref<Material[]>([])
const loading = ref(false)
const searchQuery = ref('')

const fetchMaterials = async () => {
  loading.value = true
  try {
    const params: Record<string, string | number> = { page_size: 100 }
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    const response = await http.get('/materials/', { params })
    materials.value = response.data.results
  } catch {
    ElMessage.error('获取备品数据失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  fetchMaterials()
}

onMounted(() => {
  fetchMaterials()
})
</script>

<template>
  <div class="inventory-container">
    <div class="filter-bar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索 名称, 型号, 用途..."
        style="width: 300px"
        clearable
        @keyup.enter="handleSearch"
      >
        <template #append>
          <el-button @click="handleSearch" icon="Search" />
        </template>
      </el-input>
    </div>

    <el-table :data="materials" v-loading="loading" style="width: 100%" stripe border>
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="model_number" label="型号" width="160" />
      <el-table-column prop="usage" label="用途" width="150" />
      <el-table-column prop="warehouse" label="仓库" width="100" />
      <el-table-column prop="shelf" label="货架" width="100" />
      <el-table-column prop="quantity" label="库存" width="100" />

      <el-table-column label="状态" width="100">
        <template #default="scope">
          <el-tag v-if="scope.row.quantity < scope.row.threshold" type="danger">库存不足</el-tag>
          <el-tag v-else type="success">正常</el-tag>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<style scoped>
.inventory-container {
  padding: 20px;
}
.filter-bar {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}
</style>
