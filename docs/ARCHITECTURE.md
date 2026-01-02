# Universal-SciAgent 架构说明

## 🏗️ 核心架构原则

**本项目完全基于 VeADK 框架开发，不混用其他Agent框架（如LangChain、AutoGen等）**

---

## 📚 框架选择

### 为什么选择VeADK？

1. **轻量级**: VeADK专注于Agent开发，不像LangChain那样庞大
2. **火山引擎生态**: 与豆包模型、AgentKit深度集成
3. **简单易用**: API简洁，配置清晰
4. **部署友好**: 支持AgentKit一键部署

### VeADK vs 其他框架

| 特性 | VeADK | LangChain | AutoGen |
|------|-------|-----------|---------|
| **复杂度** | 简单 | 复杂 | 中等 |
| **LLM支持** | 火山引擎/OpenAI | 多种 | 多种 |
| **部署** | AgentKit | 自行部署 | 自行部署 |
| **学习曲线** | 平缓 | 陡峭 | 中等 |
| **适用场景** | 专注Agent | 通用LLM应用 | 多Agent对话 |

---

## 🎯 本项目架构

### 1. Agent层级结构（自己实现）

```
Master Agent (主智能体)
    ├── Literature Agent (文献检索)
    ├── Hypothesis Agent (假设生成)
    ├── Experiment Design Agent (实验设计)
    └── Writing Agent (报告生成)
```

**说明**：
- ✅ 使用Python原生类继承实现多Agent协作
- ✅ **不使用**LangChain的Agent抽象
- ✅ **不使用**AutoGen的ConversableAgent

### 2. LLM调用层（VeADK）

```python
from veadk import Agent

class BaseAgent:
    def __init__(self):
        self.veadk_agent = Agent()  # 使用VeADK Agent
    
    async def call_llm(self, prompt: str) -> str:
        response = asyncio.run(self.veadk_agent.run(prompt))
        return str(response)
```

**说明**：
- ✅ 所有LLM调用通过VeADK
- ❌ **不使用**LangChain的ChatOpenAI
- ❌ **不使用**直接的OpenAI API

### 3. 工具层（自己实现）

```python
# 自己实现的Tool Registry
class ToolRegistry:
    def register(self, name, func):
        self._tools[name] = func
    
    async def call(self, tool_name, **kwargs):
        return await self._tools[tool_name](**kwargs)
```

**说明**：
- ✅ 自己实现工具注册和调用
- ❌ **不使用**LangChain的Tool抽象
- ✅ 简单、灵活、可控

---

## 📦 依赖分类

### 核心依赖（必需）

```txt
veadk-python>=0.2.27          # VeADK框架
agentkit-sdk-python>=0.2.0    # 部署SDK
```

### 外部API（必需）

```txt
arxiv>=2.1.0                  # 文献搜索
aiohttp>=3.9.0                # HTTP请求
chromadb>=0.4.22              # 向量数据库
```

### 数据处理（必需）

```txt
pandas>=2.1.0                 # 数据处理
pydantic>=2.5.0               # 数据验证
pypdf2>=3.0.0                 # PDF解析
```

### 不需要的依赖（已移除）

```txt
❌ langchain                   # 另一个Agent框架，不需要
❌ langchain-community         # LangChain社区包，不需要
❌ langchain-core              # LangChain核心，不需要
```

---

## 🔧 VeADK集成方式

### 配置（config.yaml）

```yaml
model:
  agent:
    provider: openai
    name: doubao-pro-32k
    api_base: https://ark.cn-beijing.volces.com/api/v3/
    api_key: ${VEADK_API_KEY}
```

### 初始化

```python
from veadk import Agent

# VeADK自动读取config.yaml
agent = Agent()
```

### 调用

```python
import asyncio

response = asyncio.run(agent.run("你的问题"))
```

---

## 🎨 设计模式

### 1. 策略模式（Agent调度）

```python
class MasterAgent:
    def _select_agents(self, task_type):
        if task_type == "literature_review":
            return [LiteratureAgent(), WritingAgent()]
        elif task_type == "hypothesis_generation":
            return [LiteratureAgent(), HypothesisAgent(), 
                    ExperimentDesignAgent(), WritingAgent()]
```

### 2. 模板方法模式（BaseAgent）

```python
class BaseAgent(ABC):
    @abstractmethod
    async def execute(self, context):
        pass  # 子类实现具体逻辑
    
    async def call_llm(self, prompt):
        # 统一的LLM调用方法
        return await self.veadk_agent.run(prompt)
```

### 3. 注册模式（Tool Registry）

```python
@tool_registry.register(name="arxiv_search")
async def arxiv_search(query: str):
    # 工具实现
    pass
```

---

## 🚀 执行流程

```
1. 用户输入 Task
   ↓
2. Master Agent 解析任务
   ↓
3. Master Agent 生成执行计划
   ↓
4. 调用各个 Expert Agent (通过VeADK)
   ├── Literature Agent → 文献检索
   ├── Hypothesis Agent → 假设生成
   ├── Experiment Design Agent → 实验设计
   └── Writing Agent → 报告生成
   ↓
5. 返回 TaskResult
```

**关键点**：
- ✅ Agent之间通过共享context传递数据
- ✅ 所有LLM调用通过VeADK
- ✅ 工具调用通过自己的ToolRegistry
- ❌ 不使用LangChain的Chain机制

---

## 📊 与LangChain的对比

| 功能 | 本项目（VeADK） | LangChain方案 |
|------|----------------|--------------|
| **Agent定义** | 继承BaseAgent | 继承ConversableAgent |
| **LLM调用** | VeADK Agent | ChatOpenAI/ChatAnthropic |
| **工具注册** | ToolRegistry | @tool装饰器 |
| **Agent协作** | 显式调用 | Chain/Graph |
| **配置方式** | config.yaml | 代码配置 |
| **复杂度** | 低 | 高 |
| **部署** | AgentKit | 自行部署 |

---

## 🎯 为什么不用LangChain？

### 1. **VeADK更轻量**
- LangChain: 10,000+ 行代码，数百个类
- VeADK: 核心代码简洁，专注Agent开发

### 2. **VeADK与火山引擎生态集成**
- 直接对接豆包模型
- 支持AgentKit部署
- 官方维护和优化

### 3. **VeADK更容易理解**
- API简单直接
- 配置清晰（config.yaml）
- 学习曲线平缓

### 4. **避免过度工程**
- 本项目需求明确，不需要LangChain的通用性
- 自己实现的Agent协作更灵活
- 减少依赖，降低维护成本

---

## 🔄 如果需要LangChain功能怎么办？

### VeADK可以满足：

| LangChain功能 | VeADK替代方案 |
|--------------|--------------|
| **LLM调用** | `Agent().run()` |
| **Prompt模板** | Python f-string |
| **Memory** | 自己维护context字典 |
| **Tools** | 自己实现ToolRegistry |
| **Chains** | 显式调用Agent序列 |
| **Vector Store** | ChromaDB（独立使用） |

---

## 📝 总结

### ✅ 本项目特点

1. **纯VeADK框架** - 不混用其他Agent框架
2. **自己实现Agent协作** - 灵活可控
3. **轻量级依赖** - 只安装真正需要的包
4. **清晰的架构** - 易于理解和维护
5. **火山引擎生态** - 与豆包、AgentKit深度集成

### ⚠️ 注意事项

- ❌ 不要添加LangChain依赖
- ❌ 不要添加AutoGen依赖
- ✅ 使用VeADK作为唯一的Agent框架
- ✅ 外部工具（arxiv, chromadb等）直接使用，不通过LangChain封装

---

**参考文档**:
- VeADK: https://github.com/volcengine/veadk-python
- AgentKit: https://github.com/volcengine/agentkit-sdk-python

