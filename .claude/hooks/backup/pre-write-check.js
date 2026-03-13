#!/usr/bin/env node

/**
 * Pre-Write Check Hook
 *
 * 在写文件前检查是否有活跃任务
 * 借鉴 PACEflow 的任务检查机制
 *
 * 使用方式：在 .claude/settings.local.json 中配置
 */

import { readFileSync, readdirSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROJECT_DIR = process.env.CLAUDE_PROJECT_DIR || __dirname;

/**
 * 检查 tasks 目录中是否有活跃任务
 */
function checkActiveTasks() {
  const tasksDir = join(PROJECT_DIR, 'tasks');

  if (!existsSync(tasksDir)) {
    return { hasActive: false, tasks: [] };
  }

  const files = readdirSync(tasksDir).filter(f => f.endsWith('.md') && f !== 'TASK_TEMPLATE.md');
  const activeTasks = [];

  for (const file of files) {
    const content = readFileSync(join(tasksDir, file), 'utf-8');

    // 检查是否有活跃状态 [P], [A], [C]
    const hasActive = /\[P\]|\[A\]|\[C\]/.test(content);

    // 检查是否有 APPROVED 标记
    const hasApproved = /<!--\s*APPROVED\s*-->/.test(content);

    if (hasActive) {
      activeTasks.push({
        file,
        hasActive,
        hasApproved
      });
    }
  }

  return {
    hasActive: activeTasks.length > 0,
    tasks: activeTasks
  };
}

/**
 * 主函数
 */
function main() {
  const result = checkActiveTasks();

  if (result.hasActive) {
    console.log('\n📋 活跃任务:');
    result.tasks.forEach(t => {
      const status = t.hasApproved ? '✅' : '⚠️';
      console.log(`  ${status} ${t.file}`);
    });
    console.log('');
  } else {
    console.log('\n💡 提示: 当前没有活跃任务。如果要开始新任务，建议先创建 tasks/xxx.md 文件。\n');
  }
}

main();
