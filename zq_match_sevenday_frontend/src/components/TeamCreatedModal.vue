<template>
  <view class="team-created-modal" v-if="visible">
    <view class="modal-overlay" @click="handleClose"></view>
    <view class="modal-content">
      <!-- 成功图标 -->
      <view class="success-icon-section">
        <image class="success-icon" src="/static/success/team-created.png" mode="aspectFit"></image>
      </view>
      
      <!-- 标题和内容 -->
      <view class="modal-header">
        <text class="modal-title">组队成功！</text>
        <text class="modal-subtitle">队名：{{ teamName }}</text>
        <text class="modal-description">开始你们的{{ activityDays }}天打卡之旅吧！</text>
      </view>
      
      <!-- 确认按钮 -->
      <view class="button-section">
        <view class="confirm-btn" @click="handleConfirm">
          <text class="btn-text">开始打卡</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { ACTIVITY_DAYS } from '@/utils/constants'

export default {
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    teamName: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      activityDays: ACTIVITY_DAYS
    }
  },
  methods: {
    handleClose() {
      this.$emit('close')
    },
    
    handleConfirm() {
      this.$emit('confirm')
    }
  }
}
</script>

<style scoped>
.team-created-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
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
  width: 620rpx; /* 对应310px */
  background: #FFFFFF;
  border-radius: 24rpx; /* 对应12px */
  padding: 80rpx 40rpx 40rpx; /* 对应40px 20px 20px */
  margin: 0 40rpx;
  box-sizing: border-box;
  text-align: center;
}

/* 成功图标 */
.success-icon-section {
  display: flex;
  justify-content: center;
  margin-bottom: 40rpx; /* 对应20px */
}

.success-icon {
  width: 160rpx; /* 对应80px */
  height: 160rpx; /* 对应80px */
}

/* 标题区域 */
.modal-header {
  margin-bottom: 80rpx; /* 对应40px */
}

.modal-title {
  font-family: 'Inter';
  font-weight: 700;
  font-size: 40rpx; /* 对应20px */
  line-height: 48rpx; /* 对应24px */
  color: #1F2635;
  display: block;
  margin-bottom: 30rpx; /* 对应15px */
}

.modal-subtitle {
  font-family: 'Inter';
  font-weight: 600;
  font-size: 32rpx; /* 对应16px */
  line-height: 38rpx; /* 对应19px */
  color: #A100FE;
  display: block;
  margin-bottom: 20rpx; /* 对应10px */
}

.modal-description {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 28rpx; /* 对应14px */
  line-height: 34rpx; /* 对应17px */
  color: #9094A6;
  display: block;
}

/* 按钮区域 */
.button-section {
  width: 100%;
}

.confirm-btn {
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
