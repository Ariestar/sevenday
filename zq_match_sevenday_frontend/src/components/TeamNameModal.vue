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
  flex-direction: column;
  background: linear-gradient(180deg, #F7E7FF 0%, #FFFFFF 100%);
}

.modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(180deg, #F7E7FF 0%, #FFFFFF 100%);
}

/* 顶部背景区域 */
.header-background {
  position: relative;
  width: 100%;
  height: 156rpx; /* 对应78px */
  z-index: 10;
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

.modal-content {
  position: relative;
  width: 620rpx; /* 对应310px */
  background: #FFFFFF;
  border-radius: 24rpx; /* 四个角圆角 */
  padding: 60rpx 40rpx 40rpx; /* 对应30px 20px 20px */
  margin: 0 auto;
  margin-top: 200rpx; /* 增加间距，使内容块下移 */
  box-sizing: border-box;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.15); /* 添加阴影效果 */
  z-index: 5;
}

/* 标题区域 */
.modal-header {
  text-align: center;
  margin-bottom: 60rpx; /* 对应30px */
}

.modal-title {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 55rpx; /* 对应18px */
  line-height: 44rpx; /* 对应22px */
  color: #1F2635;
  display: block;
  margin-bottom: 20rpx; /* 对应10px */
}

.modal-subtitle {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 28rpx; /* 对应14px */
  line-height: 40rpx; /* 增加行高 */
  color: #9094A6;
  display: block;
  margin-bottom: 8rpx;
}

/* 输入区域 */
.input-section {
  position: relative;
  margin-bottom: 220rpx; /* 增加间距，使按钮下移 */
}

.team-name-input {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  width: 400rpx;
  height: 96rpx; /* 对应48px */
  padding: 0 24rpx; /* 对应0 12px */
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


/* 按钮区域 */
.button-section {
  display: flex;
  justify-content: center;
}

.confirm-btn {
  width: 300rpx; /* 缩短按钮长度 */
  height: 105rpx; /* 对应47px */
  background: linear-gradient(90deg, #A100FE 0%, #FDB9E7 100%);
  border-radius: 180rpx; /* 对应90px */
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
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
</style>
