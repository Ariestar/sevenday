<template>
  <view class="single-match-result-page">
    <!-- 背景图片 -->
    <view class="result-gradient-bg"></view>

    <!-- 报名/匹配标签切换区域 -->
    <view class="tab-section">
      <view class="tab-group">
        <view class="tab-item" @click="goToSignup">
          <text class="tab-text">报名</text>
        </view>
        <view class="tab-item active">
          <text class="tab-text active">匹配</text>
          <view class="tab-indicator"></view>
        </view>
      </view>
    </view>

    <!-- 标签切换区域 -->
    <view class="result-tab-section">
      <view class="result-tab-group">
        <view class="result-tab-item" @click="backToExpectation">
          <text class="result-tab-text">你的期望</text>
        </view>
        <view class="result-tab-item active">
          <text class="result-tab-text active">智能匹配</text>
          <view class="result-tab-indicator"></view>
        </view>
        <view class="result-tab-item disabled">
          <text class="result-tab-text">确认组队</text>
        </view>
      </view>
    </view>

    <!-- 匹配结果卡片 -->
    <view class="match-result-card">
      <!-- 队友信息区域 -->
      <view class="teammate-info">
        <view class="info-item">
          <text class="info-label">姓名：</text>
          <text class="info-value">{{ matchResult.name || '张同学' }}</text>
        </view>
        <view class="info-item">
          <text class="info-label">性别：</text>
          <text class="info-value">{{ matchResult.gender || '女' }}</text>
        </view>
        <view class="info-item">
          <text class="info-label">学历：</text>
          <text class="info-value">{{ matchResult.education || '本科生' }}</text>
        </view>
        <view class="info-item">
          <text class="info-label">大类：</text>
          <text class="info-value">{{ matchResult.majorCategory || '工科' }}</text>
        </view>
        <view class="info-item">
          <text class="info-label">院系：</text>
          <text class="info-value">{{ matchResult.college || '计算机学院' }}</text>
        </view>
      </view>
    </view>

    <!-- 头像区域 -->
    <view class="avatar-section">
      <view class="avatar-circle">
        <image 
          v-if="matchResult.avatar" 
          :src="matchResult.avatar" 
          class="avatar-image" 
          mode="aspectFill" 
        />
        <text v-else class="avatar-placeholder">👤</text>
      </view>
    </view>

    <!-- 匹配信息标题 -->
    <view class="match-info-header">
      <view class="info-icon">
        <image src="/static/match-single-part1/star.png" class="info-star" mode="aspectFit" />
      </view>
      <text class="info-title">为您匹配到的队友信息</text>
    </view>

    <!-- 组队确认 -->
    <view class="team-confirm-section">
      <view class="confirm-header">
        <view class="confirm-icon">
          <image src="/static/match-single-part1/star.png" class="confirm-star" mode="aspectFit" />
        </view>
        <text class="confirm-title">是否组队？</text>
      </view>

      <!-- 确认按钮 -->
      <view class="confirm-buttons">
        <button class="confirm-btn yes-btn" @click="handleConfirmTeam">
          <text class="confirm-btn-text">是</text>
        </button>
        <button class="confirm-btn no-btn" @click="handleRejectTeam">
          <text class="confirm-btn-text">否</text>
        </button>
      </view>
    </view>

    <!-- 等待组队弹窗 -->
    <view v-if="showWaitModal" class="wait-modal-mask">
      <view class="wait-modal" :style="{ backgroundImage: 'url(/static/match-single-part2/wait-match.png)' }">
        <text class="wait-text">确认组队中...</text>
      </view>
    </view>

    <!-- 成功弹窗 -->
    <SuccessModal
      :visible="showSuccessModal"
      @update:visible="showSuccessModal = $event"
      @close="handleSuccessClose"
      :type="successType"
      :title="successTitle"
    />

    <!-- 底部导航栏 -->
    <view class="bottom-navigation">
      <!-- 报名-匹配 (选中状态) -->
      <view class="nav-item active" @click="goToMultipleMatch">
        <view class="nav-icon-wrapper">
          <image src="/static/navigation/match-on.png" class="nav-icon" mode="aspectFit" />
        </view>
        <text class="nav-text active">报名-匹配</text>
      </view>
      
      <!-- 打卡 -->
      <view class="nav-item" @click="goToCheckin">
        <view class="nav-icon-wrapper">
          <image src="/static/navigation/checkin-off.png" class="nav-icon" mode="aspectFit" />
        </view>
        <text class="nav-text">打卡</text>
      </view>
      
      <!-- 广场 -->
      <view class="nav-item" @click="goToSquare">
        <view class="nav-icon-wrapper">
          <image src="/static/navigation/square-off.png" class="nav-icon" mode="aspectFit" />
        </view>
        <text class="nav-text">广场</text>
      </view>
      
      <!-- 我的 -->
      <view class="nav-item" @click="goToMine">
        <view class="nav-icon-wrapper">
          <image src="/static/navigation/mine-off.png" class="nav-icon" mode="aspectFit" />
        </view>
        <text class="nav-text">我的</text>
      </view>
    </view>
  </view>
</template>

<script>
import SuccessModal from '../../components/SuccessModal.vue'

export default {
  components: {
    SuccessModal
  },
  data() {
    return {
      matchResult: {
        name: '',
        gender: '',
        education: '',
        majorCategory: '',
        college: '',
        avatar: ''
      },
      showSuccessModal: false,
      successType: 'team-success',
      successTitle: '组队成功！',
      showWaitModal: false // 等待组队弹窗
    }
  },
  onLoad(options) {
    console.log('单人匹配结果页面加载', options)
    
    // 从上一个页面接收匹配结果数据
    if (options.matchData) {
      try {
        this.matchResult = JSON.parse(decodeURIComponent(options.matchData))
      } catch (error) {
        console.error('解析匹配数据失败:', error)
      }
    }
    
    // 如果没有匹配数据，使用默认数据
    if (!this.matchResult.name) {
      this.matchResult = {
        name: '张同学',
        gender: '女',
        education: '本科生',
        majorCategory: '工科',
        college: '计算机学院',
        avatar: ''
      }
    }
  },
  methods: {
    // 返回期望填写界面
    backToExpectation() {
      uni.navigateBack({
        success: () => {
          console.log('返回期望页面成功')
        },
        fail: (err) => {
          console.warn('返回失败，尝试其他方式:', err)
          // 如果无法返回，尝试重定向
          uni.reLaunch({
            url: '/pages/single-match/index',
            success: () => {
              console.log('重定向到期望页面成功')
            },
            fail: (err2) => {
              console.error('跳转期望页面失败:', err2)
              uni.showToast({
                title: '请手动切换到期望页面',
                icon: 'none',
                duration: 2000
              })
            }
          })
        }
      })
    },
    // 处理组队确认
    async handleConfirmTeam() {
      try {
        // 显示等待弹窗
        this.showWaitModal = true
        
        // TODO: 调用确认组队API
        console.log('确认组队:', this.matchResult)
        
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // 隐藏等待弹窗
        this.showWaitModal = false
        
        // 跳转到确认组队页面，显示组队成功状态
        const teamData = {
          myInfo: {
            gender: '男',
            education: '本科生', 
            majorCategory: '理科',
            college: '物理学院',
            qq: '123456',
            avatar: ''
          },
          partnerInfo: this.matchResult
        }
        
        // 使用 redirectTo 替换当前页面，避免页面栈过深
        uni.redirectTo({
          url: `/pages/single-match-confirm/index?teamData=${encodeURIComponent(JSON.stringify(teamData))}`,
          success: () => {
            console.log('跳转到确认组队页面成功')
          },
          fail: (err) => {
            console.error('跳转到确认组队页面失败:', err)
            // 降级方案：尝试使用 navigateTo
            uni.navigateTo({
              url: `/pages/single-match-confirm/index?teamData=${encodeURIComponent(JSON.stringify(teamData))}`,
              success: () => {
                console.log('使用 navigateTo 跳转成功')
              },
              fail: (err2) => {
                console.error('所有跳转方式都失败:', err2)
                // 最后降级：显示成功弹窗
                this.successType = 'team-success'
                this.successTitle = '组队成功！'
                this.showSuccessModal = true
              }
            })
          }
        })
        
      } catch (error) {
        // 隐藏等待弹窗
        this.showWaitModal = false
        console.error('组队失败:', error)
        
        uni.showToast({
          title: error.message || '组队失败，请重试',
          icon: 'none'
        })
      }
    },
    // 处理拒绝组队
    async handleRejectTeam() {
      try {
        uni.showModal({
          title: '确认拒绝',
          content: '确定要拒绝与该同学组队吗？',
          success: async (res) => {
            if (res.confirm) {
              uni.showLoading({ title: '处理中...' })
              
              // TODO: 调用拒绝组队API
              console.log('拒绝组队:', this.matchResult)
              
              // 模拟API调用
              await new Promise(resolve => setTimeout(resolve, 800))
              
              uni.hideLoading()
              
              // 返回到期望填写界面，用户可以重新匹配
              this.backToExpectation()
              
              uni.showToast({
                title: '已拒绝组队',
                icon: 'success'
              })
            }
          }
        })
      } catch (error) {
        console.error('拒绝组队失败:', error)
        
        uni.showToast({
          title: error.message || '操作失败，请重试',
          icon: 'none'
        })
      }
    },
    handleSuccessClose() {
      this.showSuccessModal = false
      
      if (this.successType === 'team-success') {
        // 组队成功后跳转到其他页面（比如聊天页面或主页）
        console.log('组队成功，跳转到主页')
        uni.switchTab({
          url: '/pages/checkin-detail/index',
          fail: (err) => {
            console.warn('跳转失败:', err)
            uni.reLaunch({ url: '/pages/checkin-detail/index' })
          }
        })
      }
    },
    goToSignup() {
      // 跳转到报名页面
      uni.reLaunch({
        url: '/pages/signup/index',
        fail: (err) => {
          console.warn('跳转失败:', err)
          uni.showToast({
            title: '跳转失败，请重试',
            icon: 'none'
          })
        }
      })
    },
    goToMultipleMatch() {
      // 跳转到报名页面，而不是多人匹配页面（多人匹配未开放）
      uni.reLaunch({
        url: '/pages/signup/index',
        fail: (err) => {
          console.warn('跳转失败:', err)
          uni.navigateTo({
            url: '/pages/signup/index',
            fail: () => {
              uni.showToast({
                title: '跳转失败，请重试',
                icon: 'none'
              })
            }
          })
        }
      })
    },
    goToCheckin() {
      uni.switchTab({
        url: '/pages/checkin-detail/index',
        fail: (err) => {
          console.warn('跳转失败:', err)
          uni.reLaunch({ url: '/pages/checkin-detail/index' })
        }
      })
    },
    goToSquare() {
      uni.switchTab({
        url: '/pages/square/index',
        fail: (err) => {
          console.warn('跳转失败:', err)
          uni.reLaunch({ url: '/pages/square/index' })
        }
      })
    },
    goToMine() {
      uni.switchTab({
        url: '/pages/mine/index',
        fail: (err) => {
          console.warn('跳转失败:', err)
          uni.reLaunch({ url: '/pages/mine/index' })
        }
      })
    }
  }
}
</script>

<style scoped>
.single-match-result-page {
  width: 750rpx;
  min-height: 1624rpx; /* 对应812px */
  background: linear-gradient(180deg, #F7E7FF 0%, #FFFFFF 100%);
  position: relative;
  margin: 0 auto;
  padding-bottom: 112rpx; /* 为底部导航栏留空间 */
}

/* 结果页面背景图片 */
.result-gradient-bg {
  position: absolute;
  top: -66rpx; /* 往上移动状态栏的高度，使背景与文字对齐 */
  left: 0;
  right: 0;
  height: 312rpx; /* 对应156px */
  background-image: url('/static/match-single-part1/part2-banner-background.png');
  background-size: cover;
  background-position: center top;
  background-repeat: no-repeat;
  z-index: 1;
}

/* 报名/匹配标签切换区域 */
.tab-section {
  position: absolute;
  top: 72rpx; /* 对应36px */
  left: 138rpx; /* 对应69px */
  width: 472rpx; /* 对应236px */
  height: 74rpx; /* 对应37px */
  z-index: 10;
}

.tab-group {
  display: flex;
  height: 100%;
  position: relative;
}

.tab-item {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 74rpx;
  position: relative;
}

.tab-text {
  font-size: 32rpx; /* 对应16px */
  font-weight: 400;
  color: #FFFFFF;
}

.tab-text.active {
  font-weight: 700;
}

.tab-indicator {
  position: absolute;
  bottom: 13rpx;
  left: 50%;
  transform: translateX(-50%);
  width: 120rpx; /* 对应60px */
  height: 36rpx; /* 对应18px */
  background: rgba(255, 255, 255, 0.4);
  border-radius: 180rpx; /* 对应90px */
}

/* 结果页面标签切换区域 */
.result-tab-section {
  position: absolute;
  top: 180rpx; /* 对应90px，下移标签区域 */
  left: 60rpx; /* 对应30px，从左侧开始 */
  right: 60rpx; /* 对应右侧，实现全宽度分布 */
  height: 38rpx; /* 对应19px */
  z-index: 10;
}

.result-tab-group {
  display: flex;
  height: 100%;
  width: 100%;
  justify-content: space-between; /* 使用space-between均匀分布 */
  align-items: center;
  position: relative;
}

.result-tab-item {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 38rpx; /* 对应19px */
  position: relative;
  flex-shrink: 0; /* 防止压缩 */
}

.result-tab-text {
  font-size: 32rpx; /* 对应16px */
  font-weight: 400;
  color: #000000; /* 改为黑色 */
}

.result-tab-text.active {
  font-weight: 700;
  color: #000000; /* 保持黑色，只是加粗 */
}

.result-tab-item.disabled {
  opacity: 0.5;
  pointer-events: none; /* 禁用点击 */
}

.result-tab-indicator {
  position: absolute;
  bottom: -10rpx; /* 调整位置，在文字下方显示 */
  left: 50%;
  transform: translateX(-50%);
  width: 120rpx; /* 对应60px */
  height: 36rpx; /* 对应18px */
  background: rgba(255, 255, 255, 0.4);
  border-radius: 180rpx; /* 对应90px */
}

/* 匹配结果卡片 */
.match-result-card {
  position: absolute;
  top: 486rpx; /* 对应243px */
  left: 50%;
  transform: translateX(-50%);
  width: 622rpx; /* 对应311px */
  height: 614rpx; /* 对应307px */
  background: #FFFFFF;
  border: 4rpx solid #A100FE; /* 对应2px */
  border-radius: 18rpx; /* 对应9px */
  box-sizing: border-box; /* 确保border不会增加总宽度 */
  z-index: 10;
}

/* 头像区域 */
.avatar-section {
  position: absolute;
  top: 300rpx; /* 对应150px */
  left: 50%;
  transform: translateX(-50%);
  width: 236rpx; /* 对应118px */
  height: 236rpx; /* 对应118px */
  z-index: 15; /* 高于信息展示框的z-index(10)，确保头像显示在上层 */
}

.avatar-circle {
  width: 236rpx; /* 对应118px */
  height: 236rpx; /* 对应118px */
  border-radius: 50%;
  background: #E3E4E4;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.avatar-image {
  width: 100%;
  height: 100%;
  border-radius: 50%;
}

.avatar-placeholder {
  font-size: 80rpx;
  color: #9094A6;
}

/* 匹配信息标题 */
.match-info-header {
  position: absolute;
  top: 552rpx; /* 对应276px */
  left: calc(50% - 392rpx/2 - 17rpx); /* 对应 calc(50% - 196px/2 - 8.5px) */
  width: 392rpx; /* 对应196px */
  height: 52rpx; /* 对应26px */
  display: flex;
  align-items: center;
}

.info-icon {
  width: 66rpx; /* 对应33px */
  height: 52rpx; /* 对应26px */
  margin-right: 20rpx;
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

.info-star {
  width: 40rpx;
  height: 40rpx;
}

.info-title {
  font-size: 32rpx; /* 对应16px */
  font-weight: 400;
  color: #000000;
}

/* 队友信息区域 */
.teammate-info {
  display: none; /* 暂时隐藏详细信息，根据设计稿调整 */
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 16rpx;
  padding: 8rpx 0;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-label {
  font-size: 28rpx;
  font-weight: 400;
  color: #666666;
  width: 120rpx;
  flex-shrink: 0;
}

.info-value {
  font-size: 28rpx;
  font-weight: 400;
  color: #000000;
  flex: 1;
}

/* 组队确认区域 */
.team-confirm-section {
  position: absolute;
  top: 1154rpx; /* 对应577px */
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
}

.confirm-header {
  position: absolute;
  top: 0;
  left: calc(50% - 232rpx/2 + 1rpx); /* 对应 calc(50% - 116px/2 + 0.5px) */
  width: 232rpx; /* 对应116px */
  height: 52rpx; /* 对应26px */
  display: flex;
  align-items: center;
  justify-content: center;
}

.confirm-icon {
  width: 66rpx; /* 对应33px */
  height: 52rpx; /* 对应26px */
  margin-right: 20rpx;
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

.confirm-star {
  width: 40rpx;
  height: 40rpx;
}

.confirm-title {
  font-size: 26rpx; /* 对应16px */
  font-weight: 400;
  color: #000000;
}

/* 确认按钮 */
.confirm-buttons {
  position: absolute;
  top: 106rpx; /* 630px - 577px = 53px ≈ 106rpx */
  left: 64rpx; /* 对应32px */
  width: 622rpx; /* 对应311px */
  height: 94rpx; /* 对应47px */
  display: flex;
  gap: 46rpx; /* 按钮间距 */
  justify-content: center;
}

.confirm-btn {
  width: 280rpx; /* 对应140px */
  height: 94rpx; /* 对应47px */
  border-radius: 180rpx; /* 对应90px */
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

.confirm-btn::after {
  border: none;
}

.yes-btn {
  background: linear-gradient(90deg, #A100FE 0%, #FDB9E7 100%);
}

.no-btn {
  background: linear-gradient(90deg, #1F2735 0%, #A100FE 48.08%);
  transform: matrix(-1, 0, 0, 1, 0, 0); /* 水平翻转渐变 */
}

.confirm-btn-text {
  font-size: 32rpx; /* 对应16px */
  font-weight: 400;
  color: #FFFFFF;
}

/* 等待组队弹窗 */
.wait-modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.wait-modal {
  width: 500rpx;
  height: 500rpx;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  border-radius: 18rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.wait-text {
  font-size: 32rpx;
  font-weight: 400;
  color: #FFFFFF;
  text-align: center;
  position: absolute;
  bottom: 80rpx; /* 文字显示在图片底部 */
  left: 50%;
  transform: translateX(-50%);
  z-index: 1;
  text-shadow: 0 2rpx 4rpx rgba(0, 0, 0, 0.3); /* 添加文字阴影以提高可读性 */
}

/* 底部导航栏 */
.bottom-navigation {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 112rpx; /* 对应56px */
  background: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 0;
  z-index: 100;
  box-shadow: 0 -2rpx 10rpx rgba(0, 0, 0, 0.1);
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 112rpx; /* 对应56px */
  height: 112rpx;
  cursor: pointer;
}

.nav-icon-wrapper {
  width: 56rpx; /* 对应28px */
  height: 56rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8rpx;
}

.nav-icon {
  width: 48rpx; /* 对应24px */
  height: 48rpx;
}

.nav-text {
  font-size: 20rpx; /* 对应10px */
  color: #9094A6;
  font-weight: 400;
  text-align: center;
  line-height: 24rpx; /* 对应12px */
}

.nav-text.active {
  color: #1F2635;
  font-weight: 400;
}

/* 为"报名-匹配"选中状态特殊处理 */
.nav-item.active .nav-text {
  color: #1F2635;
}
</style>
