const api = require('../../utils/api.js')

const STATUS_FLOW = ['active', 'collected', 'graded']
const STATUS_LABELS = { active: '进行中', collected: '已收', graded: '已改' }
const TYPE_LABELS = {
  daily: '日常作业',
  experiment_report: '实验报告',
  review: '复习提纲',
  exam: '试卷',
}

Page({
  data: {
    homework: [],
    classes: [],
    filterClassId: '',
    filterStatus: '',
    loading: true,
    statusLabels: STATUS_LABELS,
    typeLabels: TYPE_LABELS,
    statusFilters: [
      { value: '', label: '全部' },
      { value: 'active', label: '进行中' },
      { value: 'collected', label: '已收' },
      { value: 'graded', label: '已改' },
    ],
  },

  onShow() {
    this.loadClasses().then(() => this.loadHomework())
  },

  async loadClasses() {
    try {
      const res = await api.get('/classes')
      const data = res.data || {}
      this.setData({ classes: data.items || [] })
    } catch (err) {
      console.error('加载班级失败', err)
    }
  },

  async loadHomework() {
    this.setData({ loading: true })
    try {
      const params = {}
      if (this.data.filterClassId) params.class_id = this.data.filterClassId
      if (this.data.filterStatus) params.status = this.data.filterStatus
      const res = await api.get('/homework', params)
      const data = res.data || {}
      this.setData({
        homework: data.items || [],
        loading: false,
      })
    } catch (err) {
      console.error('加载作业失败', err)
      this.setData({ loading: false })
    }
  },

  onStatusTap(e) {
    const status = e.currentTarget.dataset.status
    this.setData({ filterStatus: status }, () => this.loadHomework())
  },

  async onStatusChange(e) {
    const id = e.currentTarget.dataset.id
    const current = e.currentTarget.dataset.status
    const idx = STATUS_FLOW.indexOf(current)
    const next = STATUS_FLOW[(idx + 1) % STATUS_FLOW.length]
    try {
      await api.patch('/homework/' + id + '/status', { status: next })
      wx.showToast({ title: STATUS_LABELS[next], icon: 'none' })
      this.loadHomework()
    } catch (err) {
      wx.showToast({ title: '操作失败', icon: 'none' })
    }
  },

  goAdd() {
    wx.navigateTo({ url: '/pages/homework-add/homework-add' })
  },

  async onDelete(e) {
    const id = e.currentTarget.dataset.id
    const res = await wx.showModal({ title: '确认删除?' })
    if (res.confirm) {
      try {
        await api.delete('/homework/' + id)
        wx.showToast({ title: '已删除', icon: 'success' })
        this.loadHomework()
      } catch (err) {
        wx.showToast({ title: '删除失败', icon: 'none' })
      }
    }
  },

  onPullDownRefresh() {
    this.loadHomework().then(() => wx.stopPullDownRefresh())
  },
})
