<template>
  <view class="signup-page">

    <!-- 顶部紫色渐变遮罩组 -->
    <view class="mask-group">
      <view class="gradient-mask">
        <image src="/static/signup/background.png" class="background-image" mode="aspectFill" />
      </view>
    </view>

    <!-- 标签切换 -->
    <view class="tab-section">
      <view class="tab-group">
        <view class="tab-item active">
          <text class="tab-text active">报名</text>
        </view>
        <view class="tab-item" @click="goToMatch">
          <text class="tab-text">匹配</text>
        </view>
      </view>
      <view class="tab-indicator"></view>
    </view>

    <!-- 头像区域 -->
    <view class="avatar-section">
      <view class="avatar-container" @click="chooseAvatar">
        <image v-if="formData.avatar" :src="formData.avatar" class="avatar-image" mode="aspectFill" />
        <view v-else class="avatar-placeholder">
          <text class="avatar-plus">+</text>
        </view>
      </view>
    </view>

    <!-- 白色内容卡片 -->
    <view class="content-card">
      <!-- 个人信息标题和保存按钮 -->
      <view class="info-header">
        <view class="info-title-row">
          <image src="/static/signup/personal-info.png" class="info-icon" mode="aspectFit" />
          <text class="info-title">个人信息</text>
        </view>
        <button class="save-btn" @click="handleSave">保存</button>
      </view>
      
      <!-- 分割线 -->
      <view class="divider-line"></view>

      <!-- 表单字段 -->
      <view class="form-container">
        <!-- 姓名 -->
        <view class="form-row">
          <text class="form-label">姓名</text>
          <input v-model="formData.name" class="form-input-field" placeholder="请输入" />
        </view>

        <!-- 性别 -->
        <view class="form-row">
          <text class="form-label">性别</text>
          <picker mode="selector" :range="genderOptions" range-key="label" @change="onGenderChange">
            <view class="form-input-field">
              <text :class="{'placeholder': !formData.gender}">
                {{ getGenderLabel(formData.gender) || '请选择' }}
              </text>
            </view>
          </picker>
        </view>

        <!-- 我的身份 -->
        <view class="form-row">
          <text class="form-label">我的身份</text>
          <picker mode="selector" :range="degreeOptions" range-key="label" @change="onDegreeChange">
            <view class="form-input-field">
              <text :class="{'placeholder': !formData.degree}">
                {{ getDegreeLabel(formData.degree) || '请选择' }}
              </text>
            </view>
          </picker>
        </view>

        <!-- 大类 -->
        <view class="form-row">
          <text class="form-label">大类</text>
          <picker mode="selector" :range="majorOptions" range-key="label" @change="onMajorChange">
            <view class="form-input-field">
              <text :class="{'placeholder': !formData.majorCategory}">
                {{ getMajorLabel(formData.majorCategory) || '请选择' }}
              </text>
            </view>
          </picker>
        </view>

        <!-- 院系 -->
        <view class="form-row">
          <text class="form-label">院系</text>
          <input v-model="formData.college" class="form-input-field" placeholder="请输入" />
        </view>

        <!-- QQ号 -->
        <view class="form-row">
          <text class="form-label">QQ号</text>
          <input v-model="formData.qq" class="form-input-field" placeholder="请输入" type="number" />
        </view>

        <!-- 个人简介 -->
        <view class="form-row">
          <text class="form-label">个人简介</text>
          <input v-model="formData.bio" class="form-input-field" placeholder="一句话概括一下自己吧~" />
        </view>

        <!-- 学号（隐藏显示，但需要填写） -->
        <view class="form-row" style="display: none;">
          <input v-model="formData.studentNo" type="number" />
        </view>
      </view>

      <!-- 立即报名按钮 -->
      <view class="submit-section">
        <button 
          class="submit-btn-main" 
          :disabled="!canSubmit || submitting"
          :loading="submitting"
          @click="handleSubmit"
        >
          {{ submitting ? '提交中...' : '立即报名' }}
        </button>
      </view>
    </view>
    
    <!-- 自定义 TabBar -->
    <CustomTabBar :current="0" />
    
    <!-- 报名类型选择弹窗 -->
    <SignupTypePicker
      :visible="showSignupTypePicker"
      @update:visible="showSignupTypePicker = $event"
      @select="handleSignupTypeSelect"
    />
    
    <!-- 成功提示弹窗 -->
    <SuccessModal
      :visible="showSuccessModal"
      @update:visible="showSuccessModal = $event"
      @close="handleSuccessClose"
      :type="successType"
      :title="successTitle"
    />
  </view>
</template>

<script>
import { GENDER_OPTIONS, DEGREE_OPTIONS, MAJOR_CATEGORY_OPTIONS } from '../../utils/constants'
import { submitSignup, getSignupDetail } from '../../services/signup'
import { uploadAvatar } from '../../services/upload'
import CustomTabBar from '../../components/CustomTabBar.vue'
import SignupTypePicker from '../../components/SignupTypePicker.vue'
import SuccessModal from '../../components/SuccessModal.vue'

export default {
  components: {
    CustomTabBar,
    SignupTypePicker,
    SuccessModal
  },
  data() {
    return {
      formData: {
        avatar: '',
        name: '',
        gender: '',
        degree: '',
        studentNo: '',
        majorCategory: '',
        college: '',
        qq: '',
        bio: ''
      },
      genderOptions: GENDER_OPTIONS.filter(opt => opt.value !== 'unlimited'),
      degreeOptions: DEGREE_OPTIONS.filter(opt => opt.value !== 'unlimited'),
      majorOptions: MAJOR_CATEGORY_OPTIONS,
      submitting: false,
      isEdit: false,
      showSignupTypePicker: false,
      showSuccessModal: false,
      successType: 'signup',
      successTitle: '',
      pendingSignupType: null // 保存用户选择的报名类型
    }
  },
  computed: {
    canSubmit() {
      const { name, gender, degree, majorCategory, college, qq } = this.formData
      return name && gender && degree && majorCategory && college && qq
    }
  },
  onLoad() {
    this.loadSignupDetail()
  },
  onShow() {
    // 触发TabBar更新，确保选中状态正确
    uni.$emit('tabbar-update')
  },
  methods: {
    async loadSignupDetail() {
      try {
        const detail = await getSignupDetail()
        if (detail) {
          this.formData = { ...this.formData, ...detail }
          this.isEdit = true
        }
      } catch (err) {
        console.log('首次报名')
      }
    },
    onGenderChange(e) {
      const index = e.detail.value
      this.formData.gender = this.genderOptions[index].value
    },
    onDegreeChange(e) {
      const index = e.detail.value
      this.formData.degree = this.degreeOptions[index].value
    },
    onMajorChange(e) {
      const index = e.detail.value
      this.formData.majorCategory = this.majorOptions[index].value
    },
    getGenderLabel(value) {
      const option = this.genderOptions.find(opt => opt.value === value)
      return option ? option.label : ''
    },
    getDegreeLabel(value) {
      const option = this.degreeOptions.find(opt => opt.value === value)
      return option ? option.label : ''
    },
    getMajorLabel(value) {
      const option = this.majorOptions.find(opt => opt.value === value)
      return option ? option.label : ''
    },
    chooseAvatar() {
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera'],
        success: async (res) => {
          const tempFilePath = res.tempFilePaths[0]
          try {
            const avatarUrl = await uploadAvatar(tempFilePath)
            this.formData.avatar = avatarUrl
            uni.showToast({
              title: '头像上传成功',
              icon: 'success'
            })
          } catch (err) {
            console.error('上传头像失败:', err)
          }
        }
      })
    },
    async handleSave() {
      if (!this.canSubmit) {
        uni.showToast({
          title: '请填写完整信息',
          icon: 'none'
        })
        return
      }

      this.submitting = true
      let saveSuccess = false
      try {
        await submitSignup(this.formData)
        saveSuccess = true
        this.isEdit = true
      } catch (err) {
        console.error('保存失败:', err)
        // 开发阶段：如果是URL无效错误，允许模拟成功
        const errorMsg = err?.errMsg || err?.message || String(err)
        if (errorMsg.includes('invalid url') || errorMsg.includes('600009')) {
          saveSuccess = true
          console.log('开发阶段：API未配置，模拟保存成功')
          this.isEdit = true
        }
      } finally {
        this.submitting = false
      }

      // 如果保存成功，显示成功弹窗
      if (saveSuccess) {
        this.successType = 'save'
        this.successTitle = '保存成功！'
        this.showSuccessModal = true
      }
    },
    async handleSubmit() {
      if (!this.canSubmit) {
        uni.showToast({
          title: '请填写完整信息',
          icon: 'none'
        })
        return
      }

      if (!this.formData.name.trim()) {
        uni.showToast({ title: '请输入姓名', icon: 'none' })
        return
      }

      if (!this.formData.qq.trim()) {
        uni.showToast({ title: '请输入QQ号', icon: 'none' })
        return
      }

      // 显示报名类型选择弹窗
      this.showSignupTypePicker = true
    },
    async handleSignupTypeSelect(type) {
      this.pendingSignupType = type
      this.showSignupTypePicker = false
      
      // 提交报名数据
      this.submitting = true
      let submitSuccess = false
      try {
        const submitData = {
          ...this.formData,
          signupType: type // 添加报名类型
        }
        await submitSignup(submitData)
        submitSuccess = true
      } catch (err) {
        console.error('提交报名失败:', err)
        // 开发阶段：如果是URL无效错误，允许继续（模拟成功）
        const errorMsg = err?.errMsg || err?.message || String(err)
        if (errorMsg.includes('invalid url') || errorMsg.includes('600009')) {
          submitSuccess = true
          console.log('开发阶段：API未配置，模拟提交成功')
        } else {
          // 其他错误才真正失败
          this.submitting = false
          return
        }
      } finally {
        this.submitting = false
      }

      // 如果提交成功（或开发阶段模拟成功），显示成功弹窗
      if (submitSuccess) {
        this.successType = 'signup'
        this.successTitle = '报名成功！'
        this.showSuccessModal = true
      }
    },
    handleSuccessClose() {
      this.showSuccessModal = false
      
      // 简化跳转逻辑，根据报名类型跳转到不同页面
      const targetUrl = this.pendingSignupType === 'single' 
        ? '/pages/single-match/index'    // 单人匹配页面
        : '/pages/multiple-match/index'  // 多人匹配页面（tabBar页面）
      
      console.log(`报名类型: ${this.pendingSignupType}, 跳转到: ${targetUrl}`)
      
      setTimeout(() => {
        if (this.pendingSignupType === 'single') {
          // 单人匹配页面 - 使用 reLaunch 重启应用到目标页面
          uni.reLaunch({
            url: targetUrl,
            success: () => {
              console.log('跳转到单人匹配页面成功')
            },
            fail: (err) => {
              console.warn('跳转失败:', err)
              // 开发者工具中可能会失败，这是正常的
              console.log('如果在开发工具中跳转失败，请手动切换到单人匹配页面')
            }
          })
        } else {
          // 组队匹配页面 - TabBar页面，使用 switchTab
          uni.switchTab({
            url: targetUrl,
            success: () => {
              console.log('跳转到组队匹配页面成功')
            },
            fail: (err) => {
              console.warn('switchTab失败，尝试reLaunch:', err)
              uni.reLaunch({
                url: targetUrl,
                success: () => {
                  console.log('reLaunch到组队匹配页面成功')
                },
                fail: (err2) => {
                  console.warn('跳转失败:', err2)
                  console.log('如果在开发工具中跳转失败，请手动切换到匹配页面')
                }
              })
            }
          })
        }
      }, 300)
    },
    goToMatch() {
      uni.switchTab({
        url: '/pages/multiple-match/index'
      })
    }
  }
}
</script>

<style scoped>
.signup-page {
  position: relative;
  width: 750rpx;
  height: 1624rpx;
  background: #FFFFFF;
  padding-bottom: 120rpx;
}

/* 状态栏 */
.status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14rpx 38rpx;
  height: 44rpx;
}

.status-time {
  font-size: 30rpx;
  font-weight: 600;
  color: #000;
}

.status-icons {
  display: flex;
  gap: 12rpx;
}

.status-icon {
  font-size: 28rpx;
}

/* 顶部紫色渐变遮罩组 */
.mask-group {
  position: absolute;
  left: 0rpx;
  top: 0rpx;
  width: 750rpx;
  height: 442rpx;
}

.gradient-mask {
  position: absolute;
  width: 750rpx;
  height: 442rpx;
  left: 0rpx;
  top: 0rpx;
  background: linear-gradient(180deg, #AA00FF 0%, #FFBDE7 100%);
}

.background-image {
  position: absolute;
  width: 906rpx;
  height: 1610rpx;
  left: -130rpx;
  top: -538rpx;
}

/* 标签切换区域 */
.tab-section {
  position: absolute;
  left: 138rpx;
  top: 72rpx;
  z-index: 3;
}

.tab-group {
  display: flex;
  gap: 324rpx;
}

.tab-item {
  position: relative;
}

.tab-text {
  font-size: 32rpx;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 400;
}

.tab-text.active {
  color: #FFFFFF;
  font-weight: 700;
}

.tab-indicator {
  position: absolute;
  width: 120rpx;
  height: 36rpx;
  left: -62rpx;
  top: 30rpx;
  background: #FFFFFF;
  opacity: 0.4;
  border-radius: 90rpx;
}

/* 头像区域 */
.avatar-section {
  position: absolute;
  left: 50%;
  top: 190rpx;
  transform: translateX(-50%);
  z-index: 3;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.avatar-container {
  width: 236rpx;
  height: 236rpx;
  background: #E3E4E4;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.avatar-image {
  width: 100%;
  height: 100%;
}

.avatar-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.avatar-plus {
  font-size: 96rpx;
  color: #9094A6;
  font-weight: 200;
}


/* 白色内容卡片 */
.content-card {
  position: absolute;
  width: 750rpx;
  height: 1128rpx;
  left: 0rpx;
  top: 376rpx;
  background: #FFFFFF;
  border-radius: 60rpx 60rpx 0rpx 0rpx;
  z-index: 2;
}

/* 分割线 */
.divider-line {
  position: absolute;
  width: 622rpx;
  height: 2rpx;
  left: 64rpx;
  top: 260rpx;
  background: #F7E7FF;
  transform: rotate(-0.19deg);
}

/* 个人信息标题栏 */
.info-header {
  position: absolute;
  left: 64rpx;
  top: 180rpx;
  display: flex;
  align-items: center;
  width: 622rpx;
}

.info-title-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.info-icon {
  width: 66rpx;
  height: 52rpx;
}

.info-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #1F2635;
}

.save-btn {
  position: absolute;
  right: 0rpx;
  width: 130rpx;
  height: 64rpx;
  background: #1F2635;
  border-radius: 90rpx;
  color: #FFFFFF;
  font-size: 28rpx;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 表单容器 - 精确按Figma设计 */
.form-container {
  position: absolute;
  left: calc(50% - 624rpx/2 + 2rpx);
  top: 290rpx;
  width: 624rpx;
  height: 660rpx;
}

/* 统一所有字段的基础样式 */
.form-row {
  position: absolute;
  width: 558rpx;
  height: 64rpx;
  left: 64rpx;
}

.form-label {
  position: absolute;
  right: calc(100% + 20rpx);
  top: 22rpx;
  font-size: 32rpx;
  color: #1F2635;
  text-align: right;
  z-index: 1;
  white-space: nowrap;
}

.form-input-field {
  position: absolute;
  left: 0rpx;
  top: 0rpx;
  width: 474rpx;
  height: 64rpx;
  background: #F7E7FF;
  border-radius: 180rpx;
  padding: 0 32rpx;
  display: flex;
  align-items: center;
  font-size: 24rpx;
  color: #1F2635;
  border: none;
}

/* 姓名字段 */
.form-row:nth-child(1) {
  top: 16rpx;
}

.form-row:nth-child(1) .form-label {
  width: 110rpx;
  color: #1F2635;
}

/* 性别字段 */
.form-row:nth-child(2) {
  top: 114rpx;
}

.form-row:nth-child(2) .form-label {
  width: 110rpx;
  color: #1F2635;
}

/* 我的身份字段 */
.form-row:nth-child(3) {
  top: 214rpx;
}

.form-row:nth-child(3) .form-label {
  width: 144rpx;
  color: #000000;
}

/* 大类字段 */
.form-row:nth-child(4) {
  top: 314rpx;
}

.form-row:nth-child(4) .form-label {
  width: 64rpx;
  color: #000000;
}

/* 院系字段 */
.form-row:nth-child(5) {
  top: 414rpx;
}

.form-row:nth-child(5) .form-label {
  width: 110rpx;
  color: #1F2635;
}

/* QQ号字段 */
.form-row:nth-child(6) {
  top: 510rpx;
}

.form-row:nth-child(6) .form-label {
  width: 82rpx;
  color: #1F2635;
}

/* 个人简介字段 */
.form-row:nth-child(7) {
  top: 610rpx;
}

.form-row:nth-child(7) .form-label {
  width: 128rpx;
  color: #1F2635;
}

/* 通用输入框样式 */
.form-input-field input {
  width: 100%;
  height: 100%;
  border: none;
  background: transparent;
  font-size: 24rpx;
  color: #1F2635;
}

.form-input-field .placeholder,
.form-input-field::placeholder,
.form-input-field input::placeholder {
  color: #9094A6;
  font-size: 24rpx;
}

/* picker 内部文本 */
.form-input-field text {
  font-size: 24rpx;
  color: #1F2635;
}

.form-input-field text.placeholder {
  color: #9094A6;
}

/* 提交按钮区域 */
.submit-section {
  position: absolute;
  left: 50%;
  top: calc(290rpx + 610rpx + 64rpx);
  margin-top: 8vh;
  transform: translateX(-50%);
}

.submit-btn-main {
  width: 358rpx;
  height: 104rpx;
  background: #1F2635;
  border-radius: 180rpx;
  color: #FFFFFF;
  font-size: 32rpx;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

.submit-btn-main[disabled] {
  opacity: 0.5;
}

.submit-btn-main[loading] {
  opacity: 0.8;
}


/* 按钮微调 */
.submit-section .submit-btn-main {
  position: relative;
  left: -6rpx;
}
</style>

