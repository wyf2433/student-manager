const cloud = require('wx-server-sdk')
const axios = require('axios')
const FormData = require('form-data')

cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })

const BASE_URL = 'http://47.239.25.178'

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

  const url = `${BASE_URL}/api${path}`
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
      const buffer = Buffer.from(fileBase64, 'base64')
      const form = new FormData()
      form.append('file', buffer, fileName)
      for (const key in formData) {
        form.append(key, formData[key])
      }
      Object.assign(headers, form.getHeaders())

      const response = await axios({
        method: 'post',
        url,
        data: form,
        headers,
        params: query,
        timeout: 30000,
      })
      return { statusCode: response.status, data: response.data }
    }

    headers['Content-Type'] = 'application/json'
    const response = await axios({
      method: method.toLowerCase(),
      url,
      params: query,
      data: body,
      headers,
      timeout: 15000,
    })
    return { statusCode: response.status, data: response.data }
  } catch (error) {
    if (error.response) {
      return {
        statusCode: error.response.status,
        data: error.response.data,
      }
    }
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
