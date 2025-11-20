<template>
  <view class="checkin-detail-page">
    <TeamNameModal
      :visible="showTeamNameModal"
      @cancel="handleTeamNameCancel"
      @confirm="handleTeamNameConfirm"
    />

    <TeamCreatedModal
      :visible="showTeamCreatedModal"
      :teamName="currentTeamName"
      @close="handleTeamCreatedClose"
      @confirm="handleTeamCreatedConfirm"
    />

    <view v-if="hasTeam" class="checkin-content">
      <!-- 顶部背景区域 -->
      <view class="header-background">
        <view class="banner-background"></view>
        <view class="header-tabs">
          <view class="tab-item" @click="goToTeammateInfo">
            <text class="tab-text">队友信息</text>
          </view>
          <view class="tab-item">
            <text class="tab-text">组队打卡</text>
          </view>
        </view>
      </view>

      <!-- 主要内容区域 -->
      <view class="main-content">
        <!-- 进度区域：显示每天的任务完成进度 -->
        <view class="progress-section">
          <view class="progress-header">
            <text class="progress-label">进度</text>
            <text class="progress-text">{{ currentDayCompletedTasks }}/{{ allTasks.length }}</text>
          </view>
          <view class="progress-bar">
            <view class="progress-bg"></view>
            <view class="progress-fill" :style="{ width: dailyTaskProgressWidth }"></view>
          </view>
        </view>

        <!-- 20个任务横向滑动选择栏 -->
        <view class="task-scroll-section">
          <scroll-view 
            class="task-scroll-view" 
            scroll-x 
            :scroll-left="taskScrollLeft"
            :show-scrollbar="false"
          >
            <view class="task-scroll-container">
              <view 
                v-for="(task, index) in allTasks" 
                :key="task.taskId || index"
                class="task-circle"
                :class="{ 
                  selected: selectedTaskId === task.taskId,
                  completed: isTaskCompleted(task.taskId)
                }"
                @click="selectTask(task)"
              >
                <text class="circle-number">{{ index + 1 }}</text>
                <text class="circle-score">{{ getScoreDisplay(task.score) }}</text>
              </view>
            </view>
          </scroll-view>
          <view class="task-labels-scroll">
            <scroll-view 
              class="task-labels-scroll-view" 
              scroll-x 
              :scroll-left="taskScrollLeft"
              :show-scrollbar="false"
            >
              <view class="task-labels-container">
                <text 
                  v-for="(task, index) in allTasks" 
                  :key="task.taskId || index" 
                  class="task-label"
                >
                  {{ getTaskShortName(task.title || task.name) }}
                </text>
              </view>
            </scroll-view>
          </view>
        </view>

        <!-- 当前选中任务的名称和说明 -->
        <view v-if="selectedTask" class="selected-task-section">
          <text class="selected-task-name">{{ selectedTask.title || selectedTask.name }}</text>
          <text class="selected-task-description">{{ selectedTask.introduction || selectedTask.description || '' }}</text>
        </view>

        <!-- 当前选中任务的打卡记录列表 -->
        <view v-if="selectedTask" class="all-tasks-section">
          <text class="all-tasks-title">打卡记录</text>
          <view class="task-list">
            <view 
              v-for="day in 10" 
              :key="day"
              class="task-row"
              :class="[`status-${getDayStatus(selectedTask.taskId, day)}`]"
              @click="goToCheckinForDay(day)"
            >
              <view class="task-row-left">
                <view class="task-row-indicator" :class="[`status-${getDayStatus(selectedTask.taskId, day)}`]">
                  <text v-if="isDayCompleted(selectedTask.taskId, day)" class="indicator-check">✓</text>
                </view>
                <view class="task-row-texts">
                  <text class="task-row-day">第{{ day }}天</text>
                </view>
              </view>
              <text class="task-row-status" :class="[`status-${getDayStatus(selectedTask.taskId, day)}`]">
                {{ getDayStatusText(selectedTask.taskId, day) }}
              </text>
            </view>
          </view>
        </view>

        <!-- 打卡签到按钮 -->
        <view class="checkin-button-section">
          <view class="checkin-button" :class="{ disabled: isCheckinDisabled }" @click="handleCheckin">
            <text class="checkin-button-text">√ 打卡签到</text>
          </view>
        </view>
      </view>
    </view>
    <NoTeamState v-else />

    <!-- 底部导航栏 -->
    <CustomTabBar :current="1"></CustomTabBar>
  </view>
</template>

<script>
import CustomTabBar from '@/components/CustomTabBar.vue'
import TeamNameModal from '@/components/TeamNameModal.vue'
import TeamCreatedModal from '@/components/TeamCreatedModal.vue'
import NoTeamState from '@/components/NoTeamState.vue'
import { getMatchList, setTeamName } from '../../services/match'
import { getCheckinTasks, getMyCheckinList } from '../../services/checkin'

export default {
  components: {
    CustomTabBar,
    TeamNameModal,
    TeamCreatedModal,
    NoTeamState
  },
  data() {
    return {
      allTasks: [], // 20个任务列表
      selectedTaskId: null, // 当前选中的任务ID
      taskProgress: {}, // 每个任务的打卡进度 { taskId: { completedDays: [1,2,3], checkinRecords: [] } }
      dailyTaskProgress: {
        // 每天的任务完成情况 { day: 已完成任务数 }
        day1: 0,
        day2: 0,
        day3: 0,
        day4: 0,
        day5: 0,
        day6: 0,
        day7: 0,
        day8: 0,
        day9: 0,
        day10: 0,
        currentDay: 1 // 当前进行到第几天
      },
      taskScrollLeft: 0, // 任务滚动位置
      hasTeam: false,
      justCreatedTeam: false,
      currentTeamName: '',
      showTeamNameModal: false,
      showTeamCreatedModal: false
    }
  },
  computed: {
    selectedTask() {
      return this.allTasks.find(task => task.taskId === this.selectedTaskId) || null
    },
    selectedTaskCompletedDays() {
      if (!this.selectedTaskId) return 0
      const progress = this.taskProgress[this.selectedTaskId]
      return progress ? progress.completedDays.length : 0
    },
    currentDayCompletedTasks() {
      // 获取当前天数已完成的任务数
      const currentDay = this.dailyTaskProgress.currentDay
      const dayKey = `day${currentDay}`
      return this.dailyTaskProgress[dayKey] || 0
    },
    dailyTaskProgressWidth() {
      // 显示当前天数已完成任务数占总任务数的比例
      const completed = this.currentDayCompletedTasks
      const total = this.allTasks.length || 20
      const ratio = Math.min(completed, total) / total
      return `${Math.floor(ratio * 100)}%`
    },
    isCheckinDisabled() {
      return !this.hasTeam || !this.selectedTask
    }
  },
  onLoad() {
    this.checkTeamStatus()
    // 监听打卡更新事件
    uni.$on('checkin-updated', this.handleCheckinUpdate)
  },
  async onShow() {
    await this.checkTeamStatus()
    // 如果已有队伍，重新加载打卡数据以确保同步
    if (this.hasTeam) {
      await this.loadCheckinData()
    }
    // 触发TabBar更新，确保选中状态正确
    uni.$emit('tabbar-update')
  },
  onLoad() {
    this.checkTeamStatus()
    // 监听打卡更新事件
    uni.$on('checkin-updated', this.handleCheckinUpdate)
  },
  async onPullDownRefresh() {
    // 下拉刷新：重新加载所有数据
    console.log('🔄 下拉刷新打卡页面')
    await this.checkTeamStatus()
    if (this.hasTeam) {
      await this.loadCheckinData()
    }
    uni.stopPullDownRefresh()
  },
  onUnload() {
    // 移除事件监听
    uni.$off('checkin-updated', this.handleCheckinUpdate)
  },
  methods: {
    goToTeammateInfo() {
      if (!this.hasTeam) {
        uni.showToast({
          title: '请先完成组队',
          icon: 'none'
        })
        return
      }

      uni.navigateTo({
        url: '/pages/teammate-info/index',
        fail: (err) => {
          console.warn('跳转到队友信息页面失败:', err)
        }
      })
    },

    handleCheckin() {
      if (!this.selectedTask) {
        uni.showToast({
          title: '请先选择任务',
          icon: 'none'
        })
        return
      }
      
      // 天数固定为当天（当前进行到第几天）
      const currentDay = this.dailyTaskProgress.currentDay
      if (!currentDay || currentDay < 1 || currentDay > 10) {
        uni.showToast({
          title: '无法确定当前天数',
          icon: 'none'
        })
        return
      }
      
      // 检查该任务当天是否已完成
      if (this.isDayCompleted(this.selectedTask.taskId, currentDay)) {
        uni.showToast({
          title: '该任务今天已完成打卡',
          icon: 'none'
        })
        return
      }
      
      // 跳转到打卡提交页面，传递任务ID和当天天数
      uni.navigateTo({
        url: `/pages/checkin-submit/index?taskId=${this.selectedTask.taskId}&day=${currentDay}`
      })
    },

    async loadCheckinData() {
      if (!this.hasTeam) return
      await this.initializeTasks()
    },

    async checkTeamStatus() {
      // 先从本地存储读取，快速显示
      const hasTeamFromStorage = uni.getStorageSync('hasTeam')
      const teamName = uni.getStorageSync('teamName')
      const justCreatedTeam = uni.getStorageSync('justCreatedTeam')

      this.hasTeam = !!hasTeamFromStorage
      this.currentTeamName = teamName || ''
      this.justCreatedTeam = !!justCreatedTeam

      // 声明matchList变量，在try块外部也可以访问
      let matchList = null

      // 调用API获取最新的队伍状态
      try {
        const result = await getMatchList()
        console.log('获取匹配状态 (完整):', JSON.stringify(result, null, 2))
        
        // 处理不同的响应格式
        if (result && result.data) {
          matchList = result.data
          console.log('从result.data提取数据:', matchList)
        } else if (result && typeof result.isMatched !== 'undefined') {
          matchList = result
          console.log('result本身就是data:', matchList)
        }
        
        console.log('处理后的matchList:', matchList)
        console.log('isMatched:', matchList?.isMatched)
        console.log('matches:', matchList?.matches)
        console.log('team:', matchList?.team)
        
        if (matchList && matchList.isMatched === true) {
          // 更新本地存储和页面状态
          this.hasTeam = true
          uni.setStorageSync('hasTeam', true)
          
          if (matchList.team && matchList.team.name) {
            this.currentTeamName = matchList.team.name
            uni.setStorageSync('teamName', matchList.team.name)
          }
          
          // 如果有队友信息，也保存
          if (matchList.matches && matchList.matches.length > 0) {
            console.log('✅ 找到队友信息:', matchList.matches)
            // 保存队友信息到本地存储，供队友信息页面使用
            uni.setStorageSync('teammates', matchList.matches)
          } else {
            console.warn('⚠️ 已匹配但没有队友信息')
          }
        } else {
          console.log('ℹ️ 用户未匹配')
          // 如果没有队伍，清除本地存储
          this.hasTeam = false
          uni.removeStorageSync('hasTeam')
          uni.removeStorageSync('teamName')
          uni.removeStorageSync('justCreatedTeam')
          uni.removeStorageSync('teammates')
        }
      } catch (error) {
        console.error('获取匹配状态失败:', error)
        console.error('错误详情:', {
          message: error.message,
          errMsg: error.errMsg,
          errno: error.errno
        })
        // 如果API调用失败，使用本地存储的值
        // 开发阶段：如果是无效URL错误，使用本地存储
        if (error.errMsg?.includes('invalid url') || error.errno === 600009) {
          console.log('开发阶段：API未配置，使用本地存储')
        } else {
          // 其他错误，也使用本地存储，但记录日志
          console.warn('使用本地存储的队伍状态')
        }
      }

      // 处理新创建的队伍：只有队名为空时才显示创建队名弹窗
      if (this.justCreatedTeam && this.hasTeam) {
        // 检查队名是否已设置（从API返回的team.name或本地存储）
        const teamNameFromAPI = matchList?.team?.name
        const teamNameFromStorage = uni.getStorageSync('teamName')
        const hasTeamName = (teamNameFromAPI && teamNameFromAPI.trim()) || (teamNameFromStorage && teamNameFromStorage.trim())
        
        if (!hasTeamName) {
          // 队名未设置，显示创建队名弹窗
          this.showTeamNameModal = true
        } else {
          // 队名已设置，更新当前队名
          this.currentTeamName = teamNameFromAPI || teamNameFromStorage
        }
        uni.removeStorageSync('justCreatedTeam')
      } else if (this.hasTeam) {
        this.loadCheckinData()
      }
    },

    handleTeamNameCancel() {
      this.showTeamNameModal = false

      if (this.justCreatedTeam) {
        uni.showModal({
          title: '提示',
          content: '不创建队名将使用默认队名，确定吗？',
          success: (res) => {
            if (res.confirm) {
              this.currentTeamName = '默认队名'
              this.justCreatedTeam = false
              uni.setStorageSync('teamName', '默认队名')
              uni.setStorageSync('hasTeam', true)
              this.showTeamCreatedModal = true
              this.loadCheckinData()
            } else {
              this.showTeamNameModal = true
            }
          }
        })
      }
    },

    async handleTeamNameConfirm(teamName) {
      try {
        uni.showLoading({ title: '保存中...' })
        
        // 调用后端API保存队名
        const result = await setTeamName(teamName)
        console.log('队名保存成功:', result)
        
        uni.hideLoading()
        
        this.showTeamNameModal = false
        this.currentTeamName = teamName
        this.justCreatedTeam = false

        // 更新本地存储
        uni.setStorageSync('teamName', teamName)
        uni.setStorageSync('hasTeam', true)

        this.showTeamCreatedModal = true
        this.loadCheckinData()
      } catch (error) {
        uni.hideLoading()
        console.error('保存队名失败:', error)
        
        // 如果是因为队名已设置而失败，直接使用已有队名
        if (error.message && error.message.includes('不可二次更改')) {
          uni.showToast({
            title: '队名已设置，不可修改',
            icon: 'none'
          })
          this.showTeamNameModal = false
          // 重新获取队名
          this.checkTeamStatus()
        } else {
          uni.showToast({
            title: '保存队名失败，请重试',
            icon: 'none'
          })
        }
      }
    },

    handleTeamCreatedClose() {
      this.showTeamCreatedModal = false
      uni.navigateTo({
        url: '/pages/teammate-info/index',
        fail: (err) => {
          console.warn('跳转到队友信息页面失败:', err)
        }
      })
    },

    handleTeamCreatedConfirm() {
      this.showTeamCreatedModal = false
      this.justCreatedTeam = false
      this.loadCheckinData()
    },

    async initializeTasks() {
      try {
        console.log('📋 开始加载打卡任务数据...')
        
        // 从后端获取任务列表（应该有20个任务）
        const tasks = await getCheckinTasks()
        console.log('📋 获取到的任务列表:', tasks)
        
        if (!tasks || !Array.isArray(tasks) || tasks.length === 0) {
          console.warn('⚠️ 未获取到任务列表')
          return
        }
        
        // 初始化20个任务
        this.allTasks = tasks.map((task, index) => ({
          taskId: task.taskId || task.id || task.task_id,
          title: task.title || `任务${index + 1}`,
          introduction: task.introduction || task.description || '',
          score: task.score || 1, // 默认1分（⭐）
          name: task.title || `任务${index + 1}`,
          description: task.introduction || task.description || ''
        }))
        
        // 默认选择第一个任务
        if (this.allTasks.length > 0 && !this.selectedTaskId) {
          this.selectedTaskId = this.allTasks[0].taskId
        }
        
        // 加载打卡记录
        await this.loadCheckinRecords()
        
        console.log('✅ 任务列表已初始化:', this.allTasks)
      } catch (error) {
        console.error('❌ 加载打卡任务数据失败:', error)
      }
    },

    async loadCheckinRecords() {
      try {
        // 从后端获取已完成的打卡记录
        const checkinList = await getMyCheckinList()
        console.log('📋 获取到的打卡记录:', checkinList)
        
        // 初始化每个任务的进度
        this.allTasks.forEach(task => {
          if (!this.taskProgress[task.taskId]) {
            this.taskProgress[task.taskId] = {
              completedDays: [],
              checkinRecords: []
            }
          }
        })
        
        // 初始化每天的任务完成计数
        const dailyCount = {}
        for (let day = 1; day <= 10; day++) {
          dailyCount[day] = 0
        }
        
        // 处理打卡记录：按任务ID和天数组织
        if (checkinList && Array.isArray(checkinList)) {
          checkinList.forEach(post => {
            // post.task 可能是任务ID（整数）或任务对象
            const taskId = typeof post.task === 'object' ? (post.task?.id || post.task?.taskId) : post.task
            // post.day 是打卡的天数（1-10），如果没有day字段，需要从title中提取或使用默认值
            let day = post.day || post.task_day
            if (!day && post.title) {
              // 从title中提取天数，例如"第1天打卡"
              const match = post.title.match(/第(\d+)天/)
              if (match) {
                day = parseInt(match[1])
              }
            }
            
            if (taskId && day && day >= 1 && day <= 10) {
              if (!this.taskProgress[taskId]) {
                this.taskProgress[taskId] = {
                  completedDays: [],
                  checkinRecords: []
                }
              }
              
              // 记录打卡天数
              if (!this.taskProgress[taskId].completedDays.includes(day)) {
                this.taskProgress[taskId].completedDays.push(day)
                // 统计每天完成的任务数
                dailyCount[day] = (dailyCount[day] || 0) + 1
              }
              
              // 记录打卡详情
              this.taskProgress[taskId].checkinRecords.push({
                day,
                post
              })
              
              console.log(`✅ 记录打卡: taskId=${taskId}, day=${day}`)
            } else {
              console.warn(`⚠️ 打卡记录缺少必要字段: taskId=${taskId}, day=${day}`, post)
            }
          })
        }
        
        // 更新每天的任务完成进度
        this.dailyTaskProgress.day1 = dailyCount[1] || 0
        this.dailyTaskProgress.day2 = dailyCount[2] || 0
        this.dailyTaskProgress.day3 = dailyCount[3] || 0
        this.dailyTaskProgress.day4 = dailyCount[4] || 0
        this.dailyTaskProgress.day5 = dailyCount[5] || 0
        this.dailyTaskProgress.day6 = dailyCount[6] || 0
        this.dailyTaskProgress.day7 = dailyCount[7] || 0
        this.dailyTaskProgress.day8 = dailyCount[8] || 0
        this.dailyTaskProgress.day9 = dailyCount[9] || 0
        this.dailyTaskProgress.day10 = dailyCount[10] || 0
        
        // 计算当前进行到第几天（找到第一个未完成所有任务的天数）
        let currentDay = 1
        for (let day = 1; day <= 10; day++) {
          if (dailyCount[day] < this.allTasks.length) {
            currentDay = day
            break
          }
          if (day === 10 && dailyCount[10] >= this.allTasks.length) {
            currentDay = 10 // 全部完成
          }
        }
        this.dailyTaskProgress.currentDay = currentDay
        
        console.log('📋 任务进度:', this.taskProgress)
        console.log('📋 每天任务完成进度:', this.dailyTaskProgress)
      } catch (error) {
        console.error('❌ 加载打卡记录失败:', error)
      }
    },

    selectTask(task) {
      console.log('📌 选择任务:', task)
      this.selectedTaskId = task.taskId
      
      // 滚动到选中的任务位置
      const taskIndex = this.allTasks.findIndex(t => t.taskId === task.taskId)
      if (taskIndex >= 0) {
        // 计算滚动位置：每个任务圆圈宽度84rpx + 间距20rpx = 104rpx
        // 减去屏幕宽度的一半，使选中任务居中
        const circleWidth = 84 // rpx
        const gap = 20 // rpx
        const screenWidth = uni.getSystemInfoSync().windowWidth
        const scrollLeft = (taskIndex * (circleWidth + gap)) - (screenWidth / 2) + (circleWidth / 2)
        this.taskScrollLeft = Math.max(0, scrollLeft)
      }
    },

    isTaskCompleted(taskId) {
      // 检查任务是否已完成（10天全部完成）
      const progress = this.taskProgress[taskId]
      return progress && progress.completedDays.length === 10
    },

    getTaskShortName(fullName) {
      // 获取任务简短名称（用于显示在圆圈下方）
      if (!fullName) return ''
      // 移除星星符号，只保留文字部分
      const nameWithoutStars = fullName.replace(/⭐/g, '').trim()
      // 如果名称太长，截取前4个字符
      if (nameWithoutStars.length > 4) {
        return nameWithoutStars.substring(0, 4) + '...'
      }
      return nameWithoutStars
    },

    isDayCompleted(taskId, day) {
      const progress = this.taskProgress[taskId]
      return progress && progress.completedDays.includes(day)
    },

    getCurrentDay(taskId) {
      const progress = this.taskProgress[taskId]
      if (!progress || progress.completedDays.length === 0) {
        return 1 // 第一个未完成的天
      }
      // 找到第一个未完成的天
      for (let day = 1; day <= 10; day++) {
        if (!progress.completedDays.includes(day)) {
          return day
        }
      }
      return null // 全部完成
    },

    getDayStatus(taskId, day) {
      if (this.isDayCompleted(taskId, day)) {
        return 'completed'
      }
      const currentDay = this.getCurrentDay(taskId)
      if (currentDay === day) {
        return 'current'
      }
      return 'pending'
    },

    getDayStatusText(taskId, day) {
      const status = this.getDayStatus(taskId, day)
      const statusTextMap = {
        pending: '未开始',
        current: '进行中',
        completed: '已完成'
      }
      return statusTextMap[status] || '未开始'
    },

    goToCheckinForDay(day) {
      if (!this.selectedTask) {
        uni.showToast({
          title: '请先选择任务',
          icon: 'none'
        })
        return
      }
      
      // 检查是否已完成
      if (this.isDayCompleted(this.selectedTask.taskId, day)) {
        uni.showToast({
          title: '该天已完成打卡',
          icon: 'none'
        })
        return
      }
      
      // 跳转到打卡提交页面，传递任务ID和天数
      uni.navigateTo({
        url: `/pages/checkin-submit/index?taskId=${this.selectedTask.taskId}&day=${day}`
      })
    },

    getScoreDisplay(score) {
      // 根据分数显示星星：1分=⭐, 2分=⭐⭐, 3分=⭐⭐⭐
      if (!score) return '⭐'
      const scoreNum = Number(score)
      if (scoreNum === 1) return '⭐'
      if (scoreNum === 2) return '⭐⭐'
      if (scoreNum === 3) return '⭐⭐⭐'
      return `${score}分`
    },
    async handleCheckinUpdate(data) {
      console.log('📢 收到打卡更新事件:', data)
      // 重新加载打卡数据以确保数据同步（从后端获取最新状态）
      if (this.hasTeam) {
        await this.loadCheckinData()
      }
    }
  }
}
</script>

<style scoped>
/* 页面容器 */
.checkin-detail-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #F7E7FF 0%, #FFFFFF 100%);
  padding-bottom: 112rpx; /* 为底部导航栏留出空间 */
}

.checkin-content {
  min-height: 100vh;
}

/* 顶部背景区域 */
.header-background {
  position: relative;
  width: 100%;
  height: 156rpx; /* 对应78px */
}

.banner-background {
  position: absolute;
  width: 100%;
  height: 100%;
  background-image: url('/static/checkin/checkin-part2-banner-background.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  z-index: 1;
}

.header-tabs {
  position: absolute;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 54rpx; /* 对应10px 27px */
  z-index: 2;
}

.tab-item {
  width: 266rpx; /* 对应133px */
  height: 90rpx; /* 对应45px */
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20rpx 60rpx; /* 对应10px 30px */
  margin-top: 80rpx;
}

.tab-item.active {
  background: linear-gradient(180deg, #F7E8FE 0%, #F9ECFF 100%);
  border-radius: 90rpx; /* 对应45px */
  box-shadow: 0 4rpx 12rpx rgba(161, 0, 254, 0.3);
}

.tab-text {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 32rpx; /* 对应16px */
  line-height: 38rpx; /* 对应19px */
  color: #000000;
}

/* 主要内容区域 */
.main-content {
  padding: 40rpx 64rpx 0; /* 对应20px 32px 0 */
  padding-bottom: 200rpx; /* 为底部按钮预留空间 */
}

/* 进度区域 */
.progress-section {
  margin-bottom: 58rpx; /* 对应29px */
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx; /* 对应10px */
}

.progress-label {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 28rpx; /* 对应14px */
  line-height: 34rpx; /* 对应17px */
  color: #000000;
}

.progress-text {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 28rpx; /* 对应14px */
  line-height: 34rpx; /* 对应17px */
  color: #000000;
}

.progress-bar {
  position: relative;
  width: 100%;
  height: 20rpx; /* 对应10px */
  border-radius: 10rpx; /* 对应5px */
  overflow: hidden;
}

.progress-bg {
  position: absolute;
  width: 100%;
  height: 100%;
  background: #F6E2FF;
}

.progress-fill {
  position: absolute;
  height: 100%;
  background: linear-gradient(90deg, #FB90B1 0%, #EC2AD1 100%);
  transition: width 0.3s ease;
}

/* 任务横向滑动选择区域（20个任务） */
.task-scroll-section {
  margin-bottom: 52rpx; /* 对应26px */
}

.task-scroll-view {
  width: 100%;
  white-space: nowrap;
}

.task-scroll-container {
  display: inline-flex;
  gap: 20rpx; /* 对应10px */
  padding: 0 32rpx; /* 左右留出一些空间 */
}

.task-labels-scroll {
  margin-top: 24rpx; /* 对应12px */
}

.task-labels-scroll-view {
  width: 100%;
  white-space: nowrap;
}

.task-labels-container {
  display: inline-flex;
  gap: 20rpx; /* 对应10px */
  padding: 0 32rpx; /* 左右留出一些空间 */
}

.task-circle {
  width: 84rpx; /* 对应42px */
  height: 84rpx; /* 对应42px */
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 2rpx solid #83CCED; /* 对应1px */
  background: #FFFFFF;
  position: relative;
}

.task-circle.selected {
  border-color: #A100FE;
  border-width: 3rpx; /* 对应1.5px */
  background: linear-gradient(135deg, #F7E8FE 0%, #F9ECFF 100%);
}

.task-circle.completed {
  background: #00C92C;
  border-color: #00C92C;
}

.task-circle.completed.selected {
  background: #00C92C;
}

.circle-number {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 24rpx; /* 对应12px */
  line-height: 28rpx; /* 对应14px */
  color: #83CCED;
}

.circle-score {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 18rpx; /* 对应9px */
  line-height: 20rpx; /* 对应10px */
  color: #999999;
  margin-top: 2rpx;
}

.task-circle.selected .circle-number {
  color: #A100FE;
  font-weight: 600;
}

.task-circle.selected .circle-score {
  color: #A100FE;
}

.task-circle.completed .circle-number {
  color: #FFFFFF;
}

.task-circle.completed .circle-score {
  color: #FFFFFF;
}

/* 选中任务的名称和说明显示 */
.selected-task-section {
  margin-bottom: 40rpx;
  padding: 30rpx;
  background: #FFFFFF;
  border-radius: 16rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.selected-task-name {
  display: block;
  font-family: 'Inter';
  font-weight: 600;
  font-size: 32rpx; /* 对应16px */
  line-height: 38rpx; /* 对应19px */
  color: #A100FE;
  margin-bottom: 16rpx;
  text-align: center;
}

.selected-task-description {
  display: block;
  font-family: 'Inter';
  font-weight: 400;
  font-size: 28rpx; /* 对应14px */
  line-height: 40rpx; /* 对应20px */
  color: #666666;
  text-align: center;
}

/* 选中任务的10天打卡进度圆圈 */
.day-circles-section {
  margin-bottom: 52rpx; /* 对应26px */
}

.day-circle {
  width: 84rpx; /* 对应42px */
  height: 84rpx; /* 对应42px */
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2rpx solid #83CCED; /* 对应1px */
  background: #FFFFFF;
}

.day-circle.completed {
  background: #00C92C;
  border-color: #00C92C;
}

.day-circle.current {
  border-color: #A100FE;
  border-width: 3rpx; /* 对应1.5px */
}

.day-circle .circle-number {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 32rpx; /* 对应16px */
  line-height: 38rpx; /* 对应19px */
  color: #83CCED;
}

.day-circle.completed .circle-number {
  color: #FFFFFF;
}

.day-circle.current .circle-number {
  color: #A100FE;
}

.task-labels {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-start;
  gap: 20rpx; /* 对应10px，与circles-container的gap一致 */
}

.task-label {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 20rpx; /* 对应10px */
  line-height: 24rpx; /* 对应12px */
  color: #9094A6;
  width: 84rpx; /* 对应42px，与task-circle宽度一致 */
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 全部任务列表 */
.all-tasks-section {
  margin-bottom: 60rpx;
}

.all-tasks-title {
  font-family: 'Inter';
  font-weight: 600;
  font-size: 32rpx;
  line-height: 38rpx;
  color: #000000;
  margin-bottom: 32rpx;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.task-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #FFFFFF;
  border: 2rpx solid #E0C9FF;
  border-radius: 24rpx;
  padding: 24rpx 28rpx;
}

.task-row.status-current {
  border-color: transparent;
  background: linear-gradient(180deg, #F9E6FF 0%, #FDF2FF 100%);
  box-shadow: 0 16rpx 32rpx rgba(161, 0, 254, 0.12);
}

.task-row.status-completed {
  border-color: #00C92C;
  background: #F0FFF2;
}

.task-row-left {
  display: flex;
  align-items: center;
  gap: 24rpx;
}

.task-row-indicator {
  width: 32rpx;
  height: 32rpx;
  border-radius: 50%;
  border: 3rpx solid #BB48FE;
  display: flex;
  align-items: center;
  justify-content: center;
}

.task-row-indicator.status-pending {
  border-color: #D7C9F8;
}

.task-row-indicator.status-current {
  border-color: transparent;
  background: linear-gradient(180deg, #A100FE 0%, #FDB9E7 100%);
}

.task-row-indicator.status-completed {
  background: #00C92C;
  border-color: #00C92C;
}

.indicator-check {
  font-size: 20rpx;
  color: #FFFFFF;
  font-weight: 700;
}

.task-row-texts {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.task-row-day {
  font-family: 'Inter';
  font-weight: 600;
  font-size: 30rpx;
  line-height: 36rpx;
  color: #000000;
}

.task-row-name {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 26rpx;
  line-height: 32rpx;
  color: #6A6A6A;
}

.task-row-status {
  font-family: 'Inter';
  font-weight: 500;
  font-size: 26rpx;
  line-height: 32rpx;
  color: #9094A6;
}

.task-row-status.status-current {
  color: #A100FE;
}

.task-row-status.status-completed {
  color: #00C92C;
}

/* 打卡签到按钮 */
.checkin-button-section {
  display: flex;
  justify-content: center;
  margin-bottom: 40rpx; /* 对应20px */
}

.checkin-button {
  width: 320rpx; /* 对应160px */
  height: 94rpx; /* 对应47px */
  background: linear-gradient(90deg, #A100FE 0%, #FDB9E7 100%);
  border-radius: 180rpx; /* 对应90px */
  display: flex;
  align-items: center;
  justify-content: center;
}

.checkin-button.disabled {
  background: #E5D4FF;
}

.checkin-button.disabled .checkin-button-text {
  opacity: 0.6;
}

.checkin-button-text {
  font-family: 'Inter';
  font-weight: 700;
  font-size: 48rpx; /* 对应24px */
  line-height: 58rpx; /* 对应29px */
  color: #FFFFFF;
}
</style>
