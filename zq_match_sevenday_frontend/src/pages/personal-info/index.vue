<template>
  <view class="personal-info-page">
    <!-- 顶部导航 -->
    <view class="page-header">
      <view class="nav-bar">
        <view class="nav-left" @click="goBack">
          <text class="back-arrow">‹</text>
        </view>
        <text class="page-title">个人信息</text>
        <view class="nav-right"></view>
      </view>
    </view>

    <!-- 个人信息内容 -->
    <view class="content-area">
      <!-- 头像区域 -->
      <view class="avatar-section">
        <view class="avatar-container" @click="chooseAvatar">
          <image 
            v-if="userInfo.avatar && !userInfo.avatar.includes('default.jpg')" 
            :src="userInfo.avatar" 
            class="user-avatar" 
            mode="aspectFill"
          />
          <view v-else class="avatar-placeholder">
            <image src="/static/square/user-icon.png" class="default-avatar" mode="aspectFill" />
          </view>
        </view>
      </view>

      <!-- 信息表单 -->
      <view class="form-container">
        <!-- 姓名 -->
        <view class="form-row">
          <input 
            v-model="userInfo.name" 
            class="form-input" 
            placeholder="姓名" 
          />
        </view>

        <!-- 性别 -->
        <view class="form-row">
          <picker 
            mode="selector" 
            :value="genderIndex" 
            :range="genderOptions" 
            range-key="label" 
            @change="onGenderChange"
            class="form-picker"
          >
            <view class="picker-content">
              <text class="picker-text">{{ userInfo.gender ? genderOptions.find(g => g.value === userInfo.gender)?.label : '性别' }}</text>
            </view>
          </picker>
        </view>

        <!-- 学院 -->
        <view class="form-row">
          <input 
            v-model="userInfo.college" 
            class="form-input" 
            placeholder="学院" 
          />
        </view>

        <!-- 联系方式 -->
        <view class="form-row">
          <input 
            v-model="userInfo.qq" 
            class="form-input" 
            placeholder="联系方式" 
          />
        </view>
      </view>

      <!-- 保存按钮 -->
      <view class="save-section">
        <button class="save-button" @click="handleSave">保存</button>
      </view>
    </view>

    <!-- 底部导航栏 -->
    <CustomTabBar :current="3" />
  </view>
</template>

<script>
import { getUserInfo, updateUserInfo } from '../../services/auth'
import { uploadAvatar } from '../../services/upload'
import authUtils from '../../utils/auth'
import CustomTabBar from '../../components/CustomTabBar.vue'

export default {
  components: {
    CustomTabBar
  },
  data() {
    return {
      userInfo: {
        name: '',
        gender: '',
        college: '',
        qq: '',
        avatar: ''
      },
      genderOptions: [
        { value: 'male', label: '男' },
        { value: 'female', label: '女' }
      ],
      saving: false
    }
  },
  computed: {
    genderIndex() {
      return this.genderOptions.findIndex(option => option.value === this.userInfo.gender)
    }
  },
  onLoad() {
    this.loadUserInfo()
  },
  methods: {
    async loadUserInfo() {
      // 优先从服务器获取用户信息
      try {
        const info = await getUserInfo()
        if (info) {
          // 转换性别格式（如果后端返回的是中文）
          let gender = info.gender
          if (gender === '男' || gender === 'MALE' || gender === 1) {
            gender = 'male'
          } else if (gender === '女' || gender === 'FEMALE' || gender === 2) {
            gender = 'female'
          }
          
          this.userInfo = {
            name: info.name || '',
            gender: gender || '',
            college: info.college || info.department || '',
            qq: info.qq || '',
            avatar: info.avatar || ''
          }
          // 保存到本地存储
          authUtils.setUserInfo(this.userInfo)
        }
      } catch (err) {
        console.error('加载用户信息失败:', err)
        // 如果服务器获取失败，从本地存储获取
        const localUserInfo = authUtils.getUserInfo()
        if (localUserInfo) {
          this.userInfo = { ...this.userInfo, ...localUserInfo }
        }
      }
    },

    onGenderChange(e) {
      const selectedOption = this.genderOptions[e.detail.value]
      this.userInfo.gender = selectedOption.value
    },

    async chooseAvatar() {
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera'],
        success: async (res) => {
          const tempFilePath = res.tempFilePaths[0]
          uni.showLoading({ title: '上传中...' })
          try {
            const uploadRes = await uploadAvatar(tempFilePath)
            this.userInfo.avatar = uploadRes.url || uploadRes
            // 更新服务器上的用户信息
            try {
              await updateUserInfo({ avatar: this.userInfo.avatar })
            } catch (err) {
              console.warn('更新头像到服务器失败，但已保存到本地:', err)
            }
            // 保存到本地存储
            authUtils.setUserInfo(this.userInfo)
            uni.hideLoading()
            uni.showToast({ title: '头像上传成功', icon: 'success' })
          } catch (error) {
            uni.hideLoading()
            uni.showToast({ title: '头像上传失败', icon: 'none' })
            console.error('上传头像失败', error)
          }
        }
      })
    },

    async handleSave() {
      if (this.saving) {
        return
      }

      // 验证必填字段
      if (!this.userInfo.name) {
        uni.showToast({
          title: '请输入姓名',
          icon: 'none'
        })
        return
      }

      this.saving = true
      uni.showLoading({ title: '保存中...' })

      try {
        // 准备要保存的数据
        const updateData = {
          name: this.userInfo.name,
          gender: this.userInfo.gender,
          college: this.userInfo.college,
          qq: this.userInfo.qq
        }

        // 调用更新接口
        const updatedInfo = await updateUserInfo(updateData)
        
        // 更新本地用户信息
        this.userInfo = { ...this.userInfo, ...updatedInfo }
        authUtils.setUserInfo(this.userInfo)

        uni.hideLoading()
        uni.showToast({
          title: '保存成功',
          icon: 'success'
        })

        // 延迟返回上一页
        setTimeout(() => {
          this.goBack()
        }, 1500)
      } catch (error) {
        uni.hideLoading()
        console.error('保存用户信息失败:', error)
        uni.showToast({
          title: error.message || '保存失败，请重试',
          icon: 'none'
        })
      } finally {
        this.saving = false
      }
    },

    goBack() {
      uni.navigateBack({
        fail: () => {
          uni.reLaunch({ url: '/pages/mine/index' })
        }
      })
    }
  }
}
</script>

<style scoped>
.personal-info-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #F7E8FE 0%, #FFFEFF 100%);
  padding-bottom: 112rpx; /* 为TabBar留出空间 */
}

/* 顶部导航 */
.page-header {
  background: linear-gradient(89.97deg, #A100FE 0.03%, #FDB9E7 99.97%);
  padding: 88rpx 0 40rpx 0;
}

.nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32rpx;
  height: 80rpx;
}

.nav-left {
  width: 80rpx;
  height: 80rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-arrow {
  font-size: 48rpx;
  color: #FFFFFF;
  font-weight: 300;
}

.page-title {
  font-size: 32rpx;
  color: #FFFFFF;
  font-weight: 500;
}

.nav-right {
  width: 80rpx;
}

/* 内容区域 */
.content-area {
  padding: 60rpx 40rpx;
}

/* 头像区域 */
.avatar-section {
  display: flex;
  justify-content: center;
  margin-bottom: 80rpx;
}

.avatar-container {
  width: 200rpx;
  height: 200rpx;
  border-radius: 50%;
  overflow: hidden;
  background: #F0F0F0;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.user-avatar {
  width: 100%;
  height: 100%;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #F5F5F5;
}

.default-avatar {
  width: 80%;
  height: 80%;
  opacity: 0.6;
}

/* 表单容器 */
.form-container {
  display: flex;
  flex-direction: column;
  gap: 32rpx;
}

.form-row {
  background: #FFFFFF;
  border-radius: 100rpx;
  height: 100rpx;
  display: flex;
  align-items: center;
  padding: 0 40rpx;
  border: 2rpx solid #E0A7FF;
}

.form-input {
  flex: 1;
  font-size: 32rpx;
  color: #333333;
  height: 100%;
  line-height: 100rpx;
}

.form-picker {
  flex: 1;
  height: 100%;
}

.picker-content {
  height: 100%;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

.picker-text {
  font-size: 32rpx;
  color: #333333;
  width: 100%;
  text-align: left;
  line-height: 100rpx;
}

/* 保存按钮区域 */
.save-section {
  margin-top: 80rpx;
  display: flex;
  justify-content: center;
}

.save-button {
  width: 400rpx;
  height: 88rpx;
  background: linear-gradient(90deg, #A100FE 0%, #FDB9E7 100%);
  color: #FFFFFF;
  font-size: 32rpx;
  border-radius: 44rpx;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 88rpx;
  padding: 0;
  margin: 0;
}

.save-button::after {
  border: none;
}

.save-button[disabled] {
  opacity: 0.6;
}
</style>