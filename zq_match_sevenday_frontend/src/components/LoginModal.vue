<template>
  <view v-if="visible" class="login-modal-overlay" @tap="handleOverlayTap">
    <view class="login-modal-content" @tap.stop>
      <!-- 登录卡片 -->
      <view class="login-card">
        <!-- 王冠插图背景 - 占满整个modal -->
        <view class="crown-background">
          <image 
            src="/static/illustrations/login-card.png" 
            class="crown-image" 
            mode="aspectFit"
          />
          <!-- 透明度遮罩层 -->
          <view class="background-overlay"></view>
        </view>
        
        <!-- 表单内容 -->
        <view class="form-content">
          <!-- 邮箱输入 -->
          <view class="form-row">
            <text class="form-label">邮箱</text>
            <input 
              v-model="formData.email"
              class="form-input"
              type="text"
              placeholder="请输入"
              placeholder-class="input-placeholder"
            />
          </view>
          
          <!-- 验证码输入 -->
          <view class="form-row">
            <text class="form-label">验证码</text>
            <view class="verify-code-row">
              <input 
                v-model="formData.verifyCode"
                class="form-input verify-input"
                type="text"
                maxlength="6"
                placeholder="请输入6位验证码"
                placeholder-class="input-placeholder"
                @input="handleVerifyCodeInput"
              />
              <button 
                class="get-code-btn"
                :class="{ disabled: codeCountdown > 0 }"
                :disabled="codeCountdown > 0 || !formData.email"
                @tap="handleGetCode"
              >
                {{ codeCountdown > 0 ? `${codeCountdown}s` : '获取验证码' }}
              </button>
            </view>
          </view>
          
          <!-- 隐私政策 -->
          <view class="privacy-row">
            <view class="checkbox-wrapper" @tap="togglePrivacyAgreement">
              <view class="checkbox" :class="{ checked: privacyAgreed }">
                <text v-if="privacyAgreed" class="check-icon">✓</text>
              </view>
            </view>
            <text class="privacy-text">
              我已阅读并同意<text class="privacy-link" @tap="showPrivacyPolicy">《隐私政策》</text>
            </text>
          </view>
          
          <!-- 登录按钮 -->
          <button 
            class="login-btn"
            :class="{ disabled: !canLogin }"
            :disabled="!canLogin"
            @tap="handleLogin"
          >
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { sendVerifyCode, verifyEmail } from '../services/auth'
import authUtils from '../utils/auth'

export default {
  name: 'LoginModal',
  props: {
    visible: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      formData: {
        email: '',
        verifyCode: ''
      },
      privacyAgreed: false,
      codeCountdown: 0,
      loading: false
    }
  },
  computed: {
    canLogin() {
      return this.formData.email && 
             this.formData.verifyCode && 
             this.privacyAgreed &&
             !this.loading
    }
  },
  methods: {
    handleOverlayTap() {
      this.$emit('close')
    },
    
    togglePrivacyAgreement() {
      this.privacyAgreed = !this.privacyAgreed
    },
    
    showPrivacyPolicy() {
      // 跳转到隐私政策页面
      uni.navigateTo({
        url: '/pages/policy/privacy'
      })
    },
    
    async handleGetCode() {
      if (this.codeCountdown > 0 || !this.formData.email) {
        return
      }
      
      try {
        await sendVerifyCode(this.formData.email)
        uni.showToast({
          title: '验证码已发送',
          icon: 'success'
        })
        
        // 开始倒计时
        this.startCountdown()
      } catch (err) {
        console.error('发送验证码失败:', err)
      }
    },
    
    startCountdown() {
      this.codeCountdown = 60
      const timer = setInterval(() => {
        this.codeCountdown--
        if (this.codeCountdown <= 0) {
          clearInterval(timer)
        }
      }, 1000)
    },
    
    handleVerifyCodeInput(e) {
      // 只允许输入数字，限制6位
      let value = e.detail.value.replace(/\D/g, '').slice(0, 6)
      this.formData.verifyCode = value
    },
    
    async handleLogin() {
      if (!this.canLogin) {
        return
      }
      
      // 验证验证码格式
      if (!this.formData.verifyCode || this.formData.verifyCode.length !== 6) {
        uni.showToast({
          title: '请输入6位验证码',
          icon: 'none',
          duration: 2000
        })
        return
      }
      
      // 验证验证码是否为数字
      if (!/^\d{6}$/.test(this.formData.verifyCode)) {
        uni.showToast({
          title: '验证码必须为6位数字',
          icon: 'none',
          duration: 2000
        })
        return
      }
      
      this.loading = true
      try {
        // 确保验证码是字符串类型且长度为6
        const code = String(this.formData.verifyCode).trim()
        if (code.length !== 6) {
          uni.showToast({
            title: '请输入6位验证码',
            icon: 'none',
            duration: 2000
          })
          this.loading = false
          return
        }
        
        console.log('发送验证请求:', {
          email: this.formData.email,
          code: code,
          codeType: typeof code,
          codeLength: code.length
        })
        const result = await verifyEmail(this.formData.email, code)
        
        // 使用认证工具保存认证信息
        // result 已经是 data 字段的内容（request.js 已经提取）
        authUtils.login(result.token, result.userInfo)
        
        uni.showToast({
          title: '登录成功',
          icon: 'success'
        })
        
        // 通知父组件登录成功
        this.$emit('login-success', result.userInfo)
        this.$emit('close')
        
        // 重置表单
        this.resetForm()
      } catch (err) {
        console.error('登录失败:', err)
      } finally {
        this.loading = false
      }
    },
    
    resetForm() {
      this.formData = {
        email: '',
        verifyCode: ''
      }
      this.privacyAgreed = false
      this.codeCountdown = 0
      this.loading = false
    }
  },
  watch: {
    visible(newVal) {
      if (!newVal) {
        // 弹窗关闭时重置表单
        this.resetForm()
      }
    }
  }
}
</script>

<style scoped>
.login-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.login-modal-content {
  width: 600rpx;
  height: 840rpx; /* 增加高度，对应420px */
  overflow: hidden;
}

.login-card {
  background-color: #ffffff;
  border-radius: 18rpx;
  overflow: hidden;
  position: relative;
  height: 100%; /* 占满容器高度 */
}

.crown-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  overflow: hidden;
}

.crown-image {
  width: 102%; /* 85% of 120% */
  height: 102%; /* 85% of 120% */
  object-fit: cover;
  position: absolute;
  top: -80rpx; /* 往上移动 */
  left: -10rpx; /* 居中对齐 */
  opacity: 0.7; /* 70%透明度 */
}

.background-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.3) 0%, rgba(255, 255, 255, 0.6) 19.71%, rgba(255, 255, 255, 0.87) 41.83%, rgba(255, 255, 255, 1) 100%);
  z-index: 2; /* 在背景图片之上，但在表单内容之下 */
}

.form-content {
  position: absolute;
  bottom: 10%; /* 向上移动10% */
  left: 0;
  right: 0;
  height: 38%; /* 稍微增加高度以容纳所有内容 */
  padding: 15rpx 32rpx 15rpx; /* 减少padding以更好利用空间 */
  z-index: 3; /* 确保在遮罩层之上 */
  display: flex;
  flex-direction: column;
  justify-content: flex-start; /* 从顶部开始排列 */
  overflow-y: auto; /* 如果内容过多可以滚动 */
}

.form-row {
  display: flex;
  align-items: center;
  margin-bottom: 16rpx; /* 进一步减少间距 */
  gap: 16rpx;
}

.form-label {
  font-size: 32rpx;
  color: #1f2635;
  width: 120rpx; /* 固定标签宽度 */
  flex-shrink: 0;
  text-align: left;
}

.form-input {
  flex: 1;
  height: 64rpx;
  background-color: #ffffff;
  border: 2rpx solid #1f2635;
  border-radius: 90rpx;
  padding: 0 30rpx;
  font-size: 28rpx;
  color: #1f2635;
  box-sizing: border-box;
  min-width: 0;
}

.input-placeholder {
  color: #9094a6;
}

.verify-code-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
  flex: 1;
  min-width: 0;
}

.verify-input {
  flex: 1;
  min-width: 0;
}

.get-code-btn {
  width: 180rpx; /* 减小宽度以适应新布局 */
  height: 64rpx;
  background-color: #1f2635;
  color: #ffffff;
  font-size: 26rpx; /* 稍微减小字体 */
  border-radius: 90rpx;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  white-space: nowrap;
}

.get-code-btn.disabled {
  background-color: #ccc;
  color: #666;
}

.privacy-row {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx; /* 减少间距 */
  padding: 0 10rpx;
}

.checkbox-wrapper {
  margin-right: 16rpx;
}

.checkbox {
  width: 28rpx;
  height: 28rpx;
  border: 2rpx solid #ccc;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #ffffff;
}

.checkbox.checked {
  border-color: #667eea;
  background-color: #667eea;
}

.check-icon {
  color: #ffffff;
  font-size: 18rpx;
  font-weight: bold;
}

.privacy-text {
  font-size: 28rpx;
  color: #b3b3b3;
  line-height: 1.4;
}

.privacy-link {
  color: #00bfff;
  text-decoration: underline;
}

.login-btn {
  width: 260rpx; /* 稍微减小宽度 */
  height: 80rpx; /* 稍微减小高度 */
  background-color: #1f2635;
  color: #ffffff;
  font-size: 30rpx; /* 稍微减小字体 */
  border-radius: 90rpx;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

.login-btn.disabled {
  background-color: #ccc;
  color: #666;
}
</style>
