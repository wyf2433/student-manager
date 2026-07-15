const api = require('../../utils/api.js')

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
      const students = (data.items || []).map(s => ({
        ...s,
        avatarIdx: avatarIndex(s.name),
        genderEmoji: s.gender === '女' ? '👧' : '👦',
      }))
      this.setData({
        students,
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

  async addClass() {
    const res = await wx.showModal({
      title: '新建班级',
      editable: true,
      placeholderText: '如:初二三班',
    })
    if (!res.confirm || !res.content || !res.content.trim()) return
    try {
      await api.post('/classes', { name: res.content.trim() })
      wx.showToast({ title: '已创建', icon: 'success' })
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
