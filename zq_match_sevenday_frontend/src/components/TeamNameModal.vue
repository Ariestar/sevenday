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
        <view class="input-wrapper">
          <input 
            class="team-name-input" 
            v-model="teamName"
            placeholder="请输入队名（2-10个字符）"
            maxlength="10"
            :focus="inputFocus"
          />
          <view class="char-count">{{ teamName.length }}/10</view>
        </view>
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
    },
    defaultTeamName: {
      type: String,
      default: ''
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
        // 如果有默认队名，使用默认值；否则清空
        this.teamName = this.defaultTeamName || ''
        this.inputFocus = true
      }
    },
    defaultTeamName(newVal) {
      // 如果弹窗已打开且有新的默认值，更新队名
      if (this.visible && newVal) {
        this.teamName = newVal
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
  padding: 80rpx 40rpx 40rpx; /* 对应40px 20px 20px */
  margin: 0 40rpx;
  box-sizing: border-box;
  text-align: center;
}

/* 标题区域 */
.modal-header {
  margin-bottom: 60rpx; /* 对应30px */
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
  font-weight: 400;
  font-size: 28rpx; /* 对应14px */
  line-height: 34rpx; /* 对应17px */
  color: #9094A6;
  display: block;
}

/* 输入区域 */
.input-section {
  margin-bottom: 60rpx; /* 输入框和按钮之间的间距 */
  display: flex;
  justify-content: center;
  width: 100%;
}

.input-wrapper {
  position: relative;
  width: 100%;
  max-width: 540rpx;
}

.team-name-input {
  width: 100%;
  height: 96rpx; /* 对应48px */
  padding: 0 80rpx 0 24rpx; /* 右侧留出字符计数空间 */
  background: #FFFFFF;
  border: 4rpx solid #c05af3; /* 紫色边框 */
  border-radius: 180rpx; /* 圆角 */
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
  right: 24rpx;
  top: 50%;
  transform: translateY(-50%);
  font-family: 'Inter';
  font-weight: 400;
  font-size: 24rpx;
  color: #9094A6;
  pointer-events: none;
  z-index: 1;
}


/* 按钮区域 */
.button-group {
  display: flex;
  justify-content: space-between;
  gap: 40rpx;
}

.cancel-btn {
  flex: 1;
  height: 94rpx; /* 对应47px */
  background: #F5F5F5;
  border-radius: 180rpx; /* 对应90px */
  display: flex;
  align-items: center;
  justify-content: center;
}

.confirm-btn {
  flex: 1;
  height: 94rpx; /* 对应47px */
  background: linear-gradient(90deg, #A100FE 0%, #FDB9E7 100%);
  border-radius: 180rpx; /* 对应90px */
  display: flex;
  align-items: center;
  justify-content: center;
}

.confirm-btn.disabled {
  background: #E5E5E5;
  opacity: 0.6;
}

.confirm-icon {
  font-size: 32rpx;
  color: #FFFFFF;
  font-weight: 700;
}

.btn-text {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 32rpx; /* 对应16px */
  line-height: 38rpx; /* 对应19px */
  color: #FFFFFF;
}

.confirm-btn.disabled .btn-text {
  color: #9094A6;
}

.confirm-btn.disabled .confirm-icon {
  color: #9094A6;
}

.cancel-btn .btn-text {
  color: #9094A6;
}
</style>
