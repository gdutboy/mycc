import { describe, it, expect } from 'vitest'

// Title 测试用例

describe('Title - 公众号标题生成', () => {

  describe('标题生成', () => {
    it('应该生成5-10个标题', () => {
      const topic = 'AI 协作'
      const titles = generateTitles(topic)
      expect(titles.length).toBeGreaterThanOrEqual(5)
      expect(titles.length).toBeLessThanOrEqual(10)
    })

    it('标题应该围绕主题', () => {
      const topic = 'Python 编程'
      const titles = generateTitles(topic)
      const hasRelated = titles.some(t =>
        t.includes('Python') || t.includes('编程') || t.includes('代码')
      )
      expect(hasRelated).toBe(true)
    })

    it('标题应该简洁有力', () => {
      const titles = generateTitles('测试主题')
      const allShort = titles.every(t => t.length <= 25)
      expect(allShort).toBe(true)
    })
  })

  describe('标题原则验证', () => {
    it('应该引发好奇', () => {
      const titles = generateTitles('学习方法')
      const hasCurious = titles.some(t =>
        t.includes('?') || t.includes('？') || t.includes('吗')
      )
      expect(hasCurious).toBe(true)
    })

    it('应该明确价值', () => {
      const titles = generateTitles('效率')
      const hasValue = titles.some(t =>
        t.includes('技巧') || t.includes('方法') || t.includes('实战')
      )
      expect(hasValue).toBe(true)
    })

    it('应该营造氛围', () => {
      const titles = generateTitles('AI')
      const hasEmotion = titles.some(t =>
        t.includes('！') || t.includes('!') || t.includes(':')
      )
      expect(hasEmotion).toBe(true)
    })
  })

  describe('风格适配', () => {
    it('应该支持疑问风格', () => {
      const titles = generateTitles('主题', '疑问')
      const isQuestion = titles.some(t => t.includes('?'))
      expect(isQuestion).toBe(true)
    })

    it('应该支持数字导向风格', () => {
      const titles = generateTitles('主题', '数字')
      const hasNumber = /\d+/.test(titles.join(' '))
      expect(hasNumber).toBe(true)
    })

    it('应该支持故事风格', () => {
      const titles = generateTitles('主题', '故事')
      const hasStory = titles.some(t =>
        t.includes('从') || t.includes('我是') || t.includes('我的')
      )
      expect(hasStory).toBe(true)
    })
  })

  describe('输出格式', () => {
    it('应该包含标题和特点', () => {
      const output = formatOutput(generateTitles('测试'))
      expect(output).toContain('1.')
      expect(output).toContain('特点')
    })
  })
})

// 模拟函数
function generateTitles(topic, style = 'default') {
  const templates = {
    default: [
      `我是怎么用 ${topic} 的？`,
      `${topic} 实战经验分享`,
      `从 0 到 1：我的 ${topic} 方法论`,
      `一个人就是一个团队：${topic} 实践`,
      `你真的会用 ${topic} 吗？`,
      `${topic} 的 5 个技巧`,
      `关于 ${topic}，我想说的话`,
      `${topic} 入门指南`,
      `为什么 ${topic} 很重要？`,
      `${topic} 的正确打开方式`
    ],
    question: [
      `${topic} 到底是什么？`,
      `${topic} 真的有用吗？`,
      `为什么都在说 ${topic}？`,
      `${topic} 适合你吗？`,
      `${topic} 怎么入门？`
    ],
    number: [
      `${topic} 的 3 个核心技巧`,
      `5 分钟了解 ${topic}`,
      `${topic} 必知的 10 个点`,
      `从 0 到 1 学 ${topic}`,
      `${topic} 入门到精通`
    ],
    story: [
      `我是怎么学会 ${topic} 的`,
      `我的 ${topic} 进化之路`,
      `${topic} 给我带来了什么`,
      `从新手到专家：${topic} 之路`,
      `我与 ${topic} 的故事`
    ]
  }

  return templates[style] || templates.default
}

function formatOutput(titles) {
  return titles.map((t, i) => `### ${i + 1}. ${t}\n特点：xxx`).join('\n')
}
