<template>
  <view class="multiple-match-confirm-page">
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

    <!-- 你的期望 / 智能匹配 / 确认组队 标签 -->
    <view class="progress-tab-section">
      <view class="progress-tab-group">
        <view class="progress-tab-item">
          <text class="progress-tab-text">你的期望</text>
        </view>
        <view class="progress-tab-item">
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
            <view class="avatar-icon"></view>
          </view>
        </view>
        
        <!-- 个人信息标签 -->
        <view class="info-tags-container">
          <!-- 第一行：性别、身份 -->
          <view class="info-tags-row">
            <view class="info-tag">
              <text class="tag-text">{{ inviterInfo.gender || '性别' }}</text>
            </view>
            <view class="info-tag">
              <text class="tag-text">{{ inviterInfo.education || '身份' }}</text>
            </view>
          </view>
          
          <!-- 第二行：大类、院系 -->
          <view class="info-tags-row">
            <view class="info-tag">
              <text class="tag-text">{{ inviterInfo.majorCategory || '大类' }}</text>
            </view>
            <view class="info-tag">
              <text class="tag-text">{{ inviterInfo.college || '院系' }}</text>
            </view>
          </view>
          
          <!-- 个人简介标签 -->
          <view class="bio-tag">
            <text class="tag-text">{{ inviterInfo.bio || '个人简介' }}</text>
          </view>
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
            <text class="agree-btn-text">同意</text>
          </view>
          <view class="reject-btn" @click="handleReject">
            <text class="reject-btn-text">拒绝</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 设置队名弹窗（优先级更高，先显示） -->
    <TeamNameModal
      v-if="showTeamNameModal"
      :visible="showTeamNameModal"
      :defaultTeamName="currentTeamName"
      @cancel="handleTeamNameCancel"
      @confirm="handleTeamNameConfirm"
    />

    <!-- 组队成功弹窗（只有在设置队名完成后才显示） -->
    <TeamCreatedModal
      v-if="!showTeamNameModal"
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
import CustomTabBar from '../../components/CustomTabBar.vue'
import TeamCreatedModal from '../../components/TeamCreatedModal.vue'
import TeamNameModal from '../../components/TeamNameModal.vue'
import { getInvitation, confirmMatch, setTeamName } from '../../services/match'
import { getUserInfo } from '../../services/auth'
import authUtils from '../../utils/auth'

export default {
  components: {
    CustomTabBar,
    TeamCreatedModal,
    TeamNameModal
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
      showTeamNameModal: false,
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
              // 检查页面栈，如果可以返回则返回，否则跳转
              try {
                const pages = getCurrentPages()
                if (pages && pages.length > 1) {
                  uni.navigateBack({
                    fail: () => {
                      // 如果无法返回，跳转到组队匹配页面
                      this.goToIntelligentMatch()
                    }
                  })
                } else {
                  // 没有上一页，直接跳转
                  this.goToIntelligentMatch()
                }
              } catch (error) {
                // 捕获错误，直接跳转
                this.goToIntelligentMatch()
              }
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
        if (agreed) {
          // 检查是否是自己和自己组队
          try {
            // 获取当前用户信息
            let currentUserInfo = authUtils.getUserInfo()
            console.log('🔍 当前用户信息（本地）:', currentUserInfo)
            
            // 如果本地存储没有用户ID，尝试从服务器获取
            if (!currentUserInfo || !currentUserInfo.id) {
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
            
            // 检查邀请方的ID是否与当前用户ID相同
            const currentUserId = currentUserInfo?.id || uni.getStorageSync('userId')
            const inviterId = this.inviterInfo?.id
            
            console.log('🔍 邀请方ID检查:', {
              currentUserId,
              inviterId,
              isSame: currentUserId && inviterId && String(inviterId) === String(currentUserId)
            })
            
            if (currentUserId && inviterId && String(inviterId) === String(currentUserId)) {
              uni.showToast({
                title: '不能和自己组队',
                icon: 'none',
                duration: 2000
              })
              return
            }
            
            // 如果无法获取当前用户ID，也阻止匹配（安全起见）
            if (!currentUserId) {
              console.warn('⚠️ 无法获取当前用户ID，阻止匹配以确保安全')
              uni.showToast({
                title: '无法验证用户信息，请重新登录',
                icon: 'none',
                duration: 2000
              })
              return
            }
          } catch (err) {
            console.error('检查用户ID失败:', err)
            // 如果检查失败，阻止匹配以确保安全
            uni.showToast({
              title: '验证失败，请重试',
              icon: 'none',
              duration: 2000
            })
            return
          }
        }
        
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
          
          // 保存队友信息到本地存储
          const teamData = result?.data?.team || result?.team
          if (teamData) {
            // 尝试从不同字段获取队友信息
            let teammates = []
            if (teamData.users && Array.isArray(teamData.users)) {
              teammates = teamData.users
            } else if (teamData.members && Array.isArray(teamData.members)) {
              teammates = teamData.members
            } else if (Array.isArray(teamData)) {
              teammates = teamData
            }
            
            // 过滤掉当前用户自己
            // 尝试多种方式获取当前用户ID
            const currentUserInfo = authUtils.getUserInfo()
            const currentUserId = currentUserInfo?.id || uni.getStorageSync('userId') || null
            
            if (teammates.length > 0) {
              let otherTeammates = teammates
              
              // 如果有当前用户ID，过滤掉自己
              if (currentUserId) {
                otherTeammates = teammates.filter(t => {
                  const teammateId = t.id || t.userId || t.user?.id
                  return teammateId && teammateId !== currentUserId
                })
              }
              
              // 如果过滤后还有队友，保存；否则保存所有队友（可能当前用户ID获取失败）
              if (otherTeammates.length > 0) {
                console.log('✅ 保存队友信息到本地存储:', otherTeammates)
                uni.setStorageSync('teammates', otherTeammates)
              } else if (teammates.length > 0) {
                // 如果过滤后没有队友，但原始数据有，可能是当前用户ID获取失败，保存所有队友
                console.log('⚠️ 过滤后无队友，保存所有队友信息（可能当前用户ID获取失败）:', teammates)
                uni.setStorageSync('teammates', teammates)
              }
            }
          } else {
            // 如果组队成功但返回数据中没有队友信息，尝试调用 getMatchList 获取
            console.log('⚠️ 组队成功但返回数据中没有队友信息，尝试获取队友信息')
            try {
              const { getMatchList } = await import('../../services/match')
              const matchResult = await getMatchList()
              const matchList = matchResult?.data || matchResult
              
              // 尝试从 matchList 中获取队友信息
              if (matchList && matchList.team) {
                let teammates = []
                if (matchList.team.users && Array.isArray(matchList.team.users)) {
                  teammates = matchList.team.users
                } else if (matchList.team.members && Array.isArray(matchList.team.members)) {
                  teammates = matchList.team.members
                }
                
                if (teammates.length > 0) {
                  const currentUserInfo = authUtils.getUserInfo()
                  const currentUserId = currentUserInfo?.id || uni.getStorageSync('userId') || null
                  let otherTeammates = teammates
                  
                  if (currentUserId) {
                    otherTeammates = teammates.filter(t => {
                      const teammateId = t.id || t.userId || t.user?.id
                      return teammateId && teammateId !== currentUserId
                    })
                  }
                  
                  if (otherTeammates.length > 0) {
                    console.log('✅ 从 getMatchList 获取并保存队友信息:', otherTeammates)
                    uni.setStorageSync('teammates', otherTeammates)
                  } else if (teammates.length > 0) {
                    console.log('⚠️ 从 getMatchList 获取队友信息（过滤后无队友）:', teammates)
                    uni.setStorageSync('teammates', teammates)
                  }
                }
              }
            } catch (err) {
              console.error('获取队友信息失败:', err)
            }
          }
          
          // 检查后端返回的队名（如果有，作为默认值）
          const teamNameFromAPI = result?.data?.team?.name || result?.team?.name
          console.log('🔍 检查队名状态:', {
            teamNameFromAPI,
            hasTeamName: teamNameFromAPI && teamNameFromAPI.trim(),
            result: result
          })
          
          // 无论后端是否返回队名，都先显示设置队名弹窗
          // 如果后端已返回队名，可以作为默认值预填充
          if (teamNameFromAPI && teamNameFromAPI.trim()) {
            // 如果后端已设置队名，保存为当前队名（但还是要显示设置弹窗让用户确认或修改）
            this.currentTeamName = teamNameFromAPI
            // 注意：这里不保存到本地存储，等用户确认后再保存
          } else {
            // 如果后端未设置队名，清空
            this.currentTeamName = ''
          }
          
          // 确保组队成功弹窗是关闭的
          this.showTeamCreatedModal = false
          
          // 始终显示设置队名弹窗
          console.log('📝 显示设置队名弹窗')
          this.showTeamNameModal = true
          console.log('📝 showTeamNameModal 设置为:', this.showTeamNameModal)
          
          // 使用 nextTick 确保 DOM 更新
          this.$nextTick(() => {
            console.log('📝 nextTick 后 showTeamNameModal:', this.showTeamNameModal)
          })
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
            // 检查页面栈，如果可以返回则返回，否则跳转
            try {
              const pages = getCurrentPages()
              if (pages && pages.length > 1) {
                uni.navigateBack({
                  fail: () => {
                    // 如果无法返回，跳转到组队匹配页面
                    this.goToIntelligentMatch()
                  }
                })
              } else {
                // 没有上一页，直接跳转
                this.goToIntelligentMatch()
              }
            } catch (error) {
              // 捕获错误，直接跳转
              this.goToIntelligentMatch()
            }
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
            console.log('📝 开发阶段：显示设置队名弹窗')
            this.showTeamNameModal = true
            console.log('📝 showTeamNameModal 设置为:', this.showTeamNameModal)
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
    
    handleTeamNameCancel() {
      // 取消设置队名，询问是否使用默认队名
      uni.showModal({
        title: '提示',
        content: '不创建队名将使用默认队名，确定吗？',
        success: (res) => {
          if (res.confirm) {
            // 使用默认队名
            this.currentTeamName = '默认队名'
            uni.setStorageSync('teamName', '默认队名')
            this.showTeamNameModal = false
            // 显示组队成功弹窗
            this.showTeamCreatedModal = true
          }
          // 如果取消，保持弹窗打开
        }
      })
    },
    
    async handleTeamNameConfirm(teamName) {
      try {
        uni.showLoading({ title: '保存中...' })
        
        // 调用后端API保存队名
        await setTeamName(teamName)
        
        uni.hideLoading()
        
        // 保存成功，更新本地存储和当前队名
        this.currentTeamName = teamName
        uni.setStorageSync('teamName', teamName)
        
        // 关闭设置队名弹窗
        this.showTeamNameModal = false
        
        // 显示组队成功弹窗
        this.showTeamCreatedModal = true
      } catch (error) {
        uni.hideLoading()
        console.error('保存队名失败:', error)
        
        // 如果是因为队名已设置而失败，直接使用已有队名
        if (error.message?.includes('已设置') || error.message?.includes('already')) {
          uni.showToast({
            title: '队名已设置，不可修改',
            icon: 'none'
          })
          this.showTeamNameModal = false
          // 重新获取队名
          const savedTeamName = uni.getStorageSync('teamName')
          if (savedTeamName) {
            this.currentTeamName = savedTeamName
            this.showTeamCreatedModal = true
          }
        } else {
          uni.showToast({
            title: '保存队名失败，请重试',
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
  position: relative;
}

.tab-item {
  position: relative;
  display: inline-block;
  writing-mode: horizontal-tb;
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
  padding-top: 500rpx; 
  padding-left: 46rpx; /* 对应23px */
  padding-right: 46rpx; /* 对应23px */
}

/* 信息卡片 */
.info-card {
  position: relative;
  width: 100%;
  max-width: 664rpx; /* 对应332px */
  min-height: 504rpx; /* 对应252px */
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
  margin-top: 70rpx; /* 上移，减少上边距 */
  margin-bottom: 0; /* 移除底部边距，让标签容器紧贴标题 */
  position: relative;
}


.star-icon {
  width: 66rpx;
  height: 52rpx;
  /* 关键修改：使用绝对定位 */
  position: absolute;
  /* 将图标定位到标题文字的左侧 */
  right: 63%; 
  /* 让图标与标题文字在垂直方向上居中对齐 */
  top: 23%;
  transform: translateY(-50%);
  /* 保留图标与文字之间的间距 */
  margin-right: 20rpx;
}


.card-title {
  font-family: 'Inter';
  position: absolute; /* 改为绝对定位（关键），相对于最近已定位父级或页面定位 */
  left: 50%; /* 水平方向先移到50%位置 */
  top: 20%; /* 垂直方向移到20%位置（实现"中上"，可按需调整百分比） */
  transform: translate(-50%, 0); /* 水平居中（抵消left:50%的偏移），垂直不额外移动 */
  font-weight: 400;
  font-size: 32rpx; /* 保持原有字号 */
  line-height: 38rpx; /* 保持原有行高（不影响整体定位，仅控制行内间距） */
  color: #000000;
  text-align: center; /* 若文字有多行，保证行内水平居中 */
}

/* 头像区域 */
.avatar-section {
  position: absolute;
  top: -150rpx; 
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  justify-content: center;
  z-index: 6;
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

/* 信息标签容器 */
.info-tags-container {
  margin-top: 50rpx; /* 上移，减少上边距，在标题下方留出适当间距 */
  display: flex;
  flex-direction: column;
  gap: 20rpx; /* 行间距 */
  width: 100%;
  position: relative;
  z-index: 1;
}

/* 信息标签行 */
.info-tags-row {
  display: flex;
  justify-content: flex-start;
  gap: 22rpx; /* 标签间距 */
}

/* 信息标签 */
.info-tag {
  height: 64rpx; /* 对应32px */
  background: #FFFFFF;
  border: 2rpx solid #F7E7FF; /* 浅紫色边框 */
  border-radius: 32rpx; /* 对应16px */
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 20rpx;
  box-sizing: border-box;
  min-width: 146rpx; /* 最小宽度 */
  flex: 1; /* 自适应宽度 */
}

.tag-text {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 32rpx; /* 对应16px */
  line-height: 38rpx; /* 对应19px */
  color: #9094A6;
  text-align: center;
}

/* 个人简介标签 */
.bio-tag {
  background: #FFFFFF;
  border: 2rpx solid #F7E7FF; /* 浅紫色边框 */
  border-radius: 32rpx; /* 对应16px */
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20rpx;
  box-sizing: border-box;
  min-height: 64rpx; /* 最小高度 */
  margin-top: 10rpx; /* 与上方标签的间距 */
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
  width: 100%;
  box-sizing: border-box;
}

.agree-btn {
  flex: 1;
  min-width: 0;
  height: 94rpx; /* 对应47px */
  background: linear-gradient(90deg, #A100FE 0%, #FDB9E7 100%);
  border-radius: 180rpx; /* 对应90px */
  display: flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
}

.reject-btn {
  flex: 1;
  min-width: 0;
  height: 94rpx; /* 对应47px */
  background: linear-gradient(90deg, #1F2735 0%, #A100FE 48.08%);
  border-radius: 180rpx; /* 对应90px */
  display: flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  transform: scaleX(-1); /* 镜像翻转效果 */
}

.agree-btn-text {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 32rpx; /* 对应16px */
  line-height: 38rpx; /* 对应19px */
  color: #FFFFFF;
  white-space: nowrap;
  display: block;
}

.reject-btn-text {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 32rpx; /* 对应16px */
  line-height: 38rpx; /* 对应19px */
  color: #FFFFFF;
  white-space: nowrap;
  display: block;
  transform: scaleX(-1); /* 恢复拒绝按钮文字的正常方向 */
}
</style>
