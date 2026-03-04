# 飞书多维表格智能问答系统

基于智普大模型的飞书机器人应用，实现与多维表格的自然语言问答交互。

## 功能特点

- 🤖 **智能理解**：使用智普大模型理解用户自然语言问题
- 🔍 **灵活查询**：支持各种复杂的筛选条件组合
- 📊 **统计分析**：支持数据统计和分析功能
- 💬 **友好交互**：用户无需学习特定语法，直接提问即可
- 🎨 **美化展示**：自动解析富文本格式，使用图标美化输出
- � **消息去重**：防止飞书事件重复推送导致的重复回复
- �🚀 **易于部署**：基于Flask，支持多种部署方式

## 项目结构

```
feishu-bitable-qa/
├── .env                   # 环境变量配置（包含敏感信息）
├── .env.example           # 环境变量示例
├── .gitignore            # Git忽略文件
├── config.py              # 配置加载器
├── llm_service.py         # 智普大模型服务
├── intent_parser.py       # 意图解析器
├── bitable_executor.py    # 多维表格执行器
├── result_formatter.py    # 结果格式化器
├── intelligent_qa.py      # 智能问答系统
├── app.py                 # Flask应用主程序
├── test.py                # 测试脚本
├── requirements.txt       # Python依赖
└── README.md              # 项目说明
```

## 快速开始

### 1. 安装依赖

```bash
cd feishu-bitable-qa
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件（参考 `.env.example`）：

```bash
# 飞书应用配置
FEISHU_APP_ID=your_feishu_app_id
FEISHU_APP_SECRET=your_feishu_app_secret

# 多维表格配置
DEFAULT_APP_TOKEN=your_bitable_app_token
DEFAULT_TABLE_ID=your_table_id

# 智普大模型配置（必填）
ZHIPU_API_KEY=your_zhipu_api_key
ZHIPU_API_URL=https://open.bigmodel.cn/api/paas/v4/chat/completions

# Flask服务配置
FLASK_HOST=0.0.0.0
FLASK_PORT=80
FLASK_DEBUG=false

# 日志配置
LOG_LEVEL=INFO
```

### 3. 运行服务

```bash
python app.py
```

服务将在配置的地址启动（默认 `http://0.0.0.0:80`）。

### 4. 配置飞书机器人

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 进入你的应用，配置事件订阅
3. 设置请求地址：`https://your-domain.com/webhook`
4. 订阅事件：`im.message.receive_v1`
5. 添加机器人能力并发布应用

## 使用示例

### 查询类问题

```
用户：查询所有员工
机器人：✅ 查询成功，共找到 10 条记录
━━━━━━━━━━━━━━━━━━━━

📋 记录 1
┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
👤 姓名：张三
🏢 部门：技术部
💼 职位：工程师
🎂 年龄：25
...

用户：查询技术部的员工
机器人：✅ 查询成功，共找到 5 条记录
━━━━━━━━━━━━━━━━━━━━

📋 记录 1
┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
👤 姓名：张三
🏢 部门：技术部
💼 职位：工程师
...
```

### 统计类问题

```
用户：统计技术部的人数
机器人：📊 统计结果
━━━━━━━━━━━━━━━━━━━━

📈 符合条件的记录共有 5 条

💡 查询技术部的员工数量
```

### 帮助信息

```
用户：帮助
机器人：🤖 我是智能问答机器人，可以帮您查询和管理多维表格数据。
...
```

## 核心功能

### 1. 消息去重机制

防止飞书事件重复推送导致的重复回复：

- 基于消息ID的去重缓存
- 5分钟自动过期清理
- 线程安全设计

### 2. 富文本格式解析

自动解析飞书多维表格的富文本格式：

```python
# 原始数据
[{"text": "张三", "type": "text"}]

# 解析后
张三
```

### 3. 智能字段图标

根据字段名称自动匹配图标：

| 字段类型 | 图标 | 示例 |
|---------|------|------|
| 姓名/名字 | 👤 | 姓名：张三 |
| 部门 | 🏢 | 部门：技术部 |
| 职位 | 💼 | 职位：工程师 |
| 年龄 | 🎂 | 年龄：25 |
| 电话/手机 | 📞/📱 | 电话：13800138000 |
| 邮箱 | 📧 | 邮箱：test@example.com |
| 日期 | 📅 | 日期：2024-01-01 |
| 金额 | 💰 | 金额：1000元 |
| 数量/编号 | 🔢 | 数量：10 |

## API接口

### 1. Webhook接口

```
POST /webhook
```

接收飞书消息推送。

### 2. 健康检查

```
GET /health
```

返回服务状态。

### 3. 测试接口

```
POST /test
Content-Type: application/json

{
    "message": "查询所有员工"
}
```

用于测试问答功能。

## 配置说明

### 环境变量配置

所有配置项都在 `.env` 文件中管理，不在代码中硬编码：

| 配置项 | 说明 | 是否必填 |
|--------|------|----------|
| FEISHU_APP_ID | 飞书应用ID | ✅ 必填 |
| FEISHU_APP_SECRET | 飞书应用密钥 | ✅ 必填 |
| DEFAULT_APP_TOKEN | 多维表格App Token | ✅ 必填 |
| DEFAULT_TABLE_ID | 数据表ID | ✅ 必填 |
| ZHIPU_API_KEY | 智普API Key | ✅ 必填 |
| ZHIPU_API_URL | 智普API地址 | 可选 |
| FLASK_HOST | Flask监听地址 | 可选 |
| FLASK_PORT | Flask监听端口 | 可选 |
| FLASK_DEBUG | 调试模式 | 可选 |
| LOG_LEVEL | 日志级别 | 可选 |

## 获取智普API Key

1. 访问 [智普AI开放平台](https://open.bigmodel.cn/)
2. 注册并登录账号
3. 在控制台创建API Key
4. 将API Key配置到 `.env` 文件的 `ZHIPU_API_KEY`

## 飞书应用权限

确保飞书应用具有以下权限：

- `bitable:record:read` - 读取多维表格记录
- `bitable:record:write` - 写入多维表格记录
- `im:message` - 消息相关权限
- `im:message:send_as_bot` - 以机器人身份发送消息

## 部署建议

### 使用Gunicorn部署

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:80 app:app
```

### 使用Docker部署

创建 `Dockerfile`：

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 80

CMD ["python", "app.py"]
```

构建并运行：

```bash
docker build -t feishu-bitable-qa .
docker run -p 80:80 --env-file .env feishu-bitable-qa
```

## 注意事项

1. **配置安全**：`.env` 文件包含敏感信息，已在 `.gitignore` 中配置忽略
2. **API Key安全**：不要将智普API Key提交到代码仓库
3. **网络访问**：确保服务器可以被飞书服务器访问
4. **权限配置**：确保飞书应用具有足够的权限
5. **日志监控**：建议配置日志监控以便排查问题

## 故障排查

### 1. 无法收到消息

- 检查飞书应用事件订阅配置
- 确认服务器可以被公网访问
- 查看应用日志确认是否收到请求

### 2. 大模型调用失败

- 确认ZHIPU_API_KEY配置正确
- 检查智普账户余额
- 查看日志中的错误信息

### 3. 多维表格查询失败

- 确认飞书应用权限配置
- 检查APP_TOKEN和TABLE_ID是否正确
- 查看飞书开放平台的API调用日志

### 4. 重复回复问题

- 系统已内置消息去重机制
- 检查日志中是否有"消息已处理，跳过"的提示
- 确认消息ID是否正确传递

### 5. 显示格式问题

- 系统会自动解析富文本格式
- 如果显示异常，请检查多维表格字段类型
- 查看日志中的原始数据格式

## 技术栈

- **后端框架**：Flask 3.0
- **大模型**：智普GLM-4
- **API调用**：requests
- **环境变量**：python-dotenv
- **日志**：Python logging

## 更新日志

### v1.1.0 (2024-03-04)
- ✨ 添加消息去重机制，防止重复回复
- 🎨 优化回复格式，添加字段图标
- 🔧 修复富文本格式解析问题
- 🔒 配置迁移到.env文件，提高安全性
- 📝 完善文档和使用说明

### v1.0.0 (2024-03-04)
- 🎉 初始版本发布
- 🤖 集成智普大模型
- 📊 支持多维表格查询和统计

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交Issue或Pull Request。
