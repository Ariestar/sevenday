<template>
  <view class="single-match-page">
    <!-- 渐变背景容器 -->
    <view class="gradient-container">
      <!-- 顶部背景图片 -->
      <view class="gradient-bg"></view>
      
      <!-- 标签切换区域 -->
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

      <!-- 你的期望标题 -->
      <view class="expectation-header">
        <text class="expectation-title">你的期望</text>
        
        <!-- 右侧按钮组 -->
        <view class="action-buttons">
          <button class="action-btn smart-match" @click="handleIntelligentMatch">
            智能匹配
          </button>
        </view>
      </view>
    </view>

    <!-- 主要内容区域 -->
    <view class="content-section">
      <!-- 性别选择 -->
      <view class="form-group">
        <view class="form-label-row">
          <view class="form-icon">
            <image src="/static/match-single-part1/star.png" class="icon-star" mode="aspectFit" />
          </view>
          <text class="form-label">你希望匹配对象的性别</text>
        </view>
        <view class="form-input-container">
          <picker 
            :value="selectedGenderIndex" 
            :range="genderOptions" 
            range-key="label"
            @change="onGenderChange"
            class="form-picker"
          >
            <view class="picker-content">
              <text class="picker-text">{{ expectation.gender ? getGenderLabel(expectation.gender) : '请选择' }}</text>
            </view>
          </picker>
        </view>
      </view>

      <!-- 大类选择 -->
      <view class="form-group">
        <view class="form-label-row">
          <view class="form-icon">
            <image src="/static/match-single-part1/star.png" class="icon-star" mode="aspectFit" />
          </view>
          <text class="form-label">你希望匹配对象的大类</text>
        </view>
        <view class="form-input-container">
          <picker 
            :value="selectedMajorIndex" 
            :range="majorOptions" 
            range-key="label"
            @change="onMajorChange"
            class="form-picker"
          >
            <view class="picker-content">
              <text class="picker-text">{{ expectation.majorCategory ? getMajorLabel(expectation.majorCategory) : '请选择' }}</text>
            </view>
          </picker>
        </view>
      </view>

      <!-- 学院选择 -->
      <view class="form-group">
        <view class="form-label-row">
          <view class="form-icon">
            <image src="/static/match-single-part1/star.png" class="icon-star" mode="aspectFit" />
          </view>
          <text class="form-label">你希望匹配对象的学院</text>
        </view>
        <view class="form-input-container">
          <picker 
            :value="selectedAcademyIndex" 
            :range="academyOptions" 
            range-key="name"
            @change="onAcademyChange"
            class="form-picker"
          >
            <view class="picker-content">
              <text class="picker-text">{{ expectation.college || '请选择' }}</text>
            </view>
          </picker>
        </view>
      </view>
    </view>

    <!-- 底部按钮区域 -->
    <view class="bottom-buttons">
      <!-- 开始匹配按钮 -->
      <button class="start-match-btn" @click="handleStartMatch" :disabled="!isFormValid">
        <image src="/static/match-single-part1/start-match-star.png" class="btn-icon left" mode="aspectFit" />
        <text class="btn-text">开始匹配</text>
        <image src="/static/match-single-part1/start-match-star.png" class="btn-icon right" mode="aspectFit" />
      </button>
      
      <!-- 保存按钮 -->
      <button class="save-btn" @click="handleSave" :disabled="saving">
        <text class="btn-text">{{ saving ? '保存中...' : '保存' }}</text>
      </button>
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
import { GENDER_OPTIONS, MAJOR_CATEGORY_OPTIONS } from '../../utils/constants'
import { saveMatchExpectation, getMatchExpectation, recommendMatches, autoMatch } from '../../services/match'
import { getAcademies } from '../../services/academies'
import SuccessModal from '../../components/SuccessModal.vue'

export default {
  components: {
    SuccessModal
  },
  data() {
    return {
      expectation: {
        gender: '',
        degree: '',
        majorCategory: '',
        college: ''
      },
      genderOptions: GENDER_OPTIONS,
      majorOptions: MAJOR_CATEGORY_OPTIONS,
      academyOptions: [], // 院系选项列表（扁平化后的）
      showSuccessModal: false,
      successType: 'save',
      successTitle: '保存成功！',
      saving: false
    }
  },
  computed: {
    selectedGenderIndex() {
      return this.genderOptions.findIndex(item => item.value === this.expectation.gender)
    },
    selectedMajorIndex() {
      return this.majorOptions.findIndex(item => item.value === this.expectation.majorCategory)
    },
    selectedAcademyIndex() {
      return this.academyOptions.findIndex(item => item.name === this.expectation.college)
    },
    isFormValid() {
      return this.expectation.gender && this.expectation.majorCategory
    }
  },
  onLoad(options) {
    console.log('单人匹配页面加载', options)
    // 如果是从报名页面跳转过来，可能会有参数
    if (options.from === 'signup') {
      console.log('从报名页面跳转过来')
    }
    this.loadAcademies()
    this.loadMatchExpectation()
  },
  methods: {
    onGenderChange(e) {
      const index = e.detail.value
      this.expectation.gender = this.genderOptions[index]?.value || ''
    },
    onMajorChange(e) {
      const index = e.detail.value
      this.expectation.majorCategory = this.majorOptions[index]?.value || ''
    },
    onAcademyChange(e) {
      const index = e.detail.value
      const academy = this.academyOptions[index]
      if (academy) {
        this.expectation.college = academy.name
      }
    },
    async loadAcademies() {
      try {
        const academies = await getAcademies()
        // 将嵌套的院系数据扁平化，包含父级和子级
        const flatAcademies = []
        academies.forEach(parent => {
          // 添加父级院系
          flatAcademies.push({ id: parent.id, name: parent.name })
          // 添加子级院系
          if (parent.children && parent.children.length > 0) {
            parent.children.forEach(child => {
              flatAcademies.push({ id: child.id, name: child.name })
            })
          }
        })
        this.academyOptions = flatAcademies
      } catch (err) {
        console.error('加载院系列表失败:', err)
        // 如果API调用失败，使用空数组，不影响页面显示
        this.academyOptions = []
      }
    },
    async loadMatchExpectation() {
      try {
        const result = await getMatchExpectation()
        if (result) {
          // 更新期望数据
          if (result.gender) {
            // 转换格式：男/女 -> male/female
            if (result.gender === '男') {
              this.expectation.gender = 'male'
            } else if (result.gender === '女') {
              this.expectation.gender = 'female'
            } else {
              this.expectation.gender = result.gender
            }
          }
          if (result.degree) {
            this.expectation.degree = result.degree
          }
          if (result.majorCategory) {
            this.expectation.majorCategory = result.majorCategory
          }
          if (result.college) {
            this.expectation.college = result.college
          }
        }
      } catch (err) {
        console.error('加载匹配期望失败:', err)
        // 如果API调用失败，不影响页面显示
      }
    },
    getGenderLabel(value) {
      const option = this.genderOptions.find(item => item.value === value)
      return option ? option.label : ''
    },
    getMajorLabel(value) {
      const option = this.majorOptions.find(item => item.value === value)
      return option ? option.label : ''
    },
    getEducationFromGrade(grade) {
      if (!grade) return ''
      return grade <= 4 ? '本科生' : (grade <= 6 ? '研究生' : '')
    },
    async handleStartMatch() {
      if (!this.isFormValid) {
        uni.showToast({
          title: '请完善匹配条件',
          icon: 'none'
        })
        return
      }

      try {
        uni.showLoading({ title: '保存中...' })
        
        // 先保存期望信息
        const saveData = {
          gender: this.expectation.gender || '',
          degree: this.expectation.degree || '',
          majorCategory: this.expectation.majorCategory || '',
          college: this.expectation.college || ''
        }
        
        await saveMatchExpectation(saveData)
        
        // 保存成功后，检查是否有匹配对象
        uni.showLoading({ title: '匹配中...' })
        let hasMatch = false
        let matchResultData = null
        
        try {
          // 先尝试自动匹配
          const autoMatchResult = await autoMatch()
          console.log('自动匹配结果:', autoMatchResult)
          
          // 检查自动匹配是否成功（返回格式：{ teammate: {...}, team: {...} }）
          if (autoMatchResult && autoMatchResult.teammate) {
            hasMatch = true
            const teammate = autoMatchResult.teammate
            matchResultData = {
              id: teammate.id,
              name: teammate.username || teammate.name || '未知',
              gender: teammate.gender === 1 ? '男' : (teammate.gender === 2 ? '女' : ''),
              education: this.getEducationFromGrade(teammate.grade),
              majorCategory: teammate.major_category || '',
              college: teammate.academy?.name || '',
              avatar: teammate.avatar || ''
            }
          } else {
            // 如果自动匹配没有结果，尝试获取推荐列表
            const recommendResult = await recommendMatches({ limit: 10 })
            console.log('推荐结果:', recommendResult)
            
            // 处理返回的数据结构：recommendResult 可能是 { code, msg, data } 或直接是 data
            const recommendData = recommendResult?.data || recommendResult
            
            // 检查是否已经匹配成功
            if (recommendData && recommendData.isMatched === true && recommendData.teammates && recommendData.teammates.length > 0) {
              // 已经匹配成功，使用队友信息
              hasMatch = true
              const teammate = recommendData.teammates[0]
              console.log('队友原始数据:', teammate)
              matchResultData = {
                id: teammate.id,
                name: teammate.username || teammate.name || '未知',
                gender: teammate.gender === 1 ? '男' : (teammate.gender === 2 ? '女' : ''),
                education: this.getEducationFromGrade(teammate.grade),
                majorCategory: teammate.major_category || teammate.majorCategory || '',
                college: teammate.academy?.name || teammate.academy_name || teammate.college || '',
                avatar: teammate.avatar || ''
              }
            } else if (recommendData && recommendData.recommendations && recommendData.recommendations.length > 0) {
              // 有推荐对象
              hasMatch = true
              // 使用第一个推荐对象
              const rec = recommendData.recommendations[0]
              console.log('推荐对象原始数据:', rec)
              matchResultData = {
                id: rec.id,
                name: rec.username || rec.name || '未知',
                gender: rec.gender === 1 ? '男' : (rec.gender === 2 ? '女' : ''),
                education: this.getEducationFromGrade(rec.grade),
                majorCategory: rec.major_category || rec.majorCategory || '',
                college: rec.academy?.name || rec.academy_name || rec.college || '',
                avatar: rec.avatar || ''
              }
            }
          }
        } catch (matchError) {
          console.error('匹配失败:', matchError)
          
          // 检查是否是"没有匹配对象"的错误
          const errorMsg = matchError.message || matchError.msg || ''
          if (errorMsg.includes('没有找到') || errorMsg.includes('暂无') || errorMsg.includes('暂时没有')) {
            // 没有匹配对象，不跳转
            hasMatch = false
          } else if (matchError.errMsg?.includes('invalid url') || matchError.errno === 600009) {
            // 如果是无效URL错误（开发阶段），允许继续跳转
            console.log('开发阶段：API未配置，允许跳转')
            hasMatch = true // 开发阶段允许跳转
          } else {
            // 其他错误，不跳转
            hasMatch = false
          }
        }
        
        uni.hideLoading()
        
        if (hasMatch) {
          // 有匹配对象，跳转到匹配结果页面
          if (matchResultData) {
            // 传递匹配数据
            uni.navigateTo({
              url: `/pages/single-match-result/index?matchData=${encodeURIComponent(JSON.stringify(matchResultData))}`,
              success: () => {
                console.log('跳转到匹配结果页面成功')
                uni.showToast({
                  title: '匹配成功！',
                  icon: 'success'
                })
              },
              fail: (err) => {
                console.error('跳转到匹配结果页面失败:', err)
                uni.showToast({
                  title: '跳转失败，请重试',
                  icon: 'none'
                })
              }
            })
          } else {
            // 开发阶段：没有匹配数据，直接跳转让匹配结果页面自己处理
            uni.navigateTo({
              url: '/pages/single-match-result/index',
              success: () => {
                console.log('跳转到匹配结果页面成功')
              },
              fail: (err) => {
                console.error('跳转失败:', err)
                uni.showToast({
                  title: '跳转失败，请重试',
                  icon: 'none'
                })
              }
            })
          }
        } else {
          // 没有匹配对象，提示用户
          uni.showToast({
            title: '暂无匹配对象，请稍后再试',
            icon: 'none',
            duration: 2000
          })
        }
        
      } catch (error) {
        uni.hideLoading()
        console.error('保存期望或匹配失败:', error)
        
        // 开发阶段：如果是无效URL错误，允许继续
        if (error.errMsg?.includes('invalid url') || error.errno === 600009) {
          console.log('开发阶段：API未配置，继续跳转')
          uni.navigateTo({
            url: '/pages/single-match-result/index',
            fail: (err) => {
              console.error('跳转失败:', err)
            }
          })
        } else {
          uni.showToast({
            title: error.message || '操作失败，请重试',
            icon: 'none'
          })
        }
      }
    },
    async handleSave() {
      this.saving = true
      
      try {
        uni.showLoading({ title: '保存中...' })
        
        // 准备保存数据，确保包含所有字段
        const saveData = {
          gender: this.expectation.gender || '',
          degree: this.expectation.degree || '',
          majorCategory: this.expectation.majorCategory || '',
          college: this.expectation.college || ''
        }
        
        const result = await saveMatchExpectation(saveData)
        console.log('保存成功:', result)
        
        uni.hideLoading()
        
        this.successType = 'save'
        this.successTitle = '保存成功！'
        this.showSuccessModal = true
        
      } catch (error) {
        uni.hideLoading()
        console.error('保存失败:', error)
        
        // 开发阶段：如果是无效URL错误，模拟成功
        if (error.errMsg?.includes('invalid url') || error.errno === 600009) {
          console.log('开发阶段：API未配置，模拟保存成功')
          this.successType = 'save'
          this.successTitle = '保存成功！'
          this.showSuccessModal = true
        } else {
          uni.showToast({
            title: error.message || '保存失败，请重试',
            icon: 'none'
          })
        }
      } finally {
        this.saving = false
      }
    },
    async handleIntelligentMatch() {
      // 检查是否填写了期望信息
      if (!this.expectation.gender || !this.expectation.majorCategory) {
        uni.showToast({
          title: '请先填写期望信息',
          icon: 'none'
        })
        return
      }
      
      try {
        uni.showLoading({ title: '保存中...' })
        
        // 先保存期望信息
        const saveData = {
          gender: this.expectation.gender || '',
          degree: this.expectation.degree || '',
          majorCategory: this.expectation.majorCategory || '',
          college: this.expectation.college || ''
        }
        
        await saveMatchExpectation(saveData)
        
        // 保存成功后，检查是否有匹配对象
        uni.showLoading({ title: '匹配中...' })
        let hasMatch = false
        try {
          const matchResult = await recommendMatches({ limit: 10 })
          console.log('推荐结果:', matchResult)
          
          // 处理返回的数据结构：matchResult 可能是 { code, msg, data } 或直接是 data
          const matchData = matchResult?.data || matchResult
          
          // 检查是否已经匹配成功
          if (matchData && matchData.isMatched === true && matchData.teammates && matchData.teammates.length > 0) {
            // 已经匹配成功
            hasMatch = true
          } else if (matchData && matchData.recommendations && matchData.recommendations.length > 0) {
            // 有推荐对象
            hasMatch = true
          }
        } catch (matchError) {
          console.error('检查匹配对象失败:', matchError)
          // 如果是无效URL错误（开发阶段），允许继续跳转
          if (matchError.errMsg?.includes('invalid url') || matchError.errno === 600009) {
            console.log('开发阶段：API未配置，允许跳转')
            hasMatch = true // 开发阶段允许跳转
          } else {
            // 其他错误，不跳转
            hasMatch = false
          }
        }
        
        uni.hideLoading()
        
        if (hasMatch) {
          // 有匹配对象，跳转到智能匹配页面
          uni.navigateTo({
            url: '/pages/single-match-result/index',
            success: () => {
              console.log('跳转到智能匹配页面成功')
            },
            fail: (err) => {
              console.error('跳转失败:', err)
              uni.showToast({
                title: '跳转失败，请重试',
                icon: 'none'
              })
            }
          })
        } else {
          // 没有匹配对象，提示用户
          uni.showToast({
            title: '暂无匹配对象，请稍后再试',
            icon: 'none',
            duration: 2000
          })
        }
      } catch (error) {
        uni.hideLoading()
        console.error('保存期望失败:', error)
        
        // 开发阶段：如果是无效URL错误，允许继续
        if (error.errMsg?.includes('invalid url') || error.errno === 600009) {
          console.log('开发阶段：API未配置，继续跳转')
          uni.navigateTo({
            url: '/pages/single-match-result/index',
            fail: (err) => {
              console.error('跳转失败:', err)
            }
          })
        } else {
          uni.showToast({
            title: error.message || '保存失败，请重试',
            icon: 'none'
          })
        }
      }
    },
    handleSuccessClose() {
      this.showSuccessModal = false
    },
    goToSignup() {
      // 优化跳转逻辑，适配游客模式
      console.log('返回报名页面')
      uni.navigateBack({
        success: () => {
          console.log('返回成功')
        },
        fail: (err) => {
          console.warn('返回失败，尝试其他方式:', err)
          // 如果无法返回，尝试重定向
          uni.reLaunch({
            url: '/pages/signup/index',
            success: () => {
              console.log('重定向到报名页面成功')
            },
            fail: (err2) => {
              console.error('跳转报名页面失败:', err2)
              uni.showToast({
                title: '请手动切换到报名页面',
                icon: 'none',
                duration: 2000
              })
            }
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
.single-match-page {
  width: 750rpx;
  min-height: 1632rpx; /* 对应816px */
  background: #F5F5F5;
  position: relative;
  margin: 0 auto;
  padding-bottom: 112rpx; /* 为底部导航栏留空间 */
}


/* 渐变背景容器 */
.gradient-container {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 246rpx;
  z-index: 1;
}

.gradient-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 246rpx;
  background: url('/static/match-single-part1/part1-banner-background.png') no-repeat center center;
  background-size: cover;
}

/* 标签切换区域 */
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
  font-size: 32rpx;
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
  width: 120rpx;
  height: 36rpx;
  background: rgba(255, 255, 255, 0.4);
  border-radius: 180rpx;
}

/* 你的期望标题区域 */
.expectation-header {
  position: absolute;
  top: 172rpx; /* 对应86px，从背景底部开始 */
  left: 0;
  right: 0;
  height: 90rpx; /* 对应45px */
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 60rpx; /* 左右padding保持30px */
  z-index: 10;
}

.expectation-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #000000;
}

.action-buttons {
  display: flex;
  gap: 20rpx;
}

.action-btn {
  width: 200rpx;
  height: 64rpx;
  background: transparent;
  border: none;
  font-size: 32rpx;
  color: #000000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.action-btn::after {
  border: none;
}

/* 主要内容区域 */
.content-section {
  position: relative;
  top: 300rpx; /* 从渐变背景+期望标题下方开始 */
  padding: 0 60rpx 200rpx;
  z-index: 2;
}

.form-group {
  margin-bottom: 66rpx;
}

.form-label-row {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
}

.form-icon {
  width: 66rpx;
  height: 52rpx;
  margin-right: 20rpx;
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

.icon-star {
  width: 40rpx;
  height: 40rpx;
}

.form-label {
  font-size: 32rpx;
  color: #000000;
  flex: 1;
}

.form-input-container {
  width: 624rpx; /* 对应312px */
  height: 64rpx; /* 对应32px */
  background: #FFFFFF;
  border-radius: 180rpx; /* 对应90px */
  margin-left: 66rpx; /* 调整对齐 */
}

.form-picker {
  width: 100%;
  height: 100%;
}

.picker-content {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  padding: 0 40rpx;
}

.picker-text {
  font-size: 24rpx;
  color: #9094A6;
}

.form-input {
  width: 100%;
  height: 100%;
  padding: 0 40rpx;
  font-size: 24rpx;
  color: #000000;
  background: transparent;
  border: none;
}

.form-input::placeholder {
  color: #9094A6;
}

/* 底部按钮区域 */
.bottom-buttons {
  position: absolute;
  top: 1000rpx; /* 调整位置，避免被导航栏遮挡 */
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 40rpx; /* 增加按钮间距 */
  z-index: 10;
  margin-bottom: 150rpx; /* 为导航栏留出空间 */
}

.start-match-btn {
  width: 358rpx; /* 对应179px */
  height: 104rpx; /* 对应52px */
  background: linear-gradient(90deg, #A100FE 0%, #FDB9E7 100%);
  border-radius: 180rpx; /* 对应90px */
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20rpx;
  position: relative;
}

.start-match-btn:disabled {
  background: #1F2635;
}

.start-match-btn::after {
  border: none;
}

.save-btn {
  width: 358rpx; /* 对应179px */
  height: 104rpx; /* 对应52px */
  background: #1F2635;
  border-radius: 180rpx; /* 对应90px */
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

.save-btn::after {
  border: none;
}

.btn-icon {
  width: 32rpx;
  height: 32rpx;
}

.btn-icon.left {
  position: absolute;
  left: 60rpx;
}

.btn-icon.right {
  position: absolute;
  right: 58rpx;
}

.btn-text {
  font-size: 32rpx;
  color: #FFFFFF;
  font-weight: 400;
}

/* 选中状态样式 - 移除不兼容的:has()选择器 */

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
