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
        <view class="avatar-container" @click="!hasTeam && chooseAvatar()">
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
            :disabled="hasTeam"
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
            :disabled="hasTeam"
            @change="onGenderChange"
            class="form-picker"
          >
            <view class="picker-content">
              <text class="picker-text">{{ userInfo.gender ? genderOptions.find(g => g.value === userInfo.gender)?.label : '性别' }}</text>
            </view>
          </picker>
        </view>

        <!-- 我的身份 -->
        <view class="form-row">
          <picker 
            mode="selector" 
            :value="degreeIndex" 
            :range="degreeOptions" 
            range-key="label" 
            :disabled="hasTeam"
            @change="onDegreeChange"
            class="form-picker"
          >
            <view class="picker-content">
              <text class="picker-text">{{ userInfo.degree ? degreeOptions.find(d => d.value === userInfo.degree)?.label : '我的身份' }}</text>
            </view>
          </picker>
        </view>

        <!-- 大类 -->
        <view class="form-row">
          <picker 
            mode="selector" 
            :value="majorIndex" 
            :range="majorOptions" 
            range-key="label" 
            :disabled="hasTeam"
            @change="onMajorChange"
            class="form-picker"
          >
            <view class="picker-content">
              <text class="picker-text">{{ userInfo.majorCategory ? majorOptions.find(m => m.value === userInfo.majorCategory)?.label : '大类' }}</text>
            </view>
          </picker>
        </view>

        <!-- 学院 -->
        <view class="form-row">
          <picker 
            mode="selector" 
            :value="academyIndex" 
            :range="academyOptions" 
            range-key="name" 
            :disabled="hasTeam"
            @change="onAcademyChange"
            class="form-picker"
          >
            <view class="picker-content">
              <text class="picker-text">{{ userInfo.college || '学院' }}</text>
            </view>
          </picker>
        </view>

        <!-- QQ号 -->
        <view class="form-row">
          <input 
            v-model="userInfo.qq" 
            class="form-input" 
            :disabled="hasTeam"
            placeholder="QQ号" 
            type="number"
          />
        </view>

        <!-- 个人简介 -->
        <view class="form-row form-row-textarea">
          <textarea 
            v-model="userInfo.bio" 
            class="form-textarea" 
            :disabled="hasTeam"
            placeholder="一句话概括一下自己吧~" 
            :maxlength="500"
            auto-height
          />
        </view>
      </view>

      <!-- 保存按钮（未组队时显示） -->
      <view v-if="!hasTeam" class="save-section">
        <button class="save-button" @click="handleSave">保存</button>
      </view>
      
      <!-- 已组队提示 -->
      <view v-if="hasTeam" class="team-tip-section">
        <text class="team-tip-text">已组队，无法修改个人信息</text>
      </view>
    </view>

    <!-- 底部导航栏 -->
    <CustomTabBar :current="3" />
  </view>
</template>

<script>
import { getUserInfo, updateUserInfo } from '../../services/auth'
import { uploadAvatar } from '../../services/upload'
import { getAcademies } from '../../services/academies'
import { GENDER_OPTIONS, DEGREE_OPTIONS, MAJOR_CATEGORY_OPTIONS } from '../../utils/constants'
import { getSignupDetail, updateSignup } from '../../services/signup'
import { getTeamInfo } from '../../services/match'
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
        degree: '',
        majorCategory: '',
        college: '',
        academyId: null, // 院系ID
        qq: '',
        bio: '',
        avatar: ''
      },
      genderOptions: GENDER_OPTIONS.filter(opt => opt.value !== 'unlimited'),
      degreeOptions: DEGREE_OPTIONS.filter(opt => opt.value !== 'unlimited'),
      majorOptions: MAJOR_CATEGORY_OPTIONS,
      academyOptions: [], // 院系选项列表
      saving: false,
      hasTeam: false // 是否已组队
    }
  },
  computed: {
    genderIndex() {
      return this.genderOptions.findIndex(option => option.value === this.userInfo.gender)
    },
    degreeIndex() {
      return this.degreeOptions.findIndex(option => option.value === this.userInfo.degree)
    },
    majorIndex() {
      return this.majorOptions.findIndex(option => option.value === this.userInfo.majorCategory)
    },
    academyIndex() {
      if (!this.userInfo.academyId) return -1
      return this.academyOptions.findIndex(opt => opt.id === this.userInfo.academyId)
    }
  },
  async onLoad() {
    // 先加载院系列表，再加载用户信息，这样可以正确匹配院系名称
    await this.loadAcademies()
    await this.loadUserInfo()
    await this.checkTeamStatus()
  },
  methods: {
    async loadUserInfo() {
      // 优先从报名表获取完整信息，如果没有则从用户信息获取
      try {
        // 先尝试从报名表获取完整信息
        try {
          const signupDetail = await getSignupDetail()
          if (signupDetail) {
            console.log('📝 从报名表加载信息:', signupDetail)
            
            // 转换性别格式
            let gender = signupDetail.gender
            if (gender === '男' || gender === 'MALE' || gender === 1) {
              gender = 'male'
            } else if (gender === '女' || gender === 'FEMALE' || gender === 2) {
              gender = 'female'
            }
            
            // 转换学历格式
            let degree = signupDetail.degree
            if (degree === '本科' || degree === 'UNDERGRADUATE') {
              degree = 'undergraduate'
            } else if (degree === '研究生' || degree === 'POSTGRADUATE' || degree === 'GRADUATE') {
              degree = 'postgraduate'
            }
            
            // 处理院系信息
            let collegeName = signupDetail.college || signupDetail.academy_name || ''
            let academyId = signupDetail.academy || signupDetail.academyId || null
            if (academyId && !collegeName && this.academyOptions.length > 0) {
              const academy = this.academyOptions.find(a => a.id === academyId)
              if (academy) {
                collegeName = academy.name
              }
            } else if (collegeName && !academyId && this.academyOptions.length > 0) {
              const academy = this.academyOptions.find(a => a.name === collegeName)
              if (academy) {
                academyId = academy.id
              }
            }
            
            this.userInfo = {
              name: signupDetail.name || signupDetail.username || '',
              gender: gender || '',
              degree: degree || '',
              majorCategory: signupDetail.majorCategory || signupDetail.major_category || '',
              college: collegeName,
              academyId: academyId,
              qq: signupDetail.qq || '',
              bio: signupDetail.bio || signupDetail.biography || '',
              avatar: signupDetail.avatar || ''
            }
            
            // 保存到本地存储
            authUtils.setUserInfo(this.userInfo)
            return
          }
        } catch (signupErr) {
          console.log('未找到报名表信息，从用户信息加载')
        }
        
        // 如果没有报名表，从用户信息获取
        const info = await getUserInfo()
        if (info) {
          // 转换性别格式（如果后端返回的是中文）
          let gender = info.gender
          if (gender === '男' || gender === 'MALE' || gender === 1) {
            gender = 'male'
          } else if (gender === '女' || gender === 'FEMALE' || gender === 2) {
            gender = 'female'
          }
          
          // 如果有院系ID但没有名称，从已加载的院系列表中查找
          let collegeName = info.academy_name || info.college || info.department || ''
          const academyId = info.academy || null
          if (academyId && !collegeName && this.academyOptions.length > 0) {
            const academy = this.academyOptions.find(a => a.id === academyId)
            if (academy) {
              collegeName = academy.name
            }
          }
          
          this.userInfo = {
            name: info.username || info.name || '',
            gender: gender || '',
            degree: info.degree || '',
            majorCategory: info.majorCategory || info.major_category || '',
            college: collegeName,
            academyId: academyId,
            qq: info.qq || '',
            bio: info.bio || info.biography || '',
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

    onDegreeChange(e) {
      const selectedOption = this.degreeOptions[e.detail.value]
      this.userInfo.degree = selectedOption.value
    },

    onMajorChange(e) {
      const selectedOption = this.majorOptions[e.detail.value]
      this.userInfo.majorCategory = selectedOption.value
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
        
        // 如果已有院系ID但没有院系名称，根据ID查找名称
        if (this.userInfo.academyId && !this.userInfo.college) {
          const academy = flatAcademies.find(a => a.id === this.userInfo.academyId)
          if (academy) {
            this.userInfo.college = academy.name
          }
        }
        // 如果有院系名称但没有ID，根据名称查找ID
        else if (this.userInfo.college && !this.userInfo.academyId) {
          const academy = flatAcademies.find(a => a.name === this.userInfo.college)
          if (academy) {
            this.userInfo.academyId = academy.id
          }
        }
      } catch (err) {
        console.error('加载院系列表失败:', err)
        this.academyOptions = []
      }
    },

    onAcademyChange(e) {
      const index = e.detail.value
      const academy = this.academyOptions[index]
      if (academy) {
        this.userInfo.college = academy.name
        this.userInfo.academyId = academy.id
      }
    },

    async checkTeamStatus() {
      try {
        // 先从本地存储检查
        const localHasTeam = uni.getStorageSync('hasTeam')
        if (localHasTeam) {
          this.hasTeam = true
          return
        }
        
        // 从API检查
        const res = await getTeamInfo()
        if (res && res.team) {
          this.hasTeam = true
          uni.setStorageSync('hasTeam', true)
        } else {
          this.hasTeam = false
          uni.removeStorageSync('hasTeam')
        }
      } catch (err) {
        console.error('检查组队状态失败:', err)
        // 如果API调用失败，使用本地存储的值
        const localHasTeam = uni.getStorageSync('hasTeam')
        this.hasTeam = !!localHasTeam
      }
    },

    async chooseAvatar() {
      if (this.hasTeam) {
        uni.showToast({
          title: '已组队，无法修改头像',
          icon: 'none'
        })
        return
      }
      
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
        // 转换性别：前端使用 'male'/'female'，后端需要 1/2
        let genderValue = null
        if (this.userInfo.gender === 'male') {
          genderValue = 1
        } else if (this.userInfo.gender === 'female') {
          genderValue = 2
        } else if (this.userInfo.gender === 1 || this.userInfo.gender === 2) {
          genderValue = this.userInfo.gender
        }

        // 准备要保存的数据（使用后端期望的字段名）
        const updateData = {
          username: this.userInfo.name, // 后端期望 username，不是 name
          qq: this.userInfo.qq
        }

        // 如果有性别，添加性别字段
        if (genderValue !== null) {
          updateData.gender = genderValue
        }

        // 如果有学历，添加学历字段
        if (this.userInfo.degree) {
          // 转换学历：前端使用 'undergraduate'/'postgraduate'，后端需要中文或英文
          let degreeValue = this.userInfo.degree
          if (degreeValue === 'undergraduate') {
            degreeValue = '本科'
          } else if (degreeValue === 'postgraduate') {
            degreeValue = '研究生'
          }
          updateData.degree = degreeValue
        }

        // 如果有大类，添加大类字段
        if (this.userInfo.majorCategory) {
          updateData.majorCategory = this.userInfo.majorCategory
        }

        // 如果有院系ID，添加院系字段（后端期望 academy ID，不是 college 名称）
        if (this.userInfo.academyId) {
          updateData.academy = this.userInfo.academyId
        }

        // 如果有个人简介，添加个人简介字段
        if (this.userInfo.bio) {
          updateData.bio = this.userInfo.bio
        }

        // 调用更新用户信息接口
        const updatedInfo = await updateUserInfo(updateData)
        
        // 同步更新报名表（如果存在）
        try {
          const signupData = {
            name: this.userInfo.name,
            gender: this.userInfo.gender,
            degree: this.userInfo.degree,
            majorCategory: this.userInfo.majorCategory,
            college: this.userInfo.college,
            academyId: this.userInfo.academyId,
            qq: this.userInfo.qq,
            bio: this.userInfo.bio,
            avatar: this.userInfo.avatar
          }
          await updateSignup(signupData)
          console.log('✅ 报名表同步更新成功')
        } catch (signupErr) {
          console.warn('⚠️ 同步更新报名表失败（可能未报名）:', signupErr)
          // 如果报名表不存在，不报错，只更新用户信息即可
        }
        
        // 转换后端返回的数据格式到前端格式
        let gender = updatedInfo.gender
        if (gender === 1 || gender === '男' || gender === 'MALE') {
          gender = 'male'
        } else if (gender === 2 || gender === '女' || gender === 'FEMALE') {
          gender = 'female'
        }
        
        // 转换学历格式
        let degree = updatedInfo.degree
        if (degree === '本科' || degree === 'UNDERGRADUATE') {
          degree = 'undergraduate'
        } else if (degree === '研究生' || degree === 'POSTGRADUATE' || degree === 'GRADUATE') {
          degree = 'postgraduate'
        }
        
        // 更新本地用户信息（确保字段名正确映射）
        this.userInfo = {
          ...this.userInfo,
          name: updatedInfo.username || updatedInfo.name || this.userInfo.name,
          gender: gender || this.userInfo.gender,
          degree: degree || this.userInfo.degree,
          majorCategory: updatedInfo.majorCategory || updatedInfo.major_category || this.userInfo.majorCategory,
          college: updatedInfo.academy_name || this.userInfo.college,
          academyId: updatedInfo.academy || this.userInfo.academyId,
          qq: updatedInfo.qq || this.userInfo.qq,
          bio: updatedInfo.bio || updatedInfo.biography || this.userInfo.bio,
          avatar: updatedInfo.avatar || this.userInfo.avatar
        }
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

.form-row-textarea {
  height: auto;
  min-height: 100rpx;
  padding: 0;
  margin-bottom: 32rpx; /* 添加底部间距，避免与保存按钮重叠 */
  background: transparent;
  border: none;
  align-items: flex-start;
}

.form-textarea {
  width: 100%;
  font-size: 32rpx;
  color: #333333;
  min-height: 100rpx;
  padding: 20rpx 40rpx;
  background: #FFFFFF;
  border-radius: 100rpx;
  border: 2rpx solid #E0A7FF;
  box-sizing: border-box;
  line-height: 1.5;
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
  margin-top: 60rpx;
  margin-bottom: 40rpx;
  display: flex;
  justify-content: center;
}

/* 已组队提示区域 */
.team-tip-section {
  margin-top: 60rpx;
  margin-bottom: 40rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40rpx;
}

.team-tip-text {
  font-size: 28rpx;
  color: #999999;
  text-align: center;
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