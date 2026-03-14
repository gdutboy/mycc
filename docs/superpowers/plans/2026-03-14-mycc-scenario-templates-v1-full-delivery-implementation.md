# mycc 场景化模板清单 v1（完整版交付）Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 产出可直接落库的 `mycc-scenario-templates-v1.yaml`（10 条完整模板）并与既有设计文档保持一致，默认开启飞书推送。

**Architecture:** 以现有设计稿为单一约束源（ID、分类、workflow 主链路不变），通过“先校验、再生成、后验收”的最小改动流程交付完整版配置。仅修改设计文档中的冻结说明与 YAML 文件本体，不引入新依赖、不改执行器逻辑。

**Tech Stack:** YAML、Markdown、Node.js（仅用于本地校验命令）

---

## File Structure

### Existing files to modify

- Modify: `docs/superpowers/specs/2026-03-14-mycc-scenario-templates-v1-design.md`
  - 补充“已冻结约束”说明：10 条模板固定、默认 notify 推送、ID/分类/workflow 主链路不变。
- Modify: `0-Skill-Platform/mycc-scenario-templates-v1.yaml`
  - 写入可直接落库的 10 条完整模板定义。

### New files to create

- 无

### Existing tests to extend

- 无（本次以命令行结构校验 + 内容核对为验收）

### Notes

- 所有命令默认在仓库根目录 `C:/Users/gdutb/Desktop/mycc` 执行。
- 禁止新增依赖（不安装任何包）。
- `tpl-dev-001` 必须保持 `fallback_skill: none`。
- 所有模板默认 `notify.enabled: true` 且 `channel: feishu`，并必须包含 `level`。

---

## Chunk 1: 冻结约束并锁定模板矩阵

### Task 1: 同步设计文档的最终冻结口径

**Files:**
- Modify: `docs/superpowers/specs/2026-03-14-mycc-scenario-templates-v1-design.md`

- [ ] **Step 1: 先运行检查（预期失败）确认尚未有“冻结决策”段落**

Run: `node -e "const fs=require('fs');const s=fs.readFileSync('docs/superpowers/specs/2026-03-14-mycc-scenario-templates-v1-design.md','utf8');if(!s.includes('冻结决策')){throw new Error('missing_freeze_section')}console.log('OK')"`
Expected: 首次执行应 FAIL（`missing_freeze_section`）。

- [ ] **Step 2: 在设计文档中新增“冻结决策”段落**

新增内容必须明确：
- 仅 10 条模板（3/3/3/1）
- 默认 notify 推送飞书
- 严格沿用已有 `template_id`、`category`、`workflow`
- 5.5 YAML 示例不计入模板矩阵数量

- [ ] **Step 3: 再次运行文本检查确认新增段落存在**

Run: `node -e "const fs=require('fs');const s=fs.readFileSync('docs/superpowers/specs/2026-03-14-mycc-scenario-templates-v1-design.md','utf8');if(!s.includes('冻结决策')){throw new Error('missing_freeze_section')}console.log('OK')"`
Expected: `OK`

- [ ] **Step 4: 校验 7.1~7.4 模板目录中 ID 仍为 10 条（不允许增删）**

Run: `node -e "const fs=require('fs');const s=fs.readFileSync('docs/superpowers/specs/2026-03-14-mycc-scenario-templates-v1-design.md','utf8');const findHeading=(re,from=0)=>{const m=re.exec(s.slice(from));if(!m) return -1;return from+m.index;};const getSection=(startRe,nextRes)=>{const i=findHeading(startRe);if(i<0) throw new Error('section_not_found_'+startRe);let end=-1;for(const r of nextRes){const p=findHeading(r,i+1);if(p>=0&&(end<0||p<end)) end=p;}if(end<0){const anyNext=findHeading(/^##\s+/m,i+1);if(anyNext<0) throw new Error('next_heading_not_found_'+startRe);end=anyNext;}if(end<=i) throw new Error('section_order_invalid_'+startRe);return s.slice(i,end);};const sec=[getSection(/^##\s+7\.1\b/m,[/^##\s+7\.2\b/m]),getSection(/^##\s+7\.2\b/m,[/^##\s+7\.3\b/m]),getSection(/^##\s+7\.3\b/m,[/^##\s+7\.4\b/m]),getSection(/^##\s+7\.4\b/m,[/^##\s+7\.5\b/m,/^##\s+8\b/m])].join('\n');const ids=[...sec.matchAll(/`(tpl-[^`]+)`/g)].map(m=>m[1]);const uniq=[...new Set(ids)];if(uniq.length!==10) throw new Error('section7_template_count_invalid');console.log('OK',uniq);"`
Expected: 输出 `OK` 且数组长度为 10。

---

## Chunk 2: 生成完整版 YAML（10 条完整定义）

### Task 2: 建立 YAML 顶层结构与通用约束

**Files:**
- Modify: `0-Skill-Platform/mycc-scenario-templates-v1.yaml`

- [ ] **Step 1: 写入顶层结构并初始化 templates 顶层键（不使用 `[]` 内联形式）**

```yaml
version: "v1"
templates:
```

说明：后续 Task 3~5 直接在 `templates:` 下按块列表追加 `- id: ...`。

- [ ] **Step 2: 运行结构检查（先失败后修正）**

Run: `node -e "const fs=require('fs');const s=fs.readFileSync('0-Skill-Platform/mycc-scenario-templates-v1.yaml','utf8');if(!s.includes('version: \"v1\"')) throw new Error('missing_version'); if(!s.includes('templates:')) throw new Error('missing_templates'); console.log('OK')"`
Expected: `OK`

### Task 3: 写入 content 类 3 条完整模板

**Files:**
- Modify: `0-Skill-Platform/mycc-scenario-templates-v1.yaml`

- [ ] **Step 1: 写入 `tpl-content-001~003` 的完整字段**

每条必须包含：
- `id/name/category/triggers/entry_skill/fallback_skill/inputs/workflow/outputs/acceptance/notify`

- [ ] **Step 2: 校验 content 模板字段完整性**

Run: `node -e "const fs=require('fs');const y=fs.readFileSync('0-Skill-Platform/mycc-scenario-templates-v1.yaml','utf8');for (const id of ['tpl-content-001','tpl-content-002','tpl-content-003']) {const block=(y.split('- id: '+id)[1]||'').split('\n  - id: ')[0];if(!block) throw new Error(id+'_missing'); for (const k of ['entry_skill:','fallback_skill:','workflow:','outputs:','acceptance:','notify:']) {if(!block.includes(k)) throw new Error(id+'_'+k+'_missing');}} console.log('OK')"`
Expected: `OK`

### Task 4: 写入 collect 类 3 条完整模板

**Files:**
- Modify: `0-Skill-Platform/mycc-scenario-templates-v1.yaml`

- [ ] **Step 1: 写入 `tpl-collect-001~003` 的完整字段**

额外要求（验收项中明确）：
- 来源链接
- 过滤统计
- 行动项

- [ ] **Step 2: 校验 collect 模板包含 c9~c11 对应验收语义**

Run: `node -e "const fs=require('fs');const y=fs.readFileSync('0-Skill-Platform/mycc-scenario-templates-v1.yaml','utf8');for (const id of ['tpl-collect-001','tpl-collect-002','tpl-collect-003']) {const b=(y.split('- id: '+id)[1]||'').split('\n  - id: ')[0]; for (const kw of ['来源','过滤','行动']) {if(!b.includes(kw)) throw new Error(id+'_missing_'+kw);} } console.log('OK')"`
Expected: `OK`

### Task 5: 写入 dev 类 3 条 + general 类 1 条

**Files:**
- Modify: `0-Skill-Platform/mycc-scenario-templates-v1.yaml`

- [ ] **Step 1: 写入 `tpl-dev-001~003` 与 `tpl-general-001` 完整字段**

关键约束：
- `tpl-dev-001` 的 `fallback_skill` 必须是 `none`
- `tpl-general-001` 的 workflow 只保留 scheduler 注册/更新语义

- [ ] **Step 2: 校验 dev/general 关键约束**

Run: `node -e "const fs=require('fs');const y=fs.readFileSync('0-Skill-Platform/mycc-scenario-templates-v1.yaml','utf8');const d1=(y.split('- id: tpl-dev-001')[1]||'').split('\n  - id: ')[0]; if(!d1.includes('fallback_skill: none')) throw new Error('tpl-dev-001_fallback_invalid'); const g=(y.split('- id: tpl-general-001')[1]||'').split('\n  - id: ')[0]; if(!g.includes('entry_skill: scheduler')) throw new Error('tpl-general-001_entry_invalid'); console.log('OK')"`
Expected: `OK`

---

## Chunk 3: 全局验收与提交准备

### Task 6: 执行 10 条模板全量结构校验

**Files:**
- Modify: `0-Skill-Platform/mycc-scenario-templates-v1.yaml`

- [ ] **Step 1: 校验模板总数与 ID 集合**

Run: `node -e "const fs=require('fs');const y=fs.readFileSync('0-Skill-Platform/mycc-scenario-templates-v1.yaml','utf8');const ids=[...y.matchAll(/- id:\s*(\S+)/g)].map(m=>m[1]);console.log(ids.length,ids);const exp=['tpl-content-001','tpl-content-002','tpl-content-003','tpl-collect-001','tpl-collect-002','tpl-collect-003','tpl-dev-001','tpl-dev-002','tpl-dev-003','tpl-general-001'];if(ids.length!==10) throw new Error('count_invalid');for(const id of exp){if(!ids.includes(id)) throw new Error('missing_'+id)}console.log('OK')"`
Expected: 第一行显示 `10`，随后输出 `OK`

- [ ] **Step 2: 校验默认通知策略全量生效（含 level）**

Run: `node -e "const fs=require('fs');const y=fs.readFileSync('0-Skill-Platform/mycc-scenario-templates-v1.yaml','utf8');const blocks=y.split('\n  - id: ').slice(1).map((b,i)=> (i===0?'- id: '+b:'  - id: '+b));for(const b of blocks){if(!b.includes('enabled: true')) throw new Error('notify_enabled_missing');if(!b.includes('channel: feishu')) throw new Error('notify_channel_missing');if(!(b.includes('level: blue')||b.includes('level: red'))) throw new Error('notify_level_missing');}console.log('OK')"`
Expected: `OK`

### Task 7: 对齐设计文档与 YAML 一致性

**Files:**
- Modify: `docs/superpowers/specs/2026-03-14-mycc-scenario-templates-v1-design.md`
- Modify: `0-Skill-Platform/mycc-scenario-templates-v1.yaml`

- [ ] **Step 1: 逐项对照 ID、分类、workflow 主链路**

核对清单：
- ID 完全一致
- category 完全一致
- workflow 主 skill 顺序不变

- [ ] **Step 2: 执行一致性检查命令（从设计文档提取期望并对比 YAML）**

Run: `node -e "const fs=require('fs');const spec=fs.readFileSync('docs/superpowers/specs/2026-03-14-mycc-scenario-templates-v1-design.md','utf8');const y=fs.readFileSync('0-Skill-Platform/mycc-scenario-templates-v1.yaml','utf8');const s7=spec.indexOf('## 7.1');const m8=spec.slice(s7).match(/\n##\s*8\b/);if(s7<0||!m8) throw new Error('spec_section7_or_8_missing');const sec=spec.slice(s7,s7+m8.index+1);const lines=sec.split('\n');let cat='';let curr='';const exp={};for(const raw of lines){const line=raw.trim();if(/^##\s+7\.1\b/.test(line)) cat='content';else if(/^##\s+7\.2\b/.test(line)) cat='collect';else if(/^##\s+7\.3\b/.test(line)) cat='dev';else if(/^##\s+7\.4\b/.test(line)) cat='general';const mId=line.match(/`(tpl-[^`]+)`/);if(mId){curr=mId[1];exp[curr]={category:cat,workflow:[]};continue;}const mW=line.match(/workflow:\s*`([^`]+)`/);if(mW&&curr){exp[curr].workflow=mW[1].split('->').map(v=>v.trim()).filter(Boolean);}}const ids=Object.keys(exp);if(ids.length!==10) throw new Error('spec_expected_templates_invalid');for(const id of ids){const blk=(y.split('- id: '+id)[1]||'').split('\n  - id: ')[0];if(!blk) throw new Error('yaml_missing_'+id);if(!blk.includes('category: '+exp[id].category)) throw new Error('category_mismatch_'+id);let idx=0;for(const skill of exp[id].workflow){const p=blk.indexOf('skill: '+skill,idx);if(p<0) throw new Error('workflow_mismatch_'+id+'_'+skill);idx=p+1;}}console.log('OK',ids);"`
Expected: `OK` 且输出 10 个模板 ID。

### Task 8: 收口检查（不提交）

**Files:**
- Modify: `docs/superpowers/specs/2026-03-14-mycc-scenario-templates-v1-design.md`
- Modify: `0-Skill-Platform/mycc-scenario-templates-v1.yaml`

- [ ] **Step 1: 查看目标文件 diff，确认无越界改动**

Run: `git diff -- docs/superpowers/specs/2026-03-14-mycc-scenario-templates-v1-design.md 0-Skill-Platform/mycc-scenario-templates-v1.yaml`
Expected: 仅出现冻结说明补充 + 10 条模板 YAML 相关改动

- [ ] **Step 2: 执行 @superpowers:verification-before-completion 自检（可执行记录）**

执行要求：
1. 调用 `superpowers:verification-before-completion` skill。
2. 在终端输出中记录三项结论：
   - 有命令输出证据支撑“完成”声明
   - 无越界改动
   - 满足“完整版可直接落库”
3. 若任一项不满足，回到对应 Task 修正后重新执行该自检。

---

## Plan Review Checklist (for reviewer agent)

1. 是否严格保持 10 条模板，不增不减
2. 是否所有模板字段完整（含 notify）
3. 是否默认推送飞书且 `tpl-dev-001` 例外规则正确（fallback=none）
4. 是否保持 spec 的 ID/分类/workflow 主链路不变
5. 是否没有引入新依赖、没有改动执行器逻辑
