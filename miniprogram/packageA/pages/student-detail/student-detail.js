const api = require('../../../utils/api.js')
const echarts = require('../../ec-canvas/echarts.js')
const app = getApp()

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

let chartInstance = null

function initChart(canvas, width, height, dpr) {
  const chart = echarts.init(canvas, null, { width, height, devicePixelRatio: dpr })
  canvas.setChart(chart)
  chartInstance = chart
  const pages = getCurrentPages()
  const cur = pages[pages.length - 1]
  if (cur) cur._chartReady = true
  return chart
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
    showChart: false,
    ec: { onInit: initChart },
  },

  onLoad(options) {
    this._chartReady = false
    this._renderRetry = 0
    this.setData({ studentId: options.id })
    this.loadData()
  },

  onUnload() {
    chartInstance = null
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

      const trendExams = this._processExams(trend)

      this.setData({
        student: student,
        avatarIdx: avatarIndex(student.name),
        records: records,
        scores: ((scoresRes.data || {}).items || []),
        scoreGroups: this._groupScores(((scoresRes.data || {}).items || [])),
        notes: ((notesRes.data || {}).items || []),
        trend: trend,
        trendExams: trendExams,
        trendSubjects: trendSubjects,
        currentSubject: currentSubject,
        loading: false,
      }, () => {
        if (trendExams.length > 0) {
          setTimeout(() => {
            this.setData({ showChart: true }, () => {
              this._renderChart()
            })
          }, 300)
        }
      })
    } catch (err) {
      console.error('加载失败', err)
      this.setData({ loading: false })
    }
  },

  _groupScores(scores) {
    const map = {}
    const order = []
    for (const s of scores) {
      if (!map[s.exam_name]) {
        map[s.exam_name] = { exam_name: s.exam_name, subjects: [] }
        order.push(s.exam_name)
      }
      map[s.exam_name].subjects.push(s)
    }
    return order.map(name => map[name])
  },

  _processExams(trend) {
    if (!trend || !trend.exams || trend.exams.length === 0) return []
    return trend.exams.map(e => {
      let changeLabel = ''
      let changeClass = 'tag-gray'
      if (e.change !== null && e.change !== undefined) {
        if (e.change > 0) {
          changeLabel = '↑' + e.change
          changeClass = 'tag-green'
        } else if (e.change < 0) {
          changeLabel = '↓' + Math.abs(e.change)
          changeClass = 'tag-red'
        } else {
          changeLabel = '—'
        }
      }
      return { ...e, changeLabel, changeClass }
    })
  },

  _renderChart() {
    const exams = this.data.trendExams
    if (!exams || exams.length === 0) return

    if (!this._chartReady || !chartInstance) {
      if (this._renderRetry < 15) {
        this._renderRetry++
        setTimeout(() => this._renderChart(), 200)
      }
      return
    }

    const xData = exams.map(e => e.exam_name)
    const studentScores = exams.map(e => e.score)
    const classAvgs = exams.map(e => e.class_avg || null)
    const fullScore = exams[0].full_score || 100

    const hasClassAvg = classAvgs.some(v => v !== null)

    const option = {
      tooltip: { trigger: 'axis' },
      legend: {
        data: hasClassAvg ? ['本人成绩', '班级均分'] : ['本人成绩'],
        bottom: 0,
        textStyle: { fontSize: 12 },
      },
      grid: { left: 40, right: 20, top: 20, bottom: 40 },
      xAxis: {
        type: 'category',
        data: xData,
        axisLabel: { fontSize: 11, rotate: xData.length > 3 ? 15 : 0 },
      },
      yAxis: {
        type: 'value',
        min: 0,
        max: fullScore,
        axisLabel: { fontSize: 11 },
      },
      animation: false,
      series: [
        {
          name: '本人成绩',
          type: 'line',
          data: studentScores,
          smooth: true,
          symbol: 'circle',
          symbolSize: 8,
          itemStyle: { color: '#6366F1' },
          lineStyle: { color: '#6366F1', width: 3 },
          label: { show: true, position: 'top', fontSize: 11, fontWeight: 'bold' },
          areaStyle: {
            color: {
              type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(99,102,241,0.25)' },
                { offset: 1, color: 'rgba(99,102,241,0.02)' },
              ],
            },
          },
        },
      ],
    }

    if (hasClassAvg) {
      option.series.push({
        name: '班级均分',
        type: 'line',
        data: classAvgs,
        smooth: true,
        symbol: 'diamond',
        symbolSize: 6,
        itemStyle: { color: '#9CA3AF' },
        lineStyle: { color: '#9CA3AF', width: 2, type: 'dashed' },
        label: { show: false },
      })
    }

    chartInstance.clear()
    chartInstance.setOption(option)
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
      const trendExams = this._processExams(trend)
      this.setData({ trend: trend, trendExams: trendExams }, () => {
        if (trendExams.length > 0) {
          this._renderChart()
        }
      })
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
      app.globalData.dirty.records = true
      app.globalData.dirty.today = true
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
      app.globalData.dirty.notes = true
      app.globalData.dirty.today = true
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
        app.globalData.dirty.records = true
        app.globalData.dirty.today = true
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
        app.globalData.dirty.notes = true
        app.globalData.dirty.today = true
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
