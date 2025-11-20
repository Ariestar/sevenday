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
    const result = await get('/academies/', {}, { showLoading: false })
    // 如果返回的是数组，直接返回；如果是对象且有data字段，返回data
    if (Array.isArray(result)) {
      return result
    } else if (result && Array.isArray(result.data)) {
      return result.data
    } else if (result && Array.isArray(result.results)) {
      return result.results
    }
    return result || []
  } catch (err) {
    console.error('获取院系列表失败:', err)
    // 如果API调用失败，返回空数组，不影响页面显示
    return []
  }
}

