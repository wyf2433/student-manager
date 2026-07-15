const api = require('../../utils/api.js')

Page({
  data: {
    type: 'attendance',
    typeOptions: [
      { value: 'attendance', label: '考勤' },
      { value: 'leave', label: '请假' },
      { value: 'score', label: '加扣分' },
    ],
    typeIndex: 0,
    students: [],
    studentIndex: 0,
    content: '',
    value: '',
    saving: false,
  },

  onLoad() {
    this.loadStudents()
  },

  async loadStudents() {
    try {
      const res = await api.get('/students')
      const data = res.data || {}
      this.setData({ students: data.items || [] })
    } catch (err) {
      console.error('加载学生失败', err)
    }
  },

  onTypeChange(e) {
    const index = e.detail.value
    this.setData({
      typeIndex: index,
      type: this.data.typeOptions[index].value,
    })
  },

  onStudentChange(e) {
    this.setData({ studentIndex: e.detail.value })
  },

  onContentInput(e) {
    this.setData({ content: e.detail.value })
  },

  onValueInput(e) {
    this.setData({ value: e.detail.value })
  },

  async onSave() {
    const { type, students, studentIndex, content, value } = this.data
    if (students.length === 0) {
      wx.showToast({ title: '请先添加学生', icon: 'none' })
      return
    }

    const body = {
      student_id: students[studentIndex].id,
      type,
      content: content || null,
    }

    if (type === 'score') {
      const v = parseFloat(value)
      if (isNaN(v)) {
        wx.showToast({ title: '请输入分数', icon: 'none' })
        return
      }
      body.value = v
    }

    this.setData({ saving: true })
    try {
      await api.post('/records', body)
      wx.showToast({ title: '已保存', icon: 'success' })
      setTimeout(() => wx.navigateBack(), 800)
    } catch (err) {
      wx.showToast({ title: '保存失败', icon: 'none' })
      this.setData({ saving: false })
    }
  },
})
