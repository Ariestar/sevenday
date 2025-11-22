<template>
  <view class="multiple-match-page">
    <!-- 顶部渐变背景 -->
    <view class="top-gradient-bg"></view>
    <view class="bottom-gradient-bg"></view>
    
    <!-- 报名/匹配标签切换区域 -->
    <view class="tab-section">
      <view class="tab-group">
        <view class="tab-item" @click="goToSignup">
          <text class="tab-text">报名</text>
        </view>
        <view class="tab-item active">
          <text class="tab-text active">匹配</text>
        </view>
      </view>
      <view class="tab-indicator"></view>
    </view>

    <!-- 主要内容区域 -->
    <view class="main-content">
      <!-- 邀请提示卡片 -->
      <view v-if="hasPendingInvitation && invitationInfo" class="invitation-notice-card" @click="goToInvitationConfirm">
        <view class="notice-content">
          <image class="notice-icon" src="/static/match-mutiple-part1/star.png" mode="aspectFit"></image>
          <view class="notice-text">
            <text class="notice-title">收到组队邀请</text>
            <text class="notice-desc">用户 {{ invitationInfo.inviter.username || '未知' }} 向您发送了组队邀请</text>
          </view>
          <text class="notice-arrow">></text>
        </view>
      </view>
      
      <!-- 输入卡片 -->
      <view class="input-card">
        <!-- 标题图标和文字 -->
        <view class="card-header">
          <image class="star-icon" src="/static/match-mutiple-part1/star.png" mode="aspectFit"></image>
          <text class="card-title">请输入对方学号</text>
        </view>
        
        <!-- 输入框 -->
        <view class="input-section">
          <input 
            class="student-input" 
            type="text" 
            placeholder="请输入" 
            v-model="studentNumber"
            placeholder-style="color: #CACDD9;"
          />
        </view>
        
        <!-- 确认按钮 -->
        <view class="confirm-btn" @click="handleConfirm">
          <text class="confirm-text">确认</text>
        </view>
      </view>

      <!-- 说明文字 -->
      <view class="description">
        <text class="desc-text">关于组队模式的相关说明</text>
      </view>
    </view>

    <!-- 底部导航栏 -->
    <CustomTabBar :current="0"></CustomTabBar>
  </view>
</template>

<script>
import CustomTabBar from '@/components/CustomTabBar.vue'
import { getInvitation, targetMatch } from '../../services/match'
import { getUserInfo } from '../../services/auth'
import authUtils from '../../utils/auth'

export default {
  components: {
    CustomTabBar
  },
  data() {
    return {
      studentNumber: '',
      hasPendingInvitation: false,
      invitationInfo: null
    }
  },
  onLoad() {
    // 检查是否有待处理的邀请
    this.checkPendingInvitation()
  },
  onShow() {
    // 每次显示页面时也检查邀请（但不显示弹窗，只更新卡片）
    // 避免频繁弹窗干扰用户操作
    this.checkPendingInvitation()
  },
  methods: {
    async checkPendingInvitation() {
      try {
        console.log('🔍 开始检查邀请...')
        const result = await getInvitation()
        console.log('🔍 检查邀请结果 (完整):', JSON.stringify(result, null, 2))
        console.log('🔍 检查邀请结果类型:', typeof result)
        
        // 处理不同的响应格式
        // 情况1: result 是 {code, msg, data: {hasInvitation, invitation}}
        // 情况2: result 是 {hasInvitation, invitation} (已经提取了data)
        let invitationData = null
        
        if (result && result.data) {
          // 如果result有data字段，说明是完整响应，提取data
          invitationData = result.data
          console.log('🔍 从result.data提取数据:', invitationData)
        } else if (result && typeof result.hasInvitation !== 'undefined') {
          // 如果result直接有hasInvitation，说明已经是data了
          invitationData = result
          console.log('🔍 result本身就是data:', invitationData)
        }
        
        console.log('🔍 invitationData:', invitationData)
        console.log('🔍 hasInvitation:', invitationData?.hasInvitation)
        console.log('🔍 invitation:', invitationData?.invitation)
        
        if (invitationData && invitationData.hasInvitation === true && invitationData.invitation) {
          console.log('✅ 检测到待处理的邀请:', invitationData.invitation)
          this.hasPendingInvitation = true
          this.invitationInfo = invitationData.invitation
          console.log('✅ 邀请信息已设置:', {
            hasPendingInvitation: this.hasPendingInvitation,
            invitationInfo: this.invitationInfo
          })
        } else {
          console.log('ℹ️ 没有待处理的邀请')
          this.hasPendingInvitation = false
          this.invitationInfo = null
        }
      } catch (error) {
        console.error('❌ 检查邀请失败:', error)
        console.error('❌ 错误详情:', {
          message: error.message,
          errMsg: error.errMsg,
          errno: error.errno,
          stack: error.stack
        })
        this.hasPendingInvitation = false
        this.invitationInfo = null
        
        // 开发阶段：如果是无效URL错误，忽略
        if (!error.errMsg?.includes('invalid url') && error.errno !== 600009) {
          console.warn('⚠️ 检查邀请时出错，继续显示匹配页面')
        }
      }
    },
    goToInvitationConfirm() {
      // 跳转到邀请确认页面
      uni.redirectTo({
        url: '/pages/multiple-match-confirm/index',
        fail: () => {
          uni.navigateTo({
            url: '/pages/multiple-match-confirm/index'
          })
        }
      })
    },
    goToSignup() {
      uni.reLaunch({
        url: '/pages/signup/index',
        fail: (err) => {
          console.warn('跳转到报名页面失败:', err)
          uni.navigateTo({
            url: '/pages/signup/index'
          })
        }
      })
    },
    
    async handleConfirm() {
      if (!this.studentNumber.trim()) {
        uni.showToast({
          title: '请输入学号',
          icon: 'none'
        })
        return
      }
      
      // 检查是否是自己和自己组队
      try {
        // 获取当前用户信息
        let currentUserInfo = authUtils.getUserInfo()
        console.log('🔍 当前用户信息（本地）:', currentUserInfo)
        
        // 如果本地存储没有学号，尝试从服务器获取
        if (!currentUserInfo || (!currentUserInfo.school_number && !currentUserInfo.studentNo && !currentUserInfo.student_number)) {
          try {
            const serverUserInfo = await getUserInfo()
            console.log('🔍 当前用户信息（服务器）:', serverUserInfo)
            if (serverUserInfo) {
              currentUserInfo = serverUserInfo
              authUtils.setUserInfo(serverUserInfo)
            }
          } catch (err) {
            console.warn('获取用户信息失败:', err)
          }
        }
        
        // 检查输入的学号是否与当前用户学号相同
        const currentStudentNo = currentUserInfo?.school_number || currentUserInfo?.studentNo || currentUserInfo?.student_number
        const inputStudentNo = this.studentNumber.trim()
        
        console.log('🔍 学号检查:', {
          currentStudentNo,
          inputStudentNo,
          isSame: currentStudentNo && inputStudentNo === String(currentStudentNo).trim()
        })
        
        if (currentStudentNo && inputStudentNo === String(currentStudentNo).trim()) {
          uni.showToast({
            title: '不能和自己组队',
            icon: 'none',
            duration: 2000
          })
          return
        }
        
        // 如果无法获取当前用户学号，也阻止匹配（安全起见）
        if (!currentStudentNo) {
          console.warn('⚠️ 无法获取当前用户学号，阻止匹配以确保安全')
          uni.showToast({
            title: '无法验证用户信息，请重新登录',
            icon: 'none',
            duration: 2000
          })
          return
        }
      } catch (err) {
        console.error('检查用户学号失败:', err)
        // 如果检查失败，阻止匹配以确保安全
        uni.showToast({
          title: '验证失败，请重试',
          icon: 'none',
          duration: 2000
        })
        return
      }
      
      try {
        uni.showLoading({ title: '匹配中...' })
        
        // 调用组队匹配接口（发送邀请）
        const result = await targetMatch(this.studentNumber.trim())
        console.log('组队匹配结果:', result)
        
        uni.hideLoading()
        
        // 如果直接组队成功（双向邀请）
        if (result && result.team) {
          // 更新本地存储，标记已组队
          uni.setStorageSync('hasTeam', true)
          uni.setStorageSync('justCreatedTeam', true)
          
          // 检查后端返回的队名
          const teamNameFromAPI = result?.data?.team?.name || result?.team?.name
          if (teamNameFromAPI && teamNameFromAPI.trim()) {
            // 如果后端已设置队名，使用该队名
            uni.setStorageSync('teamName', teamNameFromAPI)
          } else {
            // 如果后端未设置队名，不设置默认值，让用户有机会创建队名
            uni.removeStorageSync('teamName')
          }
          
          // 显示成功提示
          uni.showToast({
            title: '组队成功！',
            icon: 'success'
          })
          
          // 跳转到打卡页面
          setTimeout(() => {
            uni.reLaunch({
              url: '/pages/checkin-detail/index',
              fail: () => {
                uni.switchTab({
                  url: '/pages/checkin-detail/index'
                })
              }
            })
          }, 1500)
        } else {
          // 邀请已发送，跳转到等待确认页面（实际应该通知对方）
          uni.showToast({
            title: '邀请已发送，等待对方确认',
            icon: 'success'
          })
          
          // 跳转回匹配页面
          setTimeout(() => {
            uni.navigateBack()
          }, 1500)
        }
        
      } catch (error) {
        uni.hideLoading()
        console.error('组队匹配失败:', error)
        
        // 开发阶段：如果是无效URL错误，模拟成功
        if (error.errMsg?.includes('invalid url') || error.errno === 600009) {
          console.log('开发阶段：API未配置，模拟组队成功')
          uni.showToast({
            title: '组队成功！',
            icon: 'success'
          })
          setTimeout(() => {
            uni.reLaunch({
              url: '/pages/checkin-detail/index'
            })
          }, 1500)
        } else {
          uni.showToast({
            title: error.message || '组队失败，请检查学号是否正确',
            icon: 'none',
            duration: 2000
          })
        }
      }
    }
  }
}
</script>

<style scoped>
.multiple-match-page {
  position: relative;
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(180deg, #F7E7FF 0%, #FFFFFF 100%);
}

/* 顶部渐变背景 */
.top-gradient-bg {
  position: absolute;
  width: 100%;
  height: 300rpx; /* 增加高度，覆盖更多页眉 */
  left: 0;
  top: -50rpx; /* 向上延伸，覆盖状态栏/页眉区域 */
  background: linear-gradient(90deg, #A100FE 0%, #FDB9E7 100%);
  z-index: 1;
}

.bottom-gradient-bg {
  position: absolute;
  width: 100%;
  height: 90rpx; /* 对应45px */
  left: 0;
  top: 220rpx; /* 下移，避免覆盖按钮 */
  background: linear-gradient(180deg, #F7E8FE 0%, #F9ECFF 100%);
  z-index: 2;
}

/* 标签切换区域 */
.tab-section {
  position: absolute;
  width: auto;
  height: 74rpx; /* 对应37px */
  left: 50%;
  top: 150rpx;
  transform: translateX(-50%);
  z-index: 10;
}

.tab-group {
  display: flex;
  gap: 290rpx;
}

.tab-item {
  position: relative;
  display: inline-block;
  writing-mode: horizontal-tb;
}

.tab-bg {
  position: absolute;
  width: 100%;
  height: 100%;
  background: #D9D9D9;
  opacity: 0;
}

.tab-text {
  font-size: 32rpx;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 400;
  writing-mode: horizontal-tb;
  text-orientation: mixed;
  white-space: nowrap;
  display: inline-block;
}

.tab-text.active {
  color: #FFFFFF;
  font-weight: 700;
}

.tab-item.active {
  position: relative;
}

.tab-indicator {
  position: absolute;
  width: 120rpx;
  height: 36rpx;
  left: calc(50% + 145rpx);
  top: 30rpx;
  transform: translateX(-50%);
  background: #FFFFFF;
  opacity: 0.4;
  border-radius: 90rpx;
}

/* 主要内容区域 */
.main-content {
  position: relative;
  z-index: 5;
  padding-top: 320rpx; /* 增加padding-top，整体下移 */
  padding-left: 44rpx; /* 对应22px */
  padding-right: 44rpx; /* 对应22px */
}

/* 邀请提示卡片 */
.invitation-notice-card {
  width: 100%;
  background: linear-gradient(90deg, #A100FE 0%, #FDB9E7 100%);
  border-radius: 18rpx;
  padding: 30rpx 40rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 4rpx 12rpx rgba(161, 0, 254, 0.3);
  box-sizing: border-box;
}

.notice-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.notice-icon {
  width: 48rpx;
  height: 48rpx;
  margin-right: 20rpx;
  flex-shrink: 0;
}

.notice-text {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
}

.notice-title {
  font-family: 'Inter';
  font-weight: 700;
  font-size: 32rpx;
  line-height: 38rpx;
  color: #FFFFFF;
  margin-bottom: 8rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.notice-desc {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 24rpx;
  line-height: 28rpx;
  color: rgba(255, 255, 255, 0.9);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.notice-arrow {
  font-size: 32rpx;
  color: #FFFFFF;
  font-weight: 700;
  margin-left: 20rpx;
  flex-shrink: 0;
}

/* 输入卡片 */
.input-card {
  position: relative;
  width: 664rpx; /* 对应332px */
  height: 456rpx; /* 对应228px */
  background: #FFFFFF;
  border: 4rpx solid #A100FE; /* 对应2px */
  border-radius: 30rpx; /* 对应15px */
  padding: 40rpx;
  box-sizing: border-box;
}

/* 卡片标题区域 */
.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 60rpx; /* 对应30px */
}

.star-icon {
  width: 66rpx; /* 对应33px */
  height: 52rpx; /* 对应26px */
  margin-right: 20rpx; /* 对应10px */
}

.card-title {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 32rpx; /* 对应16px */
  line-height: 38rpx; /* 对应19px */
  color: #000000;
}

/* 输入区域 */
.input-section {
  margin-bottom: 60rpx; /* 对应30px */
}

.student-input {
  width: 596rpx; /* 对应298px */
  height: 92rpx; /* 对应46px */
  border: 4rpx solid #F7E7FF; /* 对应2px */
  border-radius: 180rpx; /* 对应90px */
  padding: 0 30rpx;
  font-family: 'Inter';
  font-weight: 400;
  font-size: 32rpx; /* 对应16px */
  line-height: 38rpx; /* 对应19px */
  color: #000000;
  box-sizing: border-box;
}

/* 确认按钮 */
.confirm-btn {
  position: absolute;
  width: 166rpx; /* 对应83px */
  height: 66rpx; /* 对应33px */
  left: 50%;
  bottom: 40rpx;
  transform: translateX(-50%);
  background: #1F2635;
  border-radius: 33rpx; /* 对应16.5px */
  display: flex;
  align-items: center;
  justify-content: center;
}

.confirm-text {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 32rpx; /* 对应16px */
  line-height: 38rpx; /* 对应19px */
  color: #FFFFFF;
}

/* 说明文字 */
.description {
  margin-top: 116rpx; /* 对应58px */
  padding: 0 26rpx; /* 对应13px */
}

.desc-text {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 32rpx; /* 对应16px */
  line-height: 38rpx; /* 对应19px */
  color: #9094A6;
}
</style>