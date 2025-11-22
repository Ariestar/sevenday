<template>
  <view class="custom-tab-bar">
    <view
      v-for="(item, index) in visibleTabList"
      :key="index"
      class="tab-item"
      :class="{ active: currentIndex === getOriginalIndex(index) }"
      @click="switchTab(getOriginalIndex(index))"
    >
      <view class="tab-icon-wrapper">
        <image 
          :src="currentIndex === getOriginalIndex(index) ? item.selectedIconPath : item.iconPath" 
          class="tab-icon" 
          :class="{ active: currentIndex === getOriginalIndex(index) }"
          mode="aspectFit"
        />
      </view>
      <text class="tab-text" :class="{ active: currentIndex === getOriginalIndex(index) }">
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
      hasTeam: false,
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
  computed: {
    visibleTabList() {
      // 如果已组队，隐藏第一个标签（报名-匹配）
      if (this.hasTeam) {
        return this.tabList.slice(1)
      }
      return this.tabList
    }
  },
  watch: {
    current: {
      immediate: true,
      handler(val) {
        if (val !== undefined && val !== null && val >= 0) {
          this.currentIndex = val
        }
        this.$nextTick(() => {
          this.setCurrentIndex()
        })
      }
    }
  },
  mounted() {
    this.checkTeamStatus(true) // 传入 true 表示应用启动时检查，需要从 API 获取最新状态
    this.setCurrentIndex()
    uni.$on('tabbar-update', () => {
      this.$nextTick(() => {
        this.checkTeamStatus()
        this.setCurrentIndex()
      })
    })
  },
  beforeDestroy() {
    uni.$off('tabbar-update')
  },
  activated() {
    this.checkTeamStatus(true) // 组件激活时也强制检查
    this.setCurrentIndex()
  },
  methods: {
    async checkTeamStatus(forceCheck = false) {
      // 检查组队状态
      const localHasTeam = uni.getStorageSync('hasTeam')
      this.hasTeam = !!localHasTeam
      
      // 如果强制检查（应用启动时）或本地没有组队状态，尝试从 API 获取
      if (forceCheck || !localHasTeam) {
        const token = uni.getStorageSync('token')
        if (token) {
          try {
            // 动态导入 getTeamInfo 避免循环依赖
            const { getTeamInfo } = await import('../services/match')
            const res = await getTeamInfo()
            if (res && res.team) {
              this.hasTeam = true
              uni.setStorageSync('hasTeam', true)
              if (res.team.name) {
                uni.setStorageSync('teamName', res.team.name)
              }
            } else {
              this.hasTeam = false
              uni.removeStorageSync('hasTeam')
            }
          } catch (err) {
            console.log('从 API 检查组队状态失败，使用本地存储:', err)
            // 如果 API 调用失败，使用本地存储的值
            this.hasTeam = !!localHasTeam
          }
        }
      }
      
      // 如果已组队且当前在报名-匹配页面，自动跳转到打卡页面
      if (this.hasTeam) {
        const pages = getCurrentPages()
        if (pages.length > 0) {
          const currentPage = pages[pages.length - 1]
          const route = currentPage.route
          const normalizedRoute = route.startsWith('/') ? route.substring(1) : route
          
          // 如果在报名或匹配页面，跳转到打卡页面
          if (normalizedRoute === 'pages/signup/index' || 
              normalizedRoute === 'pages/multiple-match/index' ||
              normalizedRoute === 'pages/single-match/index') {
            setTimeout(() => {
              uni.switchTab({
                url: '/pages/checkin-detail/index',
                success: () => {
                  console.log('已组队，自动跳转到打卡页面')
                },
                fail: () => {
                  uni.reLaunch({
                    url: '/pages/checkin-detail/index'
                  })
                }
              })
            }, 300)
          }
        }
      }
    },
    getOriginalIndex(visibleIndex) {
      // 将可见列表的索引转换为原始列表的索引
      // 如果已组队，需要加1（因为隐藏了第一个）
      if (this.hasTeam) {
        return visibleIndex + 1
      }
      return visibleIndex
    },
    setCurrentIndex() {
      const pages = getCurrentPages()
      if (pages.length === 0) return
      
      const currentPage = pages[pages.length - 1]
      const route = currentPage.route
      
      const normalizedRoute = route.startsWith('/') ? route.substring(1) : route
      
      // 如果已组队且在报名或匹配页面，不设置索引（因为会跳转）
      if (this.hasTeam && (normalizedRoute === 'pages/signup/index' || 
                           normalizedRoute === 'pages/multiple-match/index' ||
                           normalizedRoute === 'pages/single-match/index')) {
        return
      }
      
      if (normalizedRoute === 'pages/signup/index' && !this.hasTeam) {
        this.currentIndex = 0
        return
      }
      
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
      }
    },
    switchTab(index) {
      if (this.currentIndex === index) {
        return
      }
      
      // 如果已组队，不允许点击第一个标签（报名-匹配）
      if (this.hasTeam && index === 0) {
        return
      }
      
      if (index === 0 && !this.hasTeam) {
        this.currentIndex = index
        
        uni.reLaunch({
          url: '/pages/signup/index',
          success: () => {
            setTimeout(() => {
              this.setCurrentIndex()
            }, 100)
          },
          fail: (err) => {
            console.warn('跳转到报名页面失败:', err)
            uni.navigateTo({
              url: '/pages/signup/index',
              fail: () => {
                this.setCurrentIndex()
              }
            })
          }
        })
        return
      }
      
      const path = this.tabList[index].pagePath
      const url = path.startsWith('/') ? path : '/' + path
      
      const previousIndex = this.currentIndex
      this.currentIndex = index
      
      uni.switchTab({
        url: url,
        success: () => {
          setTimeout(() => {
            this.setCurrentIndex()
          }, 100)
        },
        fail: (err) => {
          const errorMsg = err?.errMsg || String(err)
          if (errorMsg.includes('INVALID_LOGIN') || errorMsg.includes('access_token')) {
            try {
              uni.reLaunch({
                url: url,
                fail: () => {
                  console.warn('降级方案也失败，但UI状态已更新')
                }
              })
            } catch (e) {
              console.error('所有切换方式都失败:', e)
            }
          } else {
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
