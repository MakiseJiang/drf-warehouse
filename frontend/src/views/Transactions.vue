<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import http from '../http'
import { ElMessage } from 'element-plus'

// --- Transaction History ---
interface Transaction {
  id: number
  transaction_type: 'IN' | 'OUT'
  quantity: number
  date: string
  material_name: string
  material_code: string
}

const history = ref<Transaction[]>([])
const loadingHistory = ref(false)
const historyPage = ref(1)
const historyTotal = ref(0)

const fetchHistory = async () => {
  loadingHistory.value = true
  try {
    const response = await http.get('/transactions/', {
      params: { page: historyPage.value }
    })
    history.value = response.data.results
    historyTotal.value = response.data.count
  } catch (error) {
    ElMessage.error('获取历史记录失败')
  } finally {
    loadingHistory.value = false
  }
}

const handlePageChange = (page: number) => {
  historyPage.value = page
  fetchHistory()
}

// --- New Transaction ---
const activeTab = ref('new')
const transactionForm = ref({
  type: 'IN',
  material_id: null as number | null,
  quantity: 1,
})
const materials = ref<any[]>([])

const fetchMaterials = async () => {
  try {
    const response = await http.get('/materials/?page_size=1000')
    materials.value = response.data.results
  } catch (error) {
    console.error('加载备品失败')
  }
}

const submitTransaction = async () => {
  if (!transactionForm.value.material_id) {
    ElMessage.warning('请选择备品')
    return
  }
  try {
    await http.post('/transactions/', {
      material: transactionForm.value.material_id,
      transaction_type: transactionForm.value.type,
      quantity: transactionForm.value.quantity
    })
    ElMessage.success('提交成功')
    // Reset form
    transactionForm.value.material_id = null
    transactionForm.value.quantity = 1
    // Refresh history
    fetchHistory()
  } catch (error) {
    ElMessage.error('提交失败')
  }
}

onMounted(() => {
  fetchMaterials()
  fetchHistory()
})
</script>

<template>
  <div class="transactions-container">
    <el-tabs v-model="activeTab" type="border-card">
      <el-tab-pane label="新建出入库" name="new">
        <el-form :model="transactionForm" label-width="120px" style="max-width: 500px">
          <el-form-item label="操作类型">
            <el-radio-group v-model="transactionForm.type">
              <el-radio-button label="IN">入库</el-radio-button>
              <el-radio-button label="OUT">出库</el-radio-button>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item label="选择备品">
            <el-select 
              v-model="transactionForm.material_id" 
              placeholder="请选择备品" 
              filterable
              style="width: 100%"
            >
              <el-option
                v-for="item in materials"
                :key="item.id"
                :label="`${item.material_id} - ${item.name} (库存: ${item.quantity})`"
                :value="item.id"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="数量">
            <el-input-number v-model="transactionForm.quantity" :min="1" />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="submitTransaction">提交</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="历史记录" name="history">
        <el-table :data="history" v-loading="loadingHistory" style="width: 100%">
          <el-table-column prop="date" label="时间" width="180">
            <template #default="scope">
              {{ new Date(scope.row.date).toLocaleString() }}
            </template>
          </el-table-column>
          <el-table-column prop="transaction_type" label="类型" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.transaction_type === 'IN' ? 'success' : 'warning'">
                {{ scope.row.transaction_type === 'IN' ? '入库' : '出库' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="material_code" label="备品ID" width="120" />
          <el-table-column prop="material_name" label="备品名称" />
          <el-table-column prop="quantity" label="数量" width="120" />
        </el-table>
        <div class="pagination">
          <el-pagination
            background
            layout="prev, pager, next"
            :total="historyTotal"
            :page-size="10"
            @current-change="handlePageChange"
          />
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<style scoped>
.transactions-container {
  padding: 20px;
}
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
