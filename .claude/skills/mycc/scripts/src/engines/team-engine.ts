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

export type TeamMode = 'fast' | 'deep';

const MODEL_PRESETS: Record<TeamMode, { codex: string; gemini?: string }> = {
  fast: { codex: 'o4-mini', gemini: 'gemini-2.5-flash' },
  deep: { codex: 'gpt-5.4' },  // gemini 不指定，用 CLI 默认最强模型
};

export interface TeamEngineOptions {
  timeout?: number;   // 单个引擎超时时间（毫秒），默认 45 秒
  cwd?: string;       // 工作目录
  mode?: TeamMode;    // fast / deep，默认 deep
}

export class TeamEngine {
  private timeout: number;
  private cwd: string;
  private mode: TeamMode;

  constructor(options: TeamEngineOptions = {}) {
    this.timeout = options.timeout || 45 * 1000;
    this.cwd = options.cwd || process.cwd();
    this.mode = options.mode || 'deep';
  }

  /**
   * 并行运行三引擎
   */
  async run(prompt: string): Promise<EngineResult[]> {
    const preset = MODEL_PRESETS[this.mode];
    console.log(`[TeamEngine] 启动三引擎并行处理 [${this.mode}]`);
    console.log(`[TeamEngine] Codex: ${preset.codex}, Gemini: ${preset.gemini || '默认'}`);
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
      const model = MODEL_PRESETS[this.mode].codex;
      const stdout = await this.execWithTimeout(
        'codex',
        ['exec', '-m', model, '-o', outputFile, prompt],
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
        const geminiModel = MODEL_PRESETS[this.mode].gemini;
        const geminiArgs = geminiModel
          ? ['/c', 'gemini', '-m', geminiModel, '--prompt', prompt]
          : ['/c', 'gemini', '--prompt', prompt];
        const proc = nodePty.spawn('cmd.exe', geminiArgs, {
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

  /**
   * 用管道方式执行命令（通过 PowerShell echo）
   */
  private execWithPipe(cmdWithArgs: string, input: string, ms: number, extraEnv?: Record<string, string | undefined>, cwdOverride?: string): Promise<string> {
    return new Promise((resolve, reject) => {
      const env = { ...process.env } as Record<string, string | undefined>;
      if (extraEnv) {
        for (const [k, v] of Object.entries(extraEnv)) {
          if (v === undefined) delete env[k];
          else env[k] = v;
        }
      }

      // 用 PowerShell echo | 命令 方式传递多行输入
      const psCmd = `powershell -Command "${cmdWithArgs}"`;
      const proc = spawn('cmd', ['/c', `echo ${input.replace(/"/g, '\\"').replace(/\n/g, ' ')} | ${cmdWithArgs}`], {
        shell: true,
        cwd: cwdOverride || this.cwd,
        env: env as NodeJS.ProcessEnv,
        stdio: ['pipe', 'pipe', 'pipe']
      });

      let stdout = '';
      let stderr = '';

      const timer = setTimeout(() => {
        proc.kill('SIGTERM');
        reject(new Error(`[timeout] 命令超时 (${ms / 1000}s)`));
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
          reject(new Error(`[exit ${code}] 命令退出，代码 ${code}`));
        }
      });

      proc.on('error', (err) => {
        clearTimeout(timer);
        reject(err);
      });
    });
  }

  /**
   * 执行命令并通过 stdin 传递输入
   */
  private execWithStdin(cmd: string, args: string[], input: string, ms: number, extraEnv?: Record<string, string | undefined>, cwdOverride?: string): Promise<string> {
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

      // 写入 stdin 后关闭，让子进程从 stdin 读取 prompt
      proc.stdin!.write(input);
      proc.stdin!.end();

      let stdout = '';
      let stderr = '';

      const timer = setTimeout(() => {
        proc.kill('SIGTERM');
        reject(new Error(`[timeout] ${cmd} 超时 (${ms / 1000}s)`));
      }, ms);

      proc.stdout.on('data', (data) => { stdout += data.toString(); });
      proc.stderr.on('data', (data) => { stderr += data.toString(); });

      proc.on('close', (code) => {
        clearTimeout(timer);
        if (code === 0) resolve(stdout);
        else if (stderr) reject(new Error(stderr.trim()));
        else reject(new Error(`[exit ${code}] ${cmd} exited with code ${code}`));
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

  /**
   * CC 汇总分析 - 用 CC 综合三引擎结果
   */
  async summarizeWithCC(prompt: string, results: EngineResult[]): Promise<string> {
    const start = Date.now();

    // 调试：打印结果状态
    console.log(`[TeamEngine] CC 汇总开始，三引擎状态:`);
    for (const r of results) {
      console.log(`  - ${r.engine}: ${r.status}, ${r.charCount} 字`);
    }

    // 检查是否有成功的结果
    const successResults = results.filter(r => r.status === 'success');
    if (successResults.length === 0) {
      console.log(`[TeamEngine] 无成功结果，跳过汇总`);
      return '（无成功结果，跳过汇总）';
    }

    // 构建汇总 prompt
    const ccResult = results.find(r => r.engine === 'cc');
    const codexResult = results.find(r => r.engine === 'codex');
    const geminiResult = results.find(r => r.engine === 'gemini');

    const summaryPrompt = `你是一个专业的技术问题分析助手。请综合以下三个 AI 引擎对同一问题的回答，给出你的综合分析和建议。

## 用户问题
${prompt}

## 三个引擎的回答

### CC (Claude Code)
${ccResult?.status === 'success' ? ccResult.output : `（${ccResult?.status || '无'}）`}

### Codex
${codexResult?.status === 'success' ? codexResult.output : `（${codexResult?.status || '无'}）`}

### Gemini
${geminiResult?.status === 'success' ? geminiResult.output : `（${geminiResult?.status || '无'}）`}

请从以下角度进行分析：
1. 各引擎答案的核心差异
2. 哪个答案最全面/最准确
3. 你的综合建议

直接输出分析结果。`;

    console.log(`[TeamEngine] summaryPrompt 长度: ${summaryPrompt.length}`);

    // 把 prompt 写入临时文件，用 PowerShell Get-Content 传给 CC
    const promptFile = path.join(os.tmpdir(), `cc_summary_${Date.now()}.txt`);
    fs.writeFileSync(promptFile, summaryPrompt, 'utf-8');

    try {
      // 用 stdin 传递 prompt：spawn claude -p（不带参数），写入 stdin 后关闭
      const output = await this.execWithStdin(
        'claude',
        ['-p'],
        summaryPrompt,
        90 * 1000,
        { CLAUDECODE: undefined },
        os.tmpdir()
      );

      console.log(`[TeamEngine] CC 汇总完成，耗时 ${(Date.now() - start) / 1000}s`);
      return output.trim();
    } catch (e) {
      console.error(`[TeamEngine] CC 汇总失败:`, String(e).substring(0, 200));
      return `（CC 汇总失败: ${String(e).substring(0, 100)}）`;
    } finally {
      // 清理临时文件
      try { fs.unlinkSync(promptFile); } catch {}
    }
  }
}

/**
 * 格式化引擎结果为飞书消息
 */
export function formatTeamResults(results: EngineResult[], summary?: string): string {
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

  // CC 汇总（如果有）
  if (summary) {
    output += '\n---\n\n';
    output += '### 🧠 CC 综合分析\n';
    const maxSummaryLen = 4000;
    const truncatedSummary = summary.length > maxSummaryLen
      ? summary.substring(0, maxSummaryLen) + '\n...（内容过长已截断）'
      : summary;
    output += truncatedSummary + '\n';
  }

  output += '\n---\n\n';

  // 详细内容（按耗时排序）
  for (const r of results) {
    if (r.status === 'success') {
      output += `### ${r.engine.toUpperCase()} (${r.duration.toFixed(1)}s)\n`;
      const maxLen = 2500;
      const truncated = r.output.length > maxLen
        ? r.output.substring(0, maxLen) + '\n...（内容过长已截断）'
        : r.output;
      output += truncated + '\n\n';
    }
  }

  return output;
}
