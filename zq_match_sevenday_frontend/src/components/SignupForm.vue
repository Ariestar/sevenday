<template>
  <view class="signup-form">
    <!-- 头像上传 -->
    <view class="form-item">
      <view class="form-label">头像（可选）</view>
      <view class="avatar-upload" @click="chooseAvatar">
        <image v-if="formData.avatar" :src="formData.avatar" class="avatar-preview" mode="aspectFill" />
        <view v-else class="avatar-placeholder">
          <text class="placeholder-icon">+</text>
          <text class="placeholder-text">点击上传</text>
        </view>
      </view>
    </view>

    <!-- 姓名 -->
    <view class="form-item">
      <view class="form-label">姓名 <text class="required">*</text></view>
      <input v-model="formData.name" class="form-input" placeholder="请输入姓名" />
    </view>

    <!-- 性别 -->
    <view class="form-item">
      <view class="form-label">性别 <text class="required">*</text></view>
      <radio-group class="radio-group" @change="onGenderChange">
        <label class="radio-item">
          <radio value="male" :checked="formData.gender === 'male'" />
          <text>男</text>
        </label>
        <label class="radio-item">
          <radio value="female" :checked="formData.gender === 'female'" />
          <text>女</text>
        </label>
      </radio-group>
    </view>

    <!-- 学历 -->
    <view class="form-item">
      <view class="form-label">学历 <text class="required">*</text></view>
      <radio-group class="radio-group" @change="onDegreeChange">
        <label class="radio-item">
          <radio value="undergraduate" :checked="formData.degree === 'undergraduate'" />
          <text>本科</text>
        </label>
        <label class="radio-item">
          <radio value="graduate" :checked="formData.degree === 'graduate'" />
          <text>研究生</text>
        </label>
      </radio-group>
    </view>

    <!-- 学号 -->
    <view class="form-item">
      <view class="form-label">学号 <text class="required">*</text></view>
      <input v-model="formData.studentNo" class="form-input" placeholder="请输入学号" type="number" />
    </view>

    <!-- 大类 -->
    <view class="form-item">
      <view class="form-label">大类 <text class="required">*</text></view>
      <input v-model="formData.majorCategory" class="form-input" placeholder="请输入大类" />
    </view>

    <!-- 院系 -->
    <view class="form-item">
      <view class="form-label">院系 <text class="required">*</text></view>
      <input v-model="formData.college" class="form-input" placeholder="请输入院系" />
    </view>

    <!-- QQ -->
    <view class="form-item">
      <view class="form-label">QQ <text class="required">*</text></view>
      <input v-model="formData.qq" class="form-input" placeholder="请输入QQ号" type="number" />
    </view>
  </view>
</template>

<script>
import { uploadAvatar } from '../services/upload'

export default {
  name: 'SignupForm',
  props: {
    modelValue: {
      type: Object,
      default: () => ({
        avatar: '',
        name: '',
        gender: '',
        degree: '',
        studentNo: '',
        majorCategory: '',
        college: '',
        qq: ''
      })
    }
  },
  data() {
    return {
      formData: { ...this.modelValue }
    }
  },
  watch: {
    formData: {
      handler(newVal) {
        this.$emit('update:modelValue', newVal)
      },
      deep: true
    },
    modelValue: {
      handler(newVal) {
        this.formData = { ...newVal }
      },
      deep: true
    }
  },
  methods: {
    onGenderChange(e) {
      this.formData.gender = e.detail.value
    },
    onDegreeChange(e) {
      this.formData.degree = e.detail.value
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
          } catch (err) {
            console.error('上传头像失败:', err)
          }
        }
      })
    }
  }
}
</script>

<style scoped>
.signup-form {
  padding: 30rpx;
}

.form-item {
  margin-bottom: 40rpx;
}

.form-label {
  font-size: 32rpx;
  color: #333;
  margin-bottom: 20rpx;
  display: flex;
  align-items: center;
}

.required {
  color: #ff4d4f;
  margin-left: 6rpx;
}

.avatar-upload {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 160rpx;
  height: 160rpx;
  border-radius: 16rpx;
  overflow: hidden;
  background-color: #f5f5f5;
}

.avatar-preview {
  width: 100%;
  height: 100%;
}

.avatar-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.placeholder-icon {
  font-size: 48rpx;
  color: #ccc;
}

.placeholder-text {
  font-size: 24rpx;
  color: #999;
  margin-top: 8rpx;
}

.form-input {
  width: 100%;
  height: 88rpx;
  padding: 0 24rpx;
  font-size: 32rpx;
  background-color: #f5f5f5;
  border-radius: 8rpx;
}

.radio-group {
  display: flex;
  gap: 40rpx;
}

.radio-item {
  display: flex;
  align-items: center;
  font-size: 32rpx;
  color: #333;
}

.radio-item text {
  margin-left: 12rpx;
}
</style>

