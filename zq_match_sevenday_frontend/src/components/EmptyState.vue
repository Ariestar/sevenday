<template>
  <view class="empty-state">
    <image v-if="imageSrc" :src="imageSrc" class="empty-image" mode="aspectFit" />
    <text class="empty-text">{{ displayMessage }}</text>
    <text v-if="subText" class="empty-subtext">{{ subText }}</text>
    <button v-if="buttonText" class="empty-button" @click="handleClick">
      {{ buttonText }}
    </button>
  </view>
</template>

<script>
export default {
  name: 'EmptyState',
  props: {
    // 空状态类型：'no-signup', 'no-expectation', 'no-team', 'default'
    type: {
      type: String,
      default: 'default'
    },
    // 也支持直接传入图片路径（优先级高于 type）
    image: {
      type: String,
      default: ''
    },
    // 兼容旧的 text 属性
    text: {
      type: String,
      default: ''
    },
    // 新的 message 属性
    message: {
      type: String,
      default: ''
    },
    subText: {
      type: String,
      default: ''
    },
    buttonText: {
      type: String,
      default: ''
    }
  },
  computed: {
    imageSrc() {
      // 如果直接传入了图片路径，优先使用
      if (this.image) {
        return this.image
      }
      
      // 根据类型选择对应的空状态图片
      const imageMap = {
        'no-signup': '/static/empty/no-signup.png',
        'no-expectation': '/static/empty/no-expectation.png',
        'no-team': '/static/empty/no-team.png',
        'default': '/static/square/user-icon.png'
      }
      return imageMap[this.type] || imageMap.default
    },
    displayMessage() {
      // 优先使用 message，兼容旧的 text 属性
      return this.message || this.text || '暂无数据'
    }
  },
  methods: {
    handleClick() {
      this.$emit('click')
    }
  }
}
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120rpx 60rpx;
}

.empty-image {
  width: 320rpx;
  height: 320rpx;
  margin-bottom: 40rpx;
}

.empty-text {
  font-size: 32rpx;
  color: #666;
  margin-bottom: 16rpx;
}

.empty-subtext {
  font-size: 28rpx;
  color: #999;
  margin-bottom: 40rpx;
}

.empty-button {
  padding: 20rpx 60rpx;
  font-size: 28rpx;
  color: #fff;
  background-color: #07c160;
  border-radius: 8rpx;
}
</style>

