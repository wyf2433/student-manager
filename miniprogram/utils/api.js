const BASE_URL = 'http://47.239.25.178'
const API_KEY = 'REDACTED'

function request(options) {
  const { method = 'GET', path = '', query = {}, body = null } = options

  let url = `${BASE_URL}/api${path}`
  const params = []
  for (const key in query) {
    if (query[key] !== undefined && query[key] !== null) {
      params.push(`${key}=${encodeURIComponent(query[key])}`)
    }
  }
  if (params.length > 0) {
    url += `?${params.join('&')}`
  }

  return new Promise((resolve, reject) => {
    wx.request({
      url,
      method,
      data: body,
      header: {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json',
      },
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          reject(res.data || { code: -1, message: '请求失败' })
        }
      },
      fail(err) {
        reject({ code: -1, message: `网络错误: ${err.errMsg}` })
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
