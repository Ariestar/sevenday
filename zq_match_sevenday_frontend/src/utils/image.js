/**
 * 图片 URL 处理工具
 * 用于处理微信小程序不支持 HTTP 协议的问题
 */

import { API_BASE_URL } from './constants'

/**
 * 判断是否为开发环境
 */
function isDevelopment() {
  // 通过 API_BASE_URL 判断是否为本地开发
  // 微信小程序在开发环境下，如果使用 HTTP 协议，需要特殊处理
  if (!API_BASE_URL) {
    return false
  }
  return API_BASE_URL.includes('127.0.0.1') || 
         API_BASE_URL.includes('localhost') || 
         API_BASE_URL.startsWith('http://')
}

/**
 * 处理图片 URL
 * 在开发环境下，如果是 HTTP 链接，转换为本地默认图片或返回空
 * @param {string} url - 原始图片 URL
 * @param {string} defaultImage - 默认图片路径（可选，默认为用户默认头像）
 * @returns {string} 处理后的图片 URL
 */
export function processImageUrl(url, defaultImage = '/static/square/user-icon.png') {
  if (!url) {
    return defaultImage
  }

  // 如果是相对路径或已经是本地路径，直接返回
  if (url.startsWith('/') || url.startsWith('@/') || !url.startsWith('http')) {
    return url
  }

  // 在开发环境下，如果是 HTTP 链接，使用默认图片
  if (isDevelopment() && url.startsWith('http://')) {
    console.warn('⚠️ 开发环境：HTTP 图片链接不被微信小程序支持，使用默认图片:', url)
    return defaultImage
  }

  // HTTPS 链接或生产环境，直接返回
  return url
}

/**
 * 处理头像 URL
 * @param {string} avatarUrl - 头像 URL
 * @returns {string} 处理后的头像 URL
 */
export function processAvatarUrl(avatarUrl) {
  return processImageUrl(avatarUrl, '/static/square/user-icon.png')
}

/**
 * 处理通用图片 URL
 * @param {string} imageUrl - 图片 URL
 * @param {string} defaultImage - 默认图片路径
 * @returns {string} 处理后的图片 URL
 */
export function processGenericImageUrl(imageUrl, defaultImage = '/static/square/user-icon.png') {
  return processImageUrl(imageUrl, defaultImage)
}

