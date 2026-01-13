<script setup lang="ts">
import { ref, onMounted } from 'vue'
import http from '../http'
import { ElMessage } from 'element-plus'

interface Material {
  id: number
  material_id: string
  name: string
  category: string
  equipment: string
  warehouse: string
  shelf: string
  quantity: number
  threshold: number
}

const materials = ref<Material[]>([])
const loading = ref(false)
const searchQuery = ref('')
const categoryFilter = ref('')
const equipmentFilter = ref('')

const fetchMaterials = async () => {
  loading.value = true
  try {
    const params: any = { page_size: 100 } // Get all for client side filtering or use server search
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    const response = await http.get('/materials/', { params })
    materials.value = response.data.results
  } catch (error) {
    ElMessage.error('获取备品数据失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  fetchMaterials()
}

const updateStock = async (row: Material) => {
  try {
    await http.patch(`/materials/${row.id}/`, { quantity: row.quantity })
    ElMessage.success('库存更新成功')
  } catch (error) {
    ElMessage.error('库存更新失败')
    fetchMaterials() // Revert
  }
}

const updateThreshold = async (row: Material) => {
  try {
    await http.patch(`/materials/${row.id}/`, { threshold: row.threshold })
    ElMessage.success('阈值更新成功')
  } catch (error) {
    ElMessage.error('阈值更新失败')
    fetchMaterials() // Revert
  }
}

const deleteMaterial = async (id: number) => {
  try {
    await http.delete(`/materials/${id}/`)
    ElMessage.success('备品删除成功')
    fetchMaterials()
  } catch (error) {
    ElMessage.error('备品删除失败')
  }
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
        placeholder="搜索 ID, 名称, 类型..."
        style="width: 300px"
        clearable
        @keyup.enter="handleSearch"
      >
        <template #append>
          <el-button @click="handleSearch" icon="Search" />
        </template>
      </el-input>
      <!-- Additional client-side filters could be added here if not supported by backend fully -->
    </div>

    <el-table :data="materials" v-loading="loading" style="width: 100%" stripe border>
      <el-table-column prop="material_id" label="备品ID" width="100" />
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="category" label="类型" width="120" />
      <el-table-column prop="equipment" label="所属设备" width="120" />
      <el-table-column prop="warehouse" label="仓库" width="100" />
      <el-table-column prop="shelf" label="货架" width="100" />
      
      <el-table-column label="库存" width="150">
        <template #default="scope">
          <el-input-number 
            v-model="scope.row.quantity" 
            :min="0" 
            size="small"
            @change="updateStock(scope.row)"
          />
        </template>
      </el-table-column>

      <el-table-column label="告警阈值" width="150">
        <template #default="scope">
          <el-input-number 
            v-model="scope.row.threshold" 
            :min="0" 
            size="small"
            @change="updateThreshold(scope.row)"
          />
        </template>
      </el-table-column>

      <el-table-column label="状态" width="100">
        <template #default="scope">
          <el-tag v-if="scope.row.quantity < scope.row.threshold" type="danger">库存不足</el-tag>
          <el-tag v-else type="success">正常</el-tag>
        </template>
      </el-table-column>

      <el-table-column label="操作" width="100" fixed="right">
        <template #default="scope">
          <el-popconfirm title="确定要删除吗?" @confirm="deleteMaterial(scope.row.id)">
            <template #reference>
              <el-button type="danger" link size="small">删除</el-button>
            </template>
          </el-popconfirm>
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
