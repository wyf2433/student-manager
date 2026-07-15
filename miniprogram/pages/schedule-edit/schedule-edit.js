const api = require('../../utils/api.js')

Page({
  data: {
    editId: null,
    weekday: 1,
    period: 1,
    subject: '物理',
    className: '',
    saving: false,
  },

  onLoad(options) {
    if (options.id) {
      this.setData({ editId: options.id })
      this.loadSchedule(options.id)
    }
    if (options.weekday) {
      this.setData({ weekday: parseInt(options.weekday) })
    }
  },

  async loadSchedule(id) {
    try {
      const res = await api.get('/schedule')
      const items = (res.data && res.data.items) || []
      const item = items.find(s => s.id == id)
      if (item) {
        this.setData({
          weekday: item.weekday,
          period: item.period,
          subject: item.subject,
          className: item.class_name || '',
        })
      }
    } catch (err) {
      console.error('加载失败', err)
    }
  },

  onWeekdayChange(e) {
    this.setData({ weekday: parseInt(e.detail.value) + 1 })
  },

  onPeriodChange(e) {
    this.setData({ period: parseInt(e.detail.value) + 1 })
  },

  onSubjectInput(e) {
    this.setData({ subject: e.detail.value })
  },

  onClassInput(e) {
    this.setData({ className: e.detail.value })
  },

  async onSave() {
    const { editId, weekday, period, subject, className } = this.data
    if (!subject.trim()) {
      wx.showToast({ title: '请输入科目', icon: 'none' })
      return
    }

    const body = {
      weekday,
      period,
      subject: subject.trim(),
      class_name: className.trim() || null,
    }

    this.setData({ saving: true })
    try {
      if (editId) {
        await api.put('/schedule/' + editId, body)
      } else {
        await api.post('/schedule', body)
      }
      wx.showToast({ title: '已保存', icon: 'success' })
      setTimeout(() => wx.navigateBack(), 800)
    } catch (err) {
      const msg = (err && err.detail) || '保存失败'
      wx.showToast({ title: msg, icon: 'none' })
      this.setData({ saving: false })
    }
  },
})
