const api = require('../../utils/api.js')

Page({
  data: {
    step: 1,
    filePath: '',
    fileName: '',
    uploading: false,
    previewData: null,
    examName: '',
    selectedSubject: '',
    subjectIndex: 0,
    gradePrefix: '',
    hasClassColumn: false,
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
      this.setData({
        previewData: data,
        examName: data.exam_name || '',
        selectedSubject: (data.subjects || [])[0] || '',
        subjectIndex: 0,
        hasClassColumn: data.has_class_column || false,
        step: 2,
        uploading: false,
      })
    } catch (err) {
      const msg = (err && err.detail) || (err && err.message) || '解析失败'
      wx.showToast({ title: msg, icon: 'none' })
      this.setData({ uploading: false, filePath: '', fileName: '' })
    }
  },

  onExamInput(e) {
    this.setData({ examName: e.detail.value })
  },

  onGradeInput(e) {
    this.setData({ gradePrefix: e.detail.value })
  },

  onSubjectChange(e) {
    const index = e.detail.value
    this.setData({
      subjectIndex: index,
      selectedSubject: this.data.previewData.subjects[index],
    })
  },

  async confirmImport() {
    const { examName, selectedSubject, previewData, gradePrefix, hasClassColumn } = this.data
    if (!examName.trim()) {
      wx.showToast({ title: '请输入考试名称', icon: 'none' })
      return
    }
    if (hasClassColumn && !gradePrefix.trim()) {
      wx.showToast({ title: '请输入年级前缀', icon: 'none' })
      return
    }

    const students = (previewData.students || []).map(s => {
      const item = { name: s.name, score: s.scores[selectedSubject] }
      if (hasClassColumn && s.class_name) {
        item.class_name = s.class_name
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
        subject: selectedSubject,
        students,
      }
      if (hasClassColumn && gradePrefix.trim()) {
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
      selectedSubject: '',
    })
  },
})
