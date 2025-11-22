<template>
  <view class="mine-page">
    <!-- 用户信息卡片 -->
    <view class="user-info-card">
      <view class="avatar-container" @click="handleAvatarClick">
        <image 
          v-if="userInfo.avatar && !userInfo.avatar.includes('default.jpg')" 
          :src="userInfo.avatar" 
          class="user-avatar" 
          mode="aspectFill"
        />
        <view v-else class="avatar-placeholder">
          <image src="/static/square/user-icon.png" class="default-avatar" mode="aspectFill" />
        </view>
      </view>
      
      <!-- 未认证状态 -->
      <view v-if="!isAuthenticated" class="user-status-section">
        <view class="auth-prompt">
          <text class="auth-title">未登录/认证</text>
          <text class="auth-subtitle">请先进行身份认证</text>
        </view>
        <button class="auth-btn" @click="showLoginModal">去认证</button>
      </view>
      
      <!-- 已认证状态 -->
      <view v-else class="user-status-section">
        <view class="auth-prompt">
          <text class="auth-title">{{ userInfo.name || userInfo.username || '用户' }}</text>
          <text class="auth-subtitle">欢迎回来！</text>
        </view>
        <button class="auth-btn" disabled>
          <text class="auth-btn-text">已认证</text>
        </button>
      </view>
    </view>

    <!-- 功能菜单卡片 -->
    <view class="function-menu-card">
      <view class="menu-item" @click="goToPersonalInfo">
        <view class="menu-left">
          <text class="menu-text">个人信息</text>
        </view>
        <text class="arrow-icon">›</text>
      </view>
      
      <view class="menu-divider"></view>
      
      <view class="menu-item" @click="goToAbout">
        <view class="menu-left">
          <text class="menu-text">关于我们</text>
        </view>
        <text class="arrow-icon">›</text>
      </view>
      
      <view class="menu-divider"></view>
      
      <view class="menu-item" @click="goToGuide">
        <view class="menu-left">
          <text class="menu-text">使用导引</text>
        </view>
        <text class="arrow-icon">›</text>
      </view>
    </view>
    
    <!-- 空白区域 -->
    <view class="blank-area"></view>
    
    <!-- 登录弹窗 -->
    <LoginModal 
      :visible="loginModalVisible" 
      @close="handleCloseLoginModal"
      @login-success="handleLoginSuccess"
    />
    
    <!-- 自定义 TabBar -->
    <CustomTabBar :current="3" />
  </view>
</template>

<script>
import { getUserInfo } from '../../services/auth'
import { uploadAvatar } from '../../services/upload'
import { GENDER_OPTIONS } from '../../utils/constants'
import authUtils from '../../utils/auth'
import CustomTabBar from '../../components/CustomTabBar.vue'
import LoginModal from '../../components/LoginModal.vue'

export default {
  components: {
    CustomTabBar,
    LoginModal
  },
  data() {
    return {
      userInfo: {},
      loginModalVisible: false
    }
  },
  computed: {
    isAuthenticated() {
      return authUtils.isAuthenticated()
    }
  },
  onShow() {
    this.loadUserInfo()
    // 触发TabBar更新，确保选中状态正确
    uni.$emit('tabbar-update')
  },
  methods: {
    async loadUserInfo(forceRefresh = false) {
      // 如果不是强制刷新，优先从本地存储获取用户信息
      if (!forceRefresh) {
        const localUserInfo = authUtils.getUserInfo()
        if (localUserInfo) {
          this.userInfo = localUserInfo
          return
        }
      }
      
      // 如果有token，尝试从服务器获取
      const token = authUtils.getToken()
      if (token) {
        try {
          const info = await getUserInfo()
          this.userInfo = info || {}
          // 保存到本地存储
          authUtils.setUserInfo(this.userInfo)
        } catch (err) {
          console.error('加载用户信息失败:', err)
          // 如果获取失败，可能token已过期，清除本地存储
          authUtils.logout()
        }
      } else {
        // 如果没有token，尝试从本地存储获取
        const localUserInfo = authUtils.getUserInfo()
        if (localUserInfo) {
          this.userInfo = localUserInfo
        }
      }
    },
    
    showLoginModal() {
      this.loginModalVisible = true
    },
    
    handleCloseLoginModal() {
      this.loginModalVisible = false
    },
    
    async handleLoginSuccess(userInfo) {
      // 登录成功后，强制从服务器重新加载用户信息以确保数据最新
      await this.loadUserInfo(true) // 强制刷新
      this.loginModalVisible = false
      // 登录成功后跳转到报名页面（首页）填写信息
      setTimeout(() => {
        uni.navigateTo({
          url: '/pages/signup/index'
        })
      }, 500) // 延迟500ms，让登录成功提示先显示
    },
    
    handleAvatarClick() {
      if (!this.isAuthenticated) {
        this.showLoginModal()
        return
      }
      this.chooseAvatar()
    },
    
    async chooseAvatar() {
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera'],
        success: async (res) => {
          const tempFilePath = res.tempFilePaths[0]
          uni.showLoading({ title: '上传中' })
          try {
            const uploadRes = await uploadAvatar(tempFilePath)
            this.userInfo.avatar = uploadRes.url
            // 更新本地存储
            authUtils.setUserInfo(this.userInfo)
            uni.hideLoading()
            uni.showToast({ title: '头像上传成功', icon: 'success' })
          } catch (error) {
            uni.hideLoading()
            uni.showToast({ title: '头像上传失败', icon: 'none' })
            console.error('上传头像失败', error)
          }
        },
        fail: (err) => {
          console.error('选择图片失败', err)
        }
      })
    },
    
    goToPersonalInfo() {
      uni.navigateTo({
        url: '/pages/personal-info/index'
      })
    },
    
    goToAbout() {
      uni.navigateTo({
        url: '/pages/about/index'
      })
    },
    
    goToGuide() {
      uni.navigateTo({
        url: '/pages/guide/index'
      })
    }
  }
}
</script>

<style scoped>
.mine-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #F7E8FE 0%, #FFFEFF 100%);
  padding: 40rpx 32rpx 146rpx; /* 为 TabBar 留出空间 */
}

/* 用户信息卡片 */
.user-info-card {
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 40rpx;
  margin-bottom: 32rpx;
  display: flex;
  align-items: center;
  min-height: 160rpx;
  box-shadow: 0 8rpx 24rpx rgba(161, 0, 254, 0.08);
}

.avatar-container {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 32rpx;
  flex-shrink: 0;
}

.user-avatar {
  width: 100%;
  height: 100%;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #F5F5F5;
}

.default-avatar {
  width: 80rpx;
  height: 80rpx;
  opacity: 0.6;
}

.user-status-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* 未认证状态 */
.auth-prompt {
  display: flex;
  flex-direction: column;
}

.auth-title {
  font-size: 36rpx;
  font-weight: 600;
  color: #333333;
  line-height: 44rpx;
  margin-bottom: 8rpx;
}

.auth-subtitle {
  font-size: 28rpx;
  color: #666666;
  line-height: 34rpx;
}

.auth-btn {
  width: 140rpx;
  height: 64rpx;
  background: linear-gradient(90deg, #A100FE 0%, #FDB9E7 100%);
  color: #FFFFFF;
  font-size: 28rpx;
  border-radius: 32rpx;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

.auth-btn::after {
  display: none;
}

.auth-btn[disabled] {
  opacity: 0.6;
}

.auth-btn-text {
  font-size: 28rpx;
  color: #FFFFFF;
}

/* 功能菜单卡片 */
.function-menu-card {
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 0;
  box-shadow: 0 8rpx 24rpx rgba(161, 0, 254, 0.08);
}

.menu-item {
  height: 120rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 40rpx;
}

.menu-left {
  display: flex;
  align-items: center;
}

.menu-icon-circle {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 24rpx;
}

.menu-icon-circle.personal-info {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
}

.menu-icon-circle.about-us {
  background: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%);
}

.menu-icon-circle.usage-guide {
  background: linear-gradient(135deg, #A8E6CF 0%, #3D9970 100%);
}

.menu-icon {
  font-size: 32rpx;
  color: #FFFFFF;
}

.menu-text {
  font-size: 32rpx;
  color: #333333;
  font-weight: 500;
}

.arrow-icon {
  font-size: 32rpx;
  color: #CCCCCC;
}

.menu-divider {
  height: 2rpx;
  background: linear-gradient(90deg, transparent 0%, #F0F0F0 50%, transparent 100%);
  margin: 0 40rpx;
}

/* 空白区域 */
.blank-area {
  flex: 1;
  min-height: 100rpx;
}
</style>

