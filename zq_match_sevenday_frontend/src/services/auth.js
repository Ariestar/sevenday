/**
 * 身份认证相关接口
 */

import { get, post } from '../utils/request'

/**
 * 发送邮箱验证码
 * @param {string} email - 邮箱地址
 */
export function sendVerifyCode(email) {
  return post('/auth/sendCode/', { email })
}

/**
 * 验证邮箱
 * @param {string} email - 邮箱地址
 * @param {string} code - 验证码
 */
export function verifyEmail(email, code) {
  return post('/auth/verify/', { email, code })
}

/**
 * 获取当前用户信息
 */
export function getUserInfo() {
  return get('/auth/userInfo/')
}

/**
 * 更新用户信息
 * @param {object} userInfo - 用户信息对象
 */
export function updateUserInfo(userInfo) {
  return post('/auth/updateUserInfo/', userInfo)
}

/**
 * 微信登录
 * @param {string} code - 微信登录凭证
 */
export function wxLogin(code) {
  return post('/auth/wxLogin', { code })
}

