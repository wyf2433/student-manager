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
        } else if (result && result.data) {
          reject(result.data)
        } else {
          reject({ code: -1, message: '请求失败', data: null })
        }
      },
      fail(err) {
        reject({ code: -1, message: `云函数调用失败: ${err.errMsg}`, data: null })
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
}
