const api = require('../../utils/api.js')

const WEEKDAYS = [
  { value: 1, label: '周一' },
  { value: 2, label: '周二' },
  { value: 3, label: '周三' },
  { value: 4, label: '周四' },
  { value: 5, label: '周五' },
  { value: 6, label: '周六' },
  { value: 7, label: '周日' },
]

const SUBJECT_EMOJI = {
  '物理': '🔬', '语文': '📚', '数学': '➗', '英语': '🔤',
  '道法': '⚖️', '历史': '📜', '地理': '🌍', '生物': '🧬',
  '体育': '⚽', '音乐': '🎵', '美术': '🎨', '信息技术': '💻',
  '自习': '📖', '班会': '👥', '化学': '🧪',
}

function getSubjectEmoji(subject) {
  if (!subject) return '📘'
  for (const key in SUBJECT_EMOJI) {
    if (subject.indexOf(key) >= 0) return SUBJECT_EMOJI[key]
  }
  return '📘'
}

Page({
  data: {
    schedules: [],
    currentWeekday: 1,
    weekdays: WEEKDAYS,
    loading: true,
  },

  onLoad() {
    const today = new Date().getDay()
    const weekday = today === 0 ? 7 : today
    this.setData({ currentWeekday: weekday }, () => {
      this.loadSchedule()
    })
  },

  async loadSchedule() {
    this.setData({ loading: true })
    try {
      const res = await api.get('/schedule', { weekday: this.data.currentWeekday })
      const data = res.data || {}
      const schedules = (data.items || []).map(s => ({
        ...s,
        emoji: getSubjectEmoji(s.subject),
      }))
      this.setData({
        schedules: schedules,
        loading: false,
      })
    } catch (err) {
      console.error('加载课表失败', err)
      this.setData({ loading: false })
    }
  },

  onWeekdayChange(e) {
    const weekday = e.detail.value
    this.setData({ currentWeekday: weekday }, () => {
      this.loadSchedule()
    })
  },

  goAdd() {
    wx.navigateTo({
      url: `/pages/schedule-edit/schedule-edit?weekday=${this.data.currentWeekday}`,
    })
  },

  goEdit(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/schedule-edit/schedule-edit?id=${id}&weekday=${this.data.currentWeekday}`,
    })
  },

  async onDeleteSwipe(e) {
    const id = e.currentTarget.dataset.id
    const res = await wx.showModal({ title: '确认删除?' })
    if (res.confirm) {
      try {
        await api.delete('/schedule/' + id)
        wx.showToast({ title: '已删除', icon: 'success' })
        this.loadSchedule()
      } catch (err) {
        wx.showToast({ title: '删除失败', icon: 'none' })
        this.loadSchedule()
      }
    } else {
      this.loadSchedule()
    }
  },

  goOverride() {
    wx.navigateTo({ url: '/pages/override/override' })
  },

  onPullDownRefresh() {
    this.loadSchedule().then(() => wx.stopPullDownRefresh())
  },
})
