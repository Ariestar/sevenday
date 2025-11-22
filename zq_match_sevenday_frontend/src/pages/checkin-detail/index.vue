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
        <!-- 进度区域 -->
        <view class="progress-section">
          <view class="progress-header">
            <text class="progress-label">进度</text>
            <text class="progress-text">{{ completedDays }}/{{ totalDays }}</text>
          </view>
          <view class="progress-bar">
            <view class="progress-bg"></view>
            <view class="progress-fill" :style="{ width: progressWidth }"></view>
          </view>
        </view>

        <!-- 任务进度圆圈 -->
        <view class="task-circles-section">
          <view class="circles-container">
            <view 
              v-for="(day, index) in taskDays" 
              :key="index"
              class="task-circle"
              :class="{ completed: day.completed, current: day.current }"
            >
              <text class="circle-number">{{ day.day }}</text>
            </view>
          </view>
          <view class="task-labels">
            <text v-for="(day, index) in taskDays" :key="index" class="task-label">TASK</text>
          </view>
        </view>

        <!-- 任务列表 -->
        <view class="all-tasks-section">
          <text class="all-tasks-title">十天任务</text>
          <view class="task-list">
            <view 
              v-for="(task, index) in allTasks" 
              :key="index"
              class="task-row"
              :class="[`status-${task.status}`]"
            >
              <view class="task-row-left">
                <view class="task-row-indicator" :class="[`status-${task.status}`]">
                  <text v-if="task.status === 'completed'" class="indicator-check">✓</text>
                </view>
                <view class="task-row-texts">
                  <text class="task-row-day">第{{ task.day }}天</text>
                  <text class="task-row-name">{{ task.name }}</text>
                </view>
              </view>
              <text class="task-row-status" :class="[`status-${task.status}`]">{{ task.statusText }}</text>
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
import CustomTabBar from '../../components/CustomTabBar.vue'
import TeamNameModal from '../../components/TeamNameModal.vue'
import TeamCreatedModal from '../../components/TeamCreatedModal.vue'
import NoTeamState from '../../components/NoTeamState.vue'

export default {
  components: {
    CustomTabBar,
    TeamNameModal,
    TeamCreatedModal,
    NoTeamState
  },
  data() {
    const taskConfigs = Array.from({ length: 7 }, (_, index) => ({
      day: index + 1,
      name: '早起锻炼',
      description: '晨跑三十分钟或健身操'
    }))

    return {
      taskConfigs,
      totalDays: taskConfigs.length,
      completedDays: 0,
      taskDays: taskConfigs.map((config, index) => ({
        day: config.day,
        completed: false,
        current: index === 0
      })),
      allTasks: [],
      hasTeam: false,
      justCreatedTeam: false,
      currentTeamName: '',
      showTeamNameModal: false,
      showTeamCreatedModal: false
    }
  },
  computed: {
    progressWidth() {
      if (!this.totalDays) return '0%'
      const ratio = Math.min(this.completedDays, this.totalDays) / this.totalDays
      return `${Math.floor(ratio * 100)}%`
    },
    currentTask() {
      return this.allTasks.find(task => task.status === 'current') || null
    },
    isCheckinDisabled() {
      return !this.hasTeam || !this.currentTask
    }
  },
  onLoad() {
    this.checkTeamStatus()
    // 监听打卡更新事件
    uni.$on('checkin-updated', this.handleCheckinUpdate)
  },
  onShow() {
    this.checkTeamStatus()
    // 触发TabBar更新，确保选中状态正确
    uni.$emit('tabbar-update')
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
      if (!this.hasTeam) {
        uni.showToast({
          title: '请先完成组队',
          icon: 'none'
        })
        return
      }

      if (this.isCheckinDisabled) {
        uni.showToast({
          title: '本周任务已全部完成',
          icon: 'none'
        })
        return
      }

      const currentTask = this.currentTask
      const completed = this.taskDays.filter(day => day.completed).map(day => day.day)
      const params = []
      if (currentTask) {
        params.push(`day=${currentTask.day}`)
      }
      if (completed.length) {
        params.push(`completed=${encodeURIComponent(JSON.stringify(completed))}`)
      }

      uni.navigateTo({
        url: `/pages/checkin-submit/index${params.length ? '?' + params.join('&') : ''}`,
        fail: (err) => {
          console.warn('跳转到打卡提交页面失败:', err)
          uni.showToast({
            title: '跳转失败，请稍后重试',
            icon: 'none'
          })
        }
      })
    },

    loadCheckinData() {
      if (!this.hasTeam) return
      this.initializeTasks()
      this.syncProgressFromTasks()
    },

    checkTeamStatus() {
      const hasTeamFromStorage = uni.getStorageSync('hasTeam')
      const teamName = uni.getStorageSync('teamName')
      const justCreatedTeam = uni.getStorageSync('justCreatedTeam')

      this.hasTeam = !!hasTeamFromStorage
      this.currentTeamName = teamName || ''
      this.justCreatedTeam = !!justCreatedTeam

      if (this.hasTeam) {
        // 如果刚创建了队伍且有队名，显示组队成功弹窗
        if (this.justCreatedTeam && this.currentTeamName) {
          this.showTeamCreatedModal = true
          uni.removeStorageSync('justCreatedTeam')
        }
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

    handleTeamNameConfirm(teamName) {
      this.showTeamNameModal = false
      this.currentTeamName = teamName
      this.justCreatedTeam = false

      uni.setStorageSync('teamName', teamName)
      uni.setStorageSync('hasTeam', true)

      this.showTeamCreatedModal = true
      this.loadCheckinData()
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

    initializeTasks() {
      if (!this.taskConfigs.length) return
      this.allTasks = this.taskConfigs.map((config, index) =>
        this.createTaskData(config, index === 0 ? 'current' : 'pending')
      )
    },

    createTaskData(taskConfig, status) {
      return {
        ...taskConfig,
        status,
        statusText: this.getStatusText(status)
      }
    },

    getStatusText(status) {
      const statusTextMap = {
        pending: '未开始',
        current: '进行中',
        completed: '已完成'
      }
      return statusTextMap[status] || '未开始'
    },

    syncProgressFromTasks() {
      const completedCount = this.allTasks.filter(task => task.status === 'completed').length
      const currentIndex = this.allTasks.findIndex(task => task.status === 'current')
      this.completedDays = Math.min(completedCount, this.totalDays)

      this.taskDays = this.taskConfigs.map((config, index) => ({
        day: config.day,
        completed: index < completedCount,
        current: index === currentIndex
      }))
    },
    handleCheckinUpdate(data) {
      if (data && data.day) {
        // 更新指定天数的任务状态为已完成
        const taskIndex = this.allTasks.findIndex(task => task.day === data.day)
        if (taskIndex !== -1) {
          this.allTasks[taskIndex].status = 'completed'
          this.allTasks[taskIndex].statusText = this.getStatusText('completed')
          
          // 更新下一个任务为当前任务
          const nextIndex = taskIndex + 1
          if (nextIndex < this.allTasks.length) {
            this.allTasks[nextIndex].status = 'current'
            this.allTasks[nextIndex].statusText = this.getStatusText('current')
          }
          
          // 同步进度
          this.syncProgressFromTasks()
        }
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

/* 任务圆圈区域 */
.task-circles-section {
  margin-bottom: 52rpx; /* 对应26px */
}

.circles-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 46rpx; /* 对应23px */
  margin-bottom: 24rpx; /* 对应12px */
  flex-wrap: nowrap; /* 防止换行 */
}

.task-circle {
  width: 64rpx; /* 缩小到64rpx */
  height: 64rpx; /* 缩小到64rpx */
  min-width: 64rpx; /* 防止被压缩 */
  min-height: 64rpx; /* 防止被压缩 */
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2rpx solid #83CCED; /* 对应1px */
  background: #FFFFFF;
  flex-shrink: 0; /* 防止在flex容器中被压缩 */
  box-sizing: border-box; /* 确保边框包含在尺寸内 */
}

.task-circle.completed {
  background: #00C92C;
  border-color: #00C92C;
}

.task-circle.current {
  border-color: #A100FE;
  border-width: 3rpx; /* 对应1.5px */
}

.circle-number {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 24rpx; /* 缩小字体以适应更小的圆圈 */
  line-height: 28rpx; /* 调整行高 */
  color: #83CCED;
}

.task-circle.completed .circle-number {
  color: #FFFFFF;
}

.task-circle.current .circle-number {
  color: #A100FE;
}

.task-labels {
  display: flex;
  justify-content: center;
  gap: 46rpx; /* 对应23px */
}

.task-label {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 24rpx; /* 对应12px */
  line-height: 30rpx; /* 对应15px */
  color: #9094A6;
  width: 64rpx; /* 调整为与圆圈相同的宽度 */
  text-align: center;
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
