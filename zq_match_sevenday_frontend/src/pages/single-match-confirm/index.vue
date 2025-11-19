<template>
  <view class="single-match-confirm-page">
    <!-- 背景图片 -->
    <view class="result-gradient-bg"></view>
    
    <!-- 左侧渐变区域 -->
    <view class="left-gradient-area"></view>

    <!-- 报名/匹配标签切换区域 -->
    <view class="tab-section">
      <view class="tab-group">
        <view class="tab-item" @click="goToSignup">
          <text class="tab-text">报名</text>
        </view>
        <view class="tab-item active">
          <text class="tab-text active">匹配</text>
          <view class="tab-indicator"></view>
        </view>
      </view>
    </view>

    <!-- 功能标签切换区域 -->
    <view class="function-tab-section">
      <view class="function-tab-group">
        <view class="function-tab-item disabled">
          <text class="function-tab-text">你的期望</text>
        </view>
        <view class="function-tab-item disabled">
          <text class="function-tab-text">智能匹配</text>
        </view>
        <view class="function-tab-item active">
          <text class="function-tab-text active">确认组队</text>
        </view>
      </view>
    </view>

    <!-- 组队成功标题 -->
    <view class="success-section">
      <text class="success-title">组队成功！</text>
      <view class="connection-icon">
        <image src="/static/match-single-part1/star.png" class="connect-star" mode="aspectFit" />
      </view>
    </view>

    <!-- 双人头像区域 -->
    <view class="dual-avatar-section">
      <!-- 你的ID -->
      <view class="avatar-container left-avatar">
        <view class="avatar-circle">
          <image 
            v-if="myInfo.avatar" 
            :src="myInfo.avatar" 
            class="avatar-image" 
            mode="aspectFill" 
          />
          <text v-else class="avatar-placeholder">👤</text>
        </view>
        <text class="avatar-label">你的ID</text>
      </view>

      <!-- 对方的ID -->
      <view class="avatar-container right-avatar">
        <view class="avatar-circle">
          <image 
            v-if="partnerInfo.avatar" 
            :src="partnerInfo.avatar" 
            class="avatar-image" 
            mode="aspectFill" 
          />
          <text v-else class="avatar-placeholder">👤</text>
        </view>
        <text class="avatar-label">对方的ID</text>
      </view>
    </view>

    <!-- 双方信息对比卡片 -->
    <view class="info-cards-section">
      <!-- 我的信息卡片 -->
      <view class="info-card my-info-card">
        <view class="info-row">
          <text class="info-label">性别</text>
          <text class="info-value">{{ myInfo.gender || '男' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">身份</text>
          <text class="info-value">{{ myInfo.education || '本科生' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">大类</text>
          <text class="info-value">{{ myInfo.majorCategory || '理科' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">院系</text>
          <text class="info-value">{{ myInfo.college || '物理学院' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">QQ</text>
          <text class="info-value">{{ myInfo.qq || '123456' }}</text>
        </view>
      </view>

      <!-- 对方信息卡片 -->
      <view class="info-card partner-info-card">
        <view class="info-row">
          <text class="info-label">性别</text>
          <text class="info-value">{{ partnerInfo.gender || '女' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">身份</text>
          <text class="info-value">{{ partnerInfo.education || '本科生' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">大类</text>
          <text class="info-value">{{ partnerInfo.majorCategory || '工科' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">院系</text>
          <text class="info-value">{{ partnerInfo.college || '计算机学院' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">QQ</text>
          <text class="info-value">{{ partnerInfo.qq || '789012' }}</text>
        </view>
      </view>
    </view>

    <!-- 底部导航栏 -->
    <view class="bottom-navigation">
      <!-- 报名-匹配 (选中状态) -->
      <view class="nav-item active" @click="goToMultipleMatch">
        <view class="nav-icon-wrapper">
          <image src="/static/navigation/match-on.png" class="nav-icon" mode="aspectFit" />
        </view>
        <text class="nav-text active">报名-匹配</text>
      </view>
      
      <!-- 打卡 -->
      <view class="nav-item" @click="goToCheckin">
        <view class="nav-icon-wrapper">
          <image src="/static/navigation/checkin-off.png" class="nav-icon" mode="aspectFit" />
        </view>
        <text class="nav-text">打卡</text>
      </view>
      
      <!-- 广场 -->
      <view class="nav-item" @click="goToSquare">
        <view class="nav-icon-wrapper">
          <image src="/static/navigation/square-off.png" class="nav-icon" mode="aspectFit" />
        </view>
        <text class="nav-text">广场</text>
      </view>
      
      <!-- 我的 -->
      <view class="nav-item" @click="goToMine">
        <view class="nav-icon-wrapper">
          <image src="/static/navigation/mine-off.png" class="nav-icon" mode="aspectFit" />
        </view>
        <text class="nav-text">我的</text>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      myInfo: {
        gender: '',
        education: '',
        majorCategory: '',
        college: '',
        qq: '',
        avatar: ''
      },
      partnerInfo: {
        gender: '',
        education: '',
        majorCategory: '',
        college: '',
        qq: '',
        avatar: ''
      }
    }
  },
  onLoad(options) {
    console.log('确认组队页面加载', options)
    
    // 从上一个页面接收组队数据
    if (options.teamData) {
      try {
        const teamData = JSON.parse(decodeURIComponent(options.teamData))
        this.myInfo = teamData.myInfo || this.myInfo
        this.partnerInfo = teamData.partnerInfo || this.partnerInfo
      } catch (error) {
        console.error('解析组队数据失败:', error)
      }
    }
    
    // 如果没有数据，使用默认数据
    if (!this.myInfo.gender) {
      this.myInfo = {
        gender: '男',
        education: '本科生',
        majorCategory: '理科',
        college: '物理学院',
        qq: '123456',
        avatar: ''
      }
    }
    
    if (!this.partnerInfo.gender) {
      this.partnerInfo = {
        gender: '女',
        education: '本科生',
        majorCategory: '工科',
        college: '计算机学院',
        qq: '789012',
        avatar: ''
      }
    }
  },
  methods: {
    // 返回期望页面
    goToExpectation() {
      uni.reLaunch({
        url: '/pages/single-match/index',
        fail: (err) => {
          console.warn('跳转失败:', err)
          uni.showToast({
            title: '跳转失败，请重试',
            icon: 'none'
          })
        }
      })
    },
    // 返回匹配结果页面
    goToMatchResult() {
      uni.navigateBack({
        success: () => {
          console.log('返回匹配结果页面成功')
        },
        fail: (err) => {
          console.warn('返回失败，尝试其他方式:', err)
          uni.reLaunch({
            url: '/pages/single-match-result/index',
            fail: (err2) => {
              console.error('跳转匹配结果页面失败:', err2)
              uni.showToast({
                title: '跳转失败，请重试',
                icon: 'none'
              })
            }
          })
        }
      })
    },
    // 跳转到报名页面
    goToSignup() {
      uni.reLaunch({
        url: '/pages/signup/index',
        fail: (err) => {
          console.warn('跳转失败:', err)
          uni.showToast({
            title: '跳转失败，请重试',
            icon: 'none'
          })
        }
      })
    },
    
    // 开始打卡
    startCheckin() {
      // 先标记已组队状态
      uni.setStorageSync('hasTeam', true)
      uni.setStorageSync('justCreatedTeam', true)
      
      uni.reLaunch({
        url: '/pages/checkin-detail/index'
      })
    },
    
    // 导航栏跳转方法
    goToMultipleMatch() {
      // 跳转到报名页面，而不是多人匹配页面（多人匹配未开放）
      uni.reLaunch({
        url: '/pages/signup/index',
        fail: (err) => {
          console.warn('跳转失败:', err)
          uni.navigateTo({
            url: '/pages/signup/index',
            fail: () => {
              uni.showToast({
                title: '跳转失败，请重试',
                icon: 'none'
              })
            }
          })
        }
      })
    },
    goToCheckin() {
      // 先标记已组队状态
      uni.setStorageSync('hasTeam', true)
      uni.setStorageSync('justCreatedTeam', true)
      
      uni.reLaunch({
        url: '/pages/checkin-detail/index'
      })
    },
    goToSquare() {
      uni.switchTab({
        url: '/pages/square/index',
        fail: (err) => {
          console.warn('跳转失败:', err)
          uni.reLaunch({ url: '/pages/square/index' })
        }
      })
    },
    goToMine() {
      uni.switchTab({
        url: '/pages/mine/index',
        fail: (err) => {
          console.warn('跳转失败:', err)
          uni.reLaunch({ url: '/pages/mine/index' })
        }
      })
    }
  }
}
</script>

<style scoped>
.single-match-confirm-page {
  width: 750rpx;
  min-height: 1624rpx; /* 对应812px */
  background: linear-gradient(180deg, #F7E7FF 0%, #FFFFFF 100%);
  position: relative;
  margin: 0 auto;
  padding-bottom: 112rpx; /* 为底部导航栏留空间 */
}

/* 背景图片 */
.result-gradient-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  width: 100%;
  height: 312rpx; /* 对应156px */
  background-image: url('/static/match-single-part1/part3-banner-background.png');
  background-size: cover;
  background-position: center top;
  background-repeat: no-repeat;
  z-index: 1;
  overflow: hidden;
}

/* 左侧渐变区域 */
.left-gradient-area {
  position: absolute;
  top: 156rpx; /* 对应78px */
  left: 0;
  width: 322rpx; /* 对应161px */
  height: 90rpx; /* 对应45px */
  background: linear-gradient(180deg, #F7E8FE 0%, #F9ECFF 100%);
  z-index: 2;
}

/* 报名/匹配标签切换区域 */
.tab-section {
  position: absolute;
  top: 50rpx; /* 对应25px */
  left: 138rpx; /* 对应69px */
  width: 472rpx; /* 对应236px */
  height: 74rpx; /* 对应37px */
  z-index: 10;
}

.tab-group {
  display: flex;
  height: 100%;
  position: relative;
}

.tab-item {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 74rpx;
  position: relative;
}

.tab-text {
  font-size: 32rpx; /* 对应16px */
  font-weight: 400;
  color: #FFFFFF;
}

.tab-text.active {
  font-weight: 700;
}

.tab-indicator {
  position: absolute;
  bottom: 6rpx; /* 对应3px */
  left: 50%;
  transform: translateX(-50%);
  width: 120rpx; /* 对应60px */
  height: 36rpx; /* 对应18px */
  background: linear-gradient(180deg, #F7E7FF 0%, #FFFFFF 100%);
  opacity: 0.4;
  border-radius: 180rpx; /* 对应90px */
}

/* 功能标签切换区域 */
.function-tab-section {
  position: absolute;
  top: 170rpx; /* 对应85px */
  left: 54rpx; /* 对应27px */
  right: 54rpx;
  height: 38rpx; /* 对应19px */
  z-index: 10;
}

.function-tab-group {
  display: flex;
  height: 100%;
  width: 100%;
  justify-content: space-between;
  align-items: center;
  position: relative;
}

.function-tab-item {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 38rpx;
  position: relative;
  flex-shrink: 0;
}

.function-tab-text {
  font-size: 32rpx; /* 对应16px */
  font-weight: 400;
  color: #000000;
}

.function-tab-text.active {
  font-weight: 700;
  color: #000000;
}

.function-tab-item.disabled {
  opacity: 0.5;
  pointer-events: none; /* 禁用点击 */
}

/* 组队成功区域 */
.success-section {
  position: absolute;
  top: 302rpx; /* 对应151px */
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 20rpx;
  z-index: 10;
}

.success-title {
  font-size: 32rpx; /* 对应16px */
  font-weight: 400;
  color: #000000;
}

.connection-icon {
  width: 40rpx;
  height: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.connect-star {
  width: 32rpx;
  height: 32rpx;
}

/* 双人头像区域 */
.dual-avatar-section {
  position: absolute;
  top: 382rpx; /* 对应191px */
  left: 0;
  right: 0;
  height: 236rpx; /* 对应118px */
  z-index: 15;
}

.avatar-container {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20rpx;
}

.left-avatar {
  left: calc(50% - 236rpx/2 - 173rpx); /* 对应 calc(50% - 118px/2 - 86.5px) */
}

.right-avatar {
  left: calc(50% - 236rpx/2 + 173rpx); /* 对应 calc(50% - 118px/2 + 86.5px) */
}

.avatar-circle {
  width: 236rpx; /* 对应118px */
  height: 236rpx; /* 对应118px */
  border-radius: 50%;
  background: #E3E4E4;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.avatar-image {
  width: 100%;
  height: 100%;
  border-radius: 50%;
}

.avatar-placeholder {
  font-size: 80rpx;
  color: #9094A6;
}

.avatar-label {
  font-size: 32rpx; /* 对应16px */
  font-weight: 400;
  color: #000000;
  text-align: center;
}

/* 双方信息卡片区域 */
.info-cards-section {
  position: absolute;
  top: 730rpx; /* 对应365px */
  left: 0;
  right: 0;
  z-index: 10;
}

.info-card {
  position: absolute;
  width: 284rpx; /* 对应142px */
  height: 426rpx; /* 对应213px */
  background: #FFFFFF;
  border: 2rpx solid #A100FE;
  border-radius: 24rpx; /* 对应12px */
  padding: 32rpx 20rpx; /* 内边距 */
  box-sizing: border-box;
}

.my-info-card {
  left: 66rpx; /* 对应33px */
  border-color: #AC1FFE;
}

.partner-info-card {
  left: 406rpx; /* 对应203px */
  border-color: #A100FE;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32rpx; /* 对应16px */
  padding: 10rpx 0;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-label {
  font-size: 32rpx; /* 对应16px */
  font-weight: 400;
  color: #9094A6;
}

.info-value {
  font-size: 32rpx; /* 对应16px */
  font-weight: 400;
  color: #000000;
}

/* 底部导航栏 */
.bottom-navigation {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 112rpx; /* 对应56px */
  background: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 0;
  z-index: 100;
  box-shadow: 0 -2rpx 10rpx rgba(0, 0, 0, 0.1);
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 112rpx; /* 对应56px */
  height: 112rpx;
  cursor: pointer;
}

.nav-icon-wrapper {
  width: 56rpx; /* 对应28px */
  height: 56rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8rpx;
}

.nav-icon {
  width: 48rpx; /* 对应24px */
  height: 48rpx;
}

.nav-text {
  font-size: 20rpx; /* 对应10px */
  color: #9094A6;
  font-weight: 400;
  text-align: center;
  line-height: 24rpx; /* 对应12px */
}

.nav-text.active {
  color: #1F2635;
  font-weight: 400;
}

.nav-item.active .nav-text {
  color: #1F2635;
}
</style>
