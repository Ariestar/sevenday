/**
 * 上传相关接口
 */

import { API_BASE_URL } from '../utils/constants'

/**
 * 上传头像
 * @param {string} filePath - 本地文件路径
 * @returns {Promise<{url: string}>} 返回上传后的URL对象
 */
export function uploadAvatar(filePath) {
  return new Promise((resolve, reject) => {
    uni.showLoading({ title: '上传中...', mask: true })

    // 获取token
    const token = uni.getStorageSync('token') || uni.getStorageSync('access_token')
    const headers = {}
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    uni.uploadFile({
      url: `${API_BASE_URL}/users/upload-avatar/`,
      filePath,
      name: 'file',
      header: headers,
      success: (res) => {
        uni.hideLoading()

        console.log('📤 上传头像响应:', res)
        console.log('📤 res.data类型:', typeof res.data)
        console.log('📤 res.data内容:', res.data)
        console.log('📤 res.statusCode:', res.statusCode)

        try {
          // 处理响应数据：可能是字符串或对象
          let data = res.data
          if (typeof data === 'string') {
            // 如果是字符串，尝试解析JSON
            if (data.trim()) {
              data = JSON.parse(data)
            } else {
              // 空字符串，可能是错误
              throw new Error('响应为空')
            }
          } else if (typeof data === 'object' && data !== null) {
            // 已经是对象，直接使用
            data = data
          } else {
            throw new Error('响应格式不正确')
          }

          console.log('📤 解析后的data:', data)

          // 兼容多种响应格式
          let avatarUrl = ''
          if (data.code === "00000" || data.code === 0) {
            // 标准格式：{code: "00000", data: {url: "..."}}
            avatarUrl = data.data?.url || data.url || ''
          } else if (data.data && data.data.url) {
            // 嵌套格式
            avatarUrl = data.data.url
          } else if (data.url) {
            // 直接包含url
            avatarUrl = data.url
          } else if (res.statusCode === 200 || res.statusCode === 201) {
            // HTTP成功但格式不对，尝试从data中提取
            avatarUrl = data.avatar || data.data?.avatar || ''
          }

          if (avatarUrl) {
            console.log('✅ 头像URL:', avatarUrl)
            resolve(avatarUrl)
          } else {
            console.error('❌ 无法提取头像URL，响应数据:', data)
            const errorMsg = data.msg || data.message || data.detail || '上传失败，无法获取头像URL'
            uni.showToast({
              title: errorMsg,
              icon: 'none'
            })
            reject(new Error(errorMsg))
          }
        } catch (e) {
          console.error('❌ 解析响应失败:', e)
          console.error('❌ 原始响应:', res)
          uni.showToast({
            title: `解析响应失败: ${e.message || '未知错误'}`,
            icon: 'none',
            duration: 3000
          })
          reject(new Error(`解析响应失败: ${e.message || '未知错误'}`))
        }
      },
      fail: (err) => {
        uni.hideLoading()
        console.error('❌ 上传失败:', err)
        uni.showToast({
          title: err.errMsg || '上传失败',
          icon: 'none'
        })
        reject(err)
      }
    })
  })
}

/**
 * 上传打卡图片
 * @param {string} filePath - 本地文件路径
 * @returns {Promise<string>} 返回上传后的URL
 */
export function uploadCheckinImage(filePath) {
  return new Promise((resolve, reject) => {
    uni.showLoading({ title: '上传中...', mask: true })

    // 获取token
    const token = uni.getStorageSync('token') || uni.getStorageSync('access_token')
    const headers = {}
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    uni.uploadFile({
      url: `${API_BASE_URL}/upload/checkin`,
      filePath,
      name: 'file',
      header: headers,
      success: (res) => {
        uni.hideLoading()

        console.log('📤 上传打卡图片响应:', res)
        
        try {
          let data = res.data
          if (typeof data === 'string') {
            data = JSON.parse(data)
          }

          console.log('📤 解析后的data:', data)

          // 兼容多种响应格式（包括嵌套格式）
          if (data.code === "00000" || data.code === 0) {
            // 处理嵌套格式：data.data.data.url 或 data.data.url 或 data.url
            let imageUrl = ''
            if (data.data) {
              // 如果data.data是对象且包含url
              if (typeof data.data === 'object' && data.data.url) {
                imageUrl = data.data.url
              } 
              // 如果data.data是对象且包含data属性（嵌套格式）
              else if (typeof data.data === 'object' && data.data.data && data.data.data.url) {
                imageUrl = data.data.data.url
              }
              // 如果data.data直接是字符串URL
              else if (typeof data.data === 'string') {
                imageUrl = data.data
              }
            }
            // 如果没有从data.data获取到，尝试直接从data获取
            if (!imageUrl && data.url) {
              imageUrl = data.url
            }
            
            console.log('📤 提取的图片URL:', imageUrl)
            
            if (imageUrl) {
              resolve(imageUrl)
            } else {
              console.error('❌ 无法提取图片URL，响应结构:', JSON.stringify(data, null, 2))
              reject(new Error('无法获取图片URL'))
            }
          } else {
            const errorMsg = data.msg || data.message || '上传失败'
            uni.showToast({
              title: errorMsg,
              icon: 'none'
            })
            reject(new Error(errorMsg))
          }
        } catch (e) {
          console.error('❌ 解析响应失败:', e)
          uni.showToast({
            title: '解析响应失败',
            icon: 'none'
          })
          reject(new Error('解析响应失败'))
        }
      },
      fail: (err) => {
        uni.hideLoading()
        console.error('❌ 上传失败:', err)
        uni.showToast({
          title: err.errMsg || '上传失败',
          icon: 'none'
        })
        reject(err)
      }
    })
  })
}

/**
 * 批量上传打卡图片
 * @param {array} filePaths - 本地文件路径数组
 * @returns {Promise<array>} 返回上传后的URL数组
 */
export function uploadCheckinImages(filePaths) {
  const uploadPromises = filePaths.map(filePath => uploadCheckinImage(filePath))
  return Promise.all(uploadPromises)
}

