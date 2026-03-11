/**
 * 团队引擎管理器 - 并行调用三引擎 (CC + Codex + Gemini)
 */

import { spawn } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs';
import * as os from 'os';
import * as path from 'path';
import * as nodePty from 'node-pty';

const readFile = promisify(fs.readFile);

export interface EngineResult {
  engine: 'cc' | 'codex' | 'gemini';
  status: 'success' | 'error' | 'timeout';
  duration: number;    // 秒
  output: string;      // 输出内容
  charCount: number;   // 字数
}

export interface TeamEngineOptions {
  timeout?: number;   // 单个引擎超时时间（毫秒），默认 60 秒
  cwd?: string;       // 工作目录
}

export class TeamEngine {
  private timeout: number;
  private cwd: string;

  constructor(options: TeamEngineOptions = {}) {
    this.timeout = options.timeout || 60 * 1000;
    this.cwd = options.cwd || process.cwd();
  }

  /**
   * 并行运行三引擎
   */
  async run(prompt: string): Promise<EngineResult[]> {
    console.log(`[TeamEngine] 启动三引擎并行处理`);
    console.log(`[TeamEngine] Prompt: ${prompt.substring(0, 50)}...`);

    const results = await Promise.all([
      this.runCC(prompt),
      this.runCodex(prompt),
      this.runGemini(prompt)
    ]);

    // 按耗时排序
    results.sort((a, b) => a.duration - b.duration);

    return results;
  }

  /**
   * 运行 Claude Code (通过 claude CLI -p 模式)
   */
  private async runCC(prompt: string): Promise<EngineResult> {
    const start = Date.now();

    try {
      // unset CLAUDECODE 避免嵌套检测，cwd 用临时目录避免加载 hooks
      const output = await this.execWithTimeout(
        'claude',
        ['-p', prompt],
        this.timeout,
        { CLAUDECODE: undefined },
        os.tmpdir()
      );

      return {
        engine: 'cc',
        status: 'success',
        duration: (Date.now() - start) / 1000,
        output: output.trim(),
        charCount: output.trim().length
      };
    } catch (e) {
      console.error(`[TeamEngine] CC 失败:`, String(e).substring(0, 200));
      return {
        engine: 'cc',
        status: this.isTimeoutError(e) ? 'timeout' : 'error',
        duration: (Date.now() - start) / 1000,
        output: String(e),
        charCount: 0
      };
    }
  }

  /**
   * 运行 Codex CLI
   */
  private async runCodex(prompt: string): Promise<EngineResult> {
    const start = Date.now();
    const outputFile = path.join(os.tmpdir(), `codex_output_${Date.now()}.txt`);

    try {
      const stdout = await this.execWithTimeout(
        'codex',
        ['exec', '-o', outputFile, prompt],
        this.timeout
      );

      // 优先读输出文件（更干净），回退到 stdout
      let output = '';
      try {
        output = await readFile(outputFile, 'utf-8');
      } catch {
        output = stdout;
      }

      return {
        engine: 'codex',
        status: 'success',
        duration: (Date.now() - start) / 1000,
        output: output.trim(),
        charCount: output.trim().length
      };
    } catch (e) {
      console.error(`[TeamEngine] Codex 失败:`, String(e).substring(0, 200));
      return {
        engine: 'codex',
        status: this.isTimeoutError(e) ? 'timeout' : 'error',
        duration: (Date.now() - start) / 1000,
        output: String(e),
        charCount: 0
      };
    }
  }

  /**
   * 运行 Gemini CLI (通过 node-pty 分配 TTY，CLI 在非 TTY 下不工作)
   */
  private async runGemini(prompt: string): Promise<EngineResult> {
    const start = Date.now();

    return new Promise((resolve) => {
      try {
        const proc = nodePty.spawn('cmd.exe', ['/c', 'gemini', '--prompt', prompt], {
          name: 'xterm-color',
          cwd: os.tmpdir(),
          env: process.env as Record<string, string>
        });

        let output = '';
        let settled = false;

        const timer = setTimeout(() => {
          if (!settled) {
            settled = true;
            proc.kill();
            console.error(`[TeamEngine] Gemini 超时 (${this.timeout / 1000}s)`);
            resolve({
              engine: 'gemini',
              status: 'timeout',
              duration: (Date.now() - start) / 1000,
              output: 'Gemini 超时',
              charCount: 0
            });
          }
        }, this.timeout);

        proc.onData((data) => {
          output += data;
        });

        proc.onExit(({ exitCode }) => {
          clearTimeout(timer);
          if (settled) return;
          settled = true;

          // 清理 ANSI 转义序列
          const clean = output
            .replace(/\x1B\[[0-9;]*[a-zA-Z]/g, '')
            .replace(/\x1B\][^\x07]*\x07/g, '')
            .replace(/\[[\?0-9]+[hlm]/g, '')
            .replace(/Loaded cached credentials\.\s*/g, '')
            .trim();

          if (exitCode === 0 && clean.length > 0) {
            resolve({
              engine: 'gemini',
              status: 'success',
              duration: (Date.now() - start) / 1000,
              output: clean,
              charCount: clean.length
            });
          } else {
            console.error(`[TeamEngine] Gemini exit ${exitCode}, output: ${clean.substring(0, 200)}`);
            resolve({
              engine: 'gemini',
              status: 'error',
              duration: (Date.now() - start) / 1000,
              output: clean || `exit code ${exitCode}`,
              charCount: 0
            });
          }
        });
      } catch (e) {
        console.error(`[TeamEngine] Gemini 启动失败:`, String(e).substring(0, 200));
        resolve({
          engine: 'gemini',
          status: 'error',
          duration: (Date.now() - start) / 1000,
          output: String(e),
          charCount: 0
        });
      }
    });
  }

  /**
   * 执行 CLI 命令并支持超时
   */
  private execWithTimeout(cmd: string, args: string[], ms: number, extraEnv?: Record<string, string | undefined>, cwdOverride?: string): Promise<string> {
    return new Promise((resolve, reject) => {
      const env = { ...process.env } as Record<string, string | undefined>;
      if (extraEnv) {
        for (const [k, v] of Object.entries(extraEnv)) {
          if (v === undefined) delete env[k];
          else env[k] = v;
        }
      }
      const proc = spawn(cmd, args, {
        shell: true,
        cwd: cwdOverride || this.cwd,
        env: env as NodeJS.ProcessEnv,
        stdio: ['pipe', 'pipe', 'pipe']
      });
      // 关闭 stdin，否则 claude -p 等命令不会自动退出
      proc.stdin!.end();

      let stdout = '';
      let stderr = '';

      const timer = setTimeout(() => {
        proc.kill('SIGTERM');
        reject(new Error(`[timeout] ${cmd} 超时 (${ms / 1000}s)`));
      }, ms);

      proc.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      proc.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      proc.on('close', (code) => {
        clearTimeout(timer);
        if (code === 0) {
          resolve(stdout);
        } else if (stderr) {
          reject(new Error(stderr.trim()));
        } else {
          reject(new Error(`[exit ${code}] ${cmd} exited with code ${code}`));
        }
      });

      proc.on('error', (err) => {
        clearTimeout(timer);
        reject(err);
      });
    });
  }

  private isTimeoutError(e: unknown): boolean {
    return String(e).includes('timeout');
  }
}

/**
 * 格式化引擎结果为飞书消息
 */
export function formatTeamResults(results: EngineResult[]): string {
  let output = '🚀 **团队模式结果**\n\n';

  // 状态行
  for (const r of results) {
    const icon = r.status === 'success' ? '✅' : r.status === 'timeout' ? '⏱️' : '❌';
    const status = r.status === 'success'
      ? `${r.duration.toFixed(1)}s  ${r.charCount} 字`
      : r.status === 'timeout'
      ? '超时'
      : '失败';
    output += `${icon} **${r.engine.toUpperCase()}**  ${status}\n`;
  }

  output += '\n---\n\n';

  // 详细内容（按耗时排序）
  for (const r of results) {
    if (r.status === 'success') {
      output += `### ${r.engine.toUpperCase()} (${r.duration.toFixed(1)}s)\n`;
      const maxLen = 3000;
      const truncated = r.output.length > maxLen
        ? r.output.substring(0, maxLen) + '\n...（内容过长已截断）'
        : r.output;
      output += truncated + '\n\n';
    }
  }

  return output;
}
