const api = require('../../utils/api.js')

const TYPE_LABELS = {
  attendance: '考勤',
  leave: '请假',
  score: '加扣分',
  note: '速记',
}

const SUBJECT_EMOJI = {
  '物理': '🔬', '语文': '📚', '数学': '➗', '英语': '🔤',
  '道法': '⚖️', '历史': '📜', '地理': '🌍', '生物': '🧬',
  '体育': '⚽', '音乐': '🎵', '美术': '🎨', '信息技术': '💻',
  '自习': '📖', '班会': '👥', '化学': '🧪', '科学': '🔭',
}

const RECENT_EMOJI = {
  attendance: '✅',
  leave: '🚪',
  score: '⭐',
  note: '📝',
}

const HOMEWORK_TYPE_EMOJI = {
  daily: '📝',
  experiment_report: '🔬',
  review: '📋',
  exam: '📄',
}

const HOMEWORK_STATUS_LABEL = {
  active: '进行中',
  collected: '已收',
  graded: '已改',
}

function getSubjectEmoji(subject) {
  if (!subject) return '📘'
  for (const key in SUBJECT_EMOJI) {
    if (subject.indexOf(key) >= 0) return SUBJECT_EMOJI[key]
  }
  return '📘'
}

function getGreeting() {
  const h = new Date().getHours()
  if (h < 6) return '夜深了'
  if (h < 9) return '早上好'
  if (h < 12) return '上午好'
  if (h < 14) return '中午好'
  if (h < 18) return '下午好'
  return '晚上好'
}

function formatDate() {
  const d = new Date()
  const week = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  return `${d.getMonth() + 1}月${d.getDate()}日 ${week[d.getDay()]}`
}

Page({
  data: {
    overview: null,
    recent: [],
    todaySchedule: [],
    todayHomework: [],
    loading: true,
    quickNote: '',
    greeting: '',
    todayDate: '',
    scheduleCount: 0,
    homeworkCount: 0,
    recentEmojis: RECENT_EMOJI,
    hwTypeEmojis: HOMEWORK_TYPE_EMOJI,
    hwStatusLabels: HOMEWORK_STATUS_LABEL,
  },

  onShow() {
    this.setData({ greeting: getGreeting(), todayDate: formatDate() })
    this.loadData()
  },

  async loadData() {
    this.setData({ loading: true })
    try {
      const [overviewRes, recentRes, scheduleRes, homeworkRes] = await Promise.all([
        api.get('/dashboard/today'),
        api.get('/dashboard/recent'),
        api.get('/schedule/today'),
        api.get('/homework/today'),
      ])
      const recentData = recentRes.data || {}
      const items = (recentData.items || []).map(item => {
        const type = item.source === 'note' ? 'note' : item.sub_type
        return {
          id: item.id,
          type: type,
          type_label: TYPE_LABELS[type] || type,
          emoji: RECENT_EMOJI[type] || '📌',
          summary: item.content || '',
          time_label: item.created_at || '',
        }
      })
      const scheduleData = scheduleRes.data || {}
      const homeworkData = homeworkRes.data || {}
      const schedules = (scheduleData.items || []).map(s => ({
        ...s,
        emoji: getSubjectEmoji(s.subject),
      }))
      const homework = (homeworkData.items || []).map(h => ({
        ...h,
        emoji: HOMEWORK_TYPE_EMOJI[h.type] || '📝',
      }))
      this.setData({
        overview: overviewRes.data,
        recent: items,
        todaySchedule: schedules,
        todayHomework: homework,
        scheduleCount: schedules.length,
        homeworkCount: homework.length,
        loading: false,
      })
    } catch (err) {
      console.error('加载失败', err)
      this.setData({ loading: false })
      wx.showToast({ title: '加载失败', icon: 'none' })
    }
  },

  onNoteInput(e) {
    this.setData({ quickNote: e.detail.value })
  },

  async saveNote() {
    const content = this.data.quickNote.trim()
    if (!content) {
      wx.showToast({ title: '请输入内容', icon: 'none' })
      return
    }
    try {
      await api.post('/notes', { content })
      this.setData({ quickNote: '' })
      wx.showToast({ title: '已记录', icon: 'success' })
      this.loadData()
    } catch (err) {
      wx.showToast({ title: '保存失败', icon: 'none' })
    }
  },

  goSchedule() {
    wx.navigateTo({ url: '/pages/schedule/schedule' })
  },

  goHomework() {
    wx.navigateTo({ url: '/pages/homework/homework' })
  },

  goTraces() {
    wx.navigateTo({ url: '/pages/traces/traces' })
  },

  goScoreAnalysis() {
    wx.navigateTo({ url: '/pages/score-analysis/score-analysis' })
  },

  onPullDownRefresh() {
    this.loadData().then(() => wx.stopPullDownRefresh())
  },
})
