App({
  onLaunch() {
    if (!wx.cloud) {
      console.error('请使用 2.2.3 或以上的基础库以使用云能力')
    } else {
      wx.cloud.init({
        env: 'cloud1-d3gde4cs1fa50b701',
        traceUser: true,
      })
    }
  },
  globalData: {
    currentClassId: null,
    dirty: {},
  },
})
