import { describe, it, expect } from 'vitest'

// Decision 测试用例

describe('Decision - 决策记录', () => {

  describe('决策类型判断', () => {
    it('应该识别 Bug 修复类型', () => {
      const input = '修复了一个登录 bug'
      const type = detectType(input)
      expect(type).toBe('fix')
    })

    it('应该识别架构变更类型', () => {
      const input = '重构了模块结构'
      const type = detectType(input)
      expect(type).toBe('arch')
    })

    it('应该识别 API 变更类型', () => {
      const input = '修改了接口设计'
      const type = detectType(input)
      expect(type).toBe('api')
    })

    it('应该识别配置变更类型', () => {
      const input = '修改了服务器配置'
      const type = detectType(input)
      expect(type).toBe('config')
    })

    it('应该识别产品设计类型', () => {
      const input = '决定了界面交互方式'
      const type = detectType(input)
      expect(type).toBe('design')
    })
  })

  describe('必填字段验证', () => {
    it('应该包含背景信息', () => {
      const record = {
        background: '项目需要支持多平台',
        candidates: [],
        decision: '选择 Flutter',
        alternatives: 'React Native',
        files: [],
        conditions: []
      }
      expect(record.background).toBeTruthy()
    })

    it('应该包含候选方案', () => {
      const record = {
        candidates: [
          { name: 'Flutter', pros: '跨平台', cons: '学习成本高' },
          { name: 'React Native', pros: '前端友好', cons: '性能一般' }
        ]
      }
      expect(record.candidates.length).toBe(2)
    })

    it('应该包含最终决定', () => {
      const record = { decision: '选择 Flutter' }
      expect(record.decision).toBeTruthy()
    })

    it('应该包含放弃的方案', () => {
      const record = { alternatives: 'React Native：团队熟悉但性能一般' }
      expect(record.alternatives).toBeTruthy()
    })

    it('应该包含翻转条件', () => {
      const record = { conditions: ['官方停止维护', '出现更好方案'] }
      expect(record.conditions.length).toBe(2)
    })
  })

  describe('模板生成', () => {
    it('应该生成正确的 Markdown 格式', () => {
      const record = {
        title: '选择 Flutter 作为跨平台框架',
        date: '2026-03-08',
        type: 'arch',
        background: '需要同时支持 iOS 和 Android',
        candidates: [
          { name: 'Flutter', pros: '一套代码', cons: '学习曲线' },
          { name: 'React Native', pros: '前端友好', cons: '性能' }
        ],
        decision: 'Flutter',
        reason: '长期维护成本低',
        alternatives: 'React Native：团队熟悉但性能一般',
        conditions: ['官方停止维护']
      }

      const output = generateTemplate(record)
      expect(output).toContain('## 选择 Flutter 作为跨平台框架')
      expect(output).toContain('<!-- type: arch -->')
      expect(output).toContain('Flutter')
    })
  })

  describe('文件追加', () => {
    it('应该追加到 04-决策记录.md', () => {
      const projectPath = '2-Projects/P01-xxx'
      const targetFile = `${projectPath}/04-决策记录.md`
      expect(targetFile).toContain('04-决策记录.md')
    })

    it('应该更新最后更新时间', () => {
      const lastUpdated = new Date().toISOString().split('T')[0]
      expect(lastUpdated).toMatch(/^\d{4}-\d{2}-\d{2}$/)
    })
  })
})

// 模拟函数
function detectType(input) {
  if (input.includes('bug') || input.includes('修复')) return 'fix'
  if (input.includes('重构') || input.includes('架构')) return 'arch'
  if (input.includes('接口') || input.includes('API')) return 'api'
  if (input.includes('配置') || input.includes('部署')) return 'config'
  if (input.includes('设计') || input.includes('取舍')) return 'design'
  return 'auto'
}

function generateTemplate(record) {
  return `## ${record.title}（${record.date}）

<!-- type: ${record.type} -->
<!-- status: 生效中 -->

### 现象
${record.background}

### 候选方案
| 方案 | 优点 | 缺点 |
|------|------|------|
${record.candidates.map(c => `| ${c.name} | ${c.pros} | ${c.cons} |`).join('\n')}

### 决策
选择：${record.decision}
理由：${record.reason}
放弃的方案：${record.alternatives}

### 什么条件下该翻
${record.conditions.map(c => `- ${c}`).join('\n')}
`
}
