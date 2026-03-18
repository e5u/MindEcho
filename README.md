# 心灵回声 MindEcho

一个专为中国大学生设计的 AI 心理健康平台。

## 功能特性

- 💬 **AI 心理咨询**：基于情绪感知的温暖对话，支持 OpenAI 及内置回复
- 🔍 **情绪检测**：从用户输入中自动识别情绪状态（开心、悲伤、焦虑、愤怒等）
- 📊 **情绪可视化**：记录并展示情绪历史趋势，帮助用户了解自身心理状态
- 🆘 **危机检测**：自动识别自伤/自杀信号，立即提供专业心理援助热线
- 🧠 **AI 记忆系统**：沉淀用户长期情绪模式（压力/焦虑/习惯），生成个性化回应
- 🧾 **AI 心理周报**：自动分析近7天情绪趋势、可能诱因与温和建议
- 🪜 **CBT 引导模块**：通过认知行为风格提问，帮助用户重构消极想法
- ⚡ **一键情绪输入**：快速选择“压力/难过/生气”并获得即时微支持
- 🎯 **个性化日建议**：结合历史情绪与使用行为给出每日建议
- 🔐 **用户认证**：JWT 登录注册，数据安全保护

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | FastAPI + SQLAlchemy + MySQL |
| 前端 | Vue 3 + Vite + Pinia + Vue Router |
| 容器 | Docker + Docker Compose |
| AI | OpenAI API（可选，内置情绪关键词回复兜底） |

## 项目结构

```
MindEcho/
├── backend/                 # FastAPI 后端
│   ├── main.py              # 应用入口
│   ├── requirements.txt
│   ├── Dockerfile
│   └── app/
│       ├── models.py        # 数据库模型
│       ├── schemas.py       # Pydantic 模式
│       ├── auth.py          # JWT 认证
│       ├── database.py      # 数据库连接
│       ├── routers/
│       │   ├── auth.py      # 注册/登录 API
│       │   ├── chat.py      # 对话 API
│       │   └── emotions.py  # 情绪历史 API
│       └── services/
│           ├── ai_service.py       # AI 回复服务
│           ├── emotion_service.py  # 情绪&危机检测
│           ├── memory_service.py   # 长期记忆与个性化建议
│           ├── report_service.py   # 周报生成
│           └── cbt_service.py      # CBT 引导问题
├── frontend/                # Vue 3 前端
│   ├── src/
│   │   ├── views/
│   │   │   ├── Login.vue        # 登录页
│   │   │   ├── Register.vue     # 注册页
│   │   │   ├── Chat.vue         # 聊天页
│   │   │   └── EmotionHistory.vue # 情绪记录页
│   │   ├── stores/auth.js   # Pinia 认证状态
│   │   ├── router/          # Vue Router
│   │   └── api/             # Axios 封装
│   ├── Dockerfile
│   └── nginx.conf
└── docker-compose.yml
```

## 快速开始

### 使用 Docker Compose（推荐）

```bash
# 克隆项目
git clone https://github.com/e5u/MindEcho.git
cd MindEcho

# 配置环境变量（可选，配置 OpenAI）
cp backend/.env.example backend/.env
# 编辑 backend/.env，填入 OPENAI_API_KEY（不填则使用内置回复）

# 启动所有服务
docker-compose up -d

# 访问
# 前端：http://localhost:3000
# 后端 API：http://localhost:8000
# API 文档：http://localhost:8000/docs
```

### 本地开发

**后端：**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，填入 MySQL 连接信息

uvicorn main:app --reload --port 8000
```

**前端：**

```bash
cd frontend
npm install
npm run dev
# 访问 http://localhost:5173
```

## API 文档

启动后端后，访问 http://localhost:8000/docs 查看完整的交互式 API 文档。

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/auth/register` | POST | 用户注册 |
| `/api/auth/login` | POST | 用户登录 |
| `/api/auth/me` | GET | 获取当前用户 |
| `/api/chat/send` | POST | 发送消息（含 AI 回复） |
| `/api/chat/conversations` | GET | 获取对话列表 |
| `/api/chat/conversations/{id}` | GET | 获取对话详情 |
| `/api/emotions/history` | GET | 获取情绪历史 |
| `/api/emotions/trend` | GET | 获取情绪趋势 |
| `/api/emotions/quick-checkin` | POST | 一键情绪输入并返回即时微支持 |
| `/api/emotions/weekly-report` | GET | 获取近7天 AI 心理周报 |
| `/api/emotions/daily-suggestion` | GET | 获取个性化每日建议 |
| `/api/chat/cbt-guidance` | POST | 获取 CBT 风格引导问题 |

### 提示词示例（系统内部）

- **记忆增强提示**：`用户长期情绪记忆：压力模式=high；焦虑模式=medium；习惯模式=熬夜、拖延。请据此个性化回应。`
- **CBT 引导提示**：`请在回复最后加入1-2个CBT引导问题，帮助用户重新看待自动化负面想法。`
- **危机升级流程提示**：`先共情确认，再建议联系身边可信任的人，最后提供热线与紧急就医指引。`

## 心理援助热线

- 📞 北京心理危机研究与干预中心：**010-82951332**
- 📞 全国心理援助热线：**400-161-9995**
- 📞 希望24热线：**400-161-9995**
