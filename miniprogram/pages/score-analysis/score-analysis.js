const api = require('../../utils/api.js')

const SUBJECT_EMOJI = {
  '物理': '🔬', '语文': '📚', '数学': '➗', '英语': '🔤',
  '道法': '⚖️', '历史': '📜', '地理': '🌍', '生物': '🧬',
  '体育': '⚽', '音乐': '🎵', '美术': '🎨', '信息技术': '💻',
  '化学': '🧪', '科学': '🔭',
}

Page({
  data: {
    exams: [],
    loading: true,
  },

  onShow() {
    this.loadExams()
  },

  async loadExams() {
    this.setData({ loading: true })
    try {
      const res = await api.get('/scores/exams')
      const exams = (res.data.items || []).map(name => ({
        name,
        emoji: '📊',
      }))
      this.setData({ exams, loading: false })
    } catch (err) {
      console.error('加载失败', err)
      this.setData({ loading: false })
    }
  },

  goExamDetail(e) {
    const examName = e.currentTarget.dataset.name
    wx.navigateTo({
      url: `/pages/exam-detail/exam-detail?exam_name=${encodeURIComponent(examName)}`,
    })
  },

  goImport() {
    wx.navigateTo({ url: '/pages/score-import/score-import' })
  },

  onPullDownRefresh() {
    this.loadExams().then(() => wx.stopPullDownRefresh())
  },
})
