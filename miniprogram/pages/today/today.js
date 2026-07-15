const api = require('../../utils/api.js')

const TYPE_LABELS = {
  attendance: '考勤',
  leave: '请假',
  score: '加扣分',
  note: '速记',
}

Page({
  data: {
    overview: null,
    recent: [],
    todaySchedule: [],
    todayHomework: [],
    loading: true,
    quickNote: '',
  },

  onShow() {
    this.loadData()
  },

  async loadData() {
    this.setData({ loading: true })
    try {
      const [overviewRes, recentRes, scheduleRes, homeworkRes] = await Promise.all([
        api.get('/dashboard/today'),
        api.get('/dashboard/recent'),
        api.get('/schedule/today'),
        api.get('/homework/today'),
      ])
      const recentData = recentRes.data || {}
      const items = (recentData.items || []).map(item => {
        const type = item.source === 'note' ? 'note' : item.sub_type
        return {
          id: item.id,
          type: type,
          type_label: TYPE_LABELS[type] || type,
          summary: item.content || '',
          time_label: item.created_at || '',
        }
      })
      const scheduleData = scheduleRes.data || {}
      const homeworkData = homeworkRes.data || {}
      this.setData({
        overview: overviewRes.data,
        recent: items,
        todaySchedule: scheduleData.items || [],
        todayHomework: homeworkData.items || [],
        loading: false,
      })
    } catch (err) {
      console.error('加载失败', err)
      this.setData({ loading: false })
      wx.showToast({ title: '加载失败', icon: 'none' })
    }
  },

  onNoteInput(e) {
    this.setData({ quickNote: e.detail.value })
  },

  async saveNote() {
    const content = this.data.quickNote.trim()
    if (!content) {
      wx.showToast({ title: '请输入内容', icon: 'none' })
      return
    }
    try {
      await api.post('/notes', { content })
      this.setData({ quickNote: '' })
      wx.showToast({ title: '已记录', icon: 'success' })
      this.loadData()
    } catch (err) {
      wx.showToast({ title: '保存失败', icon: 'none' })
    }
  },

  goSchedule() {
    wx.navigateTo({ url: '/pages/schedule/schedule' })
  },

  goHomework() {
    wx.navigateTo({ url: '/pages/homework/homework' })
  },

  onPullDownRefresh() {
    this.loadData().then(() => wx.stopPullDownRefresh())
  },
})
