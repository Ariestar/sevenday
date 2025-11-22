/**
 * 统一的请求封装
 * 所有接口调用都通过这个方法，便于统一处理错误和响应
 */

import { API_BASE_URL } from './constants'
import authUtils from './auth'

/**
 * 发起网络请求
 * @param {string} url - 请求地址（不含前缀）
 * @param {object} options - 请求配置
 * @returns {Promise}
 */
export function request(url, options = {}) {
  const {
    method = 'GET',
    data = {},
    header = {},
    showLoading = false,
    loadingText = '加载中...'
  } = options

  // 显示加载提示
  if (showLoading) {
    uni.showLoading({ title: loadingText, mask: true })
  }

  // 自动添加认证令牌
  const token = authUtils.getToken()
  const requestHeader = {
    'Content-Type': 'application/json',
    ...header
  }
  
  if (token) {
    requestHeader['Authorization'] = `Bearer ${token}`
  }

  return new Promise((resolve, reject) => {
    uni.request({
      url: `${API_BASE_URL}${url}`,
      method,
      data,
      header: requestHeader,
      success: (res) => {
        if (showLoading) {
          uni.hideLoading()
        }

        // 添加详细的调试日志 - 小程序环境特殊处理
        console.log('🔍 ========== API 响应详情 ==========')
        console.log('🔍 完整响应对象:', res)
        console.log('🔍 statusCode:', res.statusCode)
        console.log('🔍 res.data 类型:', typeof res.data)
        console.log('🔍 res.data 内容:', res.data)
        console.log('🔍 res.data 是否为字符串:', typeof res.data === 'string')
        
        // 处理小程序可能返回字符串的情况
        let responseData = res.data
        if (typeof res.data === 'string') {
          try {
            responseData = JSON.parse(res.data)
            console.log('🔍 解析后的 JSON:', responseData)
          } catch (e) {
            console.error('🔍 JSON 解析失败:', e)
            // 如果 JSON 解析失败，使用原始数据
            responseData = res.data
          }
        }
        
        console.log('🔍 responseData:', responseData)
        console.log('🔍 responseData.code:', responseData?.code)
        console.log('🔍 responseData.code 类型:', typeof responseData?.code)
        console.log('🔍 responseData.data:', responseData?.data)
        console.log('🔍 ====================================')

        // 根据后端约定的状态码判断
        // 兼容 code 为数字 0 或字符串 "00000" 的情况
        const code = responseData?.code
        const isSuccess = code === 0 || code === '0' || code === '00000' || 
                         (typeof code === 'string' && code.startsWith('0000'))
        
        // 兼容 200 (成功) 和 201 (创建成功) 状态码
        const isHttpSuccess = res.statusCode === 200 || res.statusCode === 201
        
        console.log('🔍 判断详情:', {
          statusCode: res.statusCode,
          code: code,
          codeType: typeof code,
          isSuccess: isSuccess,
          isHttpSuccess: isHttpSuccess,
          condition1: isHttpSuccess,
          condition2: isSuccess,
          finalResult: isHttpSuccess && isSuccess,
          // 添加更详细的比较信息
          codeComparisons: {
            'code === 0': code === 0,
            'code === "0"': code === '0',
            'code === "00000"': code === '00000',
            'code == 0': code == 0,
            'code == "0"': code == '0'
          }
        })
        
        if (isHttpSuccess && isSuccess) {
          console.log('✅ 请求成功，返回数据:', responseData.data)
          resolve(responseData.data)
        } else if (res.statusCode === 401 || responseData?.code === 401 || responseData?.code === '401') {
          // 认证失败，清除本地认证信息
          authUtils.logout()
          uni.showToast({
            title: '登录已过期，请重新登录',
            icon: 'none',
            duration: 2000
          })
          reject(new Error('Authentication failed'))
        } else {
          // 接口业务错误
          console.error('❌ ========== 请求失败 ==========')
          console.error('❌ 完整响应对象:', res)
          console.error('❌ 响应字符串化:', JSON.stringify(res, null, 2))
          console.error('❌ responseData:', responseData)
          console.error('❌ 失败原因分析:', {
            statusCode: res.statusCode,
            expectedStatus: 200,
            code: responseData?.code,
            codeType: typeof responseData?.code,
            expectedCode: [0, '0', '00000'],
            dataStructure: responseData,
            isSuccess: isSuccess,
            condition1: res.statusCode === 200,
            condition2: isSuccess
          })
          // 提取错误消息，优先使用 msg，然后是 detail，最后是 message
          // detail 字段通常包含更详细的错误信息（如字段级别的验证错误）
          let errorMsg = responseData?.msg || responseData?.detail || responseData?.message || '请求失败'
          
          // 如果 detail 包含多个错误（用分号分隔），只显示第一个
          if (errorMsg.includes(';')) {
            errorMsg = errorMsg.split(';')[0].trim()
          }
          
          // 清理错误消息中的字段标签前缀（如果后端已经添加了）
          // 例如："QQ号: QQ号格式不正确" -> "QQ号格式不正确"
          const colonIndex = errorMsg.indexOf(':')
          if (colonIndex > 0 && colonIndex < errorMsg.length - 1) {
            const beforeColon = errorMsg.substring(0, colonIndex).trim()
            const afterColon = errorMsg.substring(colonIndex + 1).trim()
            // 如果冒号后的内容已经包含了完整的错误信息，使用冒号后的内容
            if (afterColon && afterColon.length > 0) {
              errorMsg = afterColon
            }
          }
          
          console.error('❌ 错误消息:', errorMsg)
          console.error('❌ 原始 detail:', responseData?.detail)
          console.error('❌ ====================================')
          
          uni.showToast({
            title: errorMsg,
            icon: 'none',
            duration: 3000  // 增加显示时长，让用户有足够时间阅读错误信息
          })
          reject(new Error(errorMsg))
        }
      },
      fail: (err) => {
        if (showLoading) {
          uni.hideLoading()
        }

        // 如果是URL无效错误（开发阶段常见），静默失败，不显示错误提示
        const errorMsg = err?.errMsg || err?.message || String(err)
        if (errorMsg.includes('invalid url') || errorMsg.includes('600009')) {
          console.warn('API请求失败（开发阶段，后端未配置）:', err)
          // 开发阶段：静默失败，允许上层代码判断是否继续执行
        } else {
          // 其他网络错误
          uni.showToast({
            title: '网络请求失败',
            icon: 'none',
            duration: 2000
          })
        }
        // 始终抛出错误，让上层代码决定如何处理
        reject(err)
      }
    })
  })
}

/**
 * GET 请求
 */
export function get(url, data = {}, options = {}) {
  return request(url, { method: 'GET', data, ...options })
}

/**
 * POST 请求
 */
export function post(url, data = {}, options = {}) {
  return request(url, { method: 'POST', data, ...options })
}

/**
 * PUT 请求
 */
export function put(url, data = {}, options = {}) {
  return request(url, { method: 'PUT', data, ...options })
}

/**
 * DELETE 请求
 */
export function del(url, data = {}, options = {}) {
  return request(url, { method: 'DELETE', data, ...options })
}

