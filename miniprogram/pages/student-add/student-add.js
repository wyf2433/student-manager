const api = require('../../utils/api.js')
const app = getApp()

Page({
  data: {
    classes: [],
    classIndex: 0,
    name: '',
    studentNo: '',
    gender: '男',
    saving: false,
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

  onNameInput(e) {
    this.setData({ name: e.detail.value })
  },

  onNoInput(e) {
    this.setData({ studentNo: e.detail.value })
  },

  onGenderChange(e) {
    this.setData({ gender: e.detail.value })
  },

  async onSave() {
    const { classes, classIndex, name, studentNo, gender } = this.data
    if (classes.length === 0) {
      wx.showToast({ title: '请先创建班级', icon: 'none' })
      return
    }
    if (!name.trim()) {
      wx.showToast({ title: '请输入姓名', icon: 'none' })
      return
    }

    this.setData({ saving: true })
    try {
      await api.post('/students', {
        class_id: classes[classIndex].id,
        name: name.trim(),
        student_no: studentNo.trim() || null,
        gender: gender,
      })
      wx.showToast({ title: '已添加', icon: 'success' })
      app.globalData.dirty.students = true
      setTimeout(() => wx.navigateBack(), 800)
    } catch (err) {
      wx.showToast({ title: '保存失败', icon: 'none' })
      this.setData({ saving: false })
    }
  },
})
