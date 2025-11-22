<template>
  <view class="team-name-page">
    <!-- 顶部背景区域 -->
    <view class="header-background">
      <view class="banner-background"></view>
      <view class="header-tabs">
        <view class="tab-item">
          <text class="tab-text">队友信息</text>
        </view>
        <view class="tab-item active">
          <text class="tab-text">组队打卡</text>
        </view>
      </view>
    </view>
    
    <!-- 创建队名弹窗 -->
    <TeamNameModal
      :visible="true"
      @cancel="handleCancel"
      @confirm="handleConfirm"
    />
  </view>
</template>

<script>
import TeamNameModal from '../../components/TeamNameModal.vue'
import { setTeamName } from '../../services/match'

export default {
  components: {
    TeamNameModal
  },
  onLoad() {
    // 页面加载时检查页面栈
    const pages = getCurrentPages()
    console.log('📊 team-name 页面加载，当前页面栈深度:', pages ? pages.length : 0)
  },
  onBackPress(options) {
    // 拦截返回按钮，使用跳转替代返回
    console.log('🔙 onBackPress 被触发')
    this.handleCancel()
    return true // 返回 true 阻止默认返回行为
  },
  methods: {
    handleCancel() {
      // 取消创建队名时，跳转到打卡页面
      // 不使用 navigateBack，避免在页面栈第一页时出错
      console.log('❌ 取消创建队名，跳转到打卡页面')
      uni.reLaunch({
        url: '/pages/checkin-detail/index',
        fail: (err) => {
          console.warn('跳转到打卡页面失败:', err)
          // 如果 reLaunch 失败，尝试使用 switchTab（如果打卡页面是 tabBar 页面）
          uni.switchTab({
            url: '/pages/checkin-detail/index',
            fail: () => {
              // 如果还是失败，使用 navigateTo 作为最后的备选
              uni.navigateTo({
                url: '/pages/checkin-detail/index'
              })
            }
          })
        }
      })
    },
    
    async handleConfirm(teamName) {
      try {
        uni.showLoading({ title: '保存中...' })
        
        // 调用后端API保存队名
        const result = await setTeamName(teamName)
        console.log('队名保存成功:', result)
        
        uni.hideLoading()
        
        // 更新本地存储
        uni.setStorageSync('teamName', teamName)
        uni.setStorageSync('hasTeam', true)
        uni.removeStorageSync('justCreatedTeam')
        
        // 跳转到打卡页面，显示组队成功弹窗
        uni.reLaunch({
          url: '/pages/checkin-detail/index',
          fail: () => {
            uni.switchTab({
              url: '/pages/checkin-detail/index'
            })
          }
        })
      } catch (error) {
        uni.hideLoading()
        console.error('保存队名失败:', error)
        
        // 如果是因为队名已设置而失败，直接使用已有队名跳转
        if (error.message && error.message.includes('不可二次更改')) {
          uni.showToast({
            title: '队名已设置，不可修改',
            icon: 'none'
          })
          // 仍然跳转到打卡页面
          setTimeout(() => {
            uni.reLaunch({
              url: '/pages/checkin-detail/index'
            })
          }, 1500)
        } else {
          uni.showToast({
            title: '保存队名失败，请重试',
            icon: 'none'
          })
        }
      }
    }
  }
}
</script>

<style scoped>
.team-name-page {
  position: relative;
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(180deg, #F7E7FF 0%, #FFFFFF 100%);
}

/* 顶部背景区域 */
.header-background {
  position: relative;
  width: 100%;
  height: 156rpx; /* 对应78px */
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
</style>



