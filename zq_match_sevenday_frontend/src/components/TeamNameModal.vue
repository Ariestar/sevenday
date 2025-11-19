<template>
  <view class="team-name-modal" v-if="visible">
    <view class="modal-overlay" @click="handleCancel"></view>
    <view class="modal-content">
      <!-- 标题 -->
      <view class="modal-header">
        <text class="modal-title">创建队名</text>
        <text class="modal-subtitle">只有一次机会，请慎重选择</text>
      </view>
      
      <!-- 输入框 -->
      <view class="input-section">
        <input 
          class="team-name-input" 
          v-model="teamName"
          placeholder="请输入队名（2-10个字符）"
          maxlength="10"
          :focus="inputFocus"
        />
        <view class="char-count">{{ teamName.length }}/10</view>
      </view>
      
      <!-- 按钮组 -->
      <view class="button-group">
        <view class="cancel-btn" @click="handleCancel">
          <text class="btn-text">取消</text>
        </view>
        <view class="confirm-btn" @click="handleConfirm" :class="{ disabled: !isValid }">
          <text class="btn-text">确认</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  props: {
    visible: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      teamName: '',
      inputFocus: false
    }
  },
  computed: {
    isValid() {
      return this.teamName.length >= 2 && this.teamName.length <= 10
    }
  },
  watch: {
    visible(newVal) {
      if (newVal) {
        this.teamName = ''
        this.inputFocus = true
      }
    }
  },
  methods: {
    handleCancel() {
      this.$emit('cancel')
    },
    
    handleConfirm() {
      if (!this.isValid) {
        uni.showToast({
          title: '队名长度应为2-10个字符',
          icon: 'none'
        })
        return
      }
      
      this.$emit('confirm', this.teamName.trim())
    }
  }
}
</script>

<style scoped>
.team-name-modal {
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
  padding: 60rpx 40rpx 40rpx; /* 对应30px 20px 20px */
  margin: 0 40rpx;
  box-sizing: border-box;
}

/* 标题区域 */
.modal-header {
  text-align: center;
  margin-bottom: 60rpx; /* 对应30px */
}

.modal-title {
  font-family: 'Inter';
  font-weight: 700;
  font-size: 36rpx; /* 对应18px */
  line-height: 44rpx; /* 对应22px */
  color: #1F2635;
  display: block;
  margin-bottom: 20rpx; /* 对应10px */
}

.modal-subtitle {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 28rpx; /* 对应14px */
  line-height: 34rpx; /* 对应17px */
  color: #9094A6;
  display: block;
}

/* 输入区域 */
.input-section {
  position: relative;
  margin-bottom: 80rpx; /* 对应40px */
}

.team-name-input {
  width: 100%;
  height: 96rpx; /* 对应48px */
  padding: 0 24rpx; /* 对应0 12px */
  background: #F8F9FA;
  border: 2rpx solid #E5E5E5; /* 对应1px */
  border-radius: 12rpx; /* 对应6px */
  font-family: 'Inter';
  font-weight: 400;
  font-size: 32rpx; /* 对应16px */
  line-height: 38rpx; /* 对应19px */
  color: #1F2635;
  box-sizing: border-box;
}

.team-name-input:focus {
  border-color: #A100FE;
  background: #FFFFFF;
}

.char-count {
  position: absolute;
  right: 24rpx; /* 对应12px */
  bottom: -40rpx; /* 对应-20px */
  font-family: 'Inter';
  font-weight: 400;
  font-size: 24rpx; /* 对应12px */
  line-height: 28rpx; /* 对应14px */
  color: #9094A6;
}

/* 按钮组 */
.button-group {
  display: flex;
  gap: 40rpx; /* 对应20px */
}

.cancel-btn, .confirm-btn {
  flex: 1;
  height: 88rpx; /* 对应44px */
  border-radius: 90rpx; /* 对应45px */
  display: flex;
  align-items: center;
  justify-content: center;
}

.cancel-btn {
  background: #F8F9FA;
  border: 2rpx solid #E5E5E5; /* 对应1px */
}

.confirm-btn {
  background: linear-gradient(90deg, #A100FE 0%, #FDB9E7 100%);
}

.confirm-btn.disabled {
  background: #E5E5E5;
  opacity: 0.6;
}

.btn-text {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 32rpx; /* 对应16px */
  line-height: 38rpx; /* 对应19px */
}

.cancel-btn .btn-text {
  color: #1F2635;
}

.confirm-btn .btn-text {
  color: #FFFFFF;
}

.confirm-btn.disabled .btn-text {
  color: #9094A6;
}
</style>
