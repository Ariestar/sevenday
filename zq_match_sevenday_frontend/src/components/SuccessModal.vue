<template>
  <view v-if="visible" class="popup-mask" @click="handleClose">
    <view class="success-modal" @click.stop>
      <image v-if="showImage" :src="imageSrc" class="success-image" mode="aspectFit" />
      <text class="success-title">{{ displayTitle }}</text>
      <text v-if="subtitle" class="success-subtitle">{{ subtitle }}</text>
      <button class="confirm-button" @click="handleClose">确定</button>
    </view>
  </view>
</template>

<script>
export default {
  name: 'SuccessModal',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    type: {
      type: String,
      default: 'signup' // signup: 报名成功, save: 保存成功, match: 匹配成功, team: 组队成功
    },
    title: {
      type: String,
      default: ''
    },
    subtitle: {
      type: String,
      default: ''
    }
  },
  computed: {
    imageSrc() {
      const imageMap = {
        'signup': '/static/success/match-success.png',
        'save': '/static/success/save-success.png',
        'match': '/static/success/match-success.png',
        'team': '/static/success/team-created.png.png',
        'auth': '/static/success/auth-success.png'
      }
      return imageMap[this.type] || imageMap.signup
    },
    displayTitle() {
      if (this.title) return this.title
      const titleMap = {
        'signup': '报名成功！',
        'save': '保存成功！',
        'match': '匹配成功！',
        'team': '组队成功！',
        'auth': '认证成功！'
      }
      return titleMap[this.type] || titleMap.signup
    },
    showImage() {
      // 报名成功时不显示图片，只显示文字
      return this.type !== 'signup'
    }
  },
  methods: {
    handleClose() {
      this.$emit('update:visible', false)
      this.$emit('close')
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

.success-modal {
  width: 626rpx;
  background: #FFFFFF;
  border-radius: 18rpx;
  padding: 80rpx 64rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
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

.success-image {
  width: 320rpx;
  height: 320rpx;
  margin-bottom: 40rpx;
}

.success-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #1F2635;
  margin-bottom: 20rpx;
  text-align: center;
}

.success-subtitle {
  font-size: 28rpx;
  color: #9094A6;
  margin-bottom: 60rpx;
  text-align: center;
}

.confirm-button {
  width: 100%;
  height: 88rpx;
  background: #1F2635;
  border-radius: 180rpx;
  color: #FFFFFF;
  font-size: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
}

.confirm-button::after {
  border: none;
}
</style>
