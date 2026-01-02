# 🔬 Universal-SciAgent

基于火山引擎 VeADK 的多智能体科研助手 | Multi-Agent Scientific Research Assistant powered by VeADK

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

### 方式一：本地运行

```bash
# 1. 克隆项目
git clone https://github.com/wanghui2323/Universal-SciAgent.git
cd Universal-SciAgent

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置 API 密钥
cp .env.example .env
# 编辑 .env，填入火山引擎 ARK API 密钥

# 5. 运行服务
python agent.py
```

### 方式二：Jupyter Notebook

```bash
jupyter notebook notebooks/demo.ipynb
```

### 方式三：部署到 AgentKit

```bash
# 1. 安装 AgentKit CLI
pip install agentkit-sdk-python

# 2. 初始化项目
agentkit init --from-agent agent.py --agent-var root_agent

# 3. 配置环境变量
agentkit config --runtime_envs "MODEL_AGENT_NAME=your-endpoint-id"
agentkit config --runtime_envs "MODEL_AGENT_API_KEY=your-api-key"

# 4. 部署
agentkit launch

# 5. 测试
agentkit invoke "帮我搜索关于大语言模型的最新研究"
```

---

## 🔧 配置说明

### 环境变量 (.env)

```ini
# 火山引擎 ARK API (必填)
MODEL_AGENT_NAME=your-endpoint-id      # 模型端点 ID
MODEL_AGENT_API_KEY=your-api-key       # API 密钥
MODEL_AGENT_API_BASE=https://ark.cn-beijing.volces.com/api/v3/
MODEL_AGENT_PROVIDER=openai

# Embedding 模型 (可选，用于长期记忆)
MODEL_EMBEDDING_NAME=your-embedding-endpoint-id
MODEL_EMBEDDING_API_KEY=your-api-key
```

### 获取 API 密钥

1. 访问 [火山引擎控制台](https://console.volcengine.com/ark/)
2. 创建模型端点 (推荐: doubao-pro-32k)
3. 复制端点 ID 和 API 密钥

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
