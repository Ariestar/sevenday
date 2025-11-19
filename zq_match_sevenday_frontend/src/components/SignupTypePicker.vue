<template>
  <view v-if="visible" class="popup-mask" @click="handleClose">
    <view class="signup-type-picker" @click.stop>
      <view class="popup-content">
        <text class="popup-title">请选择你的报名类型</text>
        <view class="options-container">
          <button class="option-button" @click="selectType('single')">
            单人
          </button>
          <button class="option-button" @click="selectType('team')">
            组队
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  name: 'SignupTypePicker',
  props: {
    visible: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    selectType(type) {
      this.$emit('select', type)
      this.handleClose()
    },
    handleClose() {
      this.$emit('update:visible', false)
    }
  }
}
</script>

<style scoped>
.popup-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.signup-type-picker {
  width: 626rpx;
  background: #FFFFFF;
  border-radius: 18rpx;
  padding: 72rpx 0 0;
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.popup-content {
  padding: 0 84rpx 96rpx;
}

.popup-title {
  font-size: 32rpx;
  color: #000000;
  margin-bottom: 80rpx;
  display: block;
  text-align: center;
}

.options-container {
  display: flex;
  gap: 36rpx;
  justify-content: center;
}

.option-button {
  width: 130rpx;
  height: 64rpx;
  background: #1F2635;
  border-radius: 180rpx;
  color: #FFFFFF;
  font-size: 28rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
}

.option-button::after {
  border: none;
}
</style>
