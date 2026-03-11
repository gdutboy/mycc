# mycc 排查手册

> 启动失败时再读这个文件，正常启动不需要。

## 首次运行

先安装依赖：
```bash
cd .claude/skills/mycc/scripts && npm install && cd -
```

## 环境要求

- **Node.js 18+**
- **cloudflared**：Windows `winget install Cloudflare.cloudflared`，macOS `brew install cloudflare/cloudflare/cloudflared`
- **网络**：需 VPN/代理（cloudflared 需访问外网）

## 常见问题

### 端口被占用

```bash
# Windows
netstat -ano | findstr :18080
taskkill /F /PID <PID>

# macOS/Linux
lsof -i :18080 -t | xargs kill
```

### cloudflared 未安装

按上面依赖说明安装。

### tunnel 启动失败

检查网络/VPN，重试即可。

## 停止服务

- Windows: `.\stop-mycc.ps1` 或 `taskkill /F /PID <PID>`
- macOS/Linux: `./stop-mycc.sh` 或 `lsof -i :18080 -t | xargs kill`

## 飞书通道配置

在 `.env` 文件中配置：
```bash
FEISHU_ENABLED=true
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret
FEISHU_ENCRYPT_KEY=your_encrypt_key
FEISHU_VERIFICATION_TOKEN=your_verification_token
```

飞书应用需开启权限：`im:message`、`im:chat`，事件订阅 `im.message.receive_v1`。

## 连接信息格式

保存在 `.claude/skills/mycc/current.json`：
```json
{
  "routeToken": "XXXXXX",
  "pairCode": "XXXXXX",
  "tunnelUrl": "https://xxx.trycloudflare.com",
  "mpUrl": "https://api.mycc.dev/XXXXXX",
  "cwd": "/path/to/project",
  "startedAt": "2026-01-27T06:00:00.000Z"
}
```

## API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/{token}/health` | GET | 健康检查 |
| `/{token}/pair` | POST | 配对验证 |
| `/{token}/chat` | POST | 发送消息 |
| `/{token}/history/list` | GET | 历史记录列表 |
| `/{token}/history/{sessionId}` | GET | 对话详情 |
