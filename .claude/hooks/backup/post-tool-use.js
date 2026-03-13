#!/usr/bin/env node

/**
 * PostToolUse Hook
 *
 * 写代码后检查是否需要归档
 * 借鉴 PACEflow 的 PostToolUse 机制
 *
 * 使用方式：在 .claude/settings.local.json 中配置
 */

import { readFileSync, readdirSync, existsSync, statSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROJECT_DIR = process.env.CLAUDE_PROJECT_DIR || __dirname;

/**
 * 检查是否需要归档
 */
function checkArchive() {
  const tasksDir = join(PROJECT_DIR, 'tasks');
  const doneDir = join(PROJECT_DIR, 'tasks', 'done');

  if (!existsSync(tasksDir)) {
    return { needsArchive: false, tasks: [] };
  }

  const files = readdirSync(tasksDir).filter(f => f.endsWith('.md') && f !== 'TASK_TEMPLATE.md');
  const needsArchive = [];

  for (const file of files) {
    const content = readFileSync(join(tasksDir, file), 'utf-8');

    // 检查是否已完成但未归档
    // 已完成：包含 [V] 或 [x]
    // 未归档：不在 tasks/done/ 中
    const hasVerified = /\[V\]/.test(content) || /\[x\]/.test(content);

    if (hasVerified) {
      const titleMatch = content.match(/^#\s+(.+)$/m);
      const title = titleMatch ? titleMatch[1] : file;

      needsArchive.push({
        file,
        title
      });
    }
  }

  return {
    needsArchive: needsArchive.length > 0,
    tasks: needsArchive
  };
}

/**
 * 主函数
 */
function main() {
  const result = checkArchive();

  if (result.needsArchive) {
    console.log('\n📦 可归档的任务:');
    result.tasks.forEach(t => {
      console.log(`  • ${t.title}`);
    });
    console.log('\n💡 归档命令: mv tasks/{文件} tasks/done/{文件}\n');
  }
}

main();
