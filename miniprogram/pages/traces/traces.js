const api = require('../../utils/api.js')

const TYPE_OPTIONS = [
  { value: '', label: '📦 全部' },
  { value: 'classroom_discipline', label: '📏 课堂纪律' },
  { value: 'experiment_record', label: '🔬 实验记录' },
  { value: 'homework_feedback', label: '📝 作业反馈' },
  { value: 'exam_analysis', label: '📊 考试分析' },
  { value: 'student_talk', label: '💬 学生谈话' },
  { value: 'parent_communication', label: '📞 家长沟通' },
  { value: 'other', label: '📎 其他' },
]

const TYPE_LABELS = {
  classroom_discipline: '课堂纪律',
  experiment_record: '实验课记录',
  homework_feedback: '作业反馈',
  exam_analysis: '考试分析',
  student_talk: '学生谈话',
  parent_communication: '家长沟通',
  other: '其他',
}

const TYPE_EMOJI = {
  classroom_discipline: '📏',
  experiment_record: '🔬',
  homework_feedback: '📝',
  exam_analysis: '📊',
  student_talk: '💬',
  parent_communication: '📞',
  other: '📎',
}

Page({
  data: {
    traces: [],
    filterType: '',
    loading: true,
    typeOptions: TYPE_OPTIONS,
    typeLabels: TYPE_LABELS,
    typeEmojis: TYPE_EMOJI,
  },

  onShow() {
    this.loadTraces()
  },

  async loadTraces() {
    this.setData({ loading: true })
    try {
      const params = {}
      if (this.data.filterType) params.type = this.data.filterType
      const res = await api.get('/traces', params)
      const data = res.data || {}
      const traces = (data.items || []).map(t => ({
        ...t,
        emoji: TYPE_EMOJI[t.type] || '📎',
      }))
      this.setData({
        traces: traces,
        loading: false,
      })
    } catch (err) {
      console.error('加载留痕失败', err)
      this.setData({ loading: false })
    }
  },

  onFilterChange(e) {
    const type = e.detail.value
    this.setData({ filterType: type }, () => {
      this.loadTraces()
    })
  },

  goAdd() {
    const type = this.data.filterType || ''
    wx.navigateTo({ url: '/pages/trace-add/trace-add' + (type ? '?type=' + type : '') })
  },

  async onDeleteSwipe(e) {
    const id = e.currentTarget.dataset.id
    const res = await wx.showModal({ title: '确认删除?' })
    if (res.confirm) {
      try {
        await api.delete('/traces/' + id)
        wx.showToast({ title: '已删除', icon: 'success' })
        this.loadTraces()
      } catch (err) {
        wx.showToast({ title: '删除失败', icon: 'none' })
        this.loadTraces()
      }
    } else {
      this.loadTraces()
    }
  },

  previewImage(e) {
    const { urls, current } = e.currentTarget.dataset
    const fullUrls = urls.map(u => 'http://47.239.25.178' + u)
    wx.previewImage({
      current: 'http://47.239.25.178' + current,
      urls: fullUrls,
    })
  },

  onPullDownRefresh() {
    this.loadTraces().then(() => wx.stopPullDownRefresh())
  },
})
