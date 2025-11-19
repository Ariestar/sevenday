<template>
  <view class="multiple-match-page">
    <!-- 顶部渐变背景 -->
    <view class="top-gradient-bg"></view>
    <view class="bottom-gradient-bg"></view>
    
    <!-- 报名/匹配标签切换区域 -->
    <view class="tab-section">
      <view class="tab-group">
        <view class="tab-item" @click="goToSignup">
          <view class="tab-bg"></view>
          <text class="tab-text">报名</text>
        </view>
        <view class="tab-item active">
          <view class="tab-bg"></view>
          <text class="tab-text active">匹配</text>
          <view class="tab-indicator"></view>
        </view>
      </view>
    </view>

    <!-- 主要内容区域 -->
    <view class="main-content">
      <!-- 输入卡片 -->
      <view class="input-card">
        <!-- 标题图标和文字 -->
        <view class="card-header">
          <image class="star-icon" src="/static/match-mutiple-part1/star.png" mode="aspectFit"></image>
          <text class="card-title">请输入对方学号</text>
        </view>
        
        <!-- 输入框 -->
        <view class="input-section">
          <input 
            class="student-input" 
            type="text" 
            placeholder="请输入" 
            v-model="studentNumber"
            placeholder-style="color: #CACDD9;"
          />
        </view>
        
        <!-- 确认按钮 -->
        <view class="confirm-btn" @click="handleConfirm">
          <text class="confirm-text">确认</text>
        </view>
      </view>

      <!-- 说明文字 -->
      <view class="description">
        <text class="desc-text">关于组队模式的相关说明</text>
      </view>
    </view>

    <!-- 底部导航栏 -->
    <CustomTabBar :current="0"></CustomTabBar>
  </view>
</template>

<script>
import CustomTabBar from '@/components/CustomTabBar.vue'

export default {
  components: {
    CustomTabBar
  },
  data() {
    return {
      studentNumber: ''
    }
  },
  methods: {
    goToSignup() {
      uni.reLaunch({
        url: '/pages/signup/index',
        fail: (err) => {
          console.warn('跳转到报名页面失败:', err)
          uni.navigateTo({
            url: '/pages/signup/index'
          })
        }
      })
    },
    
    handleConfirm() {
      if (!this.studentNumber.trim()) {
        uni.showToast({
          title: '请输入学号',
          icon: 'none'
        })
        return
      }
      
      // 显示发送组队申请成功
      uni.showToast({
        title: '组队申请已发送',
        icon: 'success'
      })
      
      // 模拟跳转到对方的确认页面（实际应用中这个页面是对方看到的）
      setTimeout(() => {
        const inviterInfo = {
          name: this.studentNumber,
          gender: '男',
          education: '本科生',
          majorCategory: '计算机类',
          college: '计算机学院',
          bio: '这是一段个人简介示例内容'
        }
        
        uni.navigateTo({
          url: `/pages/multiple-match-confirm/index?inviterInfo=${encodeURIComponent(JSON.stringify(inviterInfo))}`,
          fail: (err) => {
            console.warn('跳转到确认页面失败:', err)
            uni.showToast({
              title: '跳转失败',
              icon: 'none'
            })
          }
        })
      }, 1500)
    }
  }
}
</script>

<style scoped>
.multiple-match-page {
  position: relative;
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(180deg, #F7E7FF 0%, #FFFFFF 100%);
}

/* 顶部渐变背景 */
.top-gradient-bg {
  position: absolute;
  width: 100%;
  height: 246rpx; /* 对应123px */
  left: 0;
  top: 0;
  background: linear-gradient(90deg, #A100FE 0%, #FDB9E7 100%);
  z-index: 1;
}

.bottom-gradient-bg {
  position: absolute;
  width: 100%;
  height: 90rpx; /* 对应45px */
  left: 0;
  top: 156rpx; /* 对应78px */
  background: linear-gradient(180deg, #F7E8FE 0%, #F9ECFF 100%);
  z-index: 2;
}

/* 标签切换区域 */
.tab-section {
  position: absolute;
  width: 472rpx; /* 对应236px */
  height: 74rpx; /* 对应37px */
  left: 170rpx; /* 对应85px */
  top: 50rpx; /* 对应25px */
  z-index: 10;
}

.tab-group {
  display: flex;
  width: 100%;
  height: 100%;
  position: relative;
}

.tab-item {
  position: relative;
  width: 148rpx; /* 对应74px */
  height: 74rpx; /* 对应37px */
  display: flex;
  align-items: center;
  justify-content: center;
}

.tab-bg {
  position: absolute;
  width: 100%;
  height: 100%;
  background: #D9D9D9;
  opacity: 0;
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
  z-index: 3;
}

.tab-text.active {
  font-weight: 700;
}

.tab-item.active {
  position: relative;
}

.tab-indicator {
  position: absolute;
  width: 120rpx; /* 对应60px */
  height: 36rpx; /* 对应18px */
  left: 14rpx; /* 居中对齐 */
  bottom: -8rpx; /* 对应-4px，向下调整 */
  background: linear-gradient(180deg, #F7E7FF 0%, #FFFFFF 100%);
  opacity: 0.4;
  border-radius: 180rpx; /* 对应90px */
}

/* 主要内容区域 */
.main-content {
  position: relative;
  z-index: 5;
  padding-top: 222rpx; /* 对应111px */
  padding-left: 44rpx; /* 对应22px */
  padding-right: 44rpx; /* 对应22px */
}

/* 输入卡片 */
.input-card {
  position: relative;
  width: 664rpx; /* 对应332px */
  height: 456rpx; /* 对应228px */
  background: #FFFFFF;
  border: 4rpx solid #A100FE; /* 对应2px */
  border-radius: 30rpx; /* 对应15px */
  padding: 40rpx;
  box-sizing: border-box;
}

/* 卡片标题区域 */
.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 60rpx; /* 对应30px */
}

.star-icon {
  width: 66rpx; /* 对应33px */
  height: 52rpx; /* 对应26px */
  margin-right: 20rpx; /* 对应10px */
}

.card-title {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 32rpx; /* 对应16px */
  line-height: 38rpx; /* 对应19px */
  color: #000000;
}

/* 输入区域 */
.input-section {
  margin-bottom: 60rpx; /* 对应30px */
}

.student-input {
  width: 596rpx; /* 对应298px */
  height: 92rpx; /* 对应46px */
  border: 4rpx solid #F7E7FF; /* 对应2px */
  border-radius: 180rpx; /* 对应90px */
  padding: 0 30rpx;
  font-family: 'Inter';
  font-weight: 400;
  font-size: 32rpx; /* 对应16px */
  line-height: 38rpx; /* 对应19px */
  color: #000000;
  box-sizing: border-box;
}

/* 确认按钮 */
.confirm-btn {
  position: absolute;
  width: 166rpx; /* 对应83px */
  height: 66rpx; /* 对应33px */
  left: 50%;
  bottom: 40rpx;
  transform: translateX(-50%);
  background: #1F2635;
  border-radius: 33rpx; /* 对应16.5px */
  display: flex;
  align-items: center;
  justify-content: center;
}

.confirm-text {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 32rpx; /* 对应16px */
  line-height: 38rpx; /* 对应19px */
  color: #FFFFFF;
}

/* 说明文字 */
.description {
  margin-top: 116rpx; /* 对应58px */
  padding: 0 26rpx; /* 对应13px */
}

.desc-text {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 32rpx; /* 对应16px */
  line-height: 38rpx; /* 对应19px */
  color: #9094A6;
}
</style>