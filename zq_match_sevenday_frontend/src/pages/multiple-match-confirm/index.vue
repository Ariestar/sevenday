<template>
  <view class="multiple-match-confirm-page">
    <!-- 顶部渐变背景 -->
    <view class="top-gradient-bg"></view>
    <view class="bottom-gradient-bg"></view>
    
    <!-- 报名/匹配标签切换区域 -->
    <view class="tab-section">
      <view class="tab-group">
        <view class="tab-item" @click="goToSignup">
          <view class="tab-bg"></view>
          <text class="tab-text">报名</text>
        </view>
        <view class="tab-item active">
          <view class="tab-bg"></view>
          <text class="tab-text active">匹配</text>
          <view class="tab-indicator"></view>
        </view>
      </view>
    </view>

    <!-- 你的期望 / 智能匹配 / 确认组队 标签 -->
    <view class="progress-tab-section">
      <view class="progress-tab-group">
        <view class="progress-tab-item" @click="goToExpectation">
          <text class="progress-tab-text">你的期望</text>
        </view>
        <view class="progress-tab-item" @click="goToIntelligentMatch">
          <text class="progress-tab-text">智能匹配</text>
        </view>
        <view class="progress-tab-item active">
          <text class="progress-tab-text active">确认组队</text>
        </view>
      </view>
    </view>

    <!-- 主要内容区域 -->
    <view class="main-content">
      <!-- 邀请方信息卡片 -->
      <view class="info-card">
        <!-- 标题 -->
        <view class="card-header">
          <image class="star-icon" src="/static/match-mutiple-part1/star.png" mode="aspectFit"></image>
          <text class="card-title">邀请方的信息</text>
        </view>
        
        <!-- 用户头像 -->
        <view class="avatar-section">
          <view class="avatar-circle">
            <image v-if="inviterInfo.avatar" :src="inviterInfo.avatar" class="avatar-image" mode="aspectFill"></image>
            <view v-else class="avatar-icon"></view>
          </view>
        </view>
        
        <!-- 用户信息标签 -->
        <view class="info-tags">
          <view class="info-tag">
            <text class="tag-text">{{ inviterInfo.gender || '性别' }}</text>
          </view>
          <view class="info-tag">
            <text class="tag-text">{{ inviterInfo.education || '身份' }}</text>
          </view>
        </view>
        
        <view class="info-tags">
          <view class="info-tag large">
            <text class="tag-text">{{ inviterInfo.majorCategory || '大类' }}</text>
          </view>
          <view class="info-tag large">
            <text class="tag-text">{{ inviterInfo.college || '院系' }}</text>
          </view>
        </view>
        
        <!-- 个人简介 -->
        <view class="bio-section" v-if="inviterInfo.bio">
          <text class="bio-text">{{ inviterInfo.bio }}</text>
        </view>
      </view>

      <!-- 提示消息 -->
      <view class="request-message">
        <image class="star-icon-small" src="/static/match-mutiple-part1/star.png" mode="aspectFit"></image>
        <text class="message-text">用户{{ inviterInfo.name || 'xxxx' }}发来了组队申请</text>
      </view>

      <!-- 确认区域 -->
      <view class="confirm-section">
        <text class="confirm-title">是否同意？</text>
        
        <view class="button-group">
          <view class="agree-btn" @click="handleAgree">
            <text class="btn-text">同意</text>
          </view>
          <view class="reject-btn" @click="handleReject">
            <text class="btn-text">拒绝</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 组队成功弹窗 -->
    <TeamCreatedModal
      :visible="showTeamCreatedModal"
      :teamName="currentTeamName"
      @close="handleTeamCreatedClose"
      @confirm="handleTeamCreatedConfirm"
    />

    <!-- 底部导航栏 -->
    <CustomTabBar :current="0"></CustomTabBar>
  </view>
</template>

<script>
import CustomTabBar from '@/components/CustomTabBar.vue'
import TeamCreatedModal from '@/components/TeamCreatedModal.vue'
import { getInvitation, confirmMatch } from '../../services/match'

export default {
  components: {
    CustomTabBar,
    TeamCreatedModal
  },
  data() {
    return {
      invitationId: null,
      inviterInfo: {
        id: null,
        name: 'xxxx',
        username: '',
        gender: '性别',
        education: '身份',
        majorCategory: '大类',
        college: '院系',
        bio: '个人简介',
        avatar: ''
      },
      showTeamCreatedModal: false,
      currentTeamName: '',
      isTeamCreated: false  // 标记是否已经组队成功，避免重复加载邀请
    }
  },
  onLoad(options) {
    // 从参数中获取邀请方信息（兼容旧逻辑）
    if (options.inviterInfo) {
      try {
        const info = JSON.parse(decodeURIComponent(options.inviterInfo))
        this.inviterInfo = { ...this.inviterInfo, ...info }
      } catch (e) {
        console.warn('解析邀请方信息失败:', e)
      }
    }
    
    // 从API加载邀请信息
    this.loadInvitation()
  },
  methods: {
    async loadInvitation() {
      // 如果已经组队成功，不再加载邀请
      if (this.isTeamCreated) {
        console.log('已组队成功，跳过加载邀请')
        return
      }
      
      try {
        // 处理不同的响应格式
        const result = await getInvitation()
        console.log('获取邀请信息:', result)
        
        // 处理不同的响应格式
        let invitationData = null
        if (result && result.data) {
          invitationData = result.data
        } else if (result && typeof result.hasInvitation !== 'undefined') {
          invitationData = result
        }
        
        if (invitationData && invitationData.hasInvitation && invitationData.invitation) {
          const inviter = invitationData.invitation.inviter
          this.invitationId = invitationData.invitation.id
          
          // 更新邀请方信息
          this.inviterInfo = {
            id: inviter.id,
            name: inviter.username || inviter.name || '未知',
            username: inviter.username || '',
            gender: inviter.gender === 1 ? '男' : (inviter.gender === 2 ? '女' : ''),
            education: this.getEducationFromGrade(inviter.grade),
            majorCategory: inviter.majorCategory || inviter.major_category || '',
            college: inviter.academy?.name || inviter.college || '',
            bio: inviter.bio || inviter.interest || '',
            avatar: inviter.avatar || ''
          }
        } else {
          // 没有待处理的邀请，且不是组队成功后的情况，才提示并返回
          if (!this.isTeamCreated) {
            uni.showToast({
              title: '暂无待处理的邀请',
              icon: 'none',
              duration: 2000
            })
            // 延迟返回，让用户看到提示
            setTimeout(() => {
              uni.navigateBack({
                fail: () => {
                  // 如果无法返回，跳转到组队匹配页面
                  this.goToIntelligentMatch()
                }
              })
            }, 2000)
          }
        }
      } catch (error) {
        console.error('加载邀请信息失败:', error)
        
        // 如果已经组队成功，忽略错误
        if (this.isTeamCreated) {
          return
        }
        
        // 开发阶段：如果是无效URL错误，使用默认数据
        if (error.errMsg?.includes('invalid url') || error.errno === 600009) {
          console.log('开发阶段：API未配置，使用默认数据')
        } else {
          uni.showToast({
            title: error.message || '加载邀请失败',
            icon: 'none'
          })
        }
      }
    },
    
    getEducationFromGrade(grade) {
      if (!grade) return ''
      return grade <= 4 ? '本科生' : (grade <= 6 ? '研究生' : '')
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
    
    goToExpectation() {
      // 跳转到单人匹配页面（填写期望）
      uni.navigateTo({
        url: '/pages/single-match/index',
        fail: () => {
          uni.reLaunch({
            url: '/pages/single-match/index'
          })
        }
      })
    },
    
    goToIntelligentMatch() {
      // 跳转到单人匹配结果页面（智能匹配）
      uni.navigateTo({
        url: '/pages/single-match-result/index',
        fail: () => {
          uni.reLaunch({
            url: '/pages/single-match-result/index'
          })
        }
      })
    },
    
    handleAgree() {
      uni.showModal({
        title: '确认同意',
        content: '确定要同意组队申请吗？',
        success: (res) => {
          if (res.confirm) {
            this.confirmTeamRequest(true)
          }
        }
      })
    },
    
    handleReject() {
      uni.showModal({
        title: '确认拒绝',
        content: '确定要拒绝组队申请吗？',
        success: (res) => {
          if (res.confirm) {
            this.confirmTeamRequest(false)
          }
        }
      })
    },
    
    async confirmTeamRequest(agreed) {
      try {
        uni.showLoading({ title: agreed ? '组队中...' : '处理中...' })
        
        if (agreed) {
          // 同意邀请
          const result = await confirmMatch({
            invitationId: this.invitationId,
            accept: true
          })
          
          uni.hideLoading()
          
          console.log('组队成功:', result)
          
          // 标记已组队成功，避免后续再次加载邀请
          this.isTeamCreated = true
          
          // 更新本地存储
          uni.setStorageSync('hasTeam', true)
          uni.setStorageSync('justCreatedTeam', true)
          
          // 检查后端返回的队名
          const teamNameFromAPI = result?.data?.team?.name || result?.team?.name
          if (teamNameFromAPI && teamNameFromAPI.trim()) {
            // 如果后端已设置队名，使用该队名
            this.currentTeamName = teamNameFromAPI
            uni.setStorageSync('teamName', teamNameFromAPI)
          } else {
            // 如果后端未设置队名，不设置默认值，让用户有机会创建队名
            // 清除可能存在的旧队名
            this.currentTeamName = ''
            uni.removeStorageSync('teamName')
          }
          
          // 显示组队成功弹窗
          this.showTeamCreatedModal = true
        } else {
          // 拒绝邀请
          await confirmMatch({
            invitationId: this.invitationId,
            accept: false
          })
          
          uni.hideLoading()
          
          uni.showToast({
            title: '已拒绝组队申请',
            icon: 'success',
            duration: 2000
          })
          
          // 延迟返回上一页，让用户看到提示
          setTimeout(() => {
            uni.navigateBack({
              fail: () => {
                // 如果无法返回，跳转到组队匹配页面
                this.goToIntelligentMatch()
              }
            })
          }, 2000)
        }
      } catch (error) {
        uni.hideLoading()
        console.error('处理邀请失败:', error)
        
        // 开发阶段：如果是无效URL错误，模拟成功
        if (error.errMsg?.includes('invalid url') || error.errno === 600009) {
          console.log('开发阶段：API未配置，模拟成功')
          if (agreed) {
            uni.setStorageSync('hasTeam', true)
            uni.setStorageSync('justCreatedTeam', true)
            // 不设置默认队名，让用户有机会创建队名
            this.currentTeamName = ''
            uni.removeStorageSync('teamName')
            this.showTeamCreatedModal = true
          } else {
            uni.showToast({
              title: '已拒绝组队申请',
              icon: 'success'
            })
            setTimeout(() => {
              this.goToIntelligentMatch()
            }, 1500)
          }
        } else {
          uni.showToast({
            title: error.message || '操作失败，请重试',
            icon: 'none'
          })
        }
      }
    },
    
    handleTeamCreatedClose() {
      this.showTeamCreatedModal = false
      // 跳转到队友信息页面
      uni.navigateTo({
        url: '/pages/teammate-info/index',
        fail: () => {
          // 如果跳转失败，跳转到打卡页面
          uni.reLaunch({
            url: '/pages/checkin-detail/index'
          })
        }
      })
    },
    
    handleTeamCreatedConfirm() {
      this.showTeamCreatedModal = false
      // 跳转到打卡页面
      uni.reLaunch({
        url: '/pages/checkin-detail/index',
        fail: () => {
          uni.switchTab({
            url: '/pages/checkin-detail/index'
          })
        }
      })
    }
  }
}
</script>

<style scoped>
.multiple-match-confirm-page {
  position: relative;
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(180deg, #F7E7FF 0%, #FFFFFF 100%);
}

/* 顶部渐变背景 */
.top-gradient-bg {
  position: absolute;
  width: 100%;
  height: 246rpx; /* 对应123px */
  left: 0;
  top: -14rpx; /* 对应-7px */
  background: linear-gradient(89.97deg, #A100FE 0%, #FDB9E7 99.96%);
  z-index: 1;
}

.bottom-gradient-bg {
  position: absolute;
  width: 322rpx; /* 对应161px */
  height: 90rpx; /* 对应45px */
  left: -108rpx; /* 对应-54px */
  top: -78rpx; /* 对应-39px */
  background: linear-gradient(180deg, #F7E8FE 0%, #F9ECFF 100%);
  z-index: 2;
}

/* 标签切换区域 */
.tab-section {
  position: absolute;
  width: 472rpx; /* 对应236px */
  height: 74rpx; /* 对应37px */
  left: 170rpx; /* 对应85px */
  top: 50rpx; /* 对应25px */
  z-index: 10;
}

.tab-group {
  display: flex;
  width: 100%;
  height: 100%;
  position: relative;
}

.tab-item {
  position: relative;
  width: 148rpx; /* 对应74px */
  height: 74rpx; /* 对应37px */
  display: flex;
  align-items: center;
  justify-content: center;
}

.tab-bg {
  position: absolute;
  width: 100%;
  height: 100%;
  background: #D9D9D9;
  opacity: 0;
}

.tab-text {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 32rpx; /* 对应16px */
  line-height: 38rpx; /* 对应19px */
  background: linear-gradient(180deg, #F7E7FF 0%, #FFFFFF 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  color: transparent;
  z-index: 3;
}

.tab-text.active {
  font-weight: 700;
}

.tab-item.active {
  position: relative;
}

.tab-indicator {
  position: absolute;
  width: 120rpx; /* 对应60px */
  height: 36rpx; /* 对应18px */
  left: 14rpx; /* 居中对齐 */
  bottom: -8rpx; /* 对应-4px，向下调整 */
  background: linear-gradient(180deg, #F7E7FF 0%, #FFFFFF 100%);
  opacity: 0.4;
  border-radius: 180rpx; /* 对应90px */
}

/* 进度标签区域 */
.progress-tab-section {
  position: absolute;
  width: 642rpx; /* 对应321px */
  height: 64rpx; /* 对应32px */
  left: 66rpx; /* 对应33px */
  top: 166rpx; /* 对应83px */
  z-index: 5;
}

.progress-tab-group {
  display: flex;
  width: 100%;
  height: 100%;
  justify-content: space-between;
  align-items: center;
}

.progress-tab-item {
  width: 200rpx; /* 对应100px */
  height: 64rpx; /* 对应32px */
  display: flex;
  align-items: center;
  justify-content: center;
  background: #D9D9D9;
  opacity: 0;
}

.progress-tab-text {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 32rpx; /* 对应16px */
  line-height: 38rpx; /* 对应19px */
  color: #000000;
}

.progress-tab-text.active {
  font-weight: 700;
}

/* 主要内容区域 */
.main-content {
  position: relative;
  z-index: 5;
  padding-top: 486rpx; /* 对应243px */
  padding-left: 46rpx; /* 对应23px */
  padding-right: 46rpx; /* 对应23px */
}

/* 信息卡片 */
.info-card {
  position: relative;
  width: 664rpx; /* 对应332px */
  height: 504rpx; /* 对应252px */
  background: #FFFFFF;
  border: 4rpx solid #A100FE; /* 对应2px */
  border-radius: 18rpx; /* 对应9px */
  padding: 40rpx;
  box-sizing: border-box;
  margin-bottom: 60rpx; /* 对应30px */
}

/* 卡片标题 */
.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 30rpx; /* 对应15px */
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

/* 头像区域 */
.avatar-section {
  display: flex;
  justify-content: center;
  margin-bottom: 40rpx; /* 对应20px */
}

.avatar-circle {
  width: 236rpx; /* 对应118px */
  height: 236rpx; /* 对应118px */
  background: #E3E4E4;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-image {
  width: 100%;
  height: 100%;
  border-radius: 50%;
}

.avatar-icon {
  width: 20rpx; /* 对应10px */
  height: 90rpx; /* 对应45px */
  background: #9094A6;
  border-radius: 50% 50% 0 0;
  position: relative;
}

.avatar-icon::before {
  content: '';
  position: absolute;
  width: 40rpx; /* 对应20px */
  height: 40rpx; /* 对应20px */
  background: #9094A6;
  border-radius: 50%;
  top: -60rpx; /* 对应-30px */
  left: 50%;
  transform: translateX(-50%);
}

/* 信息标签 */
.info-tags {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 20rpx; /* 对应10px */
  gap: 22rpx; /* 间距 */
}

.info-tag {
  height: 64rpx; /* 对应32px */
  background: #FFFFFF;
  border: 2rpx solid #F7E7FF; /* 对应1px */
  border-radius: 32rpx; /* 对应16px */
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 20rpx;
  box-sizing: border-box;
}

.info-tag:first-child {
  width: 146rpx; /* 对应73px */
}

.info-tag:nth-child(2) {
  width: 164rpx; /* 对应82.19px */
}

.info-tag.large {
  width: 263rpx; /* 对应131.51px */
}

.tag-text {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 32rpx; /* 对应16px */
  line-height: 38rpx; /* 对应19px */
  color: #9094A6;
}

/* 个人简介 */
.bio-section {
  margin-top: 40rpx; /* 对应20px */
}

.bio-text {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 32rpx; /* 对应16px */
  line-height: 38rpx; /* 对应19px */
  color: #9094A6;
}

/* 提示消息 */
.request-message {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 60rpx; /* 对应30px */
}

.star-icon-small {
  width: 66rpx; /* 对应33px */
  height: 52rpx; /* 对应26px */
  margin-right: 20rpx; /* 对应10px */
}

.message-text {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 32rpx; /* 对应16px */
  line-height: 38rpx; /* 对应19px */
  color: #1F2635;
}

/* 确认区域 */
.confirm-section {
  text-align: center;
}

.confirm-title {
  font-family: 'Inter';
  font-weight: 700;
  font-size: 32rpx; /* 对应16px */
  line-height: 38rpx; /* 对应19px */
  color: #1F2635;
  margin-bottom: 60rpx; /* 对应30px */
}

.button-group {
  display: flex;
  justify-content: space-between;
  gap: 62rpx; /* 间距 */
}

.agree-btn {
  width: 280rpx; /* 对应140px */
  height: 94rpx; /* 对应47px */
  background: linear-gradient(90deg, #A100FE 0%, #FDB9E7 100%);
  border-radius: 180rpx; /* 对应90px */
  display: flex;
  align-items: center;
  justify-content: center;
}

.reject-btn {
  width: 280rpx; /* 对应140px */
  height: 94rpx; /* 对应47px */
  background: linear-gradient(90deg, #1F2735 0%, #A100FE 48.08%);
  border-radius: 180rpx; /* 对应90px */
  display: flex;
  align-items: center;
  justify-content: center;
  transform: scaleX(-1); /* 镜像翻转效果 */
}

.btn-text {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 32rpx; /* 对应16px */
  line-height: 38rpx; /* 对应19px */
  color: #FFFFFF;
}

.reject-btn .btn-text {
  transform: scaleX(-1); /* 恢复文字的正常方向 */
}
</style>
