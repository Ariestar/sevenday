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

    uni.uploadFile({
      url: `${API_BASE_URL}/upload/avatar`,
      filePath,
      name: 'file',
      success: (res) => {
        uni.hideLoading()

        const data = JSON.parse(res.data)
        if (data.code === 0) {
          resolve({ url: data.data.url })
        } else {
          uni.showToast({
            title: data.message || '上传失败',
            icon: 'none'
          })
          reject(new Error(data.message))
        }
      },
      fail: (err) => {
        uni.hideLoading()
        uni.showToast({
          title: '上传失败',
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

    uni.uploadFile({
      url: `${API_BASE_URL}/upload/checkin`,
      filePath,
      name: 'file',
      success: (res) => {
        uni.hideLoading()

        const data = JSON.parse(res.data)
        if (data.code === 0) {
          resolve(data.data.url)
        } else {
          uni.showToast({
            title: data.message || '上传失败',
            icon: 'none'
          })
          reject(new Error(data.message))
        }
      },
      fail: (err) => {
        uni.hideLoading()
        uni.showToast({
          title: '上传失败',
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

