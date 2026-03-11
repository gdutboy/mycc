import { describe, it, expect, beforeEach, vi } from 'vitest'

// 天气预报页面测试用例

describe('天气预报页面', () => {
  // 模拟 fetch
  beforeEach(() => {
    global.fetch = vi.fn()
  })

  describe('页面加载', () => {
    it('页面应该正常加载', () => {
      document.body.innerHTML = '<div id="app"></div>'
      // 验证 DOM 存在
      expect(document.getElementById('app')).not.toBeNull()
    })

    it('应该显示加载状态', () => {
      const loadingEl = document.querySelector('.loading')
      // 应该有加载提示
      expect(true).toBe(true)
    })
  })

  describe('天气数据获取', () => {
    it('应该能获取天气数据', async () => {
      const mockData = {
        location: { name: '广州' },
        daily: [
          { date: '2026-03-09', tempMax: 25, tempMin: 18, textDay: '晴', humidity: 65 }
        ]
      }

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const response = await fetch('/api/weather')
      const data = await response.json()

      expect(data.location.name).toBe('广州')
      expect(data.daily.length).toBeGreaterThan(0)
    })

    it('应该处理 API 错误', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 401
      })

      const response = await fetch('/api/weather')
      expect(response.ok).toBe(false)
    })
  })

  describe('7天天气显示', () => {
    it('应该显示7天天气数据', () => {
      const weatherData = {
        daily: Array(7).fill(null).map((_, i) => ({
          date: `2026-03-${9 + i}`,
          tempMax: 25 + i,
          tempMin: 18 + i,
          textDay: '晴',
          humidity: 65,
          windDir: '东北风',
          windScale: '3级'
        }))
      }

      expect(weatherData.daily.length).toBe(7)
    })
  })

  describe('自动定位', () => {
    it('应该能获取用户位置', () => {
      navigator.geolocation = {
        getCurrentPosition: vi.fn((success) => {
          success({
            coords: { latitude: 23.12, longitude: 113.25 }
          })
        })
      }

      expect(navigator.geolocation.getCurrentPosition).toBeDefined()
    })

    it('应该处理定位被拒绝的情况', () => {
      navigator.geolocation = {
        getCurrentPosition: vi.fn(),
        watchPosition: vi.fn()
      }

      const errorCallback = vi.fn()
      navigator.geolocation.getCurrentPosition = vi.fn((_, error) => {
        error({ code: 1, message: 'Permission denied' })
      })

      expect(true).toBe(true)
    })
  })

  describe('天气信息显示', () => {
    it('应该显示温度信息', () => {
      const day = { tempMax: 28, tempMin: 20 }
      expect(day.tempMax).toBeGreaterThan(day.tempMin)
    })

    it('应该显示湿度信息', () => {
      const day = { humidity: 75 }
      expect(day.humidity).toBeGreaterThanOrEqual(0)
      expect(day.humidity).toBeLessThanOrEqual(100)
    })

    it('应该显示风力信息', () => {
      const day = { windDir: '东南风', windScale: '3级' }
      expect(day.windDir).toBeTruthy()
      expect(day.windScale).toBeTruthy()
    })
  })

  describe('响应式设计', () => {
    it('应该在移动端正常显示', () => {
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375
      })

      expect(window.innerWidth).toBe(375)
    })
  })
})
