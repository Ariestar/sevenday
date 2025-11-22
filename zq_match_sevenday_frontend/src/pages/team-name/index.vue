<template>
  <view class="team-name-page">
    <!-- 顶部背景区域 -->
    <view class="header-background">
      <view class="banner-background"></view>
      <view class="header-tabs">
        <view class="tab-item">
          <text class="tab-text">队友信息</text>
        </view>
        <view class="tab-item active">
          <text class="tab-text">组队打卡</text>
        </view>
      </view>
    </view>
    
    <!-- 创建队名弹窗 -->
    <TeamNameModal
      :visible="true"
      @cancel="handleCancel"
      @confirm="handleConfirm"
    />
  </view>
</template>

<script>
import TeamNameModal from '@/components/TeamNameModal.vue'

export default {
  components: {
    TeamNameModal
  },
  methods: {
    handleCancel() {
      // 取消时返回上一页
      uni.navigateBack({
        fail: () => {
          // 如果无法返回，跳转到匹配页面
          uni.reLaunch({
            url: '/pages/multiple-match/index'
          })
        }
      })
    },
    
    handleConfirm(teamName) {
      // 保存队名
      uni.setStorageSync('teamName', teamName)
      uni.setStorageSync('hasTeam', true)
      uni.removeStorageSync('justCreatedTeam')
      
      // 跳转到打卡页面，显示组队成功弹窗
      uni.reLaunch({
        url: '/pages/checkin-detail/index'
      })
    }
  }
}
</script>

<style scoped>
.team-name-page {
  position: relative;
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(180deg, #F7E7FF 0%, #FFFFFF 100%);
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
  background-image: url('/static/checkin/checkin-part1-banner-background.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

.header-tabs {
  position: absolute;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-around;
  z-index: 10;
}

.tab-item {
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

.tab-item.active .tab-text {
  font-weight: 700;
}
</style>



