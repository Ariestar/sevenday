<template>
  <view class="expectation-editor">
    <view class="editor-header">
      <text class="header-title">匹配期望（最多{{ maxCount }}条）</text>
      <button 
        v-if="expectations.length < maxCount" 
        class="add-button" 
        @click="addExpectation"
      >
        + 添加期望
      </button>
    </view>

    <view v-if="expectations.length === 0" class="empty-hint">
      <text>还未添加匹配期望，点击上方按钮添加</text>
    </view>

    <view v-for="(item, index) in expectations" :key="index" class="expectation-item">
      <view class="item-header">
        <text class="item-title">期望 {{ index + 1 }}</text>
        <text class="item-delete" @click="deleteExpectation(index)">删除</text>
      </view>

      <!-- 期望性别 -->
      <view class="field-item">
        <view class="field-label">期望性别</view>
        <picker 
          mode="selector" 
          :range="genderOptions" 
          range-key="label"
          :value="getPickerIndex(genderOptions, item.gender)"
          @change="onGenderChange($event, index)"
        >
          <view class="picker-value">
            {{ getOptionLabel(genderOptions, item.gender) || '请选择' }}
          </view>
        </picker>
      </view>

      <!-- 期望学历 -->
      <view class="field-item">
        <view class="field-label">期望学历</view>
        <picker 
          mode="selector" 
          :range="degreeOptions" 
          range-key="label"
          :value="getPickerIndex(degreeOptions, item.degree)"
          @change="onDegreeChange($event, index)"
        >
          <view class="picker-value">
            {{ getOptionLabel(degreeOptions, item.degree) || '请选择' }}
          </view>
        </picker>
      </view>

      <!-- 期望大类 -->
      <view class="field-item">
        <view class="field-label">期望大类</view>
        <input 
          v-model="item.majorCategory" 
          class="field-input" 
          placeholder="请输入大类（可填 不限）" 
          @input="onExpectationChange"
        />
      </view>

      <!-- 期望院系 -->
      <view class="field-item">
        <view class="field-label">期望院系</view>
        <input 
          v-model="item.college" 
          class="field-input" 
          placeholder="请输入院系（可填 不限）" 
          @input="onExpectationChange"
        />
      </view>
    </view>
  </view>
</template>

<script>
import { MAX_MATCH_EXPECTATIONS, GENDER_OPTIONS, DEGREE_OPTIONS } from '../utils/constants'

export default {
  name: 'MatchExpectationEditor',
  props: {
    modelValue: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      maxCount: MAX_MATCH_EXPECTATIONS,
      genderOptions: GENDER_OPTIONS,
      degreeOptions: DEGREE_OPTIONS,
      expectations: [...this.modelValue]
    }
  },
  watch: {
    modelValue: {
      handler(newVal) {
        this.expectations = [...newVal]
      },
      deep: true
    }
  },
  methods: {
    addExpectation() {
      if (this.expectations.length >= this.maxCount) {
        uni.showToast({
          title: `最多添加${this.maxCount}条期望`,
          icon: 'none'
        })
        return
      }

      this.expectations.push({
        gender: '',
        degree: '',
        majorCategory: '',
        college: ''
      })
      this.onExpectationChange()
    },
    deleteExpectation(index) {
      this.expectations.splice(index, 1)
      this.onExpectationChange()
    },
    onGenderChange(e, index) {
      const selectedIndex = e.detail.value
      this.expectations[index].gender = this.genderOptions[selectedIndex].value
      this.onExpectationChange()
    },
    onDegreeChange(e, index) {
      const selectedIndex = e.detail.value
      this.expectations[index].degree = this.degreeOptions[selectedIndex].value
      this.onExpectationChange()
    },
    onExpectationChange() {
      this.$emit('update:modelValue', this.expectations)
    },
    getPickerIndex(options, value) {
      return options.findIndex(opt => opt.value === value)
    },
    getOptionLabel(options, value) {
      const option = options.find(opt => opt.value === value)
      return option ? option.label : ''
    }
  }
}
</script>

<style scoped>
.expectation-editor {
  padding: 30rpx;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30rpx;
}

.header-title {
  font-size: 34rpx;
  font-weight: bold;
  color: #333;
}

.add-button {
  padding: 16rpx 32rpx;
  font-size: 28rpx;
  color: #07c160;
  background-color: #f0f9ff;
  border: 1px solid #07c160;
  border-radius: 8rpx;
}

.empty-hint {
  padding: 80rpx 0;
  text-align: center;
  font-size: 28rpx;
  color: #999;
}

.expectation-item {
  padding: 30rpx;
  margin-bottom: 24rpx;
  background-color: #f5f5f5;
  border-radius: 12rpx;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
}

.item-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.item-delete {
  font-size: 28rpx;
  color: #ff4d4f;
}

.field-item {
  margin-bottom: 24rpx;
}

.field-label {
  font-size: 28rpx;
  color: #666;
  margin-bottom: 12rpx;
}

.picker-value {
  height: 88rpx;
  line-height: 88rpx;
  padding: 0 24rpx;
  font-size: 32rpx;
  background-color: #fff;
  border-radius: 8rpx;
}

.field-input {
  width: 100%;
  height: 88rpx;
  padding: 0 24rpx;
  font-size: 32rpx;
  background-color: #fff;
  border-radius: 8rpx;
}
</style>

