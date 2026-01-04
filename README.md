# 🔬 Universal-SciAgent v1.0.2

基于火山引擎 VeADK 的多智能体科研助手 | Multi-Agent Scientific Research Assistant powered by VeADK

[![Version](https://img.shields.io/badge/Version-1.0.2-purple.svg)](CHANGELOG.md)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://python.org)
[![VeADK](https://img.shields.io/badge/VeADK-0.2.28+-orange.svg)](https://github.com/volcengine/veadk-python)
[![AgentKit](https://img.shields.io/badge/AgentKit-Ready-red.svg)](https://github.com/volcengine/agentkit-sdk-python)

## 📖 简介

Universal-SciAgent 是一个**多智能体科研自动化系统**，帮助研究人员完成：

- 📚 **文献综述** - 自动搜索和分析学术论文
- 💡 **假设生成** - 基于文献提出研究假设
- 🧪 **实验设计** - 设计验证实验方案
- 📝 **报告撰写** - 生成结构化研究报告

支持领域：计算机科学、生物医学、材料科学、物理学、化学

---

## 🚀 快速开始

### 方式一：本地运行（5 步完成）

#### Step 1: 克隆项目
```bash
git clone https://github.com/wanghui2323/Universal-SciAgent.git
cd Universal-SciAgent
```

#### Step 2: 创建虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

#### Step 3: 安装依赖
```bash
# 推荐使用国内镜像（避免 SSL 问题）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
```

#### Step 4: 配置 API 密钥
```bash
cp .env.example .env
nano .env  # 或使用其他编辑器打开
```

在 `.env` 中填入（必填）：
```ini
MODEL_AGENT_NAME=ep-20240101xxxxx-xxxxx    # 从火山方舟获取
MODEL_AGENT_API_KEY=your_api_key_here       # 从火山方舟获取
```

> 📍 获取地址：https://console.volcengine.com/ark/

#### Step 5: 启动服务
```bash
python agent.py
```

服务启动后访问 `http://localhost:8000` 即可使用。

---

### 方式二：Jupyter Notebook

```bash
# 完成 Step 1-4 后
pip install jupyter
jupyter notebook notebooks/demo.ipynb
```

---

### 方式三：部署到 AgentKit 云端

#### Step 1: 准备凭证
从 [火山引擎 IAM](https://console.volcengine.com/iam/keymanage/) 获取 Access Key

#### Step 2: 配置认证
```bash
export VOLC_ACCESSKEY="您的Access_Key"
export VOLC_SECRETKEY="您的Secret_Key"
```

#### Step 3: 初始化并部署
```bash
agentkit init
agentkit launch
```

#### Step 4: 测试
```bash
agentkit invoke "帮我搜索关于大语言模型的最新研究"
```

---

## 🔧 配置说明

### 环境变量 (.env)

| 配置项 | 必填 | 说明 | 获取地址 |
|--------|------|------|----------|
| `MODEL_AGENT_NAME` | ✅ | 模型端点 ID (ep-xxx) | [火山方舟](https://console.volcengine.com/ark/) |
| `MODEL_AGENT_API_KEY` | ✅ | API 密钥 | [火山方舟](https://console.volcengine.com/ark/) |
| `VOLC_ACCESSKEY` | 部署时 | Access Key | [火山 IAM](https://console.volcengine.com/iam/keymanage/) |
| `VOLC_SECRETKEY` | 部署时 | Secret Key | [火山 IAM](https://console.volcengine.com/iam/keymanage/) |
| `SEMANTIC_SCHOLAR_API_KEY` | 可选 | 减少 API 限流 | [Semantic Scholar](https://www.semanticscholar.org/product/api) |

### 完整 .env 示例

```ini
# 必填 - 模型配置
MODEL_AGENT_NAME=ep-20240101xxxxx-xxxxx
MODEL_AGENT_API_KEY=your_api_key_here
MODEL_AGENT_API_BASE=https://ark.cn-beijing.volces.com/api/v3/
MODEL_AGENT_PROVIDER=openai

# 可选 - AgentKit 部署
VOLC_ACCESSKEY=your_access_key
VOLC_SECRETKEY=your_secret_key
```

### 🔑 获取 API 密钥

1. 访问 [火山方舟控制台](https://console.volcengine.com/ark/)
2. 开通服务 → 创建推理接入点 → 获取端点 ID
3. 进入「API Key 管理」→ 创建或复制 API Key
4. 填入 `.env` 文件

---

## 🔐 常见问题

| 问题 | 错误信息 | 解决方案 |
|------|----------|----------|
| SSL 证书错误 | `SSLCertVerificationError` | 使用国内镜像安装：`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn` |
| API 限流 | `Semantic Scholar API error: 429` | 等待几分钟后重试，或配置 `SEMANTIC_SCHOLAR_API_KEY` |
| 模块未找到 | `No module named 'xxx'` | 确认虚拟环境已激活，重新安装依赖 |
| API Key 错误 | `AuthenticationError` | 检查 `.env` 中的 `MODEL_AGENT_API_KEY` 是否正确 |

---

## 💻 使用示例

### Python SDK

```python
import asyncio
from backend.agents.sci_agent_system import get_sci_agent_system

async def main():
    # 初始化系统
    system = get_sci_agent_system()
    
    # 文献综述
    result = await system.literature_review(
        topic="大语言模型在科研中的应用",
        domain="computer_science",
        max_papers=10
    )
    print(result.output)

asyncio.run(main())
```

### AgentKit API

```bash
# 健康检查
curl https://your-endpoint.volceapi.com/ping

# 对话调用
agentkit invoke "帮我搜索关于 Transformer 的最新论文"
```

---

## 📁 项目结构

```
Universal-SciAgent/
├── agent.py              # 主入口 (AgentKit 部署)
├── config.yaml           # 配置文件
├── requirements.txt      # Python 依赖
├── .env.example          # 环境变量模板
├── backend/
│   ├── agents/           # 智能体实现
│   │   └── sci_agent_system.py  # 多智能体系统
│   ├── tools/            # 工具 (arxiv, pubmed...)
│   └── memory/           # 记忆系统
├── notebooks/
│   └── demo.ipynb        # Jupyter 演示
└── docs/                 # 详细文档
```

---

## 🏗️ 技术架构

```
┌────────────────────────────────────────────────┐
│           Universal-SciAgent                    │
├────────────────────────────────────────────────┤
│  Multi-Agent System (VeADK SequentialAgent)    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │Literature│→│Hypothesis│→│Experiment│→Writing│
│  └──────────┘ └──────────┘ └──────────┘       │
├────────────────────────────────────────────────┤
│  Tools: arXiv | Semantic Scholar | PubMed      │
├────────────────────────────────────────────────┤
│  Memory: ShortTerm (Session) + LongTerm (Vector)│
├────────────────────────────────────────────────┤
│            VeADK Agent + Runner                 │
├────────────────────────────────────────────────┤
│         火山引擎 ARK (豆包大模型)                │
└────────────────────────────────────────────────┘
```

---

## 🔗 相关资源

- [VeADK 文档](https://github.com/volcengine/veadk-python) - Agent 开发框架
- [AgentKit SDK](https://github.com/volcengine/agentkit-sdk-python) - 部署工具
- [AgentKit Samples](https://github.com/volcengine/agentkit-samples) - 示例项目
- [火山引擎 ARK](https://www.volcengine.com/product/ark) - 大模型服务

---

## 🧪 测试

```bash
# 运行测试
pytest tests/ -v

# 本地测试对话
python agent.py
# 然后在另一个终端:
curl -X POST http://localhost:8000/invoke \
  -H "Content-Type: application/json" \
  -H "user_id: test" \
  -H "session_id: test" \
  -d '{"prompt": "你好"}'
```

---

## ⚠️ 已知限制

| 问题 | 说明 | 解决方案 |
|------|------|----------|
| SSL 证书错误 | macOS Python 常见问题 | 使用国内镜像或配置 certifi |
| Semantic Scholar 429 | API 速率限制 | 配置 API Key 或等待重试 |
| `/docs` 端点不可用 | AgentKit 与 Pydantic 兼容性 | 不影响核心功能 |

---

## 📄 License

[Apache 2.0](LICENSE)

---

## 🙏 致谢

- [火山引擎](https://www.volcengine.com/) - VeADK & AgentKit
- [arXiv](https://arxiv.org/) - 开放论文数据库
- [Semantic Scholar](https://www.semanticscholar.org/) - 学术搜索 API
- [PubMed](https://pubmed.ncbi.nlm.nih.gov/) - 生物医学文献

---

<div align="center">

**Made with ❤️ using VeADK + AgentKit**

[Report Bug](https://github.com/wanghui2323/Universal-SciAgent/issues) · 
[Request Feature](https://github.com/wanghui2323/Universal-SciAgent/issues)

</div>
