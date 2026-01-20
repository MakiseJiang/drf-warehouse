<script setup lang="ts">
import { ref, onMounted } from 'vue'
import http from '../http'
import { ElMessage } from 'element-plus'
import warehouses from '../config/warehouses.json'

// --- Types ---
interface Transaction {
  id: number
  transaction_type: 'IN' | 'OUT'
  quantity: number
  date: string
  material_name: string
  material_code: string
  remark?: string
  operator?: string
}

interface Material {
  id: number
  material_id: string
  name: string
  quantity: number
  warehouse?: string
}

interface NewMaterialForm {
  material_id: string
  name: string
  model_number: string
  category: string
  equipment: string
  warehouse: string
  shelf: string
  threshold: number
}

interface PendingItem {
  _key: number
  type: 'IN' | 'OUT'
  isNew: boolean
  materialId?: number // ID of existing material
  existingMaterialName?: string // For display
  newMaterialData?: NewMaterialForm // Data for new material
  quantity: number
  remark?: string
  operator?: string
}

// --- State ---
const activeTab = ref('new')
const loadingHistory = ref(false)
const history = ref<Transaction[]>([])
const historyPage = ref(1)
const historyTotal = ref(0)
const materials = ref<Material[]>([])

// Transaction Form State
const transType = ref<'IN' | 'OUT'>('IN')
const isNewMaterial = ref(false)
const selectedMaterialId = ref<number | null>(null)
const transQuantity = ref(1)
const operatorName = ref('')
const transactionRemark = ref('')
const submitting = ref(false)

// New Material Form State
const newMaterialForm = ref<NewMaterialForm>({
  material_id: '',
  name: '',
  model_number: '',
  category: '',
  equipment: '',
  warehouse: '',
  shelf: '',
  threshold: 1
})

// Pending List
const pendingList = ref<PendingItem[]>([])

// --- Actions ---

const fetchMaterials = async () => {
  try {
    const response = await http.get('/materials/?page_size=1000')
    materials.value = response.data.results
  } catch (error) {
    console.error('加载备品失败')
  }
}

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

const handleTypeChange = (val: 'IN' | 'OUT') => {
  if (val === 'OUT') {
    isNewMaterial.value = false
  }
}

const addToPending = () => {
  // Validation
  if (transType.value === 'IN' && isNewMaterial.value) {
    // Validate New Material Form
    const f = newMaterialForm.value
    // User required: Name, Model, Warehouse.
    // System required: Material ID, Category.
    if (!f.name || !f.model_number || !f.warehouse) {
      ElMessage.warning('请填写所有必填项 (ID, 名称, 型号, 类型, 仓库)')
      return
    }
    // Add to list
    pendingList.value.push({
      _key: Date.now(),
      type: 'IN',
      isNew: true,
      newMaterialData: { ...f },
      quantity: transQuantity.value,
      remark: transactionRemark.value,
      operator: operatorName.value
    })
    // Reset New Material Form essential fields
    newMaterialForm.value.material_id = ''
    newMaterialForm.value.name = ''
    newMaterialForm.value.model_number = ''
    // Keep category/warehouse as they might be reused? Or reset. Let's reset for safety.
    newMaterialForm.value.category = ''
    newMaterialForm.value.warehouse = ''
    newMaterialForm.value.equipment = ''
    newMaterialForm.value.shelf = ''
    newMaterialForm.value.threshold = 1
  } else {
    // Existing Material
    if (!selectedMaterialId.value) {
      ElMessage.warning('请选择备品')
      return
    }
    const mat = materials.value.find(m => m.id === selectedMaterialId.value)
    
    // Check stock for OUT
    if (transType.value === 'OUT' && mat && mat.quantity < transQuantity.value) {
      ElMessage.warning(`库存不足 (当前: ${mat.quantity})`)
      return
    }

    pendingList.value.push({
      _key: Date.now(),
      type: transType.value,
      isNew: false,
      materialId: selectedMaterialId.value,
      existingMaterialName: mat ? `${mat.material_id} - ${mat.name}` : 'Unknown',
      quantity: transQuantity.value,
      remark: transactionRemark.value,
      operator: operatorName.value
    })
    // Reset selection
    selectedMaterialId.value = null
  }
  
  // Reset common fields
  transQuantity.value = 1
  transactionRemark.value = ''
  // operatorName.value is NOT reset, convenient for batch entry
  ElMessage.success('已加入待提交列表')
}

const removeFromPending = (index: number) => {
  pendingList.value.splice(index, 1)
}

const submitBatch = async () => {
  if (pendingList.value.length === 0) {
    ElMessage.warning('请先添加待提交记录')
    return
  }

  submitting.value = true

  try {
    for (const item of pendingList.value) {
      let materialId = item.materialId

      // 1. If new material, create it first
      if (item.isNew && item.newMaterialData) {
        try {
            const createRes = await http.post('/materials/', {
            ...item.newMaterialData,
            quantity: 0 
            })
            materialId = createRes.data.id
        } catch (e) {
            console.error('Create material failed', e)
            throw new Error(`创建备品 ${item.newMaterialData.name} 失败，可能ID重复`)
        }
      }

      // 2. Create Transaction
      if (materialId) {
        await http.post('/transactions/', {
          material: materialId,
          transaction_type: item.type,
          quantity: item.quantity,
          remark: item.remark || '',
          operator: item.operator || ''
        })
      }
    }

    ElMessage.success('批量提交成功')
    pendingList.value = []
    fetchMaterials()
    fetchHistory()
    
  } catch (error: any) {
    console.error(error)
    ElMessage.error(error.message || '提交过程中发生错误')
    fetchMaterials()
    fetchHistory()
  } finally {
    submitting.value = false
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
        <div class="new-transaction-layout">
          <!-- Left: Input Form -->
          <div class="form-section">
            <el-form label-width="100px">
              <el-form-item label="操作类型">
                <el-radio-group v-model="transType" @change="handleTypeChange">
                  <el-radio-button label="IN">入库</el-radio-button>
                  <el-radio-button label="OUT">出库</el-radio-button>
                </el-radio-group>
              </el-form-item>

              <!-- New Material Toggle (Only for IN) -->
              <el-form-item v-if="transType === 'IN'" label="备品来源">
                <el-radio-group v-model="isNewMaterial">
                  <el-radio :label="false">已有备品</el-radio>
                  <el-radio :label="true">新备品</el-radio>
                </el-radio-group>
              </el-form-item>
              
              <!-- Existing Material Selector -->
              <template v-if="!isNewMaterial">
                <el-form-item label="选择备品">
                  <el-select 
                    v-model="selectedMaterialId" 
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
              </template>

              <!-- New Material Form -->
              <template v-else>
                <div class="new-material-form">
                  <div class="form-section-title">必填项</div>
                  <el-form-item label="名称" required>
                    <el-input v-model="newMaterialForm.name" placeholder="备品名称" />
                  </el-form-item>
                  <el-form-item label="型号" required>
                    <el-input v-model="newMaterialForm.model_number" placeholder="规格型号" />
                  </el-form-item>
                  <el-form-item label="仓库" required>
                    <el-select v-model="newMaterialForm.warehouse" placeholder="选择仓库" style="width: 100%">
                      <el-option v-for="wh in warehouses" :key="wh" :label="wh" :value="wh" />
                    </el-select>
                  </el-form-item>
                  
                  <div class="form-section-title" style="margin-top: 15px">选填项</div>
                  <el-form-item label="所属设备">
                    <el-input v-model="newMaterialForm.equipment" />
                  </el-form-item>
                  <el-form-item label="类型">
                    <el-input v-model="newMaterialForm.category" placeholder="如: 五金" />
                  </el-form-item>
                  
                  <el-form-item label="物料号" >
                    <el-input v-model="newMaterialForm.material_id" />
                  </el-form-item>
                  <el-form-item label="货架">
                    <el-input v-model="newMaterialForm.shelf" />
                  </el-form-item>
                  <el-form-item label="阈值">
                    <el-input-number v-model="newMaterialForm.threshold" :min="0" />
                  </el-form-item>
                </div>
              </template>

              <el-form-item label="数量" required>
                <el-input-number v-model="transQuantity" :min="1" style="width: 100%" />
              </el-form-item>

              <el-form-item label="操作人">
                <el-input v-model="operatorName" placeholder="请输入操作人姓名" />
              </el-form-item>
              
              <el-form-item label="备注">
                <el-input v-model="transactionRemark" type="textarea" :rows="2" placeholder="备注信息" />
              </el-form-item>

              <el-form-item>
                <el-button type="success" @click="addToPending" icon="Plus" plain>加入清单</el-button>
              </el-form-item>
            </el-form>
          </div>

          <!-- Right: Pending List -->
          <div class="list-section">
            <div class="list-header">
              <h3>待提交清单</h3>
              <el-button
                type="primary"
                @click="submitBatch"
                :disabled="pendingList.length === 0"
                :loading="submitting"
              >
                全部提交 ({{ pendingList.length }})
              </el-button>
            </div>
            
            <el-table :data="pendingList" border style="width: 100%; height: 500px; overflow-y: auto;">
              <el-table-column label="类型" width="70">
                <template #default="{ row }">
                  <el-tag :type="row.type === 'IN' ? 'success' : 'warning'" size="small">{{ row.type === 'IN' ? '入' : '出' }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="备品信息" min-width="150">
                <template #default="{ row }">
                  <div v-if="row.isNew">
                    <el-tag size="small" effect="plain">新</el-tag> 
                    {{ row.newMaterialData.material_id }} - {{ row.newMaterialData.name }}
                  </div>
                  <div v-else>
                    {{ row.existingMaterialName }}
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="quantity" label="数量" width="70" />
              <el-table-column prop="operator" label="操作人" width="80" />
              <el-table-column prop="remark" label="备注" />
              <el-table-column label="操作" width="60">
                <template #default="{ $index }">
                  <el-button type="danger" link icon="Delete" @click="removeFromPending($index)" />
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="历史记录" name="history">
        <el-table :data="history" v-loading="loadingHistory" style="width: 100%">
          <el-table-column prop="date" label="时间" width="160">
            <template #default="scope">
              {{ new Date(scope.row.date).toLocaleString() }}
            </template>
          </el-table-column>
          <el-table-column prop="transaction_type" label="类型" width="80">
            <template #default="scope">
              <el-tag :type="scope.row.transaction_type === 'IN' ? 'success' : 'warning'">
                {{ scope.row.transaction_type === 'IN' ? '入库' : '出库' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="material_code" label="备品ID" width="100" />
          <el-table-column prop="material_name" label="备品名称" width="120" />
          <el-table-column prop="quantity" label="数量" width="80" />
          <el-table-column prop="operator" label="操作人" width="100" />
          <el-table-column prop="remark" label="备注" />
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
.new-transaction-layout {
  display: flex;
  gap: 20px;
}
.form-section {
  flex: 1;
  max-width: 500px;
  border-right: 1px solid #eee;
  padding-right: 20px;
}
.list-section {
  flex: 1;
}
.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.new-material-form {
  border: 1px dashed #dcdfe6;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 18px;
  background-color: #fafafa;
}
.form-section-title {
  font-size: 12px;
  color: #909399;
  margin-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 5px;
}
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
@media (max-width: 768px) {
  .new-transaction-layout {
    flex-direction: column;
  }
  .form-section {
    border-right: none;
    border-bottom: 1px solid #eee;
    padding-right: 0;
    padding-bottom: 20px;
    max-width: 100%;
  }
}
</style>
