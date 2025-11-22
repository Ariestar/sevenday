<template>
  <view v-if="visible" class="popup-mask" @click="handleClose">
    <view class="gender-picker-popup" @click.stop>
      <view class="popup-content">
        <text class="popup-title">请选择性别</text>
        <view class="options-container">
          <button
            v-for="(option, index) in options"
            :key="index"
            class="option-button"
            :class="{ 'selected': selectedValue === option.value }"
            @click="selectOption(option)"
          >
            {{ option.label }}
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  name: 'GenderPicker',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    value: {
      type: String,
      default: ''
    },
    options: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      selectedValue: ''
    }
  },
  watch: {
    visible(newVal) {
      if (newVal) {
        this.selectedValue = this.value
      }
    },
    value(newVal) {
      this.selectedValue = newVal
    }
  },
  mounted() {
    this.selectedValue = this.value
  },
  methods: {
    selectOption(option) {
      this.selectedValue = option.value
      this.$emit('input', option.value)
      this.$emit('change', option) // 传递整个选项对象
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
  align-items: flex-end;
  justify-content: center;
}

.gender-picker-popup {
  width: 100%;
  background: #FFFFFF;
  border-radius: 30rpx 30rpx 0rpx 0rpx;
  padding: 36rpx 0 40rpx;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}

.popup-content {
  padding: 0 42rpx;
}

.popup-title {
  font-size: 32rpx;
  color: #000000;
  margin-bottom: 40rpx;
  display: block;
}

.options-container {
  display: flex;
  flex-direction: column;
  gap: 50rpx;
}

.option-button {
  width: 626rpx;
  height: 84rpx;
  background: #FFFFFF;
  border: 4rpx solid #c05af3; /* 紫色圆角边框 */
  border-radius: 180rpx; /* 圆角 */
  color: #000000;
  font-size: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 84rpx;
  font-weight: 400;
}

.option-button.selected {
  background: #F7E7FF;
  border-color: #c05af3; /* 选中时保持紫色边框 */
}

.option-button::after {
  border: none;
}
</style>



