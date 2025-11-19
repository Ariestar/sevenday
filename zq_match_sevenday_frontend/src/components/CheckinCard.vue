<template>
  <view class="checkin-card" @click="handleClick">
    <view class="card-header">
      <view class="day-info">
        <text class="day-number">第 {{ day }} 天</text>
        <text v-if="taskTitle" class="task-title">{{ taskTitle }}</text>
      </view>
      <view class="status-badge" :class="`status-${status}`">
        {{ statusText }}
      </view>
    </view>

    <view v-if="myCheckin || teammateCheckin" class="card-content">
      <!-- 我的打卡状态 -->
      <view class="checkin-status">
        <text class="status-label">我的状态：</text>
        <text class="status-value" :class="`status-${myCheckin?.status || 0}`">
          {{ getStatusText(myCheckin?.status || 0) }}
        </text>
      </view>

      <!-- 队友的打卡状态 -->
      <view class="checkin-status">
        <text class="status-label">队友状态：</text>
        <text class="status-value" :class="`status-${teammateCheckin?.status || 0}`">
          {{ getStatusText(teammateCheckin?.status || 0) }}
        </text>
      </view>

      <!-- 驳回原因 -->
      <view v-if="myCheckin?.status === CHECKIN_STATUS.REJECTED && myCheckin.rejectReason" class="reject-reason">
        <text class="reason-label">驳回原因：</text>
        <text class="reason-text">{{ myCheckin.rejectReason }}</text>
      </view>
    </view>

    <view class="card-footer">
      <text v-if="canSubmit" class="action-hint">点击{{ isResubmit ? '重新' : '' }}提交打卡</text>
      <text v-else-if="canView" class="action-hint">点击查看详情</text>
    </view>
  </view>
</template>

<script>
import { CHECKIN_STATUS, CHECKIN_STATUS_TEXT } from '../utils/constants'

export default {
  name: 'CheckinCard',
  props: {
    day: {
      type: Number,
      required: true
    },
    taskTitle: {
      type: String,
      default: ''
    },
    myCheckin: {
      type: Object,
      default: null
    },
    teammateCheckin: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      CHECKIN_STATUS
    }
  },
  computed: {
    // 当前卡片的整体状态
    status() {
      const myStatus = this.myCheckin?.status || CHECKIN_STATUS.UN_SUBMIT
      const teammateStatus = this.teammateCheckin?.status || CHECKIN_STATUS.UN_SUBMIT

      // 两人都通过才算完成
      if (myStatus === CHECKIN_STATUS.APPROVED && teammateStatus === CHECKIN_STATUS.APPROVED) {
        return CHECKIN_STATUS.APPROVED
      }

      // 任一人被驳回
      if (myStatus === CHECKIN_STATUS.REJECTED || teammateStatus === CHECKIN_STATUS.REJECTED) {
        return CHECKIN_STATUS.REJECTED
      }

      // 任一人待审核
      if (myStatus === CHECKIN_STATUS.PENDING || teammateStatus === CHECKIN_STATUS.PENDING) {
        return CHECKIN_STATUS.PENDING
      }

      return CHECKIN_STATUS.UN_SUBMIT
    },
    statusText() {
      return CHECKIN_STATUS_TEXT[this.status]
    },
    // 是否可以提交
    canSubmit() {
      const myStatus = this.myCheckin?.status || CHECKIN_STATUS.UN_SUBMIT
      return myStatus === CHECKIN_STATUS.UN_SUBMIT || myStatus === CHECKIN_STATUS.REJECTED
    },
    // 是否是重新提交
    isResubmit() {
      return this.myCheckin?.status === CHECKIN_STATUS.REJECTED
    },
    // 是否可以查看详情
    canView() {
      return this.myCheckin || this.teammateCheckin
    }
  },
  methods: {
    getStatusText(status) {
      return CHECKIN_STATUS_TEXT[status]
    },
    handleClick() {
      this.$emit('click', {
        day: this.day,
        canSubmit: this.canSubmit,
        isResubmit: this.isResubmit
      })
    }
  }
}
</script>

<style scoped>
.checkin-card {
  padding: 30rpx;
  margin-bottom: 24rpx;
  background-color: #fff;
  border-radius: 16rpx;
  box-shadow: 0 2rpx 16rpx rgba(0, 0, 0, 0.06);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20rpx;
}

.day-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.day-number {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 8rpx;
}

.task-title {
  font-size: 28rpx;
  color: #666;
}

.status-badge {
  padding: 8rpx 20rpx;
  font-size: 24rpx;
  border-radius: 8rpx;
  white-space: nowrap;
}

.status-0 {
  color: #999;
  background-color: #f5f5f5;
}

.status-1 {
  color: #fa8c16;
  background-color: #fff7e6;
}

.status-2 {
  color: #52c41a;
  background-color: #f6ffed;
}

.status-3 {
  color: #ff4d4f;
  background-color: #fff1f0;
}

.card-content {
  padding: 20rpx 0;
  border-top: 1rpx solid #f0f0f0;
  border-bottom: 1rpx solid #f0f0f0;
}

.checkin-status {
  display: flex;
  align-items: center;
  margin-bottom: 12rpx;
}

.status-label {
  font-size: 28rpx;
  color: #666;
}

.status-value {
  font-size: 28rpx;
  font-weight: bold;
}

.reject-reason {
  margin-top: 16rpx;
  padding: 16rpx;
  background-color: #fff1f0;
  border-radius: 8rpx;
}

.reason-label {
  font-size: 26rpx;
  color: #ff4d4f;
  font-weight: bold;
}

.reason-text {
  font-size: 26rpx;
  color: #ff4d4f;
}

.card-footer {
  margin-top: 20rpx;
}

.action-hint {
  font-size: 26rpx;
  color: #1890ff;
}
</style>

