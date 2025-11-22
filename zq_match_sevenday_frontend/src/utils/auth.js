/**
 * 认证状态管理工具
 */

const TOKEN_KEY = 'token'
const USER_INFO_KEY = 'userInfo'

export default {
  /**
   * 检查用户是否已认证
   */
  isAuthenticated() {
    const token = uni.getStorageSync(TOKEN_KEY)
    const userInfo = uni.getStorageSync(USER_INFO_KEY)
    return !!(token && userInfo)
  },

  /**
   * 获取认证令牌
   */
  getToken() {
    return uni.getStorageSync(TOKEN_KEY)
  },

  /**
   * 设置认证令牌
   */
  setToken(token) {
    uni.setStorageSync(TOKEN_KEY, token)
  },

  /**
   * 获取用户信息
   */
  getUserInfo() {
    return uni.getStorageSync(USER_INFO_KEY)
  },

  /**
   * 设置用户信息
   */
  setUserInfo(userInfo) {
    uni.setStorageSync(USER_INFO_KEY, userInfo)
  },

  /**
   * 登录成功后保存认证信息
   */
  login(token, userInfo) {
    this.setToken(token)
    this.setUserInfo(userInfo)
  },

  /**
   * 退出登录，清除认证信息
   */
  logout() {
    console.log('清除登录信息...')
    uni.removeStorageSync(TOKEN_KEY)
    uni.removeStorageSync(USER_INFO_KEY)
    
    // 清除其他可能相关的存储（如果有的话）
    try {
      // 可以在这里添加其他需要清除的数据
      // uni.removeStorageSync('someOtherKey')
    } catch (e) {
      console.warn('清除存储数据时出错:', e)
    }
    
    console.log('登录信息已清除')
    
    // 可以添加跳转到登录页的逻辑
    // 但由于登录是弹窗形式，这里只需要清除数据
  },

  /**
   * 检查是否需要认证，如果需要则显示登录弹窗
   * 这个方法需要在页面中调用，因为需要访问页面的方法
   */
  requireAuth(showLoginModal) {
    if (!this.isAuthenticated()) {
      if (typeof showLoginModal === 'function') {
        showLoginModal()
      }
      return false
    }
    return true
  }
}
