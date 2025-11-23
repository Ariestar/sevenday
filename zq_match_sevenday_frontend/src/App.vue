<script>
export default {
  onLaunch: function () {
    console.log('App Launch');
    
    // 应用启动时检查组队状态
    this.checkTeamStatusOnLaunch()
  },
  onShow: function () {
    console.log('App Show');
    
    // 应用显示时也检查组队状态（从后台切回前台时）
    this.checkTeamStatusOnLaunch()
  },
  onHide: function () {
    console.log('App Hide');
  },
  methods: {
    async checkTeamStatusOnLaunch() {
      try {
        // 先检查本地存储
        const localHasTeam = uni.getStorageSync('hasTeam')
        let hasTeam = localHasTeam
        
        // 如果有 token（已登录），尝试从 API 获取最新的组队状态
        const token = uni.getStorageSync('token')
        if (token && !hasTeam) {
          try {
            // 动态导入 getTeamInfo 避免循环依赖
            const { getTeamInfo } = await import('./services/match')
            const teamRes = await getTeamInfo()
            if (teamRes && teamRes.team) {
              hasTeam = true
              uni.setStorageSync('hasTeam', true)
              if (teamRes.team.name) {
                uni.setStorageSync('teamName', teamRes.team.name)
              }
            } else {
              hasTeam = false
              uni.removeStorageSync('hasTeam')
            }
          } catch (err) {
            console.log('应用启动时检查组队状态失败，使用本地存储:', err)
            // 如果 API 调用失败，使用本地存储的值
            hasTeam = !!localHasTeam
          }
        }
        
        // 如果已组队，检查当前页面是否需要跳转
        if (hasTeam) {
          // 延迟检查，确保页面已加载
          setTimeout(() => {
            try {
              const pages = getCurrentPages()
              if (pages && pages.length > 0) {
                const currentPage = pages[pages.length - 1]
                const route = currentPage.route
                const normalizedRoute = route.startsWith('/') ? route.substring(1) : route
                
                // 如果在报名或匹配页面，跳转到打卡页面
                if (normalizedRoute === 'pages/signup/index' || 
                    normalizedRoute === 'pages/multiple-match/index' ||
                    normalizedRoute === 'pages/single-match/index') {
                  console.log('应用启动：已组队，从报名-匹配页面跳转到打卡页面')
                  uni.switchTab({
                    url: '/pages/checkin-detail/index',
                    fail: () => {
                      uni.reLaunch({
                        url: '/pages/checkin-detail/index'
                      })
                    }
                  })
                }
              }
            } catch (err) {
              console.error('应用启动时检查页面跳转失败:', err)
            }
          }, 500)
        }
      } catch (err) {
        console.error('应用启动时检查组队状态失败:', err)
      }
    }
  }
};
</script>

<style>
/*每个页面公共css */
</style>
