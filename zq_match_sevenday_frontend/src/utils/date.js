/**
 * 日期工具函数
 */

import { ACTIVITY_START_DATE, ACTIVITY_DAYS } from './constants'

/**
 * 获取当前是活动的第几天（基于活动开始日期）
 * @returns {number} 第几天（1-10），如果活动未开始或已结束，返回null
 */
export function getCurrentActivityDay() {
  const today = new Date()
  today.setHours(0, 0, 0, 0) // 设置为当天的00:00:00
  
  const startDate = new Date(ACTIVITY_START_DATE)
  startDate.setHours(0, 0, 0, 0)
  
  // 计算天数差
  const diffTime = today.getTime() - startDate.getTime()
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24)) + 1 // +1 因为第一天是1
  
  // 检查是否在活动期间内
  if (diffDays < 1) {
    // 活动未开始
    return null
  }
  
  if (diffDays > ACTIVITY_DAYS) {
    // 活动已结束
    return null
  }
  
  return diffDays
}

/**
 * 检查指定天数是否是今天
 * @param {number} day - 要检查的天数（1-10）
 * @returns {boolean} 是否是今天
 */
export function isToday(day) {
  const currentDay = getCurrentActivityDay()
  return currentDay !== null && currentDay === day
}

/**
 * 检查是否可以打卡指定天数
 * @param {number} day - 要打卡的天数（1-10）
 * @returns {object} { canCheckin: boolean, message: string }
 */
export function canCheckinDay(day) {
  const currentDay = getCurrentActivityDay()
  
  if (currentDay === null) {
    return {
      canCheckin: false,
      message: '活动未开始或已结束'
    }
  }
  
  if (day < currentDay) {
    return {
      canCheckin: false,
      message: '只能打卡当天的内容'
    }
  }
  
  if (day > currentDay) {
    return {
      canCheckin: false,
      message: '只能打卡当天的内容'
    }
  }
  
  return {
    canCheckin: true,
    message: ''
  }
}









