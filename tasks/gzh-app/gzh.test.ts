import { describe, it, expect } from 'vitest'

// GZH 排版测试用例

describe('GZH - 公众号排版渲染', () => {

  describe('标题渲染', () => {
    it('应该渲染一级标题', () => {
      const input = '# 主标题'
      const output = renderGZH(input)
      expect(output).toContain('font-size: 16px')
      expect(output).toContain('font-weight: bold')
    })

    it('应该渲染二级标题', () => {
      const input = '## 二级标题'
      const output = renderGZH(input)
      expect(output).toContain('font-size: 15px')
    })

    it('应该渲染三级标题', () => {
      const input = '### 三级标题'
      const output = renderGZH(input)
      expect(output).toContain('font-size: 14px')
    })
  })

  describe('正文渲染', () => {
    it('应该设置正文字体', () => {
      const input = '正文内容'
      const output = renderGZH(input)
      expect(output).toContain('font-size: 15px')
      expect(output).toContain('line-height: 1.8')
      expect(output).toContain('color: #2c2c2c')
    })

    it('应该设置段落间距', () => {
      const input = '段落1\n\n段落2'
      const output = renderGZH(input)
      expect(output).toContain('margin-bottom: 16px')
    })
  })

  describe('引用块渲染', () => {
    it('应该渲染引用块', () => {
      const input = '> 引用内容'
      const output = renderGZH(input)
      expect(output).toContain('border-left')
      expect(output).toContain('#3b82f6')
      expect(output).toContain('background')
    })
  })

  describe('代码块渲染', () => {
    it('应该渲染行内代码', () => {
      const input = '这是 `代码` 内容'
      const output = renderGZH(input)
      expect(output).toContain('background')
    })

    it('应该渲染代码块', () => {
      const input = '```\n代码块\n```'
      const output = renderGZH(input)
      expect(output).toContain('#1e1e1e')
    })
  })

  describe('列表渲染', () => {
    it('应该渲染无序列表', () => {
      const input = '- 项目1\n- 项目2'
      const output = renderGZH(input)
      expect(output).toContain('•')
    })

    it('应该渲染有序列表', () => {
      const input = '1. 项目1\n2. 项目2'
      const output = renderGZH(input)
      expect(output).toContain('1.')
    })
  })

  describe('分割线渲染', () => {
    it('应该渲染分割线', () => {
      const input = '---'
      const output = renderGZH(input)
      expect(output).toContain('hr') || output.includes('border-top')
    })
  })
})

// 模拟函数
function renderGZH(markdown) {
  // 简化模拟
  let html = markdown

  // 标题
  if (markdown.startsWith('# ')) {
    html = `<h1 style="font-size: 16px; font-weight: bold; text-align: center;">${markdown.slice(2)}</h1>`
  } else if (markdown.startsWith('## ')) {
    html = `<h2 style="font-size: 15px; font-weight: bold;">${markdown.slice(3)}</h2>`
  } else if (markdown.startsWith('### ')) {
    html = `<h3 style="font-size: 14px; font-weight: bold;">${markdown.slice(4)}</h3>`
  }

  // 正文
  if (!markdown.startsWith('#')) {
    html = `<p style="font-size: 15px; line-height: 1.8; color: #2c2c2c;">${markdown}</p>`
  }

  // 引用
  if (markdown.includes('>')) {
    html = `<blockquote style="border-left: 3px solid #3b82f6; background: #f8f9fa; font-style: italic;">${markdown}</blockquote>`
  }

  return html
}
