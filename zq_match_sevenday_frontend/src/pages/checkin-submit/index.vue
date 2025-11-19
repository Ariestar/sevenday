<template>
  <view class="submit-page">
    <view class="header">
      <view class="header-background"></view>
      <view class="header-content">
        <view class="back-button" @click="handleBack">
          <text class="back-icon">←</text>
        </view>
        <view class="header-info">
          <text class="header-title">组队打卡提交</text>
          <text v-if="selectedTask" class="header-subtitle">{{ selectedTask.name }}</text>
        </view>
      </view>
    </view>

    <scroll-view class="page-body" scroll-y>
      <!-- 任务选择条 -->
      <view class="task-selector" v-if="taskConfigs.length">
        <view class="task-selector-title">选择打卡任务</view>
        <view class="task-chip-list">
          <view
            v-for="task in taskConfigs"
            :key="task.day"
            class="task-chip"
            :class="{
              selected: task.day === selectedDay,
              completed: completedDays.includes(task.day)
            }"
            @click="selectTask(task.day)"
          >
            <text class="task-chip-number">{{ task.day }}</text>
            <text class="task-chip-label">TASK</text>
          </view>
        </view>
      </view>

      <!-- 未选择任务占位 -->
      <view v-if="!selectedTask" class="empty-state">
        <text class="empty-title">选择一个任务开始打卡吧~</text>
        <text class="empty-desc">请先在上方选择今日要完成的任务，然后填写打卡内容</text>
      </view>

      <!-- 已选择任务内容 -->
      <view v-else class="task-detail">
        <view class="task-card">
          <view class="task-meta">
            <image class="task-icon" src="/static/checkin/check-in-star.png" mode="widthFix" />
            <text class="task-name">{{ selectedTask.name }}</text>
          </view>

          <!-- 图片上传 -->
          <view class="form-section image-section">
            <text class="section-title">打卡图片</text>
            <view class="image-list">
              <view
                v-for="(img, index) in formData.images"
                :key="index"
                class="image-item"
              >
                <image :src="img" class="image-preview" mode="aspectFill" />
                <view class="image-remove" @click="deleteImage(index)">×</view>
              </view>
              <view
                v-if="formData.images.length < maxImages"
                class="image-uploader"
                @click="chooseImages"
              >
                <text class="uploader-icon">+</text>
                <text class="uploader-text">添加照片</text>
                <text class="uploader-tip">支持 jpg/png，小于 5M</text>
              </view>
            </view>
          </view>

          <!-- 打卡内容 -->
          <view class="form-section diary-section">
            <text class="section-title required">打卡日记</text>
            <view class="textarea-wrapper">
              <textarea
                v-model="formData.content"
                class="content-textarea"
                placeholder="分享今天的打卡内容和感悟..."
                placeholder-style="color:#8A8A8A;"
                maxlength="500"
                auto-height
              />
              <text class="textarea-count">{{ formData.content.length }} / 500</text>
            </view>
          </view>

          <view class="actions-row">
            <view class="switch-group">
              <text class="switch-label">同步到广场</text>
              <switch :checked="formData.syncToSquare" @change="toggleSync" color="#A100FE" />
            </view>
            <button
              class="submit-button"
              :loading="submitting"
              :disabled="submitDisabled"
              @click="handleSubmit"
            >提交</button>
          </view>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script>
import { submitCheckin } from '@/services/checkin'
import { ACTIVITY_DAYS } from '@/utils/constants'

const MAX_IMAGES = 9

export default {
  data() {
    const taskConfigs = Array.from({ length: 7 }, (_, index) => ({
      day: index + 1,
      name: '早起锻炼',
      description: '晨跑三十分钟或健身操'
    }))

    return {
      ACTIVITY_DAYS,
      taskConfigs,
      selectedDay: null,
      completedDays: [],
      formData: {
        content: '',
        images: [],
        syncToSquare: false
      },
      submitting: false,
      maxImages: MAX_IMAGES
    }
  },
  computed: {
    selectedTask() {
      return this.taskConfigs.find(task => task.day === this.selectedDay) || null
    },
    submitDisabled() {
      return !this.selectedTask || !this.formData.content.trim() || this.submitting
    }
  },
  onLoad(options) {
    if (options && options.day) {
      const dayNum = Number(options.day)
      if (!Number.isNaN(dayNum)) {
        this.selectedDay = dayNum
      }
    }

    if (options && options.completed) {
      try {
        const parsed = JSON.parse(decodeURIComponent(options.completed))
        if (Array.isArray(parsed)) {
          this.completedDays = parsed
        }
      } catch (e) {
        console.warn('解析完成任务失败:', e)
      }
    }
  },
  methods: {
    handleBack() {
      uni.navigateBack({ fail: () => uni.reLaunch({ url: '/pages/checkin-detail/index' }) })
    },
    selectTask(day) {
      this.selectedDay = this.selectedDay === day ? null : day
    },
    chooseImages() {
      const remaining = this.maxImages - this.formData.images.length
      uni.chooseImage({
        count: remaining,
        sizeType: ['compressed'],
        success: (res) => {
          const files = res.tempFilePaths || []
          this.formData.images = this.formData.images.concat(files).slice(0, this.maxImages)
        }
      })
    },
    deleteImage(index) {
      this.formData.images.splice(index, 1)
    },
    toggleSync(e) {
      this.formData.syncToSquare = !!e.detail.value
    },
    syncPostToSquare() {
      const posts = uni.getStorageSync('squarePosts') || []
      const now = Date.now()
      const teamName = uni.getStorageSync('teamName') || '我的队伍'
      
      const newPost = {
        id: `${now}`,
        day: this.selectedDay,
        taskName: this.selectedTask?.name || '',
        content: this.formData.content.trim(),
        images: [...this.formData.images],
        teamName,
        createdAt: now,
        updatedAt: now,
        likeCount: 0,
        commentCount: 0,
        viewCount: 0,
        isLiked: false,
        comments: [],
        latestCommentTime: null,
        avatar1: '/static/square/user-icon.png', // 默认头像
        avatar2: '/static/square/user-icon.png'
      }

      posts.unshift(newPost)
      uni.setStorageSync('squarePosts', posts)
      
      // 通知广场页面数据更新
      uni.$emit('square-updated')
    },
    async handleSubmit() {
      if (this.submitDisabled) {
        return
      }

      this.submitting = true
      try {
        await submitCheckin({
          day: this.selectedDay,
          content: this.formData.content.trim(),
          images: this.formData.images,
          syncToSquare: this.formData.syncToSquare
        })

        // 如果选择同步到广场，保存到本地存储
        if (this.formData.syncToSquare) {
          this.syncPostToSquare()
        }

        // 通知打卡页面更新进度
        uni.$emit('checkin-updated', { day: this.selectedDay })

        // 显示"打卡完成"弹窗
        uni.showModal({
          title: '打卡完成',
          content: '恭喜你完成今日打卡任务！',
          showCancel: false,
          confirmText: '知道了',
          success: () => {
            // 返回并刷新打卡页面
            uni.navigateBack({
              fail: () => {
                uni.reLaunch({ url: '/pages/checkin-detail/index' })
              }
            })
          }
        })
      } catch (error) {
        console.error('提交打卡失败:', error)
        uni.showToast({
          title: error?.message || '提交失败，请稍后重试',
          icon: 'none'
        })
      } finally {
        this.submitting = false
      }
    }
  }
}
</script>

<style scoped>
.submit-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, #F7E7FF 0%, #FFFFFF 100%);
}

.header {
  position: relative;
  height: 200rpx;
}

.header-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: linear-gradient(89.97deg, #A100FE 0.03%, #FDB9E7 99.97%);
}

.header-content {
  position: relative;
  display: flex;
  align-items: center;
  padding: 80rpx 40rpx 0;
}

.back-button {
  width: 72rpx;
  height: 72rpx;
  border-radius: 36rpx;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 24rpx;
}

.back-icon {
  font-size: 36rpx;
  color: #ffffff;
  font-weight: 600;
}

.header-info {
  display: flex;
  flex-direction: column;
}

.header-title {
  font-size: 36rpx;
  font-weight: 600;
  color: #ffffff;
}

.header-subtitle {
  margin-top: 8rpx;
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.85);
}

.page-body {
  flex: 1;
  padding: 0 40rpx;
  box-sizing: border-box;
  padding-bottom: 160rpx;
}

.task-selector {
  margin-top: 32rpx;
}

.task-selector-title {
  font-size: 30rpx;
  color: #1F2635;
  margin-bottom: 24rpx;
}

.task-chip-list {
  display: flex;
  justify-content: space-between;
}

.task-chip {
  width: 80rpx;
  height: 110rpx;
  border-radius: 24rpx;
  background: rgba(255, 255, 255, 0.5);
  border: 2rpx solid transparent;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.task-chip.selected {
  background: linear-gradient(180deg, #FDB9E7 0%, #A100FE 100%);
  border-color: #A100FE;
  box-shadow: 0 12rpx 28rpx rgba(161, 0, 254, 0.18);
}

.task-chip.completed {
  border-color: #00C92C;
}

.task-chip-number {
  font-size: 30rpx;
  font-weight: 600;
  color: #1F2635;
}

.task-chip.selected .task-chip-number {
  color: #ffffff;
}

.task-chip-label {
  margin-top: 8rpx;
  font-size: 20rpx;
  color: #9094A6;
}

.task-chip.selected .task-chip-label {
  color: rgba(255, 255, 255, 0.8);
}

.empty-state {
  margin-top: 120rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  color: #9094A6;
}

.empty-icon {
  width: 160rpx;
  margin-bottom: 32rpx;
}

.empty-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #1F2635;
  margin-bottom: 16rpx;
}

.empty-desc {
  font-size: 26rpx;
  line-height: 40rpx;
  color: #9094A6;
  width: 420rpx;
}

.task-detail {
  margin-top: 32rpx;
  padding-bottom: 60rpx;
}

.task-card {
  background: #ffffff;
  border-radius: 24rpx;
  padding: 32rpx;
  box-shadow: 0 20rpx 40rpx rgba(161, 0, 254, 0.06);
  display: flex;
  flex-direction: column;
  gap: 36rpx;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.task-icon {
  width: 36rpx;
  height: 36rpx;
}

.task-name {
  font-size: 36rpx;
  font-weight: 600;
  color: #1F2635;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.section-title {
  font-size: 30rpx;
  color: #1F2635;
}

.section-title.required::after {
  content: '*';
  color: #EC2AD1;
  margin-left: 8rpx;
}

.image-list {
  display: flex;
  flex-wrap: wrap;
  gap: 24rpx;
}

.image-item {
  position: relative;
  width: 210rpx;
  height: 210rpx;
  border-radius: 24rpx;
  overflow: hidden;
  box-shadow: 0 12rpx 24rpx rgba(0, 0, 0, 0.08);
}

.image-preview {
  width: 100%;
  height: 100%;
}

.image-remove {
  position: absolute;
  top: 12rpx;
  right: 12rpx;
  width: 44rpx;
  height: 44rpx;
  border-radius: 22rpx;
  background: rgba(0, 0, 0, 0.5);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
}

.image-uploader {
  width: 210rpx;
  height: 210rpx;
  border-radius: 24rpx;
  border: 2rpx dashed #DC9FFE;
  background: rgba(255, 255, 255, 0.6);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.uploader-icon {
  font-size: 48rpx;
  color: #A100FE;
  font-weight: 600;
}

.uploader-text {
  margin-top: 8rpx;
  font-size: 26rpx;
  color: #A100FE;
}

.uploader-tip {
  margin-top: 8rpx;
  font-size: 22rpx;
  color: #9094A6;
}

.textarea-wrapper {
  position: relative;
}

.content-textarea {
  width: 100%;
  min-height: 220rpx;
  border-radius: 24rpx;
  background: #ffffff;
  padding: 24rpx;
  font-size: 28rpx;
  color: #1F2635;
  box-shadow: 0 12rpx 24rpx rgba(161, 0, 254, 0.08);
}

.textarea-count {
  position: absolute;
  bottom: 24rpx;
  right: 24rpx;
  font-size: 24rpx;
  color: #9094A6;
}

.actions-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 32rpx;
  margin-top: 12rpx;
}

.switch-group {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.switch-label {
  font-size: 30rpx;
  font-weight: 600;
  color: #1F2635;
}

.submit-button {
  width: 220rpx;
  height: 86rpx;
  border-radius: 90rpx;
  font-size: 30rpx;
  font-weight: 600;
  color: #ffffff;
  background-image: linear-gradient(90deg, #A100FE 0%, #FDB9E7 100%);
  border: none;
}

.submit-button:disabled {
  background: #E2D4F5;
  color: #ffffff;
}

.submit-button::after {
  display: none;
}
</style>

