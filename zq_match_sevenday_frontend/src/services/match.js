/**
 * 匹配/组队相关接口
 */

import { get, post } from '../utils/request'

/**
 * 系统自动匹配
 */
export function autoMatch() {
  return post('/match/auto', {}, { showLoading: true, loadingText: '匹配中...' })
}

/**
 * 定向匹配（通过学号）
 * @param {string} studentNo - 对方学号
 */
export function targetMatch(studentNo) {
  return post('/match/target', { studentNo }, { showLoading: true, loadingText: '匹配中...' })
}

/**
 * 确认匹配（接受/拒绝）
 * @param {string} matchId - 匹配ID
 * @param {boolean} accept - 是否接受
 */
export function confirmMatch(matchId, accept) {
  return post('/match/confirm', { matchId, accept })
}

/**
 * 获取匹配列表
 */
export function getMatchList() {
  return get('/match/list')
}

/**
 * 获取当前队伍信息
 */
export function getTeamInfo() {
  return get('/match/team')
}

/**
 * 设置队伍名称
 * @param {string} teamName - 队伍名称
 */
export function setTeamName(teamName) {
  return post('/match/teamName', { teamName })
}

/**
 * 解散队伍
 */
export function disbandTeam() {
  return post('/match/disband', {}, { showLoading: true, loadingText: '解散中...' })
}

/**
 * 检查是否可以拆队（是否已用过拆队机会）
 */
export function checkDisbandPermission() {
  return get('/match/checkDisband')
}

/**
 * 保存匹配期望
 * @param {object} expectation - 期望信息 { gender, majorCategory, college }
 */
export function saveMatchExpectation(expectation) {
  return post('/match/expectation', expectation, { showLoading: true, loadingText: '保存中...' })
}

/**
 * 获取匹配期望
 */
export function getMatchExpectation() {
  return get('/match/expectation')
}

