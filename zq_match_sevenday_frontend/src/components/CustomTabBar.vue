<template>
  <view class="custom-tab-bar">
    <view
      v-for="(item, index) in tabList"
      :key="index"
      class="tab-item"
      :class="{ active: currentIndex === index }"
      @click="switchTab(index)"
    >
      <view class="tab-icon-wrapper">
        <!-- 使用图片图标，根据选中状态显示不同图标 -->
        <image 
          :src="currentIndex === index ? item.selectedIconPath : item.iconPath" 
          class="tab-icon" 
          :class="{ active: currentIndex === index }"
          mode="aspectFit"
        />
      </view>
      <text class="tab-text" :class="{ active: currentIndex === index }">
        {{ item.text }}
      </text>
    </view>
  </view>
</template>

<script>
export default {
  name: 'CustomTabBar',
  props: {
    current: {
      type: Number,
      default: 0
    }
  },
  data() {
    return {
      currentIndex: 0,
      tabList: [
        {
          pagePath: 'pages/multiple-match/index',
          text: '报名-匹配',
          iconPath: '/static/navigation/match-off.png',
          selectedIconPath: '/static/navigation/match-on.png'
        },
        {
          pagePath: 'pages/checkin-detail/index',
          text: '打卡',
          iconPath: '/static/navigation/checkin-off.png',
          selectedIconPath: '/static/navigation/checkin-on.png'
        },
        {
          pagePath: 'pages/square/index',
          text: '广场',
          iconPath: '/static/navigation/square-off.png',
          selectedIconPath: '/static/navigation/square-on.png'
        },
        {
          pagePath: 'pages/mine/index',
          text: '我的',
          iconPath: '/static/navigation/mine-off.png',
          selectedIconPath: '/static/navigation/mine-on.png'
        }
      ]
    }
  },
  watch: {
    current: {
      immediate: true,
      handler(val) {
        // 如果传入的current值有效，先设置，然后通过路由检测确认
        if (val !== undefined && val !== null && val >= 0) {
          this.currentIndex = val
        }
        // 无论prop值如何，都通过路由检测来确保准确性
        this.$nextTick(() => {
          this.setCurrentIndex()
        })
      }
    }
  },
  mounted() {
    // 根据当前页面路径设置选中状态
    this.setCurrentIndex()
    // 监听页面显示事件，确保页面切换时更新TabBar状态
    uni.$on('tabbar-update', () => {
      this.$nextTick(() => {
        this.setCurrentIndex()
      })
    })
  },
  beforeDestroy() {
    // 移除事件监听
    uni.$off('tabbar-update')
  },
  activated() {
    // keep-alive 激活时更新状态
    this.setCurrentIndex()
  },
  methods: {
    setCurrentIndex() {
      const pages = getCurrentPages()
      if (pages.length === 0) return
      
      const currentPage = pages[pages.length - 1]
      const route = currentPage.route // 获取当前页面路由，格式：pages/multiple-match/index
      
      // 标准化路由路径（移除前导斜杠）
      const normalizedRoute = route.startsWith('/') ? route.substring(1) : route
      
      // 特殊处理：报名页面应该映射到第一个tab（报名-匹配）
      if (normalizedRoute === 'pages/signup/index') {
        this.currentIndex = 0
        return
      }
      
      // 匹配页面路径（支持多种格式）
      const index = this.tabList.findIndex(item => {
        const normalizedItemPath = item.pagePath.startsWith('/') ? item.pagePath.substring(1) : item.pagePath
        return normalizedItemPath === normalizedRoute || 
               item.pagePath === route || 
               item.pagePath === '/' + route ||
               '/' + item.pagePath === '/' + route ||
               normalizedItemPath === route
      })
      
      if (index !== -1) {
        this.currentIndex = index
        console.log(`CustomTabBar: 检测到路由 ${route}，设置为tab ${index}`)
      } else {
        console.log(`CustomTabBar: 未找到匹配的路由 ${route}`)
      }
    },
    switchTab(index) {
      if (this.currentIndex === index) {
        return
      }
      
      // 第一个tab（报名-匹配）应该跳转到报名页面，而不是多人匹配页面
      if (index === 0) {
        // 先更新UI状态
        this.currentIndex = index
        
        // 跳转到报名页面
        uni.reLaunch({
          url: '/pages/signup/index',
          success: () => {
            console.log('成功跳转到报名页面')
            // 延迟更新状态，确保页面已加载完成
            setTimeout(() => {
              this.setCurrentIndex()
            }, 100)
          },
          fail: (err) => {
            console.warn('跳转到报名页面失败:', err)
            // 尝试 navigateTo 作为降级
            uni.navigateTo({
              url: '/pages/signup/index',
              fail: () => {
                console.error('所有跳转方式都失败')
                // 恢复UI状态
                this.setCurrentIndex()
              }
            })
          }
        })
        return
      }
      
      const path = this.tabList[index].pagePath
      // 确保路径格式正确（uni.switchTab 需要路径以 / 开头）
      const url = path.startsWith('/') ? path : '/' + path
      
      // 先更新UI状态，提供更好的用户体验
      const previousIndex = this.currentIndex
      this.currentIndex = index
      
      // 尝试切换Tab
      uni.switchTab({
        url: url,
        success: () => {
          console.log('成功切换到Tab:', index)
          // 延迟更新状态，确保页面已切换完成
          setTimeout(() => {
            this.setCurrentIndex()
          }, 100)
        },
        fail: (err) => {
          console.warn('切换 Tab 失败:', err)
          // 如果是游客模式错误（INVALID_LOGIN），保持UI状态已更新
          const errorMsg = err?.errMsg || String(err)
          if (errorMsg.includes('INVALID_LOGIN') || errorMsg.includes('access_token')) {
            // 游客模式下，UI状态已更新，尝试使用 reLaunch 作为降级方案
            console.warn('游客模式：无法使用 switchTab，尝试降级方案')
            try {
              uni.reLaunch({
                url: url,
                fail: () => {
                  // 如果 reLaunch 也失败，至少UI状态已经更新了
                  console.warn('降级方案也失败，但UI状态已更新')
                }
              })
            } catch (e) {
              console.error('所有切换方式都失败:', e)
              // 即使所有方式都失败，UI状态已经更新，用户体验不受影响
            }
          } else {
            // 其他错误，恢复之前的选中状态
            this.currentIndex = previousIndex
          }
        }
      })
    }
  }
}
</script>

<style scoped>
.custom-tab-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 100rpx;
  background-color: #ffffff;
  border-top: 1rpx solid #e5e5e5;
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding-bottom: env(safe-area-inset-bottom);
  z-index: 1000;
  box-shadow: 0 -2rpx 10rpx rgba(0, 0, 0, 0.05);
}

.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 10rpx 0;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tab-item.active {
  transform: scale(1.05);
}

.tab-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 48rpx;
  margin-bottom: 4rpx;
}

.tab-icon {
  width: 48rpx;
  height: 48rpx;
  transition: all 0.3s ease;
  display: block;
}

.tab-icon.active {
  transform: scale(1.1);
}

.tab-text {
  font-size: 20rpx;
  color: #999999;
  line-height: 1.2;
  transition: color 0.3s ease;
}

.tab-text.active {
  color: #667eea;
  font-weight: bold;
}
</style>

