# Universal-SciAgent 快速启动指南

> 5分钟快速上手 Universal-SciAgent

---

## 📋 前置要求

- **Python**: 3.12+ 
- **环境管理**: venv 或 conda
- **API Key**: 火山引擎 ARK (豆包) API Key

---

## 🚀 快速启动（3步）

### Step 1: 环境配置

```bash
# 1. 进入项目目录
cd Universal-SciAgent

# 2. 创建虚拟环境
python3 -m venv venv

# 3. 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

# 4. 安装依赖（推荐：先安装核心依赖）
pip install -r requirements.txt

# 如果遇到安装慢的问题，可以先安装最小依赖：
# pip install -r requirements.minimal.txt
```

### Step 2: 配置 API Key

```bash
# 1. 复制配置模板
cp .env.example .env

# 2. 编辑 .env 文件
# 在 macOS/Linux:
nano .env
# 或
vim .env

# 在 Windows:
notepad .env
```

在 `.env` 文件中设置：

```ini
# 必须配置（从火山引擎控制台获取）
VEADK_API_KEY=your_volcengine_ark_api_key_here

# 可选配置
VEADK_MODEL=doubao-pro-32k
SEMANTIC_SCHOLAR_API_KEY=your_ss_key  # 可选，提升文献搜索质量
```

**获取 API Key**:
1. 访问 [火山引擎控制台](https://console.volcengine.com/ark)
2. 创建 API Key
3. 复制到 `.env` 文件

### Step 3: 运行示例

```bash
# 运行完整示例（推荐首次使用）
python examples/simple_example.py

# 或运行单个示例：
python examples/simple_example.py 1  # 文献综述
python examples/simple_example.py 2  # 假设生成
python examples/simple_example.py 3  # 实验设计
python examples/simple_example.py 4  # 完整研究流程
```

**预期输出**:
```
================================================================================
Universal-SciAgent Examples (Powered by VeADK)
================================================================================

VeADK Features Used:
  ✓ Multi-Agent System (Master + 4 Specialists)
  ✓ Memory Management (Short-term + Long-term)
  ✓ Tool Integration (arXiv, Semantic Scholar, PubMed)
  ✓ Workflow Orchestration (Hierarchical)
  ✓ Cost Tracking & Observability
================================================================================

================================================================================
Example 1: Literature Review
================================================================================

Topic: 深度学习在计算机视觉中的最新进展
Domain: computer_science

Executing literature review workflow...

--- Results ---
Agent: literature
Task Type: literature_review
Cost: $0.0234

Content Preview:
基于最新文献调研，深度学习在计算机视觉领域取得了以下进展...

--- Cost Statistics ---
Total Cost: $0.0234
Total Tokens: 12,345
Total Calls: 3
...
```

---

## 📚 使用 Jupyter Notebook

如果您更喜欢交互式环境：

```bash
# 1. 确保已安装 Jupyter
pip install jupyter  # 如果 requirements.txt 已包含则跳过

# 2. 启动 Jupyter
jupyter notebook

# 3. 在浏览器中打开 notebooks/demo.ipynb
```

---

## 🛠️ 常见问题

### Q1: pip install 很慢或失败

**方案 A - 使用国内镜像**:
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**方案 B - 先安装核心依赖**:
```bash
# 只安装核心依赖（更快）
pip install -r requirements.minimal.txt

# 需要时再安装完整依赖
pip install -r requirements.txt
```

**方案 C - 使用 uv (最快)**:
```bash
# 安装 uv
pip install uv

# 使用 uv 安装依赖（速度快10倍+）
uv pip install -r requirements.txt
```

### Q2: 提示 "No module named 'veadk'"

**解决方案**:
```bash
# 确认虚拟环境已激活
which python  # 应该显示 venv/bin/python

# 重新安装 veadk
pip install --upgrade veadk-python>=0.5.0
```

### Q3: API Key 错误

**检查清单**:
- [ ] `.env` 文件存在且位于项目根目录
- [ ] `VEADK_API_KEY` 已正确设置（无引号）
- [ ] API Key 在火山引擎控制台是激活状态
- [ ] API Key 有足够的配额

**测试 API Key**:
```bash
# 创建测试脚本
cat > test_api.py << 'EOF'
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("VEADK_API_KEY")
print(f"API Key loaded: {'✓' if api_key else '✗'}")
print(f"API Key (first 10 chars): {api_key[:10] if api_key else 'None'}...")
EOF

python test_api.py
```

### Q4: ChromaDB 数据库错误

**解决方案**:
```bash
# 删除旧的数据库（会丢失已存储的数据）
rm -rf data/chromadb

# 重新运行
python examples/simple_example.py
```

### Q5: 成本显示为 $0.00

**原因**: VeADK 的完整多智能体功能可能还未发布，系统使用了 fallback 模式。

**解决方案**:
- 这是正常的，fallback 模式仍然可用
- 等待 VeADK 0.5.0+ 正式发布
- 当前使用的是基础 Agent 模式

---

## 🎯 下一步

### 1. 尝试自定义任务

```python
# custom_task.py
import asyncio
from backend.agents.sci_agent_system import get_sci_agent_system

async def main():
    system = get_sci_agent_system()
    
    # 自定义您的研究任务
    result = await system.literature_review(
        topic="您感兴趣的研究主题",
        domain="computer_science",  # 或其他领域
        max_papers=20
    )
    
    print(result.content)
    print(f"\nCost: ${result.cost_usd:.4f}")

asyncio.run(main())
```

### 2. 探索不同领域

支持的领域：
- `computer_science` - 计算机科学
- `materials_science` - 材料科学
- `biomedical` - 生物医学
- `physics` - 物理学
- `chemistry` - 化学

```python
# 生物医学示例
result = await system.literature_review(
    topic="CRISPR基因编辑技术的最新进展",
    domain="biomedical"
)
```

### 3. 完整研究流程

```python
# 运行完整的研究工作流
result = await system.run_task(
    task="探索量子计算在密码学中的应用与安全性分析",
    domain="computer_science",
    task_type="full_research"
)

# 查看所有结果
print("文献综述:", result['result']['literature_review'])
print("研究假设:", result['result']['hypotheses'])
print("实验设计:", result['result']['experiment_design'])
print("研究报告:", result['result']['report'])
```

### 4. 查看成本统计

```python
from backend.utils.cost_tracker import get_cost_tracker

# 获取成本统计
tracker = get_cost_tracker()
stats = tracker.get_statistics()

print(f"总成本: ${stats['total_cost_usd']:.4f}")
print(f"总调用: {stats['total_calls']}")

# 按 Agent 查看
for agent, metrics in stats['cost_by_agent'].items():
    print(f"{agent}: ${metrics['cost']:.4f}")
```

---

## 📖 深入学习

### 文档
- **[README.md](README.md)** - 项目概述和功能介绍
- **[架构设计](VEADK_NATIVE_ARCHITECTURE.md)** - 详细架构说明
- **[VeADK 集成](VEADK_INTEGRATION.md)** - VeADK 功能详解
- **[部署指南](DEPLOYMENT_GUIDE.md)** - 生产环境部署

### 代码示例
- **[examples/simple_example.py](examples/simple_example.py)** - 完整示例代码
- **[notebooks/demo.ipynb](notebooks/demo.ipynb)** - Jupyter 演示

### 源码
- **[backend/agents/sci_agent_system.py](backend/agents/sci_agent_system.py)** - 多智能体系统
- **[backend/tools/veadk_tools.py](backend/tools/veadk_tools.py)** - 工具实现
- **[backend/memory/veadk_memory.py](backend/memory/veadk_memory.py)** - 记忆管理

---

## 💡 使用技巧

### 1. 节省成本

```bash
# 使用更便宜的模型
export VEADK_MODEL=doubao-lite-32k  # 比 pro 便宜 60%

# 限制每次搜索的论文数量
max_papers=10  # 默认 20
```

### 2. 提升速度

```bash
# 启用并行执行（需要 VeADK 0.5.0+）
# 在 config.yaml 中:
advanced:
  parallel:
    enabled: true
    max_workers: 4
```

### 3. 调试模式

```bash
# 设置日志级别为 DEBUG
export LOG_LEVEL=DEBUG

# 运行示例查看详细日志
python examples/simple_example.py
```

---

## 🐛 遇到问题？

### 1. 查看日志
```bash
# 日志文件位置
cat data/logs/veadk.log
```

### 2. 重置环境
```bash
# 删除虚拟环境
rm -rf venv

# 重新开始
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 寻求帮助
- **GitHub Issues**: [提交问题](https://github.com/your-org/Universal-SciAgent/issues)
- **文档**: 查看 [FAQ](README.md#faq)
- **社区**: 加入讨论群（见 README）

---

## ✅ 检查清单

启动前确认：
- [ ] Python 3.12+ 已安装
- [ ] 虚拟环境已创建并激活
- [ ] 依赖已安装 (`pip install -r requirements.txt`)
- [ ] `.env` 文件已配置
- [ ] `VEADK_API_KEY` 已设置
- [ ] 网络连接正常（需要访问 arXiv 等 API）

全部完成后：
```bash
python examples/simple_example.py
```

---

## 🎉 开始使用！

```bash
# 一键运行完整示例
python examples/simple_example.py

# 或使用 Jupyter
jupyter notebook notebooks/demo.ipynb
```

**祝您使用愉快！如有问题，请查看文档或提交 Issue。**

---

<div align="center">

Made with ❤️ using **VeADK**

[Back to README](README.md) | [Architecture](VEADK_NATIVE_ARCHITECTURE.md) | [Deployment](DEPLOYMENT_GUIDE.md)

</div>
