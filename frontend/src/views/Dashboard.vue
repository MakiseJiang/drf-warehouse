<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import http from '../http'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import VChart, { THEME_KEY } from 'vue-echarts'

use([
  CanvasRenderer,
  PieChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

interface Material {
  id: number
  name: string
  usage: string
  quantity: number
  threshold: number
}

interface Transaction {
  id: number
  transaction_type: string
  material_name: string
  quantity: number
  date: string
}

const materials = ref<Material[]>([])
const recentTransactions = ref<Transaction[]>([])
const loading = ref(false)

// Fetch Data
const fetchData = async () => {
  loading.value = true
  try {
    // Fetch all materials for stats (assuming dataset is small enough for client-side aggregation)
    const matResponse = await http.get('/materials/?page_size=1000')
    materials.value = matResponse.data.results

    // Fetch recent transactions
    const transResponse = await http.get('/transactions/?page_size=10')
    recentTransactions.value = transResponse.data.results
  } catch (error) {
    console.error('获取仪表盘数据失败', error)
  } finally {
    loading.value = false
  }
}

// Low Stock Items
const lowStockItems = computed(() => {
  return materials.value.filter(m => m.quantity < m.threshold)
})

// Chart 1: Inventory by Usage
const usageOption = computed(() => {
  const usageMap = new Map<string, number>()
  materials.value.forEach(m => {
    const key = m.usage || '未指定'
    const count = usageMap.get(key) || 0
    usageMap.set(key, count + m.quantity)
  })

  const data = Array.from(usageMap.entries()).map(([name, value]) => ({ name, value }))

  return {
    title: { text: '库存用途占比', left: 'center' },
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [
      {
        name: '数量',
        type: 'pie',
        radius: '50%',
        data: data,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
})

// Chart 2: Top 5 Stock Items
const topStockOption = computed(() => {
  const sorted = [...materials.value].sort((a, b) => b.quantity - a.quantity).slice(0, 5)
  return {
    title: { text: '库存量 Top 5', left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: sorted.map(m => m.name) },
    yAxis: { type: 'value' },
    series: [
      {
        data: sorted.map(m => m.quantity),
        type: 'bar',
        itemStyle: { color: '#409EFF' }
      }
    ]
  }
})

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="dashboard-container" v-loading="loading">
    <el-row :gutter="20">
      <!-- Stats Cards -->
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <template #header>备品总数</template>
          <div class="stat-value">{{ materials.length }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card alert-card">
          <template #header>库存告警</template>
          <div class="stat-value danger">{{ lowStockItems.length }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <template #header>库存总量</template>
          <div class="stat-value">{{ materials.reduce((acc, curr) => acc + curr.quantity, 0) }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card>
          <v-chart class="chart" :option="usageOption" autoresize />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <v-chart class="chart" :option="topStockOption" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="list-row">
      <el-col :span="12">
        <el-card header="库存告警列表">
          <el-table :data="lowStockItems" style="width: 100%" height="300">
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="quantity" label="库存" width="80" />
            <el-table-column prop="threshold" label="阈值" width="80" />
            <el-table-column label="状态">
              <template #default>
                <el-tag type="danger" size="small">库存不足</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card header="最近出入库记录">
          <el-table :data="recentTransactions" style="width: 100%" height="300">
            <el-table-column prop="date" label="时间" width="160">
              <template #default="scope">
                {{ new Date(scope.row.date).toLocaleDateString() }} {{ new Date(scope.row.date).toLocaleTimeString() }}
              </template>
            </el-table-column>
            <el-table-column prop="material_name" label="备品" />
            <el-table-column label="操作" width="100">
              <template #default="scope">
                <el-tag :type="scope.row.transaction_type === 'IN' ? 'success' : 'warning'" size="small">
                  {{ scope.row.transaction_type === 'IN' ? '入库' : '出库' }}
                </el-tag>
                {{ scope.row.quantity }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.dashboard-container {
  padding: 20px;
}
.stat-card {
  text-align: center;
}
.stat-value {
  font-size: 24px;
  font-weight: bold;
}
.danger {
  color: #f56c6c;
}
.alert-card :deep(.el-card__header) {
  background-color: #fef0f0;
  color: #f56c6c;
}
.chart-row {
  margin-top: 20px;
}
.chart {
  height: 300px;
}
.list-row {
  margin-top: 20px;
}
</style>
