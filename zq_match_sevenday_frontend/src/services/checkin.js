/**
 * 打卡相关接口
 */

import { get, post } from '../utils/request'

/**
 * 获取打卡任务列表（10天）
 */
export function getCheckinTasks() {
  return get('/api/checkin/tasks/')
}

/**
 * 提交打卡
 * @param {object} data - 打卡数据
 * @param {number} data.day - 第几天（1-10）
 * @param {string} data.content - 打卡内容（文字）
 * @param {array} data.images - 图片URL数组
 * @param {boolean} data.syncToSquare - 是否同步到广场
 */
export function submitCheckin(data) {
  return post('/api/checkin/submit/', data, { showLoading: true, loadingText: '提交中...' })
}

/**
 * 获取某天的打卡详情
 * @param {number} day - 第几天
 */
export function getCheckinDetail(day) {
  return get('/api/checkin/detail/', { day })
}

/**
 * 获取我的打卡记录列表
 */
export function getMyCheckinList() {
  return get('/api/checkin/myList/')
}

/**
 * 获取队友的打卡记录列表
 */
export function getTeammateCheckinList() {
  return get('/api/checkin/teammateList/')
}

/**
 * 重新提交打卡（被驳回后）
 * @param {number} checkinId - 打卡ID
 * @param {object} data - 新的打卡数据
 */
export function resubmitCheckin(checkinId, data) {
  return post('/api/checkin/resubmit/', { checkinId, ...data }, { showLoading: true, loadingText: '提交中...' })
}

