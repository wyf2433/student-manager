const api = require('../../utils/api.js')
const app = getApp()

function avatarIndex(name) {
  if (!name) return 0
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = hash + name.charCodeAt(i)
  }
  return hash % 8
}

Page({
  data: {
    students: [],
    classes: [],
    currentClassId: '',
    classIndex: 0,
    keyword: '',
    loading: true,
    showClassModal: false,
    gradeOptions: ['初一', '初二', '初三'],
    classNoOptions: ['1', '2', '3', '4', '5', '6'],
    newGradeIndex: 1,
    newClassNoIndex: 0,
  },

  _scrollTop: 0,
  _loaded: false,

  onLoad() {
    this.loadClasses().then(() => this.loadStudents())
  },

  onShow() {
    if (this._loaded && !app.globalData.dirty.students) {
      wx.pageScrollTo({ scrollTop: this._scrollTop, duration: 0 })
      return
    }
    app.globalData.dirty.students = false
    this.loadClasses().then(() => this.loadStudents())
  },

  onPageScroll(e) {
    this._scrollTop = e.scrollTop
  },

  async loadClasses() {
    try {
      const res = await api.get('/classes')
      const classes = (res.data && res.data.items) || res.data || []
      this.setData({ classes })
      if (classes.length > 0 && !this.data.currentClassId) {
        this.setData({ currentClassId: classes[0].id, classIndex: 0 })
      }
    } catch (err) {
      console.error('加载班级失败', err)
    }
  },

  async loadStudents() {
    this.setData({ loading: true })
    try {
      const params = {}
      if (this.data.currentClassId) {
        params.class_id = this.data.currentClassId
      }
      if (this.data.keyword) {
        params.keyword = this.data.keyword
      }
      const res = await api.get('/students', params)
      const data = res.data || {}
      const students = (data.items || []).map(s => ({
        ...s,
        avatarIdx: avatarIndex(s.name),
      }))
      this.setData({
        students,
        loading: false,
      })
      this._loaded = true
    } catch (err) {
      console.error('加载学生失败', err)
      this.setData({ loading: false })
    }
  },

  onClassChange(e) {
    const index = e.detail.value
    this.setData({
      classIndex: index,
      currentClassId: this.data.classes[index].id,
    }, () => {
      this.loadStudents()
    })
  },

  onSearch(e) {
    const value = e.detail.value || e.detail.keyword || ''
    this.setData({ keyword: value }, () => {
      this.loadStudents()
    })
  },

  goDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/packageA/pages/student-detail/student-detail?id=${id}` })
  },

  async addClass() {
    const today = new Date()
    const grade = today.getFullYear() - 2024 + 7
    const gradeIdx = grade === 7 ? 0 : grade === 8 ? 1 : 2
    this.setData({ showClassModal: true, newGradeIndex: gradeIdx, newClassNoIndex: 0 })
  },

  closeClassModal() {
    this.setData({ showClassModal: false })
  },

  onGradePick(e) {
    this.setData({ newGradeIndex: e.detail.value })
  },

  onClassNoPick(e) {
    this.setData({ newClassNoIndex: e.detail.value })
  },

  async confirmAddClass() {
    const { gradeOptions, classNoOptions, newGradeIndex, newClassNoIndex } = this.data
    const grade = gradeOptions[newGradeIndex]
    const classNo = classNoOptions[newClassNoIndex]
    const name = grade + classNo + '班'
    try {
      await api.post('/classes', { name, grade })
      wx.showToast({ title: '已创建', icon: 'success' })
      this.setData({ showClassModal: false })
      await this.loadClasses()
      const newIdx = this.data.classes.length - 1
      this.setData({ classIndex: newIdx, currentClassId: this.data.classes[newIdx].id }, () => {
        this.loadStudents()
      })
    } catch (err) {
      wx.showToast({ title: '创建失败', icon: 'none' })
    }
  },

  goAdd() {
    if (this.data.classes.length === 0) {
      wx.showToast({ title: '请先创建班级', icon: 'none' })
      return
    }
    wx.navigateTo({ url: '/pages/student-add/student-add' })
  },

  goImport() {
    wx.navigateTo({ url: '/pages/student-import/student-import' })
  },

  goScoreImport() {
    wx.navigateTo({ url: '/pages/score-import/score-import' })
  },

  onPullDownRefresh() {
    Promise.all([this.loadClasses(), this.loadStudents()]).then(() =>
      wx.stopPullDownRefresh()
    )
  },
})
