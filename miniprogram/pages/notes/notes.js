const api = require('../../utils/api.js')
const app = getApp()

const STICKY_CLASSES = ['sticky-yellow', 'sticky-pink', 'sticky-green', 'sticky-blue', 'sticky-purple']

Page({
  data: {
    notes: [],
    loading: true,
    showInput: false,
    noteContent: '',
    keyword: '',
    filterDate: '',
  },

  _loaded: false,
  _scrollTop: 0,

  onShow() {
    if (this._loaded && !app.globalData.dirty.notes) {
      wx.pageScrollTo({ scrollTop: this._scrollTop, duration: 0 })
      return
    }
    app.globalData.dirty.notes = false
    this.loadNotes()
  },

  onPageScroll(e) {
    this._scrollTop = e.scrollTop
  },

  async loadNotes() {
    this.setData({ loading: true })
    try {
      const params = {}
      if (this.data.keyword) params.keyword = this.data.keyword
      if (this.data.filterDate) params.date = this.data.filterDate
      const res = await api.get('/notes', params)
      const data = res.data || {}
      const notes = (data.items || []).map((n, i) => ({
        ...n,
        stickyClass: STICKY_CLASSES[i % STICKY_CLASSES.length],
      }))
      this.setData({
        notes: notes,
        loading: false,
      })
      this._loaded = true
    } catch (err) {
      console.error('加载速记失败', err)
      this.setData({ loading: false })
    }
  },

  onSearch(e) {
    const value = e.detail.value || e.detail.keyword || ''
    this.setData({ keyword: value }, () => {
      this.loadNotes()
    })
  },

  onDateChange(e) {
    this.setData({ filterDate: e.detail.value }, () => {
      this.loadNotes()
    })
  },

  clearDate() {
    this.setData({ filterDate: '' }, () => {
      this.loadNotes()
    })
  },

  toggleInput() {
    this.setData({ showInput: !this.data.showInput })
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
      await api.post('/notes', { content })
      this.setData({ noteContent: '', showInput: false })
      wx.showToast({ title: '已记录', icon: 'success' })
      this.loadNotes()
    } catch (err) {
      wx.showToast({ title: '保存失败', icon: 'none' })
    }
  },

  async onDeleteSwipe(e) {
    const id = e.currentTarget.dataset.id
    const res = await wx.showModal({ title: '确认删除?' })
    if (res.confirm) {
      try {
        await api.delete('/notes/' + id)
        wx.showToast({ title: '已删除', icon: 'success' })
        this.loadNotes()
      } catch (err) {
        wx.showToast({ title: '删除失败', icon: 'none' })
        this.loadNotes()
      }
    } else {
      this.loadNotes()
    }
  },

  onPullDownRefresh() {
    this.loadNotes().then(() => wx.stopPullDownRefresh())
  },
})
