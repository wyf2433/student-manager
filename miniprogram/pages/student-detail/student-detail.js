const api = require('../../utils/api.js')

Page({
  data: {
    student: null,
    records: [],
    studentId: null,
    loading: true,
    typeLabels: {
      attendance: '考勤',
      leave: '请假',
      score: '加扣分',
    },
  },

  onLoad(options) {
    this.setData({ studentId: options.id })
    this.loadData()
  },

  async loadData() {
    this.setData({ loading: true })
    try {
      const [studentRes, recordsRes] = await Promise.all([
        api.get('/students/' + this.data.studentId),
        api.get('/records', { student_id: this.data.studentId }),
      ])
      const recordsData = recordsRes.data || {}
      this.setData({
        student: studentRes.data,
        records: recordsData.items || [],
        loading: false,
      })
    } catch (err) {
      console.error('加载失败', err)
      this.setData({ loading: false })
    }
  },

  onPullDownRefresh() {
    this.loadData().then(() => wx.stopPullDownRefresh())
  },
})
