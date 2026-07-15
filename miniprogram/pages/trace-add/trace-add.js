const api = require('../../utils/api.js')
const IMG_BASE = 'http://47.239.25.178'

const TYPE_OPTIONS = [
  { value: 'classroom_discipline', label: '课堂纪律' },
  { value: 'experiment_record', label: '实验课记录' },
  { value: 'homework_feedback', label: '作业反馈' },
  { value: 'exam_analysis', label: '考试分析' },
  { value: 'student_talk', label: '学生谈话' },
  { value: 'parent_communication', label: '家长沟通' },
  { value: 'other', label: '其他' },
]

Page({
  data: {
    typeOptions: TYPE_OPTIONS,
    typeIndex: 6,
    type: 'other',
    title: '',
    note: '',
    images: [],
    saving: false,
  },

  onLoad(options) {
    if (options.type) {
      const idx = TYPE_OPTIONS.findIndex(t => t.value === options.type)
      if (idx >= 0) {
        this.setData({
          typeIndex: idx,
          type: TYPE_OPTIONS[idx].value,
          title: TYPE_OPTIONS[idx].label,
        })
        return
      }
    }
    this.setData({ typeIndex: 6, type: 'other' })
  },

  onTypeChange(e) {
    const index = e.detail.value
    this.setData({
      typeIndex: index,
      type: TYPE_OPTIONS[index].value,
      title: this.data.title || TYPE_OPTIONS[index].label,
    })
  },

  onTitleInput(e) {
    this.setData({ title: e.detail.value })
  },

  onNoteInput(e) {
    this.setData({ note: e.detail.value })
  },

  chooseImage() {
    const count = 9 - this.data.images.length
    if (count <= 0) {
      wx.showToast({ title: '最多9张图片', icon: 'none' })
      return
    }
    wx.showActionSheet({
      itemList: ['拍照', '从相册选择'],
      success: (res) => {
        if (res.tapIndex === 0) {
          this.takePhoto()
        } else {
          this.chooseFromAlbum(count)
        }
      },
    })
  },

  takePhoto() {
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['camera'],
      camera: 'back',
      success: (res) => {
        this.uploadImage(res.tempFiles[0].tempFilePath)
      },
    })
  },

  chooseFromAlbum(count) {
    wx.chooseMedia({
      count,
      mediaType: ['image'],
      sourceType: ['album'],
      success: (res) => {
        for (const file of res.tempFiles) {
          this.uploadImage(file.tempFilePath)
        }
      },
    })
  },

  async uploadImage(filePath) {
    wx.showLoading({ title: '上传中...' })
    try {
      const res = await api.upload('/traces/upload/image', filePath)
      const url = res.data.url
      if (!url) {
        throw new Error('返回数据无url字段: ' + JSON.stringify(res))
      }
      this.setData({
        images: [...this.data.images, url],
      })
      wx.hideLoading()
    } catch (err) {
      wx.hideLoading()
      console.error('上传失败详情:', JSON.stringify(err))
      wx.showToast({ title: '上传失败', icon: 'none' })
    }
  },

  removeImage(e) {
    const index = e.currentTarget.dataset.index
    const images = [...this.data.images]
    images.splice(index, 1)
    this.setData({ images })
  },

  previewImage(e) {
    const current = e.currentTarget.dataset.url
    const urls = this.data.images.map(url => IMG_BASE + url)
    wx.previewImage({
      current: IMG_BASE + current,
      urls,
    })
  },

  async onSave() {
    const { type, title, note, images } = this.data
    if (!title.trim()) {
      wx.showToast({ title: '请输入标题', icon: 'none' })
      return
    }

    this.setData({ saving: true })
    try {
      await api.post('/traces', {
        title: title.trim(),
        type,
        note: note.trim() || null,
        image_urls: images.length > 0 ? images : null,
      })
      wx.showToast({ title: '已保存', icon: 'success' })
      setTimeout(() => wx.navigateBack(), 800)
    } catch (err) {
      wx.showToast({ title: '保存失败', icon: 'none' })
      this.setData({ saving: false })
    }
  },
})
