/**
 * 院系相关接口
 */

import { get } from '../utils/request'

/**
 * 获取院系列表
 * @returns {Promise<Array>} 返回院系列表，格式为 [{id, name, children: [{id, name}]}]
 */
export async function getAcademies() {
  try {
    console.log('📚 [academies.js] 开始调用院系列表接口: /academies/')
    const result = await get('/academies/', {}, { showLoading: false })
    console.log('📚 [academies.js] 接口返回的原始数据:', result)
    console.log('📚 [academies.js] 数据类型:', typeof result)
    console.log('📚 [academies.js] 是否为数组:', Array.isArray(result))
    console.log('📚 [academies.js] 是否为null:', result === null)
    console.log('📚 [academies.js] 是否为undefined:', result === undefined)
    
    // 如果返回的是数组，直接返回
    if (Array.isArray(result)) {
      console.log('📚 [academies.js] ✓ 返回数组格式，长度:', result.length)
      console.log('📚 [academies.js] 数组内容预览:', result.slice(0, 2))
      return result
    } 
    
    // 如果是对象，检查各种可能的字段
    if (result && typeof result === 'object') {
      console.log('📚 [academies.js] 返回对象格式，检查字段...')
      console.log('📚 [academies.js] result.data:', result.data)
      console.log('📚 [academies.js] result.results:', result.results)
      console.log('📚 [academies.js] result.list:', result.list)
      
      // 如果是对象且有data字段，返回data
      if (Array.isArray(result.data)) {
        console.log('📚 [academies.js] ✓ 使用data字段，长度:', result.data.length)
        return result.data
      } 
      
      // 如果是对象且有results字段，返回results
      if (Array.isArray(result.results)) {
        console.log('📚 [academies.js] ✓ 使用results字段，长度:', result.results.length)
        return result.results
      }
      
      // 如果是对象且有list字段，返回list
      if (Array.isArray(result.list)) {
        console.log('📚 [academies.js] ✓ 使用list字段，长度:', result.list.length)
        return result.list
      }
    }
    
    console.warn('⚠️ [academies.js] 院系列表返回的数据格式不符合预期:', result)
    console.warn('⚠️ [academies.js] 返回空数组')
    return []
  } catch (err) {
    console.error('❌ [academies.js] 获取院系列表失败:', err)
    console.error('❌ [academies.js] 错误详情:', {
      message: err?.message,
      errMsg: err?.errMsg,
      stack: err?.stack
    })
    // 如果API调用失败，返回空数组，不影响页面显示
    return []
  }
}

