/**
 * 广场相关接口
 */

import { get, post } from '../utils/request'

/**
 * 获取广场列表
 * @param {number} page - 页码
 * @param {number} pageSize - 每页数量
 */
export function getSquareList(page = 1, pageSize = 20) {
  return get('/api/square/list', { page, pageSize })
}

/**
 * 点赞/取消点赞
 * @param {string} postId - 内容ID
 */
export function toggleLike(postId) {
  return post('/api/square/like', { postId })
}

/**
 * 获取广场详情
 * @param {string} postId - 内容ID
 */
export function getSquareDetail(postId) {
  return get('/api/square/detail', { postId })
}

/**
 * 提交评论
 * @param {string} postId - 内容ID
 * @param {string} content - 评论内容
 */
export function submitComment(postId, content) {
  return post('/api/square/comment', { postId, content })
}

