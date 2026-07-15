const api = require('../../utils/api.js')

const TYPE_LABELS = {
  attendance: '考勤',
  leave: '请假',
  score: '加扣分',
}

Page({
  data: {
    records: [],
    filterType: '',
    loading: true,
    typeLabels: TYPE_LABELS,
    typeFilters: [
      { value: '', label: '全部' },
      { value: 'attendance', label: '考勤' },
      { value: 'leave', label: '请假' },
      { value: 'score', label: '加扣分' },
    ],
  },

  onShow() {
    this.loadRecords()
  },

  async loadRecords() {
    this.setData({ loading: true })
    try {
      const params = {}
      if (this.data.filterType) {
        params.type = this.data.filterType
      }
      const res = await api.get('/records', params)
      const data = res.data || {}
      this.setData({
        records: data.items || [],
        loading: false,
      })
    } catch (err) {
      console.error('加载记录失败', err)
      this.setData({ loading: false })
    }
  },

  onFilterChange(e) {
    const type = e.detail.value
    this.setData({ filterType: type }, () => {
      this.loadRecords()
    })
  },

  goAdd() {
    const type = this.data.filterType || ''
    wx.navigateTo({ url: '/pages/add-record/add-record' + (type ? '?type=' + type : '') })
  },

  async onDeleteSwipe(e) {
    const id = e.currentTarget.dataset.id
    const res = await wx.showModal({ title: '确认删除?', content: '删除后不可恢复' })
    if (res.confirm) {
      try {
        await api.delete('/records/' + id)
        wx.showToast({ title: '已删除', icon: 'success' })
        this.loadRecords()
      } catch (err) {
        wx.showToast({ title: '删除失败', icon: 'none' })
        this.loadRecords()
      }
    } else {
      this.loadRecords()
    }
  },

  onPullDownRefresh() {
    this.loadRecords().then(() => wx.stopPullDownRefresh())
  },
})
