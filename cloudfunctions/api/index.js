const cloud = require('wx-server-sdk')
const axios = require('axios')

cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })

const BASE_URL = 'http://47.239.15.178'
const API_KEY = process.env.API_KEY || 'REDACTED'

exports.main = async (event, context) => {
  const {
    method = 'GET',
    path = '',
    query = {},
    body = null,
  } = event

  const url = `${BASE_URL}/api${path}`
  const headers = {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json',
  }

  try {
    const response = await axios({
      method: method.toLowerCase(),
      url,
      params: query,
      data: body,
      headers,
      timeout: 15000,
    })

    return {
      statusCode: response.status,
      data: response.data,
    }
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
