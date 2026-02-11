<script setup lang="ts">
import { ref, onMounted } from 'vue'
import http from '../http'
import { ElMessage, ElMessageBox } from 'element-plus'

const warehouses = ref<string[]>([])
const newWarehouse = ref('')
const loading = ref(false)

const fetchWarehouses = async () => {
  loading.value = true
  try {
    const response = await http.get('/settings/warehouses/')
    warehouses.value = response.data
  } catch (error) {
    ElMessage.error('加载仓库列表失败')
  } finally {
    loading.value = false
  }
}

const addWarehouse = async () => {
  if (!newWarehouse.value.trim()) return
  if (warehouses.value.includes(newWarehouse.value.trim())) {
    ElMessage.warning('该仓库已存在')
    return
  }
  
  const updated = [...warehouses.value, newWarehouse.value.trim()]
  try {
    await http.post('/settings/warehouses/', { warehouses: updated })
    warehouses.value = updated
    newWarehouse.value = ''
    ElMessage.success('添加成功')
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

const removeWarehouse = async (index: number) => {
  try {
    await ElMessageBox.confirm('确定要删除该仓库吗?', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const updated = [...warehouses.value]
    updated.splice(index, 1)
    
    await http.post('/settings/warehouses/', { warehouses: updated })
    warehouses.value = updated
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const clearZeroStock = async () => {
  try {
    await ElMessageBox.confirm('确定要清除所有库存为 0 的备品吗? 此操作不可恢复。', '警告', {
      confirmButtonText: '确定清除',
      cancelButtonText: '取消',
      type: 'error'
    })
    
    const response = await http.post('/settings/clear_zero_stock/')
    ElMessage.success(`操作成功，已清除 ${response.data.deleted_count} 条记录`)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

onMounted(() => {
  fetchWarehouses()
})
</script>

<template>
  <div class="settings-container">
    <el-card header="仓库列表管理" class="section-card">
      <div class="warehouse-input">
        <el-input 
          v-model="newWarehouse" 
          placeholder="输入新仓库名称" 
          @keyup.enter="addWarehouse"
          style="width: 300px; margin-right: 10px"
        />
        <el-button type="primary" @click="addWarehouse" icon="Plus">添加</el-button>
      </div>
      
      <div class="warehouse-list" v-loading="loading">
        <el-tag
          v-for="(wh, index) in warehouses"
          :key="index"
          closable
          size="large"
          @close="removeWarehouse(index)"
          style="margin: 5px"
        >
          {{ wh }}
        </el-tag>
        <div v-if="warehouses.length === 0" class="empty-text">暂无仓库数据</div>
      </div>
    </el-card>

    <el-card header="数据维护" class="section-card" style="margin-top: 20px">
      <div class="maintenance-item">
        <span>清除零库存备品</span>
        <p class="desc">删除所有库存数量小于或等于 0 的备品记录。</p>
        <el-button type="danger" @click="clearZeroStock">立即执行</el-button>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.settings-container {
  padding: 20px;
  max-width: 800px;
}
.warehouse-input {
  margin-bottom: 20px;
}
.empty-text {
  color: #909399;
  font-size: 14px;
  padding: 10px 0;
}
.maintenance-item {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: flex-start;
}
.desc {
  color: #606266;
  font-size: 14px;
  margin: 0;
}
</style>
