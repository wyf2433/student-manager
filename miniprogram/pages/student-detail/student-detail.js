const api = require('../../utils/api.js')

Page({
  data: {
    student: null,
    records: [],
    scores: [],
    notes: [],
    studentId: null,
    loading: true,
    typeLabels: {
      attendance: '考勤',
      leave: '请假',
      score: '加扣分',
    },
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
      const [studentRes, recordsRes, scoresRes, notesRes] = await Promise.all([
        api.get('/students/' + this.data.studentId),
        api.get('/records', { student_id: this.data.studentId }),
        api.get('/scores', { student_id: this.data.studentId }),
        api.get('/notes', { student_id: this.data.studentId }),
      ])
      this.setData({
        student: studentRes.data,
        records: (recordsRes.data || {}).items || [],
        scores: (scoresRes.data || {}).items || [],
        notes: (notesRes.data || {}).items || [],
        loading: false,
      })
    } catch (err) {
      console.error('加载失败', err)
      this.setData({ loading: false })
    }
  },

  showActionSheet() {
    wx.showActionSheet({
      itemList: ['记考勤', '记请假', '加扣分'],
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
