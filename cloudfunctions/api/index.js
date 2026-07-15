const http = require('http')
const URL = require('url')

const BASE_HOST = '47.239.25.178'
const BASE_PORT = 80

function httpRequest({ method, path, query, body, headers, timeout }) {
  return new Promise((resolve, reject) => {
    let qs = ''
    if (query && Object.keys(query).length > 0) {
      const params = Object.entries(query)
        .filter(([_, v]) => v !== undefined && v !== null)
        .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
      qs = params.length > 0 ? '?' + params.join('&') : ''
    }

    const options = {
      hostname: BASE_HOST,
      port: BASE_PORT,
      path: '/api' + path + qs,
      method: method.toUpperCase(),
      headers: headers || {},
      timeout: timeout || 15000,
    }

    let dataStr = null
    if (body !== null && body !== undefined) {
      if (Buffer.isBuffer(body)) {
        dataStr = body
      } else {
        dataStr = JSON.stringify(body)
        options.headers['Content-Type'] = options.headers['Content-Type'] || 'application/json'
      }
      options.headers['Content-Length'] = Buffer.byteLength(dataStr)
    }

    const req = http.request(options, (res) => {
      let chunks = []
      res.on('data', (chunk) => chunks.push(chunk))
      res.on('end', () => {
        const raw = Buffer.concat(chunks).toString('utf8')
        let parsed
        try {
          parsed = JSON.parse(raw)
        } catch (e) {
          parsed = { code: -1, message: raw }
        }
        resolve({ statusCode: res.statusCode, data: parsed })
      })
    })

    req.on('timeout', () => {
      req.destroy()
      reject(new Error('请求超时'))
    })

    req.on('error', reject)

    if (dataStr) {
      req.write(dataStr)
    }
    req.end()
  })
}

function buildMultipart(fields, fileBuffer, fileName) {
  const boundary = '----FormBoundary' + Math.random().toString(16).slice(2)
  const parts = []

  for (const [key, value] of Object.entries(fields)) {
    if (value === undefined || value === null) continue
    parts.push(
      `--${boundary}\r\n` +
      `Content-Disposition: form-data; name="${key}"\r\n\r\n` +
      `${value}\r\n`
    )
  }

  if (fileBuffer) {
    const header =
      `--${boundary}\r\n` +
      `Content-Disposition: form-data; name="file"; filename="${fileName}"\r\n` +
      `Content-Type: application/octet-stream\r\n\r\n`
    parts.push(Buffer.from(header, 'utf8'))
    parts.push(fileBuffer)
    parts.push(Buffer.from('\r\n', 'utf8'))
  }

  parts.push(Buffer.from(`--${boundary}--\r\n`, 'utf8'))

  return {
    buffer: Buffer.concat(parts.map(p => typeof p === 'string' ? Buffer.from(p, 'utf8') : p)),
    contentType: 'multipart/form-data; boundary=' + boundary,
  }
}

exports.main = async (event, context) => {
  const {
    method = 'GET',
    path = '',
    query = {},
    body = null,
    isUpload = false,
    fileBase64 = null,
    fileName = 'file',
    formData = {},
  } = event

  const apiKey = process.env.API_KEY
  if (!apiKey) {
    return {
      statusCode: 500,
      data: { code: -1, message: '云函数未配置 API_KEY 环境变量', data: null },
    }
  }

  const headers = { 'X-API-Key': apiKey }

  try {
    if (isUpload && fileBase64) {
      const fileBuffer = Buffer.from(fileBase64, 'base64')
      const { buffer, contentType } = buildMultipart(formData, fileBuffer, fileName)
      headers['Content-Type'] = contentType

      const result = await httpRequest({
        method: 'POST',
        path,
        query,
        body: buffer,
        headers,
        timeout: 30000,
      })
      return result
    }

    const result = await httpRequest({
      method,
      path,
      query,
      body,
      headers,
      timeout: 15000,
    })
    return result
  } catch (error) {
    return {
      statusCode: 500,
      data: {
        code: -1,
        message: `云函数请求失败: ${error.message}`,
        data: null,
      },
    }
  }
}
