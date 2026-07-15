const api = require('../../utils/api.js')

const DIFFICULTY_EMOJI = {
  easy: '🟢',
  moderate: '🟡',
  hard: '🟠',
  very_hard: '🔴',
}

const RANGE_COLORS = ['tag-red', 'tag-orange', 'tag-blue', 'tag-green', 'tag-purple']

Page({
  data: {
    examName: '',
    subjects: [],
    selectedSubject: '',
    subjectIndex: 0,
    analysis: null,
    ranking: null,
    activeTab: 0,
    loading: true,
    rangeColors: RANGE_COLORS,
    diffEmoji: DIFFICULTY_EMOJI,
    maxRangePercent: 0,
  },

  onLoad(options) {
    const examName = decodeURIComponent(options.exam_name || '')
    this.setData({ examName })
    this.loadSubjects(examName)
  },

  async loadSubjects(examName) {
    try {
      const res = await api.get(`/scores/exams/${encodeURIComponent(examName)}/subjects`)
      const subjects = res.data.items || []
      if (subjects.length === 0) {
        wx.showToast({ title: '无成绩数据', icon: 'none' })
        this.setData({ loading: false })
        return
      }
      this.setData({
        subjects,
        selectedSubject: subjects[0],
        subjectIndex: 0,
      })
      this.loadAnalysis()
    } catch (err) {
      console.error('加载科目失败', err)
      this.setData({ loading: false })
    }
  },

  onSubjectChange(e) {
    const index = e.detail.value
    this.setData({
      subjectIndex: index,
      selectedSubject: this.data.subjects[index],
    })
    this.loadAnalysis()
  },

  async loadAnalysis() {
    this.setData({ loading: true })
    const { examName, selectedSubject } = this.data
    try {
      const [analysisRes, rankingRes] = await Promise.all([
        api.get('/scores/analysis/exam', {
          exam_name: examName,
          subject: selectedSubject,
        }),
        api.get('/scores/analysis/ranking', {
          exam_name: examName,
          subject: selectedSubject,
        }),
      ])
      const analysis = analysisRes.data
      const ranking = rankingRes.data

      let maxPercent = 0
      if (analysis && analysis.score_ranges) {
        for (const key in analysis.score_ranges) {
          if (analysis.score_ranges[key].percent > maxPercent) {
            maxPercent = analysis.score_ranges[key].percent
          }
        }
      }

      this.setData({
        analysis,
        ranking,
        maxRangePercent: maxPercent,
        loading: false,
      })
    } catch (err) {
      console.error('加载分析失败', err)
      this.setData({ loading: false })
      wx.showToast({ title: '加载失败', icon: 'none' })
    }
  },

  onTabChange(e) {
    this.setData({ activeTab: e.detail.value })
  },

  goStudentDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/student-detail/student-detail?id=${id}` })
  },

  onPullDownRefresh() {
    this.loadAnalysis().then(() => wx.stopPullDownRefresh())
  },
})
