#!/usr/bin/env node

/**
 * SessionStart Hook
 *
 * 会话开始时自动注入当前任务状态
 * 借鉴 PACEflow 的 SessionStart 机制
 *
 * 使用方式：在 .claude/settings.local.json 中配置
 */

import { readFileSync, readdirSync, existsSync, statSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROJECT_DIR = process.env.CLAUDE_PROJECT_DIR || __dirname;

/**
 * 获取当前任务状态摘要
 */
function getTaskSummary() {
  const tasksDir = join(PROJECT_DIR, 'tasks');

  if (!existsSync(tasksDir)) {
    return { active: [], recent: [] };
  }

  let files;
  try {
    files = readdirSync(tasksDir)
      .filter(f => f.endsWith('.md') && f !== 'TASK_TEMPLATE.md')
      .sort((a, b) => {
        try {
          const statA = statSync(join(tasksDir, a));
          const statB = statSync(join(tasksDir, b));
          return statB.mtime - statA.mtime;
        } catch (e) {
          return 0;
        }
      });
  } catch (e) {
    return { active: [], recent: [] };
  }

  const activeTasks = [];
  const recentTasks = [];

  for (const file of files.slice(0, 5)) {
    let content = '';
    try {
      content = readFileSync(join(tasksDir, file), 'utf-8');
    } catch (e) {
      continue;
    }

    // 检查是否有活跃状态
    const hasActive = /\[P\]|\[A\]|\[C\]/.test(content);
    const hasApproved = /<!--\s*APPROVED\s*-->/.test(content);
    const hasVerified = /<!--\s*VERIFIED\s*-->/.test(content);

    const titleMatch = content.match(/^#\s+(.+)$/m);
    const title = titleMatch ? titleMatch[1] : file;

    const taskInfo = {
      file,
      title,
      hasActive,
      hasApproved,
      hasVerified
    };

    if (hasActive) {
      activeTasks.push(taskInfo);
    }
    recentTasks.push(taskInfo);
  }

  return { active: activeTasks, recent: recentTasks };
}

/**
 * 输出格式化摘要
 */
function main() {
  const summary = getTaskSummary();

  console.log('\n📋 任务状态摘要\n');

  if (summary.active.length > 0) {
    console.log('🔄 进行中的任务:');
    summary.active.forEach(t => {
      const status = t.hasApproved ? '✅' : '⚠️';
      console.log(`  ${status} ${t.title}`);
    });
    console.log('');
  } else {
    console.log('💡 当前没有进行中的任务\n');
  }

  if (summary.recent.length > 0) {
    console.log('📝 最近任务:');
    summary.recent.forEach(t => {
      const status = t.hasVerified ? '✓' : t.hasActive ? '●' : '○';
      console.log(`  [${status}] ${t.title}`);
    });
  }

  console.log('\n💡 使用 tasks/TASK_TEMPLATE.md 创建新任务\n');
}

main();
