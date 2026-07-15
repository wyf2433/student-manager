const api = require('../../utils/api.js')

const TYPE_OPTIONS = [
  { value: 'daily', label: '日常作业' },
  { value: 'experiment_report', label: '实验报告' },
  { value: 'review', label: '复习提纲' },
  { value: 'exam', label: '试卷' },
]

Page({
  data: {
    classes: [],
    classIndex: 0,
    typeOptions: TYPE_OPTIONS,
    typeIndex: 0,
    content: '',
    dueDate: '',
    note: '',
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

  onTypeChange(e) {
    this.setData({ typeIndex: e.detail.value })
  },

  onContentInput(e) {
    this.setData({ content: e.detail.value })
  },

  onDueDateChange(e) {
    this.setData({ dueDate: e.detail.value })
  },

  onNoteInput(e) {
    this.setData({ note: e.detail.value })
  },

  async onSave() {
    const { classes, classIndex, typeOptions, typeIndex, content, dueDate, note } = this.data
    if (classes.length === 0) {
      wx.showToast({ title: '请先创建班级', icon: 'none' })
      return
    }
    if (!content.trim()) {
      wx.showToast({ title: '请输入作业内容', icon: 'none' })
      return
    }

    const body = {
      class_id: classes[classIndex].id,
      content: content.trim(),
      type: typeOptions[typeIndex].value,
    }
    if (dueDate) body.due_date = dueDate
    if (note.trim()) body.note = note.trim()

    this.setData({ saving: true })
    try {
      await api.post('/homework', body)
      wx.showToast({ title: '已布置', icon: 'success' })
      setTimeout(() => wx.navigateBack(), 800)
    } catch (err) {
      wx.showToast({ title: '保存失败', icon: 'none' })
      this.setData({ saving: false })
    }
  },
})
