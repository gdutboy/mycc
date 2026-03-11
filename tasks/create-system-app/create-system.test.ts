import { describe, it, expect } from 'vitest'

// Create System 测试用例

describe('Create System - 创作系统路由', () => {

  describe('任务类型判断', () => {
    it('应该识别标题生成任务', () => {
      const input = '帮我起个标题'
      const type = detectTaskType(input)
      expect(type).toBe('title')
    })

    it('应该识别大纲生成任务', () => {
      const input = '帮我写个大纲'
      const type = detectTaskType(input)
      expect(type).toBe('outline')
    })

    it('应该识别初稿写作任务', () => {
      const input = '帮我写篇文章'
      const type = detectTaskType(input)
      expect(type).toBe('draft')
    })

    it('应该识别精修任务', () => {
      const input = '帮我精修一下'
      const type = detectTaskType(input)
      expect(type).toBe('polish')
    })

    it('应该识别排版任务', () => {
      const input = '帮我排版'
      const type = detectTaskType(input)
      expect(type).toBe('gzh')
    })
  })

  describe('技能路由', () => {
    it('应该正确映射到 title 技能', () => {
      const skill = getSkill('title')
      expect(skill.name).toBe('title')
      expect(skill.file).toBe('title/SKILL.md')
    })

    it('应该正确映射到 outline 技能', () => {
      const skill = getSkill('outline')
      expect(skill.name).toBe('outline')
    })

    it('应该正确映射到 draft 技能', () => {
      const skill = getSkill('draft')
      expect(skill.name).toBe('draft')
    })

    it('应该正确映射到 polish 技能', () => {
      const skill = getSkill('polish')
      expect(skill.name).toBe('polish')
    })

    it('应该正确映射到 gzh 技能', () => {
      const skill = getSkill('gzh')
      expect(skill.name).toBe('gzh')
    })

    it('应该正确映射到 brush 技能', () => {
      const skill = getSkill('brush')
      expect(skill.name).toBe('brush')
    })
  })

  describe('完整创作流程', () => {
    it('应该支持完整流程：标题→大纲→初稿→精修→排版', () => {
      const workflow = ['title', 'outline', 'draft', 'polish', 'gzh']
      const steps = getWorkflow('完整文章')

      expect(steps).toContain('title')
      expect(steps).toContain('outline')
      expect(steps).toContain('draft')
    })

    it('应该支持快速流程：直接写文章', () => {
      const steps = getWorkflow('直接写')
      expect(steps).toContain('draft')
    })
  })

  describe('参数提取', () => {
    it('应该提取文章主题', () => {
      const input = '写一篇关于 AI 协作的文章'
      const topic = extractTopic(input)
      expect(topic).toContain('AI 协作')
    })

    it('应该提取目标读者', () => {
      const input = '给程序员看的文章'
      const audience = extractAudience(input)
      expect(audience).toContain('程序员')
    })
  })

  describe('错误处理', () => {
    it('应该处理未知任务类型', () => {
      const input = '随便什么'
      const type = detectTaskType(input)
      expect(type).toBe('draft') // 默认到 draft
    })

    it('应该处理空输入', () => {
      const input = ''
      const type = detectTaskType(input)
      expect(type).toBe('draft')
    })
  })
})

// 模拟函数
function detectTaskType(input) {
  const patterns = {
    title: ['标题', 'title', '起名'],
    outline: ['大纲', 'outline', '提纲', '列提纲'],
    draft: ['写', '文章', 'draft', '创作'],
    polish: ['精修', 'polish', '打磨', '润色'],
    gzh: ['排版', 'gzh', '渲染', '公众号'],
    brush: ['图', '画', '配图', 'brush']
  }

  for (const [type, keywords] of Object.entries(patterns)) {
    if (keywords.some(k => input.includes(k))) {
      return type
    }
  }
  return 'draft'
}

function getSkill(type) {
  const skills = {
    title: { name: 'title', file: 'title/SKILL.md' },
    outline: { name: 'outline', file: 'outline/SKILL.md' },
    draft: { name: 'draft', file: 'draft/SKILL.md' },
    polish: { name: 'polish', file: 'polish/SKILL.md' },
    gzh: { name: 'gzh', file: 'gzh/SKILL.md' },
    brush: { name: 'brush', file: 'brush/SKILL.md' }
  }
  return skills[type]
}

function getWorkflow(mode) {
  if (mode === '完整文章') {
    return ['title', 'outline', 'draft', 'polish', 'gzh']
  }
  return ['draft']
}

function extractTopic(input) {
  const match = input.match(/关于(.+?)[的]/)?.[1]
  return match || input
}

function extractAudience(input) {
  const match = input.match(/给(.+?)看/)?.[1]
  return match || '通用'
}
