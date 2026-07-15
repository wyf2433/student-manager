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
    classes: [],
    classIndex: 0,
    students: [],
    importing: false,
  },

  onLoad() {
    this.loadClasses()
  },

  async loadClasses() {
    try {
      const res = await api.get('/classes')
      const data = res.data || {}
      const classes = data.items || []
      this.setData({ classes })
      if (classes.length === 0) {
        wx.showToast({ title: '请先创建班级', icon: 'none' })
      }
    } catch (err) {
      console.error('加载班级失败', err)
    }
  },

  onClassChange(e) {
    this.setData({ classIndex: e.detail.value })
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

  onSubjectChange(e) {
    const index = e.detail.value
    this.setData({
      subjectIndex: index,
      selectedSubject: this.data.previewData.subjects[index],
    })
  },

  async confirmImport() {
    const { examName, selectedSubject, previewData, classes, classIndex } = this.data
    if (!examName.trim()) {
      wx.showToast({ title: '请输入考试名称', icon: 'none' })
      return
    }
    if (classes.length === 0) {
      wx.showToast({ title: '请先创建班级', icon: 'none' })
      return
    }

    const students = (previewData.students || []).map(s => ({
      name: s.name,
      score: s.scores[selectedSubject],
    }))

    if (students.length === 0) {
      wx.showToast({ title: '无有效数据', icon: 'none' })
      return
    }

    this.setData({ importing: true })
    try {
      const res = await api.post('/scores/import/confirm', {
        exam_name: examName.trim(),
        subject: selectedSubject,
        class_id: classes[classIndex].id,
        students,
      })

      const imported = res.data.imported_count
      const autoCreated = res.data.auto_created_students || 0
      let msg = `已导入${imported}条成绩`
      if (autoCreated > 0) {
        msg += `\n自动创建${autoCreated}名学生(学号待补)`
      }
      wx.showModal({ title: '导入完成', content: msg, showCancel: false })
      this.setData({ importing: false })
      setTimeout(() => wx.navigateBack(), 1500)
    } catch (err) {
      wx.showToast({ title: '导入失败', icon: 'none' })
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
