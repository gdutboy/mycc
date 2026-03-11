#!/usr/bin/env node

/**
 * Stop Check Hook
 *
 * 会话结束前检查未完成任务
 * 借鉴 PACEflow 的 Stop Hook 机制
 *
 * 使用方式：在 .claude/settings.local.json 中配置
 */

import { readFileSync, readdirSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROJECT_DIR = process.env.CLAUDE_PROJECT_DIR || __dirname;

/**
 * 检查 tasks 目录中未完成的任务
 */
function checkUnfinishedTasks() {
  const tasksDir = join(PROJECT_DIR, 'tasks');

  if (!existsSync(tasksDir)) {
    return { hasUnfinished: false, tasks: [] };
  }

  const files = readdirSync(tasksDir).filter(f => f.endsWith('.md') && f !== 'TASK_TEMPLATE.md');
  const unfinishedTasks = [];

  for (const file of files) {
    const content = readFileSync(join(tasksDir, file), 'utf-8');

    // 检查是否未完成 ([P], [A], [C] 状态)
    const hasActive = /\[P\]|\[A\]|\[C\]/.test(content);
    // 检查是否未验收（有 C 状态但无 V 状态）
    const hasPendingCheck = /\[C\]/.test(content) && !/\[V\]/.test(content);

    if (hasActive || hasPendingCheck) {
      // 提取任务标题
      const titleMatch = content.match(/^#\s+(.+)$/m);
      const title = titleMatch ? titleMatch[1] : file;

      unfinishedTasks.push({
        file,
        title,
        hasActive,
        hasPendingCheck
      });
    }
  }

  return {
    hasUnfinished: unfinishedTasks.length > 0,
    tasks: unfinishedTasks
  };
}

/**
 * 主函数
 */
function main() {
  const result = checkUnfinishedTasks();

  if (result.hasUnfinished) {
    console.log('\n⚠️  未完成的任务:');
    result.tasks.forEach(t => {
      const status = t.hasPendingCheck ? '⏳ 待验收' : '🔄 进行中';
      console.log(`  • ${t.title} (${status})`);
    });
    console.log('\n建议: 完成后添加 <!-- VERIFIED --> 标记，或归档到 tasks/done/\n');

    // PACEflow 会在未完成任务时 exit 2 阻止退出
    // MYCC 采用轻量方式，只提示不阻止
  } else {
    console.log('\n✅ 所有任务已完成！\n');
  }
}

main();
