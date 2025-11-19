<template>
  <view class="square-detail-page">
    <!-- 顶部 Banner -->
    <view class="header-banner">
      <view class="header-gradient"></view>
      <view class="header-nav">
        <view class="back-section" @click="goBack">
          <view class="back-arrow">←</view>
          <text class="nav-title">打卡详情</text>
        </view>
      </view>
    </view>

    <scroll-view v-if="postData" class="detail-content" scroll-y enable-flex>
      <!-- 队伍信息 Card -->
      <view class="team-card">
        <view class="team-avatar-circle">
          <image 
            :src="postData.avatar1 || '/static/square/user-icon.png'" 
            class="avatar-image" 
            mode="aspectFill"
          />
        </view>
        <view class="team-info-section">
          <view class="team-name-text">{{ postData.teamName || 'xxxxxxxx小队' }}</view>
          <view class="task-number">TASK {{ postData.day }}</view>
        </view>
      </view>

      <!-- 任务 Card -->
      <view class="task-card">
        <view class="task-title">{{ postData.taskName || '早起锻炼' }}</view>
        <view class="checkin-date">打卡日期：{{ formatDate(postData.createdAt) }}</view>
      </view>

      <!-- 图片 Card -->
      <view v-if="postData.images && postData.images.length > 0" class="images-card">
        <view class="image-grid">
          <image 
            v-for="(img, index) in postData.images" 
            :key="index"
            :src="img" 
            class="checkin-image" 
            mode="aspectFill"
            @click="previewImage(postData.images, index)"
          />
        </view>
      </view>

      <!-- 文字 Card -->
      <view class="text-card">
        <view class="content-title">打卡文字内容</view>
        <view class="content-text">{{ postData.content }}</view>
      </view>

      <!-- 数据 Card -->
      <view class="stats-card">
        <view class="stats-text">
          点赞：{{ postData.likeCount || 12 }}　
          评论：{{ postData.commentCount || 5 }}　
          浏览：{{ postData.viewCount || 127 }}
        </view>
      </view>

      <!-- 交互按钮 Card -->
      <view class="action-buttons-card">
        <view class="like-button" @click="toggleLike">
          <image 
            :src="postData.isLiked ? '/static/square/Liked-logo.png' : '/static/square/detail-like.png'" 
            class="button-icon" 
            mode="aspectFit" 
          />
          <text class="button-text">点赞</text>
        </view>
        <view class="comment-button" @click="showCommentModal">
          <image src="/static/square/detail-comment.png" class="button-icon" mode="aspectFit" />
          <text class="button-text">评论</text>
        </view>
        <view class="share-button" @click="sharePost">
          <image src="/static/square/detail-share.png" class="button-icon" mode="aspectFit" />
          <text class="button-text">分享</text>
        </view>
      </view>
      
      <!-- 底部占位，为底部导航栏留出空间 -->
      <view class="bottom-placeholder"></view>
    </scroll-view>

    <!-- 底部导航栏 -->
    <CustomTabBar :current="2" />

    <!-- 评论弹窗 -->
    <view v-if="showComment" class="comment-modal" @touchmove.stop.prevent>
      <view class="modal-overlay" @click="hideCommentModal"></view>
      <view class="modal-content">
        <view class="modal-header">
          <text class="modal-title">写评论</text>
          <view class="close-button" @click="hideCommentModal">×</view>
        </view>
        <textarea
          v-model="commentContent"
          class="comment-textarea"
          placeholder="说说你的想法..."
          auto-focus
          maxlength="200"
        />
        <view class="modal-footer">
          <text class="char-count">{{ commentContent.length }}/200</text>
          <button 
            class="submit-button"
            :disabled="!commentContent.trim()"
            @click="submitComment"
          >发布</button>
        </view>
      </view>
    </view>

    <!-- 加载状态 -->
    <view v-if="loading" class="loading-overlay">
      <text class="loading-text">加载中...</text>
    </view>
  </view>
</template>

<script>
import { getSquareDetail, toggleLike } from '@/services/square'
import CustomTabBar from '../../components/CustomTabBar.vue'

export default {
  components: {
    CustomTabBar
  },
  data() {
    return {
      postId: '',
      postData: null,
      comments: [],
      loading: false,
      showComment: false,
      commentContent: ''
    }
  },
  onLoad(options) {
    if (options.id) {
      this.postId = options.id
      this.loadDetail()
      this.incrementViewCount()
    }
  },
  methods: {
    async loadDetail() {
      if (!this.postId) return

      this.loading = true
      try {
        // 先从本地存储查找
        const localPosts = uni.getStorageSync('squarePosts') || []
        let postData = localPosts.find(post => post.id === this.postId)

        if (!postData) {
          // 如果本地没有，尝试从服务器获取
          const result = await getSquareDetail(this.postId)
          postData = result.data
        }

        if (postData) {
          this.postData = postData
          this.comments = postData.comments || []
          
          // 如果没有图片数据，添加测试图片（方便测试显示效果）
          if (!this.postData.images || this.postData.images.length === 0) {
            this.postData.images = [
              '/static/square/user-icon.png',
              '/static/square/user-icon.png'
            ]
          }
          
          // 初始化点赞状态（如果不存在）
          if (this.postData.isLiked === undefined) {
            this.postData.isLiked = false
          }
        } else {
          uni.showToast({
            title: '未找到相关内容',
            icon: 'none'
          })
          setTimeout(() => {
            uni.navigateBack()
          }, 1500)
        }
      } catch (error) {
        console.error('加载详情失败:', error)
        uni.showToast({
          title: '加载失败',
          icon: 'none'
        })
      } finally {
        this.loading = false
      }
    },
    incrementViewCount() {
      if (!this.postData) return

      // 增加浏览量
      this.postData.viewCount = (this.postData.viewCount || 0) + 1
      this.updateLocalPost()
    },
    getImageGridClass(count) {
      if (count === 1) return 'grid-1'
      if (count === 2) return 'grid-2'  
      if (count === 3) return 'grid-3'
      if (count === 4) return 'grid-4'
      return 'grid-many'
    },
    formatTime(timestamp) {
      if (!timestamp) return ''
      
      const now = Date.now()
      const diff = now - timestamp
      const minute = 60 * 1000
      const hour = 60 * minute
      const day = 24 * hour

      if (diff < minute) {
        return '刚刚'
      } else if (diff < hour) {
        return `${Math.floor(diff / minute)}分钟前`
      } else if (diff < day) {
        return `${Math.floor(diff / hour)}小时前`
      } else {
        const date = new Date(timestamp)
        return `${date.getMonth() + 1}月${date.getDate()}日`
      }
    },
    formatDate(timestamp) {
      if (!timestamp) return ''
      const date = new Date(timestamp)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    },
    async toggleLike() {
      if (!this.postData) return

      try {
        const originalState = this.postData.isLiked
        const originalCount = this.postData.likeCount
        
        // 立即更新UI状态
        this.postData.isLiked = !this.postData.isLiked
        this.postData.likeCount = this.postData.isLiked 
          ? (this.postData.likeCount || 0) + 1 
          : Math.max((this.postData.likeCount || 1) - 1, 0)

        this.updateLocalPost()

        try {
          await toggleLike(this.postId)
          uni.showToast({
            title: this.postData.isLiked ? '点赞成功' : '取消点赞',
            icon: 'success',
            duration: 1000
          })
        } catch (err) {
          console.warn('网络点赞失败:', err)
          // 回滚状态
          this.postData.isLiked = originalState
          this.postData.likeCount = originalCount
          this.updateLocalPost()
          
          uni.showToast({
            title: '操作失败，请重试',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('点赞失败:', error)
        uni.showToast({
          title: '操作失败',
          icon: 'none'
        })
      }
    },
    updateLocalPost() {
      const localPosts = uni.getStorageSync('squarePosts') || []
      const index = localPosts.findIndex(p => p.id === this.postId)
      if (index !== -1) {
        localPosts[index] = { ...this.postData }
        uni.setStorageSync('squarePosts', localPosts)
      }
    },
    showCommentModal() {
      this.showComment = true
    },
    hideCommentModal() {
      this.showComment = false
      this.commentContent = ''
    },
    async submitComment() {
      if (!this.commentContent.trim()) return

      const newComment = {
        id: `comment_${Date.now()}`,
        content: this.commentContent.trim(),
        userName: '我',
        avatar: '/static/square/user-icon.png',
        createdAt: Date.now()
      }

      // 添加到评论列表
      this.comments.unshift(newComment)
      
      // 更新帖子数据
      this.postData.commentCount = (this.postData.commentCount || 0) + 1
      this.postData.comments = this.comments
      this.postData.latestCommentTime = Date.now()
      
      this.updateLocalPost()
      this.hideCommentModal()

      uni.showToast({
        title: '评论成功',
        icon: 'success'
      })
    },
    previewImage(images, current) {
      uni.previewImage({
        urls: images,
        current
      })
    },
    sharePost() {
      uni.showActionSheet({
        itemList: ['分享给好友', '分享到朋友圈'],
        success: (res) => {
          uni.showToast({
            title: res.tapIndex === 0 ? '分享给好友' : '分享到朋友圈',
            icon: 'success'
          })
        }
      })
    },
    goBack() {
      uni.navigateBack({
        fail: () => {
          uni.reLaunch({
            url: '/pages/square/index'
          })
        }
      })
    }
  }
}
</script>

<style scoped>
/* 页面整体样式 - 按照 Figma 设计 */
.square-detail-page {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100vh;
  background: linear-gradient(180deg, #F7E8FE 0%, #FFFEFF 100%);
}

/* 顶部 Banner */
.header-banner {
  position: relative;
  width: 100%;
  height: 186rpx; /* 93px * 2 */
}

.header-gradient {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 186rpx;
  background: linear-gradient(89.97deg, #A100FE 0.03%, #FDB9E7 99.97%);
}

.header-nav {
  position: relative;
  z-index: 2;
  padding: 60rpx 0 0 0;
}

.back-section {
  display: flex;
  align-items: center;
  padding-left: 54rpx;
  height: 80rpx;
}

.back-arrow {
  width: 16rpx;
  height: 33rpx;
  font-size: 32rpx;
  color: #FFFFFF;
  font-weight: 600;
  margin-right: 38rpx;
  line-height: 1;
}

.nav-title {
  font-family: 'Inter';
  font-size: 32rpx;
  font-weight: 400;
  color: #FFFFFF;
  line-height: 38rpx;
}

/* 详情内容区域 */
.detail-content {
  flex: 1;
  padding: 20rpx;
  height: calc(100vh - 186rpx - 112rpx); /* 减去顶部banner和底部导航栏的高度 */
  box-sizing: border-box;
}

/* 队伍信息 Card */
.team-card {
  width: calc(100% - 40rpx);
  height: 220rpx; /* 110px * 2 */
  margin: 20rpx 20rpx;
  background: #FFFFFF;
  border-radius: 32rpx; /* 16px * 2 */
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.25);
  display: flex;
  align-items: center;
  padding: 40rpx 50rpx;
  box-sizing: border-box;
}

.team-avatar-circle {
  width: 108rpx; /* 54px * 2 */
  height: 108rpx;
  border-radius: 50%;
  background: #D9D9D9;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 34rpx;
}

.avatar-image {
  width: 100%;
  height: 100%;
  border-radius: 50%;
}

.team-info-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.team-name-text {
  font-family: 'Inter';
  font-size: 32rpx; /* 16px * 2 */
  font-weight: 400;
  color: #000000;
  line-height: 38rpx;
  margin-bottom: 10rpx;
  text-align: left;
}

.task-number {
  font-family: 'Inter';
  font-size: 72rpx; /* 36px * 2 */
  font-weight: 700;
  color: #FF6F32;
  line-height: 88rpx;
  text-align: left;
}

/* 任务 Card */
.task-card {
  width: calc(100% - 40rpx);
  height: 160rpx; /* 80px * 2 */
  margin: 20rpx 20rpx;
  background: #FFFFFF;
  border-radius: 32rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.25);
  padding: 30rpx 52rpx;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.task-title {
  font-family: 'Inter';
  font-size: 44rpx; /* 22px * 2 */
  font-weight: 400;
  color: #000000;
  line-height: 54rpx;
  margin-bottom: 20rpx;
  text-align: left;
}

.checkin-date {
  font-family: 'Inter';
  font-size: 32rpx; /* 16px * 2 */
  font-weight: 400;
  color: #868686;
  line-height: 38rpx;
  text-align: left;
}

/* 图片 Card */
.images-card {
  width: calc(100% - 40rpx);
  min-height: 280rpx; /* 140px * 2 */
  margin: 20rpx 20rpx;
  background: #FFFFFF;
  border-radius: 32rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.25);
  padding: 40rpx;
  box-sizing: border-box;
}

.image-grid {
  display: flex;
  gap: 24rpx;
  flex-wrap: wrap;
}

.checkin-image {
  width: 200rpx; /* 100px * 2 */
  height: 200rpx;
  background: #D9D9D9;
  border-radius: 8rpx;
}

/* 文字 Card */
.text-card {
  width: calc(100% - 40rpx);
  min-height: 300rpx; /* 150px * 2 */
  margin: 20rpx 20rpx;
  background: #FFFFFF;
  border-radius: 32rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.25);
  padding: 40rpx 52rpx;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.content-title {
  font-family: 'Inter';
  font-size: 32rpx; /* 16px * 2 */
  font-weight: 400;
  color: #000000;
  line-height: 38rpx;
  margin-bottom: 30rpx;
  text-align: left;
}

.content-text {
  font-family: 'Inter';
  font-size: 28rpx; /* 14px * 2 */
  font-weight: 400;
  color: #000000;
  line-height: 40rpx;
  word-break: break-word;
  text-align: left;
  flex: 1;
}

/* 数据 Card */
.stats-card {
  width: calc(100% - 40rpx);
  height: 80rpx; /* 40px * 2 */
  margin: 20rpx 20rpx;
  background: #FFFFFF;
  border-radius: 32rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20rpx;
  box-sizing: border-box;
}

.stats-text {
  font-family: 'Inter';
  font-size: 32rpx; /* 16px * 2 */
  font-weight: 400;
  color: #000000;
  line-height: 38rpx;
  text-align: center;
}

/* 底部占位符 */
.bottom-placeholder {
  height: 80rpx; /* 为底部导航栏留出空间 */
}

/* 交互按钮 Card */
.action-buttons-card {
  width: calc(100% - 40rpx);
  height: 120rpx; /* 60px * 2 */
  margin: 20rpx 20rpx;
  background: #FFFFFF;
  border-radius: 32rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.25);
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 20rpx;
  box-sizing: border-box;
}

.like-button {
  width: 180rpx; /* 90px * 2 */
  height: 80rpx; /* 40px * 2 */
  background: #118ACB;
  border-radius: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
}

.comment-button,
.share-button {
  width: 120rpx; /* 60px * 2 */
  height: 80rpx; /* 40px * 2 */
  background: rgba(255, 255, 255, 0.8);
  border: 2rpx solid #E5E5E5;
  border-radius: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
}

.button-icon {
  width: 40rpx; /* 20px * 2 */
  height: 40rpx;
}

.button-text {
  font-family: 'Inter';
  font-size: 28rpx; /* 14px * 2 */
  font-weight: 400;
  line-height: 34rpx;
}

.like-button .button-text {
  color: #FFFFFF;
}

.comment-button .button-text,
.share-button .button-text {
  color: #333333;
}

/* 评论弹窗 */
.comment-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  display: flex;
  align-items: flex-end;
}

.modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
}

.modal-content {
  position: relative;
  width: 100%;
  background: #FFFFFF;
  border-radius: 24rpx 24rpx 0 0;
  padding: 32rpx;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24rpx;
}

.modal-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #000000;
}

.close-button {
  font-size: 48rpx;
  color: #9094A6;
  line-height: 1;
}

.comment-textarea {
  width: 100%;
  min-height: 200rpx;
  border-radius: 16rpx;
  background: #F5F5F5;
  padding: 16rpx;
  font-size: 28rpx;
  color: #000000;
  margin-bottom: 24rpx;
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.char-count {
  font-size: 24rpx;
  color: #9094A6;
}

.submit-button {
  width: 120rpx;
  height: 64rpx;
  border-radius: 32rpx;
  background: linear-gradient(90deg, #A100FE 0%, #FDB9E7 100%);
  color: #FFFFFF;
  font-size: 28rpx;
  border: none;
}

.submit-button:disabled {
  background: #E5D4FF;
}

.submit-button::after {
  display: none;
}

/* 加载状态 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.loading-text {
  font-size: 28rpx;
  color: #666666;
}
</style>
