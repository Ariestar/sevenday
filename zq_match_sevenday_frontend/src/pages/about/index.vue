<template>
  <view class="about-page">
    <!-- 顶部导航 -->
    <view class="page-header">
      <view class="nav-bar">
        <view class="nav-left" @click="goBack">
          <text class="back-arrow">‹</text>
        </view>
        <text class="page-title">关于我们</text>
        <view class="nav-right"></view>
      </view>
    </view>

    <!-- 内容区域 -->
    <view class="content-area">
      <view class="logo-container">
        <image 
          src="/static/mine/about-us.png" 
          class="about-logo" 
          mode="aspectFit"
        />
      </view>
    </view>

    <!-- 底部导航栏 -->
    <CustomTabBar :current="3" />
  </view>
</template>

<script>
import CustomTabBar from '../../components/CustomTabBar.vue'

export default {
  components: {
    CustomTabBar
  },
  methods: {
    goBack() {
      uni.navigateBack({
        fail: () => {
          uni.reLaunch({ url: '/pages/mine/index' })
        }
      })
    }
  }
}
</script>

<style scoped>
.about-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #F7E8FE 0%, #FFFEFF 100%);
  padding-bottom: 112rpx; /* 为TabBar留出空间 */
}

/* 顶部导航 */
.page-header {
  background: linear-gradient(89.97deg, #A100FE 0.03%, #FDB9E7 99.97%);
  padding: 88rpx 0 40rpx 0;
}

.nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32rpx;
  height: 80rpx;
}

.nav-left {
  width: 80rpx;
  height: 80rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-arrow {
  font-size: 48rpx;
  color: #FFFFFF;
  font-weight: 300;
}

.page-title {
  font-size: 32rpx;
  color: #FFFFFF;
  font-weight: 500;
}

.nav-right {
  width: 80rpx;
}

/* 内容区域 */
.content-area {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60rpx 40rpx;
}

.logo-container {
  display: flex;
  align-items: center;
  justify-content: center;
}

.about-logo {
  max-width: 400rpx;
  max-height: 400rpx;
}
</style>