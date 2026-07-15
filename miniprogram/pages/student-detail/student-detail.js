const api = require('../../utils/api.js')

const TYPE_LABELS = {
  attendance: '考勤',
  leave: '请假',
  score: '加扣分',
}

const RECORD_EMOJI = {
  attendance: '✅',
  leave: '🚪',
  score: '⭐',
}

function avatarIndex(name) {
  if (!name) return 0
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = hash + name.charCodeAt(i)
  }
  return hash % 8
}

Page({
  data: {
    student: null,
    records: [],
    scores: [],
    notes: [],
    trend: null,
    trendSubjects: [],
    currentSubject: '',
    studentId: null,
    loading: true,
    avatarIdx: 0,
    typeLabels: TYPE_LABELS,
    recordEmojis: RECORD_EMOJI,
    showAction: false,
    actionType: '',
    actionContent: '',
    actionValue: '',
    noteContent: '',
    saving: false,
  },

  onLoad(options) {
    this.setData({ studentId: options.id })
    this.loadData()
  },

  async loadData() {
    this.setData({ loading: true })
    try {
      const [studentRes, recordsRes, scoresRes, notesRes, trendRes] = await Promise.all([
        api.get('/students/' + this.data.studentId),
        api.get('/records', { student_id: this.data.studentId }),
        api.get('/scores', { student_id: this.data.studentId }),
        api.get('/notes', { student_id: this.data.studentId }),
        api.get('/scores/analysis/trend', { student_id: this.data.studentId, subject: this.data.currentSubject || undefined }).catch(() => ({ data: null })),
      ])
      const student = studentRes.data
      const records = ((recordsRes.data || {}).items || []).map(r => ({
        ...r,
        emoji: RECORD_EMOJI[r.type] || '📌',
        dotClass: r.type === 'attendance' ? 'dot-green' : r.type === 'leave' ? 'dot-orange' : 'dot-red',
        tagClass: r.type === 'attendance' ? 'tag-green' : r.type === 'leave' ? 'tag-orange' : 'tag-red',
      }))

      const trend = trendRes.data
      const trendSubjects = (trend && trend.subjects) || []
      const currentSubject = (trend && trend.current_subject) || ''

      if (trend && trend.exams && trend.exams.length > 0) {
        trend.exams = this._buildChartPoints(trend.exams)
      }

      this.setData({
        student: student,
        avatarIdx: avatarIndex(student.name),
        records: records,
        scores: ((scoresRes.data || {}).items || []),
        notes: ((notesRes.data || {}).items || []),
        trend: trend,
        trendSubjects: trendSubjects,
        currentSubject: currentSubject,
        loading: false,
      })
    } catch (err) {
      console.error('加载失败', err)
      this.setData({ loading: false })
    }
  },

  _buildChartPoints(exams) {
    const n = exams.length
    if (n === 0) return exams
    const fullScore = exams[0].full_score || 100
    const pts = []
    for (let i = 0; i < n; i++) {
      pts.push({
        ...exams[i],
        xPercent: n === 1 ? 50 : i / (n - 1) * 100,
        yPercent: exams[i].score / fullScore * 100,
        classYPercent: exams[i].class_avg ? exams[i].class_avg / fullScore * 100 : null,
      })
    }
    const segments = []
    for (let i = 0; i < n - 1; i++) {
      const x1 = pts[i].xPercent
      const y1 = 100 - pts[i].yPercent
      const x2 = pts[i + 1].xPercent
      const y2 = 100 - pts[i + 1].yPercent
      const dx = x2 - x1
      const dy = y2 - y1
      const len = Math.sqrt(dx * dx + dy * dy)
      const angle = Math.atan2(dy, dx) * 180 / Math.PI
      segments.push({ left: x1, top: y1, length: len, angle })
    }
    pts.lineSegments = segments
    return pts
  },

  onTrendSubjectChange(e) {
    this.setData({ currentSubject: this.data.trendSubjects[e.detail.value] }, () => {
      this.loadTrend()
    })
  },

  async loadTrend() {
    try {
      const res = await api.get('/scores/analysis/trend', {
        student_id: this.data.studentId,
        subject: this.data.currentSubject || undefined,
      })
      const trend = res.data
      if (trend && trend.exams && trend.exams.length > 0) {
        trend.exams = this._buildChartPoints(trend.exams)
      }
      this.setData({ trend: trend })
    } catch (err) {
      console.error('加载趋势失败', err)
    }
  },

  showActionSheet() {
    wx.showActionSheet({
      itemList: ['📅 记考勤', '🚪 记请假', '⭐ 加扣分'],
      success: (res) => {
        const types = ['attendance', 'leave', 'score']
        this.setData({
          showAction: true,
          actionType: types[res.tapIndex],
          actionContent: '',
          actionValue: '',
        })
      },
    })
  },

  quickAction(e) {
    const type = e.currentTarget.dataset.type
    this.setData({
      showAction: true,
      actionType: type,
      actionContent: '',
      actionValue: '',
    })
  },

  closeAction() {
    this.setData({ showAction: false })
  },

  onActionContentInput(e) {
    this.setData({ actionContent: e.detail.value })
  },

  onActionValueInput(e) {
    this.setData({ actionValue: e.detail.value })
  },

  async saveAction() {
    const { actionType, actionContent, actionValue } = this.data
    const body = {
      student_id: parseInt(this.data.studentId),
      type: actionType,
      content: actionContent.trim() || null,
    }
    if (actionType === 'score') {
      const v = parseFloat(actionValue)
      if (isNaN(v)) {
        wx.showToast({ title: '请输入分数', icon: 'none' })
        return
      }
      body.value = v
    }
    this.setData({ saving: true })
    try {
      await api.post('/records', body)
      wx.showToast({ title: '已记录', icon: 'success' })
      this.setData({ showAction: false, saving: false })
      this.loadData()
    } catch (err) {
      wx.showToast({ title: '保存失败', icon: 'none' })
      this.setData({ saving: false })
    }
  },

  onNoteInput(e) {
    this.setData({ noteContent: e.detail.value })
  },

  async saveNote() {
    const content = this.data.noteContent.trim()
    if (!content) {
      wx.showToast({ title: '请输入内容', icon: 'none' })
      return
    }
    try {
      await api.post('/notes', { content, student_id: parseInt(this.data.studentId) })
      this.setData({ noteContent: '' })
      wx.showToast({ title: '已记录', icon: 'success' })
      this.loadData()
    } catch (err) {
      wx.showToast({ title: '保存失败', icon: 'none' })
    }
  },

  async deleteRecordSwipe(e) {
    const id = e.currentTarget.dataset.id
    const res = await wx.showModal({ title: '确认删除?' })
    if (res.confirm) {
      try {
        await api.delete('/records/' + id)
        wx.showToast({ title: '已删除', icon: 'success' })
        this.loadData()
      } catch (err) {
        wx.showToast({ title: '删除失败', icon: 'none' })
        this.loadData()
      }
    } else {
      this.loadData()
    }
  },

  async deleteNoteSwipe(e) {
    const id = e.currentTarget.dataset.id
    const res = await wx.showModal({ title: '确认删除?' })
    if (res.confirm) {
      try {
        await api.delete('/notes/' + id)
        wx.showToast({ title: '已删除', icon: 'success' })
        this.loadData()
      } catch (err) {
        wx.showToast({ title: '删除失败', icon: 'none' })
        this.loadData()
      }
    } else {
      this.loadData()
    }
  },

  onPullDownRefresh() {
    this.loadData().then(() => wx.stopPullDownRefresh())
  },
})
