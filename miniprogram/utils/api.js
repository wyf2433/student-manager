function request(options) {
  const { method = 'GET', path = '', query = {}, body = null } = options

  return new Promise((resolve, reject) => {
    wx.cloud.callFunction({
      name: 'api',
      data: { method, path, query, body },
      success(res) {
        const result = res.result
        if (result && result.statusCode >= 200 && result.statusCode < 300) {
          resolve(result.data)
        } else {
          reject((result && result.data) || { code: -1, message: '请求失败' })
        }
      },
      fail(err) {
        reject({ code: -1, message: `云函数调用失败: ${err.errMsg}` })
      },
    })
  })
}

function getMimeType(fileName) {
  const ext = (fileName || '').split('.').pop().toLowerCase()
  const map = { jpg: 'image/jpeg', jpeg: 'image/jpeg', png: 'image/png', webp: 'image/webp', gif: 'image/gif' }
  return map[ext] || 'application/octet-stream'
}

function upload(path, filePath, formData) {
  return new Promise((resolve, reject) => {
    const fs = wx.getFileSystemManager()
    fs.readFile({
      filePath,
      encoding: 'base64',
      success(readRes) {
        const fileName = filePath.split('/').pop()
        const fileType = getMimeType(fileName)
        wx.cloud.callFunction({
          name: 'api',
          data: {
            method: 'POST',
            path,
            isUpload: true,
            fileBase64: readRes.data,
            fileName,
            fileType,
            formData,
          },
          success(res) {
            const result = res.result
            if (result && result.statusCode >= 200 && result.statusCode < 300) {
              resolve(result.data)
            } else {
              reject((result && result.data) || { code: -1, message: '上传失败' })
            }
          },
          fail(err) {
            reject({ code: -1, message: `云函数调用失败: ${err.errMsg}` })
          },
        })
      },
      fail(err) {
        reject({ code: -1, message: `文件读取失败: ${err.errMsg}` })
      },
    })
  })
}

module.exports = {
  get(path, query) {
    return request({ method: 'GET', path, query })
  },
  post(path, body) {
    return request({ method: 'POST', path, body })
  },
  put(path, body) {
    return request({ method: 'PUT', path, body })
  },
  patch(path, body) {
    return request({ method: 'PATCH', path, body })
  },
  delete(path) {
    return request({ method: 'DELETE', path })
  },
  upload,
}
