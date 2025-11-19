<template>
  <view class="square-page">
    <!-- 顶部标题区 -->
    <view class="page-header">
      <view class="header-content">
        <!-- 圆形LOGO区域 -->
        <view class="logo-circle">
          <image src="/static/square/square-logo.png" class="square-logo" mode="widthFix" />
        </view>
        
        <!-- 主标题 -->
        <text class="main-title">相交遇见你</text>
        
        <!-- 副标题 -->
        <text class="sub-title">看看大家的打卡动态</text>
        
        <!-- 装饰线条和星星 -->
        <view class="decoration-line">
          <view class="line-left"></view>
          <image src="/static/square/line.png" class="star-icon" mode="widthFix" />
          <view class="line-right"></view>
        </view>
      </view>
    </view>

    <!-- 排序选择器暂时隐藏 -->
    <!-- <view class="sort-selector">
      <view 
        class="sort-option"
        :class="{ active: sortType === 'latest' }"
        @click="changeSortType('latest')"
      >
        <text class="sort-text">最新发布</text>
      </view>
      <view 
        class="sort-option"
        :class="{ active: sortType === 'comment' }"
        @click="changeSortType('comment')"
      >
        <text class="sort-text">最新评论</text>
      </view>
    </view> -->

    <!-- 打卡列表 -->
    <scroll-view 
      class="post-list" 
      scroll-y
      @scrolltolower="loadMore"
      enable-back-to-top
    >
      <view 
        v-for="post in postList" 
        :key="post.id" 
        class="post-card" 
        @click="goToDetail(post.id)"
      >
        <!-- 卡片内容区域 -->
        <view class="card-content">
          <!-- 队伍头像 -->
          <view class="team-avatars">
            <view class="avatar-wrapper avatar-1">
              <image 
                :src="post.avatar1 || '/static/square/user-icon.png'" 
                class="team-avatar" 
                mode="aspectFill"
                @error="handleImageError"
              />
            </view>
            <view class="avatar-wrapper avatar-2">
              <image 
                :src="post.avatar2 || '/static/square/user-icon.png'" 
                class="team-avatar" 
                mode="aspectFill"
                @error="handleImageError"
              />
            </view>
          </view>

          <!-- 队伍信息 -->
          <view class="team-info">
            <text class="team-name">{{ post.teamName || 'xxxx队' }}</text>
            <text class="checkin-day">第{{ post.day }}次打卡</text>
          </view>

          <!-- 点赞按钮（右上角） -->
          <view class="like-section-top" @click.stop="handleLike(post)">
            <image 
              :src="post.isLiked ? '/static/square/Liked-logo.png' : '/static/square/Like-logo.png'"
              class="like-icon-top" 
              mode="widthFix"
            />
            <text class="like-count-top">{{ post.likeCount || 12 }}</text>
          </view>

          <!-- 打卡内容区域 - 暂时隐藏 -->
          <!-- <view v-if="!post.images || post.images.length === 0" class="post-content-area">
            <text class="content-text">{{ post.content }}</text>
          </view> -->

          <!-- 图片展示已移除，简化页面逻辑 -->

          <!-- 互动区域 -->
          <view class="interaction-bar">
            <!-- 进度条 -->
            <view class="progress-section">
              <view class="progress-bg"></view>
              <view class="progress-fill" :style="{ width: `${(post.day / 10) * 100}%` }"></view>
            </view>
          </view>

          <!-- 右上角装饰 -->
          <view class="corner-deco corner-top-right"></view>

          <!-- 左下角装饰 -->
          <view class="corner-deco corner-bottom-left"></view>
        </view>
      </view>

      <!-- 加载状态 -->
      <view v-if="loading" class="loading-state">
        <text>加载中...</text>
      </view>

      <!-- 没有更多 -->
      <view v-if="!loading && !hasMore" class="end-state">
        <text>没有更多了</text>
      </view>

      <!-- 空状态 -->
      <EmptyState 
        v-if="!loading && postList.length === 0" 
        message="还没有人分享打卡动态" 
        desc="快去完成打卡并同步到广场吧~"
      />
    </scroll-view>
    
    <!-- 自定义 TabBar -->
    <CustomTabBar :current="2" />
  </view>
</template>

<script>
import EmptyState from '../../components/EmptyState.vue'
import CustomTabBar from '../../components/CustomTabBar.vue'
import { getSquareList, toggleLike } from '../../services/square'

export default {
  components: {
    CustomTabBar,
    EmptyState
  },
  data() {
    return {
      postList: [],
      allPosts: [], // 保存所有数据
      page: 1,
      pageSize: 20,
      loading: false,
      hasMore: true,
      sortType: 'latest' // 'latest' | 'comment'
    }
  },
  onLoad() {
    // 监听广场数据更新
    uni.$on('square-updated', this.handleSquareUpdate)
    // 初始化模拟数据（如果没有本地数据）
    this.initMockData()
  },
  onUnload() {
    // 移除事件监听
    uni.$off('square-updated', this.handleSquareUpdate)
  },
  onShow() {
    this.refreshData()
    // 触发TabBar更新，确保选中状态正确
    uni.$emit('tabbar-update')
  },
  onPullDownRefresh() {
    this.refreshData()
  },
  methods: {
    initMockData() {
      // 强制清理旧数据并重新初始化（用于更新头像路径）
      // const existingPosts = uni.getStorageSync('squarePosts') || []
      // if (existingPosts.length > 0) {
      //   return // 已有数据，不需要初始化
      // }
      
      // 创建模拟数据
      const mockPosts = [
        {
          id: 'mock-1',
          day: 1,
          taskName: '早起锻炼',
          content: '今天早上6点起床，在公园跑了5公里，感觉精神状态特别好！坚持就是胜利💪',
          images: [],
          teamName: '早起鸟队',
          createdAt: Date.now() - 2 * 60 * 60 * 1000, // 2小时前
          updatedAt: Date.now() - 2 * 60 * 60 * 1000,
          likeCount: 12,
          commentCount: 3,
          viewCount: 45,
          isLiked: false,
          comments: [],
          latestCommentTime: null,
          avatar1: '/static/square/user-icon.png',
          avatar2: '/static/square/user-icon.png'
        },
        {
          id: 'mock-2',
          day: 3,
          taskName: '健康饮食',
          content: '今天准备了营养丰富的早餐：燕麦粥配水果，还有一杯豆浆。健康生活从每一餐开始！',
          images: [],
          teamName: '健康生活队',
          createdAt: Date.now() - 5 * 60 * 60 * 1000, // 5小时前
          updatedAt: Date.now() - 5 * 60 * 60 * 1000,
          likeCount: 8,
          commentCount: 1,
          viewCount: 32,
          isLiked: true,
          comments: [],
          latestCommentTime: null,
          avatar1: '/static/square/user-icon.png',
          avatar2: '/static/square/user-icon.png'
        },
        {
          id: 'mock-3',
          day: 2,
          taskName: '阅读学习',
          content: '今天读了《高效能人士的七个习惯》第二章，收获很多。知识就是力量，学习永无止境📚',
          images: [],
          teamName: '学霸联盟',
          createdAt: Date.now() - 1 * 24 * 60 * 60 * 1000, // 1天前
          updatedAt: Date.now() - 1 * 24 * 60 * 60 * 1000,
          likeCount: 15,
          commentCount: 5,
          viewCount: 68,
          isLiked: false,
          comments: [],
          latestCommentTime: Date.now() - 3 * 60 * 60 * 1000, // 3小时前有评论
          avatar1: '/static/square/user-icon.png',
          avatar2: '/static/square/user-icon.png'
        }
      ]
      
      // 保存到本地存储
      uni.setStorageSync('squarePosts', mockPosts)
      console.log('已初始化模拟打卡数据')
    },
    async refreshData() {
      this.page = 1
      this.hasMore = true
      this.postList = []
      this.allPosts = []
      await this.loadData()
      uni.stopPullDownRefresh()
    },
    async loadData() {
      if (this.loading || !this.hasMore) return

      this.loading = true
      try {
        // 优先从本地存储获取数据
        const localPosts = uni.getStorageSync('squarePosts') || []
        let result = { list: [] }
        
        try {
          // 尝试获取服务端数据
          result = await getSquareList(this.page, this.pageSize)
        } catch (err) {
          console.warn('获取服务端数据失败，使用本地数据:', err)
        }
        
        // 合并本地数据和服务端数据
        const serverPosts = result.list || []
        const mergedPosts = [...localPosts, ...serverPosts]
        
        // 去重并排序
        const uniquePosts = this.removeDuplicates(mergedPosts)
        const sortedPosts = this.sortPosts(uniquePosts)
        
        if (this.page === 1) {
          this.allPosts = sortedPosts
          this.postList = sortedPosts.slice(0, this.pageSize)
        } else {
          const startIndex = (this.page - 1) * this.pageSize
          const endIndex = startIndex + this.pageSize
          this.postList.push(...sortedPosts.slice(startIndex, endIndex))
        }

        this.hasMore = this.postList.length < this.allPosts.length
        this.page++
      } catch (err) {
        console.error('加载广场列表失败:', err)
      } finally {
        this.loading = false
      }
    },
    removeDuplicates(posts) {
      const seen = new Set()
      return posts.filter(post => {
        if (seen.has(post.id)) {
          return false
        }
        seen.add(post.id)
        return true
      })
    },
    sortPosts(posts) {
      return posts.sort((a, b) => {
        if (this.sortType === 'latest') {
          // 按发布时间排序
          return (b.createdAt || 0) - (a.createdAt || 0)
        } else {
          // 按最新评论时间排序
          const aTime = a.latestCommentTime || a.createdAt || 0
          const bTime = b.latestCommentTime || b.createdAt || 0
          return bTime - aTime
        }
      })
    },
    changeSortType(type) {
      if (this.sortType === type) return
      
      this.sortType = type
      // 重新排序并刷新显示
      const sortedPosts = this.sortPosts([...this.allPosts])
      this.allPosts = sortedPosts
      this.page = 1
      this.postList = sortedPosts.slice(0, this.pageSize)
      this.hasMore = this.postList.length < this.allPosts.length
    },
    handleSquareUpdate() {
      // 广场数据更新时刷新列表
      this.refreshData()
    },
    loadMore() {
      if (!this.hasMore || this.loading) return
      
      const startIndex = this.postList.length
      const endIndex = startIndex + this.pageSize
      const morePosts = this.allPosts.slice(startIndex, endIndex)
      
      if (morePosts.length > 0) {
        this.postList.push(...morePosts)
        this.hasMore = this.postList.length < this.allPosts.length
      } else {
        this.hasMore = false
      }
    },
    async handleLike(post) {
      try {
        // 先更新本地状态
        const originalState = post.isLiked
        post.isLiked = !post.isLiked
        post.likeCount = post.isLiked ? (post.likeCount || 0) + 1 : Math.max((post.likeCount || 1) - 1, 0)
        
        // 更新本地存储
        this.updateLocalPost(post)
        
        try {
          // 尝试同步到服务器
          await toggleLike(post.id)
          
          uni.showToast({
            title: post.isLiked ? '点赞成功' : '取消点赞',
            icon: 'success',
            duration: 1000
          })
        } catch (err) {
          // 网络失败时回滚状态
          console.warn('网络点赞失败，已保存到本地:', err)
          post.isLiked = originalState
          post.likeCount = originalState ? (post.likeCount || 0) + 1 : Math.max((post.likeCount || 1) - 1, 0)
          this.updateLocalPost(post)
        }
      } catch (err) {
        console.error('点赞操作失败:', err)
      }
    },
    updateLocalPost(post) {
      const localPosts = uni.getStorageSync('squarePosts') || []
      const index = localPosts.findIndex(p => p.id === post.id)
      if (index !== -1) {
        localPosts[index] = { ...post }
        uni.setStorageSync('squarePosts', localPosts)
      }
    },
    goToDetail(postId) {
      uni.navigateTo({
        url: `/pages/square-detail/index?id=${postId}`
      })
    },
    handleImageError(e) {
      console.log('头像加载失败:', e)
      // 可以在这里设置默认头像或显示占位图
    }
  }
}
</script>

<style scoped>
.square-page {
  min-height: 100vh;
  background: #FDF8FF;
  overflow-y: scroll;
  padding-bottom: 120rpx; /* 为 TabBar 留出空间 */
}

/* 顶部标题区 - 调整间距 */
.page-header {
  position: relative;
  width: 100%;
  padding: 40rpx 20rpx 60rpx;
  background: #FDF8FF;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.header-content {
  position: relative;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* LOGO 圆形区域 */
.logo-circle {
  width: 136rpx;
  height: 136rpx;
  background: linear-gradient(139.18deg, #E602D7 1.8%, #F263C8 41.44%, #FFA4A6 70.26%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24rpx;
}

.square-logo {
  width: 60rpx;
  height: 60rpx;
}

/* 相交遇见你 - 主标题 */
.main-title {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 400;
  font-size: 52rpx;
  line-height: 62rpx;
  text-align: center;
  background: linear-gradient(270deg, #F25FA9 0%, #C253E3 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 16rpx;
}

/* 看看大家的打卡动态 - 副标题 */
.sub-title {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 400;
  font-size: 28rpx;
  line-height: 34rpx;
  text-align: center;
  color: #A70DFC;
  margin-bottom: 32rpx;
}

/* 装饰线条区域 */
.decoration-line {
  position: relative;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 20rpx;
}

/* 左侧线条 */
.line-left {
  flex: 1;
  max-width: 150rpx;
  height: 4rpx;
  background: #E0620D;
  margin-right: 20rpx;
}

/* 右侧线条 */
.line-right {
  flex: 1;
  max-width: 150rpx;
  height: 4rpx;
  background: #E0620D;
  margin-left: 20rpx;
}

/* 星星图标 */
.star-icon {
  width: 32rpx;
  height: 32rpx;
}

/* 排序选择 */
.sort-selector {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 80rpx;
  padding: 40rpx 20rpx;
  background: #FDF8FF;
}

.sort-option {
  padding: 12rpx 24rpx;
  border-radius: 32rpx;
  transition: all 0.2s;
}

.sort-option.active {
  background: rgba(167, 13, 252, 0.1);
}

.sort-text {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 400;
  font-size: 28rpx;
  line-height: 34rpx;
  color: #1F2635;
}

.sort-option.active .sort-text {
  color: #A70DFC;
  font-weight: 500;
}

/* 打卡列表 */
.post-list {
  flex: 1;
  padding: 20rpx 20rpx 0; 
  margin-top: 20rpx; /* 给头部留出空间 */
}

.post-card {
  position: relative;
  margin-bottom: 40rpx;
  box-sizing: border-box;
  width: 100%;
  background: #FFFFFF;
  border-radius: 24rpx; /* 更大的圆角 */
  padding: 40rpx;
  box-shadow: 0 8rpx 24rpx rgba(161, 0, 254, 0.08); /* 添加阴影效果 */
}

/* 卡片内容区域 */
.card-content {
  position: relative;
  width: 100%;
  min-height: 200rpx; /* 调整最小高度 */
  background: #FFFFFF;
  border-radius: 24rpx;
}

/* 队伍头像 */
.team-avatars {
  position: absolute;
  left: 5.1%;
  top: 13.38%;
  display: flex;
  align-items: center;
  z-index: 2;
}

.avatar-wrapper {
  position: relative;
}

.avatar-wrapper.avatar-1 {
  width: 48rpx;
  height: 48rpx;
}

.avatar-wrapper.avatar-2 {
  width: 48rpx;
  height: 48rpx;
  margin-left: -12rpx;
}

.team-avatar {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: #FFFFFF;
  border: 2rpx solid #FFFFFF;
  box-shadow: 0 4rpx 8rpx rgba(192, 192, 192, 0.25);
  object-fit: cover; /* 确保图片正确裁剪 */
}

/* 队伍信息 */
.team-info {
  position: absolute;
  left: 19.54%;
  top: 11.45%;
  display: flex;
  flex-direction: column;
}

.team-name {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 400;
  font-size: 28rpx;
  line-height: 34rpx;
  color: #5F0095;
  margin-bottom: 8rpx;
}

.checkin-day {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 400;
  font-size: 24rpx;
  line-height: 30rpx;
  color: #A70DFC;
}

/* 右上角点赞按钮 */
.like-section-top {
  position: absolute;
  right: 7.37%;
  top: 12.68%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  z-index: 3;
}

.like-icon-top {
  width: 24rpx;
  height: 24rpx;
}

.like-count-top {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 400;
  font-size: 16rpx;
  line-height: 20rpx;
  color: #A70DFC;
  text-align: center;
}

/* 打卡内容区域 */
.post-content-area {
  position: absolute;
  left: 4.25%;
  right: 7.37%;
  top: 53.52%;
  bottom: 12.68%;
  background: #FDF8FF;
  padding: 20rpx;
  border-radius: 8rpx;
}

.content-text {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 400;
  font-size: 28rpx;
  line-height: 40rpx;
  color: #000000;
  word-break: break-word;
}

/* 图片展示区域已移除 */

/* 互动区域 */
.interaction-bar {
  position: absolute;
  left: 8.5%;
  right: 9.63%;
  top: 73.94%;
  bottom: 19.01%;
  display: flex;
  align-items: center;
  z-index: 2;
}

/* 进度条 */
.progress-section {
  position: relative;
  width: 100%;
  height: 28rpx;
  border-radius: 14rpx;
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
  left: 0;
  height: 100%;
  background: linear-gradient(90deg, #FB90B1 0%, #EC2AD1 100%);
  transition: width 0.3s ease;
}

/* 圆角装饰 */
.corner-deco {
  position: absolute;
  background: #FDF8FF;
  z-index: 1;
  pointer-events: none;
}

.corner-top-right {
  top: 0;
  right: 0;
  width: 8.5%;
  height: 21.13%;
  border-bottom-left-radius: 100rpx;
  border-top-right-radius: 24rpx;
}

.corner-bottom-left {
  bottom: 0;
  left: 0;
  width: 8.5%;
  height: 21.13%;
  border-top-right-radius: 100rpx;
  border-bottom-left-radius: 24rpx;
  transform: rotate(180deg);
}

/* 加载和结束状态 */
.loading-state,
.end-state {
  padding: 60rpx 0;
  text-align: center;
  font-size: 28rpx;
  color: #9094A6;
}
</style>

