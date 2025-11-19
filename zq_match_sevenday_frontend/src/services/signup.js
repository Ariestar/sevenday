/**
 * 报名相关接口
 */

import { get, post } from '../utils/request'

/**
 * 提交报名信息
 * @param {object} data - 报名数据
 * @param {string} data.name - 姓名
 * @param {string} data.gender - 性别
 * @param {string} data.degree - 学历（本科/研究生）
 * @param {string} data.studentNo - 学号
 * @param {string} data.majorCategory - 大类
 * @param {string} data.college - 院系
 * @param {string} data.qq - QQ号
 * @param {string} data.avatar - 头像URL（可选）
 * @param {array} data.matchExpectations - 匹配期望列表（最多3条）
 */
export function submitSignup(data) {
  return post('/signup/', data, { showLoading: true, loadingText: '提交中...' })
}

/**
 * 获取报名详情
 */
export function getSignupDetail() {
  return get('/signup/detail/')
}

/**
 * 更新报名信息
 * @param {object} data - 报名数据
 */
export function updateSignup(data) {
  return post('/signup/update/', data, { showLoading: true, loadingText: '更新中...' })
}

/**
 * 检查是否已报名
 */
export function checkSignupStatus() {
  return get('/signup/status/')
}

