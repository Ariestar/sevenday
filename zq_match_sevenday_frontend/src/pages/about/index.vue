<template>
  <view class="about-page">
    <!-- 顶部导航 -->
    <view class="page-header">
      <view class="nav-bar">
        <view class="nav-left" @click="goBack">
          <text class="back-arrow">‹</text>
        </view>
        <text class="page-title">关于我们</text>
        <view class="nav-right"></view>
      </view>
    </view>

    <!-- 内容区域 -->
    <scroll-view class="content-area" scroll-y>
      <view class="content-container">
        <!-- 附录1：免责声明 -->
        <view class="section">
          <view class="section-title">附录1：免责声明</view>
          <view class="section-content">
            <text class="paragraph">在参加本次活动之前，请您务必仔细阅读并透彻理解本声明。如果您不同意以下任何内容，请立即停止参与本次活动。凡以任何形式参与本次活动的参与者，均视为自愿接受本活动声明的约束。</text>
            
            <text class="paragraph">"专交遇见你"是由武汉大学自强网络文化工作室主办，武汉大学大学生心理健康协会协办的一次旨在为促进武汉大学学生学习与交流的，通过线上小程序进行的活动。</text>
            
            <text class="paragraph">请您在参与活动时务必注意保护个人隐私，不轻易向他人泄露身份证号、手机号码、住址、银行账户等敏感信息；同时提高警惕，防范各类诈骗行为，不轻信陌生链接、不随意转账汇款，确保个人财产与人身安全。如遇可疑情况，请及时与活动方联系。</text>
            
            <text class="paragraph">鉴于本活动仅为武汉大学学生提供第三方交流平台，并在一定程度上起到促进参与者交流的作用，您在参与本活动时不能侵犯任何第三方的权益，否则由此产生的任何侵权责任或结果由您自己承担，由此造成的活动方的损失，包括但不限于直接损失和可得利益损失，以及活动方为维权而进行的必要支出将由您全部承担。</text>
            
            <text class="paragraph">活动方在未经您同意的情况下，不会将您的任何资料以任何方式泄露给任何第三方。当政府司法机关以及校方依照正当程序要求活动方披露个人资料时，我们将根据相关单位的要求或为公共安全的目的提供个人资料。在此情况下的任何披露，活动方均得免责。</text>
            
            <text class="paragraph">本声明未涉及的问题参见国家有关法律法规，当本声明与国家法律法规冲突时，以国家法律法规为准。</text>
            
            <text class="paragraph">本活动的声明以及其修改权、更新权及最终解释权均属武汉大学自强网络文化工作室所有。</text>
          </view>
        </view>

        <!-- 附录二：关于我们 -->
        <view class="section">
          <view class="section-title">附录二：关于我们</view>
          <view class="section-content">
            <text class="paragraph">武汉大学自强网络文化工作室（自强 Studio），是武汉大学党委学生工作部指导的校级学生组织，是华中地区最大的学生互联网团队之一，是教育部授权的"全国高校网络文化工作室" 之一。自强网络文化工作室下设技术开发中心、新闻宣传中心、品牌推广中心、站务管理中心4大中心，共有15个部门。</text>
            
            <text class="paragraph">【专业交换·遇见你】是由自强网络文化工作室主办的活动，旨在帮助有意愿的学生探索陌生学科的知识脉络，参与多元学术思维的碰撞，为转专业或修习双学位的学生储备跨学科认知。本届活动携手武汉大学大学生心理卫生协会，融合线上、线下开展方式，助力有专业交换想法的同学探索新领域。</text>
            
            <text class="paragraph">如有疑问，加入活动QQ群（群号：518568761），工作人员将为你解答。</text>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- 底部导航栏 -->
    <CustomTabBar :current="3" />
  </view>
</template>

<script>
import CustomTabBar from '../../components/CustomTabBar.vue'

export default {
  components: {
    CustomTabBar
  },
  methods: {
    goBack() {
      uni.navigateBack({
        fail: () => {
          uni.reLaunch({ url: '/pages/mine/index' })
        }
      })
    }
  }
}
</script>

<style scoped>
.about-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #F7E8FE 0%, #FFFEFF 100%);
  padding-bottom: 112rpx; /* 为TabBar留出空间 */
}

/* 顶部导航 */
.page-header {
  background: linear-gradient(89.97deg, #A100FE 0.03%, #FDB9E7 99.97%);
  padding: 88rpx 0 40rpx 0;
}

.nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32rpx;
  height: 80rpx;
}

.nav-left {
  width: 80rpx;
  height: 80rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-arrow {
  font-size: 48rpx;
  color: #FFFFFF;
  font-weight: 300;
}

.page-title {
  font-size: 32rpx;
  color: #FFFFFF;
  font-weight: 500;
}

.nav-right {
  width: 80rpx;
}

/* 内容区域 */
.content-area {
  width: 100%;
  height: calc(100vh - 200rpx);
  padding: 40rpx 32rpx;
  box-sizing: border-box;
}

.content-container {
  padding-bottom: 40rpx;
}

/* 章节样式 */
.section {
  margin-bottom: 60rpx;
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 40rpx 32rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
}

.section-title {
  font-size: 36rpx;
  font-weight: 600;
  color: #333333;
  margin-bottom: 32rpx;
  padding-bottom: 20rpx;
  border-bottom: 2rpx solid #F0F0F0;
}

.section-content {
  display: flex;
  flex-direction: column;
}

.paragraph {
  font-size: 28rpx;
  line-height: 1.8;
  color: #666666;
  margin-bottom: 24rpx;
  text-align: justify;
  word-break: break-all;
}

.paragraph:last-child {
  margin-bottom: 0;
}
</style>