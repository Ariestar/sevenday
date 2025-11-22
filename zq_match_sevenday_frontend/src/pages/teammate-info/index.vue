<template>
  <view class="teammate-info-page">
    <!-- 顶部背景区域 -->
    <view class="header-background">
      <view class="banner-background"></view>
      <view class="header-tabs">
        <view class="tab-item">
          <text class="tab-text">队友信息</text>
        </view>
        <view class="tab-item" @click="goToCheckin">
          <text class="tab-text">组队打卡</text>
        </view>
      </view>
    </view>

    <!-- 主要内容区域 -->
    <view class="main-content">
      <!-- 队友头像和基本信息卡片 -->
      <view class="profile-card">
        <!-- 装饰性圆角元素 -->
        <view class="decoration-corner top-right"></view>
        
        <!-- 队友头像and基本信息 -->
        <view class="teammate-profile">
          <!-- 头像区域 -->
          <view class="avatar-section">
            <view class="avatar-circle">
              <image 
                v-if="teammateInfo.avatar" 
                :src="teammateInfo.avatar" 
                class="avatar-image" 
                mode="aspectFill"
              />
              <view v-else class="avatar-icon"></view>
            </view>
          </view>
          
          <!-- 申请换队友按钮 -->
          <view class="exchange-button" @click="handleExchangeTeammate">
            <image class="exchange-icon" src="/static/checkin/exchange-teammate-button.png" mode="aspectFit"></image>
            <text class="exchange-text">申请换队友</text>
          </view>
          
          <!-- 分割线 -->
          <view class="profile-separator"></view>
          
          <!-- 基本信息标签（带装饰星星） -->
          <view class="info-section">
            <view class="info-tag">
              <text class="info-tag-text">基本信息</text>
            </view>
            
            <!-- 装饰星星 -->
            <view class="star-decorations">
              <image class="star-left" src="/static/checkin/star.png" mode="aspectFit"></image>
              <image class="star-right" src="/static/checkin/star.png" mode="aspectFit"></image>
            </view>
          </view>
          
          <!-- 基本信息字段列表 -->
          <view class="info-fields">
            <view class="info-field-item">
              <text class="info-field-label">姓名</text>
              <text class="info-field-value">{{ teammateInfo.username || '未填写' }}</text>
            </view>
            <view class="info-field-item">
              <text class="info-field-label">性别</text>
              <text class="info-field-value">{{ teammateInfo.gender || '未填写' }}</text>
            </view>
            <view class="info-field-item">
              <text class="info-field-label">身份</text>
              <text class="info-field-value">{{ teammateInfo.education || '未填写' }}</text>
            </view>
            <view class="info-field-item">
              <text class="info-field-label">大类</text>
              <text class="info-field-value">{{ teammateInfo.majorCategory || '未填写' }}</text>
            </view>
            <view class="info-field-item">
              <text class="info-field-label">院系</text>
              <text class="info-field-value">{{ teammateInfo.college || '未填写' }}</text>
            </view>
            <view class="info-field-item">
              <text class="info-field-label">联系方式</text>
              <text class="info-field-value">{{ teammateInfo.contact || '未填写' }}</text>
            </view>
            <view class="info-field-item">
              <text class="info-field-label">其他信息</text>
              <text class="info-field-value">{{ teammateInfo.bio || '未填写' }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 统计信息区域 -->
      <view class="stats-container">
        <!-- 装饰性圆角元素 -->
        <view class="decoration-corner bottom-left-stats"></view>
        
        <view class="stats-cards">
          <!-- 组队天数卡片 -->
          <view class="stat-card team-days-card">
            <view class="card-icon">
              <image class="icon-image" src="/static/checkin/teammate-info-day-logo.png" mode="aspectFit"></image>
            </view>
            <view class="card-content">
              <text class="card-label">你们已经组队了</text>
              <text class="card-value">{{ teamStats.days }}天</text>
            </view>
            <view class="corner-decoration green"></view>
          </view>

          <!-- 完成任务卡片 -->
          <view class="stat-card tasks-card">
            <view class="card-icon">
              <image class="icon-image" src="/static/checkin/teammate-info-achivement-logo.png" mode="aspectFit"></image>
            </view>
            <view class="card-content">
              <text class="card-label">你们已经完成了</text>
              <text class="card-value">{{ teamStats.completedTasks }}次打卡任务</text>
            </view>
            <view class="corner-decoration blue"></view>
          </view>

          <!-- 积分卡片 -->
          <view class="stat-card credits-card">
            <view class="card-icon">
              <image class="icon-image" src="/static/checkin/teammate-info-credit-logo.png" mode="aspectFit"></image>
            </view>
            <view class="card-content">
              <text class="card-label">你们已经获得了</text>
              <text class="card-value">{{ teamStats.credits }}个积分</text>
            </view>
            <view class="corner-decoration yellow"></view>
          </view>
        </view>
      </view>

      <!-- 分割线 -->
      <view class="divider"></view>

      <!-- 打卡记录区域 -->
      <view class="records-container">
        <view class="checkin-records">
          <view class="records-header">
            <image class="star-icon" src="/static/checkin/checkin.png" mode="aspectFit"></image>
            <text class="records-title">你们的打卡记录</text>
          </view>

          <!-- 下拉选择框 -->
          <view class="dropdown-selector" @click="toggleDropdown">
            <text class="dropdown-text">第x天打卡记录</text>
            <view class="dropdown-arrow" :class="{ expanded: dropdownExpanded }">
              <text class="arrow-icon">▼</text>
            </view>
          </view>

          <!-- 打卡记录列表 -->
          <view class="records-list">
            <view 
              v-for="(record, index) in checkinRecords" 
              :key="index"
              class="record-item"
              :class="getRecordItemClass(record.status)"
            >
              <view class="record-content">
                <!-- 左侧编号圆圈 -->
                <view class="number-circle" :class="getNumberCircleClass(record.status)">
                  <text v-if="record.status === 'completed'" class="circle-number">{{ record.day }}</text>

                </view>
                
                <!-- 中间文本内容 -->
                <view class="record-text-content">
                  <text class="record-day-text">第{{ record.day }}天</text>
                  <text v-if="record.completedTime" class="record-time-text">{{ record.completedTime }}</text>
                </view>
                
                <!-- 右侧完成状态圆圈 -->
                <view v-if="record.status === 'completed-checked'" class="completion-circle">
                  <image class="completion-check" src="/static/checkin/checkin-done.png" mode="aspectFit"></image>
                </view>
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 底部导航栏 -->
    <CustomTabBar :current="1"></CustomTabBar>

    <!-- 申请换队友确认弹窗 -->
    <view v-if="showExchangeConfirmModal" class="modal-overlay" @tap="closeExchangeConfirmModal">
      <view class="exchange-confirm-modal" @tap.stop>
        <view class="modal-header">
          <text class="modal-title">申请换队友</text>
        </view>
        <view class="modal-content">
          <text class="modal-text">确定要申请换队友吗？</text>
        </view>
        <view class="modal-actions">
          <view class="modal-button cancel" @tap="closeExchangeConfirmModal">
            <text class="button-text">取消</text>
          </view>
          <view class="modal-button confirm" @tap="confirmExchangeRequest">
            <text class="button-text">是</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 等待对方回应弹窗 -->
    <view v-if="showWaitingModal" class="modal-overlay">
      <view class="waiting-modal">
        <view class="waiting-header">
          <image class="waiting-logo" src="/static/checkin/wait.png" mode="aspectFit"></image>
        </view>
        <view class="waiting-content">
          <text class="waiting-title">等待对方回应</text>
        </view>
        <view class="waiting-actions">
          <view class="waiting-button" @tap="cancelExchangeRequest">
            <text class="waiting-button-text">取消申请</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 换队友结果弹窗 -->
    <view v-if="showResultModal" class="modal-overlay" @tap="closeResultModal">
      <view class="result-modal" :class="{ success: exchangeResult.title === '换队友成功' }" @tap.stop>
        <view class="result-header">
          <text class="result-title">{{ exchangeResult.title }}</text>
        </view>
        <view class="result-content">
          <text class="result-text">{{ exchangeResult.message }}</text>
        </view>
        <view class="result-actions">
          <view class="result-button" @tap="handleResultConfirm">
            <text class="result-button-text">确定</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 收到换队友申请弹窗 -->
    <view v-if="showReceivedExchangeModal" class="modal-overlay" @tap.stop>
      <view class="received-exchange-modal" @tap.stop>
        <view class="modal-header">
          <text class="modal-title">换队友申请</text>
        </view>
        <view class="modal-content">
          <text class="modal-text">您的队友发起了更换队友申请</text>
          <text class="modal-text">是否同意更换队友?</text>
        </view>
        <view class="modal-actions">
          <view class="modal-button agree" @tap="handleAgreeExchange">
            <text class="button-text">同意</text>
          </view>
          <view class="modal-button disagree" @tap="handleDisagreeExchange">
            <text class="button-text">不同意</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import CustomTabBar from '@/components/CustomTabBar.vue'
import { getMatchList, requestExchangeTeammate, getExchangeRequest, respondExchangeRequest } from '../../services/match'
import { getMyCheckinList, getCheckinTasks } from '../../services/checkin'
import authUtils from '../../utils/auth'

export default {
  components: {
    CustomTabBar
  },
  data() {
    return {
      dropdownExpanded: false,
      showExchangeConfirmModal: false,
      showWaitingModal: false,
      showResultModal: false,
      showReceivedExchangeModal: false,
      exchangeRequestId: null,
      checkExchangeInterval: null,
      exchangeResult: {
        title: '',
        message: ''
      },
      teammateInfo: {
        id: null,
        username: '',
        avatar: '',
        gender: '',
        education: '',
        majorCategory: '',
        college: '',
        contact: '',
        bio: ''
      },
      teamStats: {
        days: 0,
        completedTasks: 0,
        credits: 0
      },
      checkinRecords: []
    }
  },
  onLoad() {
    this.loadTeammateData()
    this.loadTeamStats()
    this.loadCheckinRecords()
    this.checkExchangeRequest()
    // 定期检查换队友申请
    this.checkExchangeInterval = setInterval(() => {
      this.checkExchangeRequest()
    }, 3000) // 每3秒检查一次
  },
  async onShow() {
    // 页面显示时刷新数据
    await this.loadTeamStats()
    await this.loadCheckinRecords()
  },
  onUnload() {
    // 清除定时器
    if (this.checkExchangeInterval) {
      clearInterval(this.checkExchangeInterval)
    }
  },
  methods: {
    toggleDropdown() {
      this.dropdownExpanded = !this.dropdownExpanded
    },
    
    getRecordItemClass(status) {
      return {
        'completed-checked': status === 'completed-checked',
        'pending': status === 'pending' || status === 'not-started'
      }
    },
    
    getNumberCircleClass(status) {
      return {
        'completed': status === 'completed-checked',
        'pending': status === 'pending' || status === 'not-started'
      }
    },
    
    goToCheckin() {
      uni.switchTab({
        url: '/pages/checkin-detail/index',
        fail: (err) => {
          console.warn('跳转到打卡页面失败:', err)
          uni.reLaunch({
            url: '/pages/checkin-detail/index'
          })
        }
      })
    },
    
    handleExchangeTeammate() {
      this.showExchangeConfirmModal = true
    },

    closeExchangeConfirmModal() {
      this.showExchangeConfirmModal = false
    },

    async confirmExchangeRequest() {
      try {
        this.showExchangeConfirmModal = false
        uni.showLoading({ title: '发送中...' })
        
        // 调用API发送换队友申请
        await requestExchangeTeammate()
        
        uni.hideLoading()
        this.showWaitingModal = true
        
        // 开始轮询检查申请状态
        this.startPollingExchangeStatus()
      } catch (error) {
        uni.hideLoading()
        console.error('发送换队友申请失败:', error)
        uni.showToast({
          title: error.message || '发送失败，请重试',
          icon: 'none'
        })
      }
    },
    
    async startPollingExchangeStatus() {
      // 每3秒检查一次申请状态
      const pollInterval = setInterval(async () => {
        try {
          const result = await getMatchList()
          const matchList = result?.data || result
          
          // 如果队伍已解散，说明对方同意了
          if (!matchList?.isMatched) {
            clearInterval(pollInterval)
            this.showWaitingModal = false
            this.exchangeResult = {
              title: '换队友成功',
              message: '对方已同意换队友申请，队伍已解散。'
            }
            this.showResultModal = true
          }
        } catch (error) {
          console.error('检查申请状态失败:', error)
        }
      }, 3000)
      
      // 30秒后停止轮询
      setTimeout(() => {
        clearInterval(pollInterval)
      }, 30000)
    },

    cancelExchangeRequest() {
      this.showWaitingModal = false
      // 注意：这里只是取消等待弹窗，实际的申请仍然有效
      // 如果需要真正取消申请，需要调用API删除申请
      uni.showToast({
        title: '已关闭等待窗口',
        icon: 'none'
      })
    },

    async checkExchangeRequest() {
      try {
        const result = await getExchangeRequest()
        const data = result?.data || result
        
        if (data?.hasRequest && data?.request) {
          this.exchangeRequestId = data.request.id
          this.showReceivedExchangeModal = true
        }
      } catch (error) {
        console.error('检查换队友申请失败:', error)
      }
    },
    
    async handleAgreeExchange() {
      try {
        uni.showLoading({ title: '处理中...' })
        
        await respondExchangeRequest(this.exchangeRequestId, true)
        
        uni.hideLoading()
        this.showReceivedExchangeModal = false
        
        // 清除本地存储
        uni.removeStorageSync('hasTeam')
        uni.removeStorageSync('teamName')
        uni.removeStorageSync('justCreatedTeam')
        uni.removeStorageSync('teammates')
        
        // 跳转到匹配页面
        uni.reLaunch({
          url: '/pages/multiple-match/index',
          success: () => {
            uni.showToast({
              title: '队伍已解散，可重新匹配',
              icon: 'none'
            })
          }
        })
      } catch (error) {
        uni.hideLoading()
        console.error('同意换队友失败:', error)
        uni.showToast({
          title: error.message || '处理失败，请重试',
          icon: 'none'
        })
      }
    },
    
    async handleDisagreeExchange() {
      try {
        uni.showLoading({ title: '处理中...' })
        
        await respondExchangeRequest(this.exchangeRequestId, false)
        
        uni.hideLoading()
        this.showReceivedExchangeModal = false
        
        uni.showToast({
          title: '已拒绝换队友申请',
          icon: 'success'
        })
        
        // 清除申请ID，避免重复显示
        this.exchangeRequestId = null
      } catch (error) {
        uni.hideLoading()
        console.error('拒绝换队友失败:', error)
        uni.showToast({
          title: error.message || '处理失败，请重试',
          icon: 'none'
        })
      }
    },

    closeResultModal() {
      this.showResultModal = false
    },

    handleResultConfirm() {
      this.showResultModal = false
      
      // 如果换队友成功，返回匹配页面
      if (this.exchangeResult.message.includes('队伍已解散')) {
        // 清除本地存储的组队信息，但保留报名信息
        uni.removeStorageSync('hasTeam')
        uni.removeStorageSync('teamName')
        uni.removeStorageSync('justCreatedTeam')
        uni.removeStorageSync('teammates')
        
        // 跳转到多人匹配页面，保留报名信息
        uni.reLaunch({
          url: '/pages/multiple-match/index',
          success: () => {
            uni.showToast({
              title: '队伍已解散，可重新匹配',
              icon: 'none'
            })
          }
        })
      } else if (this.exchangeResult.message.includes('拒绝')) {
        // 如果拒绝，显示提示信息
        uni.showToast({
          title: '已维持当前组队，有问题请联系工作人员',
          icon: 'none',
          duration: 3000
        })
      }
      // 其他情况保持当前页面
    },
    
    toggleRecord(index) {
      this.checkinRecords[index].expanded = !this.checkinRecords[index].expanded
    },
    
    getRecordStatusClass(status) {
      return `status-${status}`
    },
    
    getStatusCircleClass(status) {
      switch (status) {
        case 'completed':
          return 'circle-completed'
        case 'completed-checked':
          return 'circle-checked'
        case 'pending':
          return 'circle-pending'
        default:
          return 'circle-default'
      }
    },
    
    getStatusMainText(record) {
      switch (record.status) {
        case 'completed':
        case 'completed-checked':
          return `第${record.day}天`
        case 'pending':
          return '待完成'
        default:
          return '未开始'
      }
    },
    
    async loadTeammateData() {
      try {
        console.log('🔍 开始加载队友数据...')
        
        // 先从本地存储读取
        const teammatesFromStorage = uni.getStorageSync('teammates')
        if (teammatesFromStorage && teammatesFromStorage.length > 0) {
          console.log('从本地存储读取队友信息:', teammatesFromStorage)
          const teammate = teammatesFromStorage[0] // 取第一个队友
          this.updateTeammateInfo(teammate)
        }
        
        // 调用API获取最新的队友信息
        const result = await getMatchList()
        console.log('获取队友数据 (完整):', JSON.stringify(result, null, 2))
        
        // 处理不同的响应格式
        let matchList = null
        if (result && result.data) {
          matchList = result.data
          console.log('从result.data提取数据:', matchList)
        } else if (result && typeof result.isMatched !== 'undefined') {
          matchList = result
          console.log('result本身就是data:', matchList)
        }
        
        // 尝试多种数据格式获取队友信息
        let teammates = []
        
        // 方式1: 从 matches 字段获取（旧格式）
        if (matchList && matchList.matches && Array.isArray(matchList.matches) && matchList.matches.length > 0) {
          teammates = matchList.matches
          console.log('✅ 从 matches 字段找到队友信息:', teammates)
        }
        // 方式2: 从 team.users 字段获取（新格式）
        else if (matchList && matchList.team && matchList.team.users && Array.isArray(matchList.team.users) && matchList.team.users.length > 0) {
          teammates = matchList.team.users
          console.log('✅ 从 team.users 字段找到队友信息:', teammates)
        }
        // 方式3: 从 team.members 字段获取
        else if (matchList && matchList.team && matchList.team.members && Array.isArray(matchList.team.members) && matchList.team.members.length > 0) {
          teammates = matchList.team.members
          console.log('✅ 从 team.members 字段找到队友信息:', teammates)
        }
        // 方式4: 从 team 字段直接获取（如果 team 本身是用户数组）
        else if (matchList && matchList.team && Array.isArray(matchList.team) && matchList.team.length > 0) {
          teammates = matchList.team
          console.log('✅ 从 team 数组找到队友信息:', teammates)
        }
        
        if (teammates.length > 0) {
          // 过滤掉当前用户自己
          // 尝试多种方式获取当前用户ID
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
            const teammate = otherTeammates[0] // 取第一个队友（排除自己）
            console.log('✅ 找到队友信息:', teammate)
            this.updateTeammateInfo(teammate)
            
            // 保存到本地存储
            uni.setStorageSync('teammates', otherTeammates)
          } else if (teammates.length > 0) {
            // 如果过滤后没有队友，但原始数据有，可能是当前用户ID获取失败
            // 如果只有2个用户，其中一个就是队友
            if (teammates.length === 2) {
              // 取第一个作为队友（如果ID不匹配）
              const teammate = teammates[0]
              console.log('⚠️ 过滤后无队友，但原始数据有2个用户，使用第一个作为队友:', teammate)
              this.updateTeammateInfo(teammate)
              uni.setStorageSync('teammates', [teammate])
            } else {
              console.warn('⚠️ 未找到其他队友（可能只有自己）')
              // 如果API没有返回队友信息，尝试使用本地存储
              if (teammatesFromStorage && teammatesFromStorage.length > 0) {
                const teammate = teammatesFromStorage[0]
                this.updateTeammateInfo(teammate)
              }
            }
          } else {
            console.warn('⚠️ 未找到其他队友（可能只有自己）')
            // 如果API没有返回队友信息，尝试使用本地存储
            if (teammatesFromStorage && teammatesFromStorage.length > 0) {
              const teammate = teammatesFromStorage[0]
              this.updateTeammateInfo(teammate)
            }
          }
        } else {
          console.warn('⚠️ 未找到队友信息，matchList:', matchList)
          // 如果API没有返回队友信息，尝试使用本地存储
          if (teammatesFromStorage && teammatesFromStorage.length > 0) {
            const teammate = teammatesFromStorage[0]
            this.updateTeammateInfo(teammate)
          }
        }
      } catch (error) {
        console.error('加载队友数据失败:', error)
        
        // 如果API调用失败，尝试使用本地存储
        const teammatesFromStorage = uni.getStorageSync('teammates')
        if (teammatesFromStorage && teammatesFromStorage.length > 0) {
          console.log('API失败，使用本地存储的队友信息')
          const teammate = teammatesFromStorage[0]
          this.updateTeammateInfo(teammate)
        }
      }
    },
    
    updateTeammateInfo(teammate) {
      if (!teammate) {
        console.warn('⚠️ teammate为空，无法更新')
        return
      }
      
      console.log('📝 ========== 处理队友数据 ==========')
      console.log('📝 完整teammate对象:', JSON.stringify(teammate, null, 2))
      console.log('📝 原始gender值:', teammate.gender, '类型:', typeof teammate.gender)
      console.log('📝 原始grade值:', teammate.grade, '类型:', typeof teammate.grade)
      
      // 处理性别：前端直接转换
      let gender = ''
      const genderValue = teammate.gender
      if (genderValue !== null && genderValue !== undefined && genderValue !== '') {
        // 转换为数字进行比较
        const genderNum = Number(genderValue)
        if (genderNum === 1 || genderValue === '1' || genderValue === 1) {
          gender = '男'
        } else if (genderNum === 2 || genderValue === '2' || genderValue === 2) {
          gender = '女'
        } else if (genderValue === '男' || genderValue === '女') {
          // 如果已经是中文，直接使用
          gender = genderValue
        }
      }
      
      // 处理联系方式：优先显示QQ，如果没有则显示手机号
      let contact = ''
      if (teammate.qq && teammate.qq.trim()) {
        contact = `QQ: ${teammate.qq}`
      } else if (teammate.phone && teammate.phone.trim()) {
        contact = `手机: ${teammate.phone}`
      }
      
      // 处理身份（学历）：前端从年级推断
      const education = this.getEducationFromGrade(teammate.grade)
      
      this.teammateInfo = {
        id: teammate.id,
        username: teammate.username || teammate.name || '未知',
        avatar: teammate.avatar || '',
        gender: gender,
        education: education,
        majorCategory: teammate.major_category || teammate.majorCategory || '',
        college: teammate.academy?.name || teammate.academy_name || teammate.college || '',
        contact: contact,
        bio: teammate.interest || teammate.bio || ''
      }
      
      console.log('✅ ========== 队友信息已更新 ==========')
      console.log('✅ 最终teammateInfo:', JSON.stringify(this.teammateInfo, null, 2))
      console.log('✅ 性别:', this.teammateInfo.gender, '(是否为空:', !this.teammateInfo.gender, ')')
      console.log('✅ 身份:', this.teammateInfo.education, '(是否为空:', !this.teammateInfo.education, ')')
      console.log('✅ ====================================')
    },
    
    getEducationFromGrade(grade) {
      if (grade === null || grade === undefined || grade === '') {
        console.log('⚠️ grade为空，无法推断学历')
        return ''
      }
      const gradeNum = Number(grade)
      if (isNaN(gradeNum)) {
        console.log('⚠️ grade不是有效数字:', grade)
        return ''
      }
      const result = gradeNum <= 4 ? '本科' : (gradeNum <= 6 ? '研究生' : '')
      console.log('📚 从年级推断学历:', gradeNum, '->', result)
      return result
    },
    
    async loadTeamStats() {
      try {
        console.log('📊 开始加载团队统计数据...')
        
        // 获取匹配列表，包含团队信息
        const result = await getMatchList()
        const matchList = result?.data || result
        
        if (matchList && matchList.team) {
          const team = matchList.team
          
          // 获取已完成任务数：从打卡记录中统计
          let completedTasks = 0
          try {
            const checkinList = await getMyCheckinList()
            if (checkinList && Array.isArray(checkinList)) {
              completedTasks = checkinList.length
            }
          } catch (err) {
            console.warn('获取打卡记录失败，使用默认值:', err)
          }
          
          // 获取积分：从team.score或计算
          const credits = team.score || 0
          
          // 计算组队天数：从第一个打卡记录的时间开始计算
          let days = 0
          try {
            const checkinList = await getMyCheckinList()
            if (checkinList && checkinList.length > 0) {
              // 找到最早的打卡记录
              const earliestPost = checkinList[checkinList.length - 1] // 列表是倒序的，最后一个是最早的
              if (earliestPost && earliestPost.create_time) {
                const createTime = new Date(earliestPost.create_time)
                const now = new Date()
                const diffTime = now - createTime
                days = Math.floor(diffTime / (1000 * 60 * 60 * 24)) + 1 // 加1是因为当天也算一天
                if (days < 1) days = 1 // 至少是1天
              }
            }
            // 如果没有打卡记录，默认显示1天
            if (days === 0) days = 1
          } catch (err) {
            console.warn('计算组队天数失败，使用默认值:', err)
            days = 1
          }
          
          this.teamStats = {
            days: days,
            completedTasks: completedTasks,
            credits: credits
          }
          
          console.log('✅ 团队统计数据已加载:', this.teamStats)
        } else {
          console.warn('⚠️ 未找到团队信息')
          // 使用默认值
          this.teamStats = {
            days: 0,
            completedTasks: 0,
            credits: 0
          }
        }
      } catch (error) {
        console.error('加载团队统计数据失败:', error)
        // 使用默认值
        this.teamStats = {
          days: 0,
          completedTasks: 0,
          credits: 0
        }
      }
    },
    
    async loadCheckinRecords() {
      try {
        console.log('📝 开始加载打卡记录...')
        
        // 获取我的打卡记录列表
        const checkinList = await getMyCheckinList()
        console.log('📝 打卡记录列表:', checkinList)
        
        if (!checkinList || checkinList.length === 0) {
          this.checkinRecords = []
          console.log('⚠️ 暂无打卡记录')
          return
        }
        
        // 获取所有任务列表，用于匹配day
        const tasks = await getCheckinTasks().catch(() => [])
        const taskMap = {}
        if (tasks && Array.isArray(tasks)) {
          tasks.forEach((task, index) => {
            // 支持多种ID字段名
            const taskId = task.id || task.taskId || task.task_id
            if (taskId) {
              taskMap[taskId] = task.day || (index + 1) // 优先使用task.day，否则使用索引+1
            }
          })
        }
        
        console.log('📋 任务映射表:', taskMap)
        
        // 转换打卡记录格式
        const records = checkinList.map(post => {
          // post.task 可能是任务ID（整数）或任务对象
          let taskId = null
          if (typeof post.task === 'object' && post.task !== null) {
            taskId = post.task.id || post.task.taskId || post.task.task_id
          } else {
            taskId = post.task
          }
          
          // 从映射表中获取day，如果没有则尝试从title中提取
          let day = taskMap[taskId] || 0
          if (day === 0 && post.title) {
            // 从title中提取天数，例如"第1天打卡"
            const match = post.title.match(/第(\d+)天/)
            if (match) {
              day = parseInt(match[1])
            }
          }
          
          console.log(`📝 处理打卡记录: taskId=${taskId}, day=${day}`, post)
          const createTime = post.create_time ? new Date(post.create_time) : null
          
          // 格式化完成时间
          let completedTime = null
          if (createTime) {
            const now = new Date()
            const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
            const postDate = new Date(createTime.getFullYear(), createTime.getMonth(), createTime.getDate())
            
            if (postDate.getTime() === today.getTime()) {
              // 今天完成的
              const hours = createTime.getHours().toString().padStart(2, '0')
              const minutes = createTime.getMinutes().toString().padStart(2, '0')
              completedTime = `今日${hours}:${minutes}完成`
            } else {
              // 之前完成的
              const month = (createTime.getMonth() + 1).toString().padStart(2, '0')
              const date = createTime.getDate().toString().padStart(2, '0')
              const hours = createTime.getHours().toString().padStart(2, '0')
              const minutes = createTime.getMinutes().toString().padStart(2, '0')
              completedTime = `${month}-${date} ${hours}:${minutes}完成`
            }
          }
          
          return {
            day: day,
            status: 'completed-checked', // 已完成的打卡
            completedTime: completedTime,
            expanded: false,
            details: post.description || post.title || '已完成打卡'
          }
        })
        
        // 按day排序
        records.sort((a, b) => a.day - b.day)
        
        this.checkinRecords = records
        console.log('✅ 打卡记录已加载:', this.checkinRecords)
      } catch (error) {
        console.error('加载打卡记录失败:', error)
        this.checkinRecords = []
      }
    }
  }
}
</script>

<style scoped>
.teammate-info-page {
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

/* 主要内容区域 */
.main-content {
  position: relative;
  padding: 60rpx 36rpx 120rpx; /* 对应30px 18px 60px，底部留空间给导航栏 */
}

/* 档案卡片 */
.profile-card {
  position: relative;
  width: 676rpx; /* 对应338px */
  min-height: 420rpx; /* 对应210px，改为min-height以适应内容 */
  margin: 0 auto 40rpx; /* 对应0 auto 20px */
  background: #FFFFFF;
  border-radius: 24rpx; /* 对应12px */
  padding: 40rpx; /* 对应20px */
  box-sizing: border-box;
}

/* 统计信息容器 */
.stats-container {
  position: relative;
  width: 676rpx; /* 对应338px */
  margin: 0 auto 40rpx; /* 对应0 auto 20px */
  background: #FFFFFF;
  border-radius: 24rpx; /* 对应12px */
  padding: 30rpx; /* 对应15px */
}

/* 装饰性圆角元素 */
.decoration-corner {
  position: absolute;
  width: 82rpx; /* 对应41px */
  height: 82rpx; /* 对应41px */
  background: #FDF8FF;
  border-radius: 0 24rpx 0 200rpx; /* 对应0 12px 0 100px */
}

.decoration-corner.top-right {
  top: 0;
  right: 0;
}

.decoration-corner.bottom-left-stats {
  position: absolute;
  width: 82rpx; /* 对应41px */
  height: 82rpx; /* 对应41px */
  background: #FDF8FF;
  border-radius: 0 24rpx 0 200rpx; /* 对应0 12px 0 100px */
  bottom: 170rpx; /* 调整位置 */
  left: 0;
  transform: rotate(-180deg);
}

/* 队友档案区域 */
.teammate-profile {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 0;
  padding: 40rpx 0; /* 对应20px 0 */
}

.avatar-section {
  margin-bottom: 20rpx; /* 对应10px */
}

.avatar-circle {
  width: 160rpx; /* 对应80px */
  height: 160rpx; /* 对应80px */
  background: #E3E4E4;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-icon {
  width: 20rpx; /* 对应10px */
  height: 60rpx; /* 对应30px */
  background: #9094A6;
  border-radius: 50% 50% 0 0;
  position: relative;
}

.avatar-icon::before {
  content: '';
  position: absolute;
  width: 32rpx; /* 对应16px */
  height: 32rpx; /* 对应16px */
  background: #9094A6;
  border-radius: 50%;
  top: -48rpx; /* 对应-24px */
  left: 50%;
  transform: translateX(-50%);
}

.avatar-image {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

/* 基本信息区域 */
.info-section {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 20rpx; /* 对应10px */
}

.info-tag {
  padding: 10rpx 30rpx; /* 对应5px 15px */
  background: #F7E7FF;
  border-radius: 180rpx; /* 对应90px */
}

.info-tag-text {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 28rpx; /* 对应14px */
  line-height: 34rpx; /* 对应17px */
  color: #A100FE;
}

/* 基本信息字段列表 */
.info-fields {
  width: 100%;
  margin-top: 30rpx; /* 对应15px */
  padding: 0 20rpx; /* 对应0 10px */
}

.info-field-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 0; /* 对应10px 0 */
  border-bottom: 1rpx solid #F0F0F0; /* 对应0.5px */
}

.info-field-item:last-child {
  border-bottom: none;
}

.info-field-label {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 28rpx; /* 对应14px */
  line-height: 34rpx; /* 对应17px */
  color: #666666;
  flex-shrink: 0;
  margin-right: 20rpx; /* 对应10px */
}

.info-field-value {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 28rpx; /* 对应14px */
  line-height: 34rpx; /* 对应17px */
  color: #000000;
  text-align: right;
  flex: 1;
  word-break: break-all;
}

.exchange-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 264rpx; /* 对应132px */
  height: 42rpx; /* 对应21px */
  background: linear-gradient(90deg, #FFCE51 0%, #FFA11E 100%);
  border-radius: 32rpx; /* 对应16px */
  gap: 10rpx; /* 对应5px */
  margin: 20rpx auto; /* 居中并添加上下间距 */
}

.exchange-icon {
  width: 32rpx; /* 对应16px */
  height: 32rpx; /* 对应16px */
}

.exchange-text {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 28rpx; /* 对应14px */
  line-height: 34rpx; /* 对应17px */
  color: #FFFFFF;
}

/* 档案内分割线 */
.profile-separator {
  width: 618rpx; /* 对应309px */
  height: 1rpx; /* 对应0.5px */
  background: #DB86FF;
  margin: 30rpx auto; /* 对应15px auto */
}

/* 装饰星星 */
.star-decorations {
  position: absolute;
  width: 100%;
  top: 50%;
  transform: translateY(-50%);
}

.star-left, .star-right {
  position: absolute;
  width: 32rpx; /* 对应16px */
  height: 32rpx; /* 对应16px */
}

.star-left {
  left: -60rpx; /* 对应-30px */
  top: 50%;
  transform: translateY(-50%);
}

.star-right {
  right: -60rpx; /* 对应-30px */
  top: 50%;
  transform: translateY(-50%);
}

/* 统计卡片组 */
.stats-cards {
  margin-bottom: 40rpx; /* 对应20px */
}

.stat-card {
  position: relative;
  width: 612rpx; /* 对应306px */
  height: 112rpx; /* 对应56px */
  margin: 0 auto 8rpx; /* 对应0 auto 4px */
  padding: 20rpx; /* 对应10px */
  border-radius: 24rpx; /* 对应12px */
  display: flex;
  align-items: center;
  box-sizing: border-box;
}

.team-days-card {
  background: #EBFFF2;
  border: 2rpx solid #BCFFCB; /* 对应1px */
}

.tasks-card {
  background: rgba(145, 222, 255, 0.41);
  border: 2rpx solid rgba(13, 146, 255, 0.33); /* 对应1px */
}

.credits-card {
  background: #FFFDEB;
  border: 2rpx solid #D9F100; /* 对应1px */
}

.card-icon {
  width: 64rpx; /* 对应32px */
  height: 64rpx; /* 对应32px */
  border-radius: 24rpx; /* 对应12px */
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20rpx; /* 对应10px */
}

.team-days-card .card-icon {
  background: linear-gradient(138.22deg, #00A22C 14.98%, #34FF7B 84.73%);
}

.tasks-card .card-icon {
  background: linear-gradient(138.22deg, #002BA2 14.98%, #34F5FF 84.73%);
}

.credits-card .card-icon {
  background: linear-gradient(316.91deg, #FFD000 25.6%, #FFA11E 72.53%);
}

.icon-image {
  width: 40rpx; /* 对应20px */
  height: 40rpx; /* 对应20px */
}

.card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.card-label {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 28rpx; /* 对应14px */
  line-height: 34rpx; /* 对应17px */
  margin-bottom: 4rpx; /* 对应2px */
}

.team-days-card .card-label {
  color: #00801C;
}

.tasks-card .card-label {
  color: #070596;
}

.credits-card .card-label {
  color: #803C00;
}

.card-value {
  font-family: 'Inter';
  font-weight: 700;
  font-size: 52rpx; /* 对应26px */
  line-height: 62rpx; /* 对应31px */
}

.team-days-card .card-value {
  color: #00801C;
}

.tasks-card .card-value {
  color: #070596;
}

.credits-card .card-value {
  color: #803C00;
}

.corner-decoration {
  position: absolute;
  width: 48rpx; /* 对应24px */
  height: 48rpx; /* 对应24px */
  top: 0;
  right: 0;
  border-radius: 0 24rpx 0 200rpx; /* 对应0 12px 0 100px */
}

.corner-decoration.green {
  background: #BCFFCB;
}

.corner-decoration.blue {
  background: #90D2FF;
}

.corner-decoration.yellow {
  background: #D9F100;
}

/* 分割线 */
.divider {
  width: 618rpx; /* 对应309px */
  height: 1rpx; /* 对应0.5px */
  background: #DB86FF;
  margin: 40rpx auto; /* 对应20px auto */
}

/* 打卡记录容器 */
.records-container {
  position: relative;
  width: 676rpx; /* 对应338px */
  margin: 0 auto;
  background: #FFFFFF;
  border-radius: 24rpx; /* 对应12px */
  padding: 30rpx; /* 对应15px */
}

/* 打卡记录区域 */
.checkin-records {
  width: 100%;
}

.records-header {
  display: flex;
  align-items: center;
  margin-bottom: 30rpx; /* 对应15px */
  padding-left: 20rpx; /* 对应10px */
}

.star-icon {
  width: 46rpx; /* 对应23px */
  height: 46rpx; /* 对应23px */
  margin-right: 20rpx; /* 对应10px */
}

.records-title {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 28rpx; /* 对应14px */
  line-height: 34rpx; /* 对应17px */
  color: #A100FE;
}

/* 下拉选择框样式 */
.dropdown-selector {
  width: 100%;
  height: 80rpx; /* 对应40px */
  background: #FFFFFF;
  border: 2rpx solid #C0C0C0; /* 对应1px */
  border-radius: 24rpx; /* 对应12px */
  margin-bottom: 20rpx; /* 对应10px */
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24rpx; /* 对应0 12px */
  box-sizing: border-box;
}

.dropdown-text {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 28rpx; /* 对应14px */
  line-height: 34rpx; /* 对应17px */
  color: #000000;
}

.dropdown-arrow {
  transition: transform 0.3s ease;
}

.dropdown-arrow.expanded {
  transform: rotate(180deg);
}

.arrow-icon {
  font-size: 24rpx; /* 对应12px */
  color: #000000;
}

/* 打卡记录列表样式 */
.records-list {
  width: 100%;
}

.record-item {
  width: 100%;
  height: 104rpx; /* 对应52px */
  margin: 0 0 16rpx; /* 对应0 0 8px */
  background: #F6FFF9;
  border: 2rpx solid #7DE670; /* 对应1px */
  border-radius: 32rpx; /* 对应16px */
  box-shadow: 0 8rpx 8rpx rgba(148, 148, 148, 0.25);
  overflow: hidden;
}

.record-item.pending {
  background: #F5F5F5;
  border: 2rpx solid #C0C0C0;
}

.record-content {
  padding: 0 24rpx; /* 对应0 12px */
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 24rpx; /* 对应12px */
}

/* 左侧编号圆圈 */
.number-circle {
  width: 57rpx; /* 对应28.47px */
  height: 56rpx; /* 对应28px */
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.number-circle.completed {
  background: linear-gradient(324.16deg, #7EFFAB 15.86%, #00C92C 48.99%);
}

.number-circle.pending {
  background: #E3E4E4;
}

.circle-number {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 28rpx; /* 对应14px */
  line-height: 34rpx; /* 对应17px */
  color: #FFFFFF;
}

.check-icon {
  width: 32rpx; /* 对应16px */
  height: 32rpx; /* 对应16px */
}

/* 中间文本内容 */
.record-text-content {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  flex: 1;
}

.record-day-text {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 28rpx; /* 对应14px */
  line-height: 34rpx; /* 对应17px */
  color: #0F8500;
  text-align: center;
}

.record-item.pending .record-day-text {
  color: #666666;
}

.record-time-text {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 24rpx; /* 对应12px */
  line-height: 30rpx; /* 对应15px */
  color: #00BA32;
  text-align: center;
  margin-top: 2rpx; /* 对应1px */
}

.record-item.pending .record-time-text {
  color: #999999;
}

/* 右侧完成状态圆圈 */
.completion-circle {
  width: 49rpx; /* 对应24.4px */
  height: 48rpx; /* 对应24px */
  border-radius: 50%;
  background: linear-gradient(324.16deg, #7EFFAB 15.86%, #00C92C 48.99%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.completion-check {
  width: 20rpx; /* 对应10px */
  height: 20rpx; /* 对应10px */
}

/* 模态框基础样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(51, 51, 51, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

/* 申请换队友确认弹窗样式 */
.exchange-confirm-modal {
  width: 600rpx; /* 对应300px */
  background: #FFFFFF;
  border-radius: 24rpx; /* 对应12px */
  padding: 0;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.15);
}

.modal-header {
  padding: 50rpx 40rpx 30rpx;
  text-align: center;
}

.modal-title {
  font-family: 'Inter';
  font-weight: 600;
  font-size: 36rpx; /* 对应18px */
  line-height: 44rpx; /* 对应22px */
  color: #000000;
}

.modal-content {
  padding: 0 40rpx 40rpx;
  text-align: center;
}

.modal-text {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 30rpx; /* 对应15px */
  line-height: 40rpx; /* 对应20px */
  color: #666666;
}

.modal-actions {
  display: flex;
  border-top: 1rpx solid #E8E8E8;
}

.modal-button {
  flex: 1;
  height: 100rpx; /* 对应50px */
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.modal-button.cancel {
  border-right: 1rpx solid #E8E8E8;
}

.modal-button.confirm {
  background: #FF5A5A;
  border-radius: 0 0 24rpx 0;
}

.modal-button.cancel .button-text {
  color: #999999;
}

.modal-button.confirm .button-text {
  color: #FFFFFF;
  font-weight: 600;
}

.button-text {
  font-family: 'Inter';
  font-size: 32rpx; /* 对应16px */
  line-height: 40rpx; /* 对应20px */
}

/* 等待对方回应弹窗样式 */
.waiting-modal {
  width: 620rpx; /* 对应310px */
  background: #FFFFFF;
  border-radius: 32rpx; /* 对应16px */
  padding: 80rpx 60rpx 60rpx;
  text-align: center;
  box-shadow: 0 12rpx 40rpx rgba(0, 0, 0, 0.15);
}

.waiting-header {
  margin-bottom: 50rpx; /* 对应25px */
}

.waiting-logo {
  width: 160rpx; /* 对应80px */
  height: 160rpx; /* 对应80px */
}

.waiting-content {
  margin-bottom: 80rpx; /* 对应40px */
}

.waiting-title {
  font-family: 'Inter';
  font-weight: 600;
  font-size: 40rpx; /* 对应20px */
  line-height: 50rpx; /* 对应25px */
  color: #000000;
  margin-bottom: 20rpx; /* 对应10px */
  display: block;
}

.waiting-subtitle {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 30rpx; /* 对应15px */
  line-height: 40rpx; /* 对应20px */
  color: #666666;
  display: block;
}

.waiting-actions {
  display: flex;
  justify-content: center;
}

.waiting-button {
  padding: 24rpx 60rpx; /* 对应12px 30px */
  border: 2rpx solid #E8E8E8; /* 对应1px */
  border-radius: 50rpx; /* 对应25px */
  background: #FFFFFF;
}

.waiting-button-text {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 30rpx; /* 对应15px */
  line-height: 40rpx; /* 对应20px */
  color: #666666;
}

/* 换队友结果弹窗样式 */
.result-modal {
  width: 600rpx; /* 对应300px */
  background: #FFFFFF;
  border-radius: 24rpx; /* 对应12px */
  padding: 0;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.15);
}

.result-header {
  padding: 50rpx 40rpx 30rpx;
  text-align: center;
}

.result-title {
  font-family: 'Inter';
  font-weight: 600;
  font-size: 36rpx; /* 对应18px */
  line-height: 44rpx; /* 对应22px */
  color: #FF5A5A;
}

.result-modal.success .result-title {
  color: #00BA32;
}

.result-content {
  padding: 0 40rpx 40rpx;
  text-align: center;
}

.result-text {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 30rpx; /* 对应15px */
  line-height: 40rpx; /* 对应20px */
  color: #666666;
}

.result-actions {
  display: flex;
  border-top: 1rpx solid #E8E8E8;
}

.result-button {
  flex: 1;
  height: 100rpx; /* 对应50px */
  display: flex;
  align-items: center;
  justify-content: center;
  background: #007AFF;
  border-radius: 0 0 24rpx 24rpx;
}

.result-button-text {
  font-family: 'Inter';
  font-weight: 600;
  font-size: 32rpx; /* 对应16px */
  line-height: 40rpx; /* 对应20px */
  color: #FFFFFF;
}

/* 收到换队友申请弹窗样式 */
.received-exchange-modal {
  width: 600rpx; /* 对应300px */
  background: #FFFFFF;
  border-radius: 24rpx; /* 对应12px */
  padding: 0;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.15);
}

.received-exchange-modal .modal-header {
  padding: 50rpx 40rpx 30rpx;
  text-align: center;
}

.received-exchange-modal .modal-content {
  padding: 0 40rpx 40rpx;
  text-align: center;
}

.received-exchange-modal .modal-text {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 30rpx; /* 对应15px */
  line-height: 40rpx; /* 对应20px */
  color: #000000;
  display: block;
  margin-bottom: 10rpx;
}

.received-exchange-modal .modal-actions {
  display: flex;
  border-top: 1rpx solid #E8E8E8;
}

.received-exchange-modal .modal-button {
  flex: 1;
  height: 100rpx; /* 对应50px */
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.received-exchange-modal .modal-button.agree {
  background: #00BA32;
  border-radius: 0 0 0 24rpx;
}

.received-exchange-modal .modal-button.disagree {
  background: #FF5A5A;
  border-radius: 0 0 24rpx 0;
  border-left: 1rpx solid #E8E8E8;
}

.received-exchange-modal .modal-button .button-text {
  font-family: 'Inter';
  font-weight: 600;
  font-size: 32rpx; /* 对应16px */
  line-height: 40rpx; /* 对应20px */
  color: #FFFFFF;
}

</style>