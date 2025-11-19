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
              <view class="avatar-icon"></view>
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
          <text class="modal-text">确定要申请换队友吗？此操作会通知管理员处理。</text>
        </view>
        <view class="modal-actions">
          <view class="modal-button cancel" @tap="closeExchangeConfirmModal">
            <text class="button-text">取消</text>
          </view>
          <view class="modal-button confirm" @tap="confirmExchangeRequest">
            <text class="button-text">确定</text>
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
          <text class="waiting-subtitle">已向管理员发送换队友申请</text>
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
  </view>
</template>

<script>
import CustomTabBar from '@/components/CustomTabBar.vue'

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
      exchangeResult: {
        title: '',
        message: ''
      },
      teamStats: {
        days: 2,
        completedTasks: 5,
        credits: 12
      },
      checkinRecords: [
        {
          day: 1,
          status: 'completed-checked',
          completedTime: '今日14:05完成',
          expanded: false,
          details: '今日完成晨跑30分钟，上传了运动照片和心得体会。'
        },
        {
          day: 2,
          status: 'pending',
          completedTime: null,
          expanded: false,
          details: '等待提交打卡内容。'
        },
        {
          day: 3,
          status: 'not-started',
          completedTime: null,
          expanded: false,
          details: '任务尚未开始。'
        }
      ]
    }
  },
  onLoad() {
    this.loadTeammateData()
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

    confirmExchangeRequest() {
      this.showExchangeConfirmModal = false
      this.showWaitingModal = true
      
      // 模拟等待对方回应的过程（实际项目中这里应该调用API）
      this.simulateExchangeResponse()
    },

    cancelExchangeRequest() {
      this.showWaitingModal = false
      uni.showToast({
        title: '已取消申请',
        icon: 'none'
      })
    },

    simulateExchangeResponse() {
      // 模拟4秒后收到对方回应
      setTimeout(() => {
        this.showWaitingModal = false
        
        // 随机模拟对方同意或拒绝（实际项目中这里应该是真实的服务器响应）
        const isAccepted = Math.random() > 0.5
        
        if (isAccepted) {
          // 对方同意换队友
          this.exchangeResult = {
            title: '换队友成功',
            message: '对方已同意换队友申请，队伍已解散。'
          }
        } else {
          // 对方拒绝换队友
          this.exchangeResult = {
            title: '对方已拒绝更换队友申请！',
            message: '对方拒绝了换队友申请，将继续保持当前组队。'
          }
        }
        
        this.showResultModal = true
      }, 4000)
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
      }
      // 如果拒绝，则保持当前页面，不做任何操作
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
    
    loadTeammateData() {
      // TODO: 从接口加载队友数据和打卡记录
      console.log('加载队友数据')
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
  height: 420rpx; /* 对应210px */
  margin: 0 auto 40rpx; /* 对应0 auto 20px */
  background: #FFFFFF;
  border-radius: 24rpx; /* 对应12px */
  padding: 40rpx; /* 对应20px */
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

</style>