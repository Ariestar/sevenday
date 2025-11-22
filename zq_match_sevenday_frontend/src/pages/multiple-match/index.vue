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
            :class="{ 'input-error': errorMessage }"
            type="text" 
            placeholder="请输入" 
            v-model="studentNumber"
            @input="handleInput"
            placeholder-style="color: #CACDD9;"
          />
          <!-- 错误提示 -->
          <view v-if="errorMessage" class="error-message">
            <text class="error-text">{{ errorMessage }}</text>
          </view>
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
      invitationInfo: null,
      currentStudentNo: null, // 当前用户的学号
      errorMessage: '' // 错误提示信息
    }
  },
  onLoad() {
    // 检查是否有待处理的邀请
    this.checkPendingInvitation()
    // 获取当前用户的学号
    this.loadCurrentStudentNo()
  },
  onShow() {
    // 每次显示页面时也检查邀请（但不显示弹窗，只更新卡片）
    // 避免频繁弹窗干扰用户操作
    this.checkPendingInvitation()
  },
  methods: {
    async loadCurrentStudentNo() {
      // 获取当前用户的学号
      try {
        let currentUserInfo = authUtils.getUserInfo()
        
        // 如果本地存储没有学号，尝试从服务器获取
        if (!currentUserInfo || (!currentUserInfo.school_number && !currentUserInfo.studentNo && !currentUserInfo.student_number)) {
          try {
            const serverUserInfo = await getUserInfo()
            if (serverUserInfo) {
              currentUserInfo = serverUserInfo
              authUtils.setUserInfo(serverUserInfo)
            }
          } catch (err) {
            console.warn('获取用户信息失败:', err)
          }
        }
        
        // 保存当前用户的学号
        this.currentStudentNo = currentUserInfo?.school_number || currentUserInfo?.studentNo || currentUserInfo?.student_number || null
        console.log('🔍 当前用户学号已加载:', this.currentStudentNo)
      } catch (err) {
        console.error('加载当前用户学号失败:', err)
      }
    },
    
    handleInput(e) {
      // 实时检查输入的学号
      const inputValue = e.detail.value.trim()
      this.studentNumber = inputValue
      
      // 清空之前的错误提示
      this.errorMessage = ''
      
      // 如果输入为空，不检查
      if (!inputValue) {
        return
      }
      
      // 如果还没有加载当前用户学号，尝试加载
      if (!this.currentStudentNo) {
        this.loadCurrentStudentNo()
        // 延迟检查，等待学号加载完成
        setTimeout(() => {
          this.checkStudentNumber(inputValue)
        }, 100)
      } else {
        // 立即检查
        this.checkStudentNumber(inputValue)
      }
    },
    
    checkStudentNumber(inputValue) {
      // 检查输入的学号是否与当前用户学号相同
      if (this.currentStudentNo && inputValue === String(this.currentStudentNo).trim()) {
        this.errorMessage = '不能与自己组队'
      } else {
        this.errorMessage = ''
      }
    },
    
    async checkPendingInvitation() {
      try {
        console.log('🔍 开始检查邀请...')
        const result = await getInvitation()
        console.log('🔍 检查邀请结果 (完整):', JSON.stringify(result, null, 2))
        console.log('🔍 检查邀请结果类型:', typeof result)
        
        // 处理不同的响应格式
        // 情况1: result 是 {code, msg, data: {hasInvitation, invitation}}
        // 情况2: result 是 {hasInvitation, invitation} (已经提取了data)
        // 情况3: result 可能有嵌套的 data.data
        let invitationData = null
        
        // 先检查是否有嵌套的 data.data（根据后端实际返回格式）
        if (result && result.data && result.data.data) {
          invitationData = result.data.data
          console.log('🔍 从result.data.data提取数据:', invitationData)
        } else if (result && result.data) {
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
        console.log('🔍 hasInvitation类型:', typeof invitationData?.hasInvitation)
        console.log('🔍 invitation:', invitationData?.invitation)
        
        // 使用更宽松的判断条件，允许 truthy 值而不只是 === true
        if (invitationData && invitationData.hasInvitation && invitationData.invitation) {
          console.log('✅ 检测到待处理的邀请:', invitationData.invitation)
          this.hasPendingInvitation = true
          this.invitationInfo = invitationData.invitation
          console.log('✅ 邀请信息已设置:', {
            hasPendingInvitation: this.hasPendingInvitation,
            invitationInfo: this.invitationInfo
          })
        } else {
          console.log('ℹ️ 没有待处理的邀请')
          console.log('ℹ️ 判断详情:', {
            hasInvitationData: !!invitationData,
            hasInvitation: invitationData?.hasInvitation,
            hasInvitationObject: !!invitationData?.invitation
          })
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
      
      // 如果已经有错误提示（比如不能与自己组队），直接返回
      if (this.errorMessage) {
        uni.showToast({
          title: this.errorMessage,
          icon: 'none',
          duration: 2000
        })
        return
      }
      
      // 再次检查是否是自己和自己组队（双重验证）
      try {
        // 如果还没有加载当前用户学号，先加载
        if (!this.currentStudentNo) {
          await this.loadCurrentStudentNo()
        }
        
        // 检查输入的学号是否与当前用户学号相同
        const inputStudentNo = this.studentNumber.trim()
        
        if (this.currentStudentNo && inputStudentNo === String(this.currentStudentNo).trim()) {
          this.errorMessage = '不能与自己组队'
          uni.showToast({
            title: '不能和自己组队',
            icon: 'none',
            duration: 2000
          })
          return
        }
        
        // 如果无法获取当前用户学号，也阻止匹配（安全起见）
        if (!this.currentStudentNo) {
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
        
        // 检查响应格式，判断是否真的组队成功
        // 根据后端返回的结构：{code: "00000", msg: "您已经匹配成功", data: {...}}
        // 需要检查 data.data.team 或 data.team 是否存在
        // 如果只是发送了邀请，后端不会返回 team 对象，应该等待对方确认
        
        // 处理嵌套的 data 结构
        const innerData = result?.data?.data || result?.data || result
        const teamData = innerData?.team || result?.team
        
        console.log('📊 检查组队结果:', {
          result,
          innerData,
          teamData,
          hasTeam: !!teamData && (teamData.id || teamData.name)
        })
        
        // 只有当后端明确返回了 team 对象且有 id 或 name 时，才算组队成功
        // 如果后端返回 "您已经匹配成功" 但这是指邀请已发送（没有 team 对象），不算组队成功
        if (teamData && (teamData.id || teamData.name)) {
          // 真正组队成功（可能是双向邀请直接匹配成功）
          // 更新本地存储，标记已组队
          uni.setStorageSync('hasTeam', true)
          uni.setStorageSync('justCreatedTeam', true)
          
          // 检查后端返回的队名
          const teamNameFromAPI = teamData.name
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
          // 邀请已发送，等待对方确认
          // 不要标记为组队成功，不要设置 hasTeam
          uni.showToast({
            title: '邀请已发送，等待对方确认',
            icon: 'success'
          })
          
          // 清空输入框，保持当前页面
          this.studentNumber = ''
          
          // 刷新邀请状态，检查是否有新的邀请（可能是双向邀请）
          setTimeout(() => {
            this.checkPendingInvitation()
          }, 1000)
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

.student-input.input-error {
  border-color: #FF6B6B; /* 错误状态下的边框颜色 */
}

.error-message {
  margin-top: 20rpx;
  padding-left: 30rpx;
}

.error-text {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 28rpx;
  line-height: 34rpx;
  color: #FF6B6B;
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