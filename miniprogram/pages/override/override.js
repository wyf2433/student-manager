const api = require('../../utils/api.js')

const ACTION_OPTIONS = [
  { value: 'cancel', label: '停课' },
  { value: 'change', label: '改科目' },
  { value: 'add', label: '加课' },
]

Page({
  data: {
    overrides: [],
    loading: true,
    showForm: false,
    actionOptions: ACTION_OPTIONS,
    actionIndex: 0,
    date: '',
    period: 1,
    action: 'cancel',
    newSubject: '',
    newClassName: '',
    note: '',
    saving: false,
  },

  onLoad(options) {
    const today = new Date()
    const dateStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`
    this.setData({ date: dateStr })
    if (options.mode === 'add') {
      this.setData({ showForm: true })
    }
  },

  onShow() {
    this.loadOverrides()
  },

  async loadOverrides() {
    this.setData({ loading: true })
    try {
      const res = await api.get('/schedule/overrides')
      const data = res.data || {}
      this.setData({
        overrides: data.items || [],
        loading: false,
      })
    } catch (err) {
      console.error('加载调课失败', err)
      this.setData({ loading: false })
    }
  },

  toggleForm() {
    this.setData({ showForm: !this.data.showForm })
  },

  onDateChange(e) {
    this.setData({ date: e.detail.value })
  },

  onPeriodChange(e) {
    this.setData({ period: parseInt(e.detail.value) + 1 })
  },

  onActionChange(e) {
    const index = parseInt(e.detail.value)
    this.setData({
      actionIndex: index,
      action: ACTION_OPTIONS[index].value,
    })
  },

  onSubjectInput(e) {
    this.setData({ newSubject: e.detail.value })
  },

  onClassInput(e) {
    this.setData({ newClassName: e.detail.value })
  },

  onNoteInput(e) {
    this.setData({ note: e.detail.value })
  },

  async onSave() {
    const { date, period, action, newSubject, newClassName, note } = this.data
    if (!date) {
      wx.showToast({ title: '请选择日期', icon: 'none' })
      return
    }

    const body = { date, period, action }
    if (action !== 'cancel') {
      if (newSubject.trim()) body.new_subject = newSubject.trim()
      if (newClassName.trim()) body.new_class_name = newClassName.trim()
    }
    if (note.trim()) body.note = note.trim()

    this.setData({ saving: true })
    try {
      await api.post('/schedule/overrides', body)
      wx.showToast({ title: '已保存', icon: 'success' })
      this.setData({
        showForm: false,
        saving: false,
        newSubject: '',
        newClassName: '',
        note: '',
        actionIndex: 0,
        action: 'cancel',
      })
      this.loadOverrides()
    } catch (err) {
      wx.showToast({ title: '保存失败', icon: 'none' })
      this.setData({ saving: false })
    }
  },

  async onDelete(e) {
    const id = e.currentTarget.dataset.id
    const res = await wx.showModal({ title: '确认删除?' })
    if (res.confirm) {
      try {
        await api.delete('/schedule/overrides/' + id)
        wx.showToast({ title: '已删除', icon: 'success' })
        this.loadOverrides()
      } catch (err) {
        wx.showToast({ title: '删除失败', icon: 'none' })
      }
    }
  },
})
