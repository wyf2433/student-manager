const api = require('../../utils/api.js')

Page({
  data: {
    classes: [],
    classIndex: 0,
    step: 1,
    filePath: '',
    fileName: '',
    previewStudents: [],
    importing: false,
    uploading: false,
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
      const res = await api.upload('/students/import/preview', this.data.filePath)
      const students = (res.data && res.data.students) || []
      this.setData({
        previewStudents: students,
        step: 2,
        uploading: false,
      })
    } catch (err) {
      const msg = (err && err.detail) || (err && err.message) || '解析失败'
      wx.showToast({ title: msg, icon: 'none' })
      this.setData({ uploading: false, filePath: '', fileName: '' })
    }
  },

  async confirmImport() {
    const { classes, classIndex, previewStudents } = this.data
    if (classes.length === 0) {
      wx.showToast({ title: '请先创建班级', icon: 'none' })
      return
    }

    this.setData({ importing: true })
    try {
      const res = await api.post('/students/import/confirm', {
        class_id: classes[classIndex].id,
        students: previewStudents,
      })
      const count = res.data.imported_count
      wx.showToast({ title: `已导入${count}人`, icon: 'success' })
      setTimeout(() => wx.navigateBack(), 1000)
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
      previewStudents: [],
    })
  },
})
