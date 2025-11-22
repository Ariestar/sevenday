<template>
  <view class="mine-page">
    <!-- 用户信息卡片 -->
    <view class="user-info-card">
      <view class="avatar-container" @click="handleAvatarClick">
        <image 
          v-if="userInfo && userInfo.avatar && !userInfo.avatar.includes('default.jpg')" 
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
        <view class="user-welcome">
          <text class="welcome-text">欢迎回来！</text>
          <text class="user-name">{{ (userInfo && (userInfo.name || userInfo.username)) || '用户' }}</text>
          <text v-if="!userInfo || (!userInfo.name && !userInfo.username)" class="user-hint">点击下方"个人信息"完善资料</text>
        </view>
        <view class="user-badge">
          <text class="badge-text">已认证</text>
        </view>
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
      
      <!-- 退出登录按钮（已登录时显示） -->
      <view v-if="isAuthenticated" class="menu-divider"></view>
      <view v-if="isAuthenticated" class="menu-item logout-item" @click="handleLogout">
        <view class="menu-left">
          <text class="menu-text logout-text">退出登录</text>
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
      // 检查是否有token，只要有token就认为已认证
      try {
        if (!authUtils || !authUtils.getToken) {
          return false
        }
        const token = authUtils.getToken()
        return !!token
      } catch (e) {
        console.error('获取token失败:', e)
        return false
      }
    }
  },
  onLoad() {
    console.log('mine页面 onLoad')
    try {
      // 监听用户登出事件
      uni.$on('user-logout', this.handleUserLogout)
      // 页面加载时立即从本地存储获取用户信息，确保快速显示正确的登录状态
      this.initUserInfo()
    } catch (e) {
      console.error('mine页面 onLoad 错误:', e)
    }
  },
  onShow() {
    console.log('mine页面 onShow')
    try {
      // 触发TabBar更新，确保选中状态正确
      uni.$emit('tabbar-update')
      
      // 先同步从本地存储获取，确保页面立即显示正确的登录认证状态
      if (!authUtils) {
        console.error('authUtils 未定义')
        this.userInfo = {}
        return
      }
      
      const localUserInfo = authUtils.getUserInfo ? authUtils.getUserInfo() : null
      const token = authUtils.getToken ? authUtils.getToken() : null
      
      if (token) {
        // 有token说明已登录，显示用户信息（如果有的话）
        if (localUserInfo) {
          this.userInfo = localUserInfo
        } else {
          // 有token但没有本地用户信息，设置为空对象（会显示"已认证"但提示完善资料）
          this.userInfo = {}
        }
        // 异步从服务器获取最新信息
        this.loadUserInfo(true).catch(err => {
          console.error('从服务器加载用户信息失败:', err)
          // 即使加载失败，也保持当前状态
        })
      } else {
        // 没有token说明未登录，清空用户信息，显示未认证状态
        this.userInfo = {}
      }
    } catch (e) {
      console.error('mine页面 onShow 错误:', e)
      this.userInfo = {}
    }
  },
  onUnload() {
    // 移除事件监听
    uni.$off('user-logout', this.handleUserLogout)
  },
  methods: {
    initUserInfo() {
      // 同步初始化用户信息，不阻塞页面渲染
      try {
        if (!authUtils) {
          console.error('authUtils 未定义')
          this.userInfo = {}
          return
        }
        const localUserInfo = authUtils.getUserInfo ? authUtils.getUserInfo() : null
        const token = authUtils.getToken ? authUtils.getToken() : null
        
        if (token) {
          // 有token说明已登录
          this.userInfo = localUserInfo || {}
        } else {
          // 没有token说明未登录
          this.userInfo = {}
        }
      } catch (e) {
        console.error('初始化用户信息失败:', e)
        this.userInfo = {}
      }
    },
    async loadUserInfo(forceRefresh = false) {
      try {
        // 如果不是强制刷新，优先从本地存储获取用户信息
        if (!forceRefresh) {
          const localUserInfo = authUtils.getUserInfo()
          if (localUserInfo) {
            this.userInfo = localUserInfo || {}
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
            if (info) {
              authUtils.setUserInfo(this.userInfo)
            }
          } catch (err) {
            console.error('加载用户信息失败:', err)
            // 如果获取失败，可能token已过期或用户不存在，清除本地存储
            authUtils.logout()
            // 清空用户信息
            this.userInfo = {}
            // 触发用户登出事件
            uni.$emit('user-logout')
          }
        } else {
          // 如果没有token，尝试从本地存储获取
          const localUserInfo = authUtils.getUserInfo()
          if (localUserInfo) {
            this.userInfo = localUserInfo || {}
          } else {
            this.userInfo = {}
          }
        }
      } catch (err) {
        console.error('loadUserInfo 发生错误:', err)
        // 确保即使出错也有默认值
        this.userInfo = {}
      }
    },
    
    showLoginModal() {
      this.loginModalVisible = true
    },
    
    handleCloseLoginModal() {
      this.loginModalVisible = false
    },
    
    async handleLoginSuccess(userInfo) {
      // 登录成功后，更新本地用户信息（即使为空对象也可以）
      // 保存登录返回的用户信息到本地（可能是空对象，但token已保存）
      if (userInfo) {
        authUtils.setUserInfo(userInfo)
        this.userInfo = userInfo
      } else {
        // 如果没有用户信息，至少确保有token的情况下设置为已认证
        // token已经在LoginModal中保存了，这里只需要刷新状态
        this.userInfo = {}
      }
      
      // 关闭登录弹窗
      this.loginModalVisible = false
      
      // 尝试从服务器获取完整的用户信息（如果服务器有的话）
      try {
        const token = authUtils.getToken()
        if (token) {
          const info = await getUserInfo()
          if (info) {
            this.userInfo = info
            authUtils.setUserInfo(info)
          }
        }
      } catch (err) {
        // 获取用户信息失败不影响登录状态，token已经保存
        console.log('获取用户信息失败（可能用户信息为空），但不影响登录状态:', err)
      }
      
      // 登录成功，不再强制跳转到个人信息页面
      // 用户可以在"我的"页面看到已认证状态，也可以随时点击"个人信息"去填写
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
            // 确保 userInfo 存在
            if (!this.userInfo) {
              this.userInfo = {}
            }
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
    },
    
    handleUserLogout() {
      // 处理用户登出事件
      this.userInfo = {}
      console.log('用户已登出，清除本地状态')
    },
    
    handleLogout() {
      // 确认退出登录
      uni.showModal({
        title: '提示',
        content: '确定要退出登录吗？',
        success: (res) => {
          if (res.confirm) {
            // 清除认证信息
            authUtils.logout()
            // 清空用户信息
            this.userInfo = {}
            // 触发用户登出事件
            uni.$emit('user-logout')
            // 显示提示
            uni.showToast({
              title: '已退出登录',
              icon: 'success',
              duration: 2000
            })
            // 延迟刷新页面状态
            setTimeout(() => {
              this.loadUserInfo()
            }, 500)
          }
        }
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

/* 已认证状态 */
.user-welcome {
  display: flex;
  flex-direction: column;
}

.welcome-text {
  font-size: 28rpx;
  color: #666666;
  line-height: 34rpx;
  margin-bottom: 8rpx;
}

.user-name {
  font-size: 36rpx;
  font-weight: 600;
  color: #333333;
  line-height: 44rpx;
  margin-bottom: 8rpx;
}

.user-hint {
  font-size: 24rpx;
  color: #999999;
  line-height: 30rpx;
}

.user-badge {
  background: linear-gradient(90deg, #A100FE 0%, #FDB9E7 100%);
  border-radius: 20rpx;
  padding: 8rpx 16rpx;
}

.badge-text {
  font-size: 24rpx;
  color: #FFFFFF;
  line-height: 30rpx;
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

/* 退出登录按钮样式 */
.logout-item {
  color: #FF6B6B;
}

.logout-text {
  color: #FF6B6B !important;
}
</style>

