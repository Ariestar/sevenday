/**
 * 专交遇见你 - 核心常量配置
 * 所有业务常量集中管理，便于统一修改
 */

// 活动天数
export const ACTIVITY_DAYS = 10

// 活动开始日期（格式：'YYYY-MM-DD'）
// 请根据实际活动开始日期修改此值
export const ACTIVITY_START_DATE = '2025-11-22'

// 打卡状态枚举
export const CHECKIN_STATUS = {
  UN_SUBMIT: 0,   // 未提交
  PENDING: 1,     // 待审核
  APPROVED: 2,    // 审核通过
  REJECTED: 3     // 被驳回
}

// 打卡状态文本映射
export const CHECKIN_STATUS_TEXT = {
  [CHECKIN_STATUS.UN_SUBMIT]: '未提交',
  [CHECKIN_STATUS.PENDING]: '待审核',
  [CHECKIN_STATUS.APPROVED]: '已通过',
  [CHECKIN_STATUS.REJECTED]: '已驳回'
}

// 匹配期望最大数量
export const MAX_MATCH_EXPECTATIONS = 3

// 性别选项
export const GENDER_OPTIONS = [
  { label: '男', value: 'male' },
  { label: '女', value: 'female' },
  { label: '不限', value: 'unlimited' }
]

// 学历选项
export const DEGREE_OPTIONS = [
  { label: '本科', value: 'undergraduate' },
  { label: '研究生', value: 'postgraduate' },
  { label: '不限', value: 'unlimited' }
]

// 大类选项
export const MAJOR_CATEGORY_OPTIONS = [
  { label: '理科类', value: 'science' },
  { label: '工科类', value: 'engineering' },
  { label: '医学类', value: 'medical' },
  { label: '文科类', value: 'arts' },
  { label: '艺术类', value: 'art' }
]

// API 接口前缀
// 正式环境：设置为实际后端服务器地址
export const API_BASE_URL = 'http://121.40.155.61:8000'// 空字符串表示使用相对路径，或者设置为完整URL如 'https://api.example.com/api'

