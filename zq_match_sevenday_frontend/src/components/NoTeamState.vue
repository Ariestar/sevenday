<template>
  <view class="no-team-state">
    <!-- 顶部渐变背景 -->
    <view class="top-gradient-bg"></view>
    
    <!-- 顶部导航栏 -->
    <view class="page-header">
      <view class="header-tabs">
        <view class="header-tab disabled">
          <text class="tab-text">队友信息</text>
        </view>
        <view class="header-tab active">
          <text class="tab-text">组队打卡</text>
        </view>
      </view>
    </view>

    <!-- 内容区域 -->
    <view class="content-container">
      <!-- 提示图片 -->
      <view class="illustration-section">
        <image class="no-match-image" src="/static/checkin/check-in-donot-match.png" mode="aspectFit"></image>
      </view>
      
      <!-- 提示文字 -->
      <view class="message-section">
        <text class="main-message">你还没有队友哦</text>
        <text class="sub-message">快去报名匹配找到你的搭档吧！</text>
      </view>
      
      <!-- 操作按钮 -->
      <view class="action-section">
        <view class="goto-signup-btn" @click="goToSignup">
          <text class="btn-text">前往报名</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  methods: {
    goToSignup() {
      uni.switchTab({
        url: '/pages/signup/index',
        fail: (err) => {
          console.warn('跳转到报名页面失败:', err)
          uni.reLaunch({
            url: '/pages/signup/index'
          })
        }
      })
    }
  }
}
</script>

<style scoped>
.no-team-state {
  position: relative;
  width: 100%;
  height: 100vh;
  background: linear-gradient(180deg, #F7E7FF 0%, #FFFFFF 100%);
}

/* 顶部渐变背景 */
.top-gradient-bg {
  position: absolute;
  width: 100%;
  height: 246rpx; /* 对应123px */
  left: 0;
  top: -14rpx; /* 对应-7px */
  background: linear-gradient(89.97deg, #A100FE 0%, #FDB9E7 99.96%);
  z-index: 1;
}

/* 顶部导航栏 */
.page-header {
  position: relative;
  z-index: 10;
  padding: 100rpx 0 40rpx; /* 对应50px 0 20px */
}

.header-tabs {
  display: flex;
  justify-content: center;
  gap: 120rpx; /* 对应60px */
}

.header-tab {
  position: relative;
  padding: 20rpx 40rpx; /* 对应10px 20px */
}

.tab-text {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 32rpx; /* 对应16px */
  line-height: 38rpx; /* 对应19px */
  background: linear-gradient(180deg, #F7E7FF 0%, #FFFFFF 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  color: transparent;
}

.header-tab.active .tab-text {
  font-weight: 700;
}

.header-tab.disabled .tab-text {
  opacity: 0.5;
}

.header-tab.active::after {
  content: '';
  position: absolute;
  bottom: -10rpx;
  left: 50%;
  transform: translateX(-50%);
  width: 120rpx; /* 对应60px */
  height: 6rpx; /* 对应3px */
  background: linear-gradient(180deg, #F7E7FF 0%, #FFFFFF 100%);
  border-radius: 6rpx;
  opacity: 0.8;
}

/* 内容区域 */
.content-container {
  position: relative;
  z-index: 5;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100rpx 60rpx; /* 对应50px 30px */
  height: calc(100vh - 300rpx); /* 减去顶部导航高度 */
}

/* 插图区域 */
.illustration-section {
  margin-bottom: 80rpx; /* 对应40px */
}

.no-match-image {
  width: 400rpx; /* 对应200px */
  height: 400rpx; /* 对应200px */
}

/* 消息区域 */
.message-section {
  text-align: center;
  margin-bottom: 120rpx; /* 对应60px */
}

.main-message {
  font-family: 'Inter';
  font-weight: 700;
  font-size: 40rpx; /* 对应20px */
  line-height: 48rpx; /* 对应24px */
  color: #1F2635;
  display: block;
  margin-bottom: 30rpx; /* 对应15px */
}

.sub-message {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 28rpx; /* 对应14px */
  line-height: 34rpx; /* 对应17px */
  color: #9094A6;
  display: block;
}

/* 操作区域 */
.action-section {
  width: 100%;
  max-width: 500rpx; /* 对应250px */
}

.goto-signup-btn {
  width: 100%;
  height: 88rpx; /* 对应44px */
  background: linear-gradient(90deg, #A100FE 0%, #FDB9E7 100%);
  border-radius: 90rpx; /* 对应45px */
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-text {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 32rpx; /* 对应16px */
  line-height: 38rpx; /* 对应19px */
  color: #FFFFFF;
}
</style>
