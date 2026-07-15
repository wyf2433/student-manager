const api = require('../../utils/api.js')

Page({
  data: {
    students: [],
    classes: [],
    currentClassId: '',
    classIndex: 0,
    keyword: '',
    loading: true,
  },

  onShow() {
    this.loadClasses().then(() => this.loadStudents())
  },

  async loadClasses() {
    try {
      const res = await api.get('/classes')
      const classes = (res.data && res.data.items) || res.data || []
      this.setData({ classes })
      if (classes.length > 0) {
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
      this.setData({
        students: data.items || [],
        loading: false,
      })
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
    wx.navigateTo({ url: `/pages/student-detail/student-detail?id=${id}` })
  },

  goAdd() {
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
