const api = require('../../utils/api.js')

const FULL_SCORE_DEFAULTS = {
  '初一': { '语文': 150, '数学': 150, '英语': 150, '物理': 0, '政治': 50, '历史': 50, '地理': 30, '生物': 30, '化学': 0 },
  '初二': { '语文': 150, '数学': 150, '英语': 150, '物理': 100, '政治': 50, '历史': 50, '地理': 30, '生物': 30, '化学': 0 },
  '初三': { '语文': 150, '数学': 150, '英语': 150, '物理': 90, '政治': 50, '历史': 50, '地理': 30, '生物': 30, '化学': 100 },
}

function getFullScoreDefaults(grade, subjects) {
  const map = FULL_SCORE_DEFAULTS[grade] || FULL_SCORE_DEFAULTS['初二']
  const result = {}
  for (const s of subjects) {
    result[s] = map[s] || 100
  }
  return result
}

Page({
  data: {
    step: 1,
    filePath: '',
    fileName: '',
    uploading: false,
    previewData: null,
    examName: '',
    subjects: [],
    fullScores: {},
    gradePrefix: '',
    hasClassColumn: false,
    hasGradeColumn: false,
    importing: false,
  },

  onLoad() {
    const today = new Date()
    const grade = today.getFullYear() - 2024 + 7
    const gradeMap = { 7: '初一', 8: '初二', 9: '初三' }
    this.setData({ gradePrefix: gradeMap[grade] || '初二' })
  },

  chooseFile() {
    wx.chooseMessageFile({
      count: 1,
      type: 'file',
      extension: ['xlsx', 'xls'],
      success: (res) => {
        const file = res.tempFiles[0]
        if (file.size > 10 * 1024 * 1024) {
          wx.showToast({ title: '文件不能超过10MB', icon: 'none' })
          return
        }
        this.setData({
          filePath: file.path,
          fileName: file.name,
        })
        this.uploadPreview()
      },
      fail: () => {},
    })
  },

  async uploadPreview() {
    this.setData({ uploading: true })
    try {
      const res = await api.upload('/scores/import/preview', this.data.filePath)
      const data = res.data || {}
      const subjects = data.subjects || []
      const detectedGrade = (data.has_grade_column && data.students[0] && data.students[0].grade)
        ? this._normalizeGrade(data.students[0].grade) : this.data.gradePrefix
      const fullScores = getFullScoreDefaults(detectedGrade, subjects)
      this.setData({
        previewData: data,
        examName: data.exam_name || '',
        subjects,
        fullScores,
        hasClassColumn: data.has_class_column || false,
        hasGradeColumn: data.has_grade_column || false,
        gradePrefix: detectedGrade,
        step: 2,
        uploading: false,
      })
    } catch (err) {
      const msg = (err && err.detail) || (err && err.message) || '解析失败'
      wx.showToast({ title: msg, icon: 'none' })
      this.setData({ uploading: false, filePath: '', fileName: '' })
    }
  },

  _normalizeGrade(raw) {
    if (!raw) return '初二'
    const s = String(raw).trim()
    const map = { '7': '初一', '8': '初二', '9': '初三', '七': '初一', '八': '初二', '九': '初三' }
    if (map[s]) return map[s]
    for (const k in map) {
      if (s.indexOf(k) >= 0) return map[k]
    }
    return '初二'
  },

  onExamInput(e) {
    this.setData({ examName: e.detail.value })
  },

  onGradeInput(e) {
    this.setData({ gradePrefix: e.detail.value })
  },

  onFullScoreInput(e) {
    const subject = e.currentTarget.dataset.subject
    const val = e.detail.value
    this.setData({ ['fullScores.' + subject]: val })
  },

  async confirmImport() {
    const { examName, previewData, gradePrefix, hasClassColumn, hasGradeColumn, subjects, fullScores } = this.data
    if (!examName.trim()) {
      wx.showToast({ title: '请输入考试名称', icon: 'none' })
      return
    }
    if (hasClassColumn && !hasGradeColumn && !gradePrefix.trim()) {
      wx.showToast({ title: '请输入年级前缀', icon: 'none' })
      return
    }

    const fullScoresNum = {}
    for (const s of subjects) {
      const v = parseFloat(fullScores[s])
      if (isNaN(v) || v <= 0) {
        wx.showToast({ title: s + ' 满分无效', icon: 'none' })
        return
      }
      fullScoresNum[s] = v
    }

    const students = (previewData.students || []).map(s => {
      const item = { name: s.name, scores: {} }
      for (const subj of subjects) {
        if (s.scores[subj] !== null && s.scores[subj] !== undefined) {
          item.scores[subj] = s.scores[subj]
        }
      }
      if (hasClassColumn && s.class_name) {
        item.class_name = s.class_name
      }
      if (hasGradeColumn && s.grade) {
        item.grade = s.grade
      }
      return item
    })

    if (students.length === 0) {
      wx.showToast({ title: '无有效数据', icon: 'none' })
      return
    }

    this.setData({ importing: true })
    try {
      const body = {
        exam_name: examName.trim(),
        full_scores: fullScoresNum,
        students,
      }
      if (hasClassColumn && !hasGradeColumn && gradePrefix.trim()) {
        body.grade_prefix = gradePrefix.trim()
      }

      const res = await api.post('/scores/import/confirm', body)

      const imported = res.data.imported_count
      const autoStudents = res.data.auto_created_students || 0
      const autoClasses = res.data.auto_created_classes || 0
      let msg = `已导入 ${imported} 条成绩`
      if (autoClasses > 0) {
        msg += `\n自动创建 ${autoClasses} 个班级`
      }
      if (autoStudents > 0) {
        msg += `\n自动创建 ${autoStudents} 名学生`
      }
      wx.showModal({ title: '导入完成', content: msg, showCancel: false })
      this.setData({ importing: false })
      setTimeout(() => wx.navigateBack(), 1500)
    } catch (err) {
      const msg = (err && err.detail) || '导入失败'
      wx.showToast({ title: msg, icon: 'none' })
      this.setData({ importing: false })
    }
  },

  reset() {
    this.setData({
      step: 1,
      filePath: '',
      fileName: '',
      previewData: null,
      examName: '',
      subjects: [],
      fullScores: {},
    })
  },
})
