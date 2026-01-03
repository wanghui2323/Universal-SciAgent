# 安装指南

## 问题说明

由于 `veadk-python` 和 `agentkit-sdk-python` 可能尚未发布到PyPI，我们提供了几种安装方案。

---

## 方案1: 使用修改后的 requirements.txt（推荐）

我们已经更新了 `requirements.txt`，暂时注释掉了VeADK相关依赖。

### 安装步骤

```bash
# 1. 升级pip
python3 -m pip install --upgrade pip

# 2. 安装基础依赖
pip3 install -r requirements.txt

# 3. 从GitHub安装VeADK（如果可用）
# pip3 install git+https://github.com/volcengine/veadk-python.git

# 4. 从GitHub安装AgentKit（如果可用）
# pip3 install git+https://github.com/volcengine/agentkit-sdk-python.git
```

---

## 方案2: 不依赖VeADK，使用OpenAI/Anthropic

如果VeADK暂时无法安装，可以修改代码使用其他LLM提供商。

### 修改 `backend/agents/base_agent.py`

找到 `__init__` 方法，修改为：

```python
def __init__(self, name: str, description: str = ""):
    self.name = name
    self.description = description
    self.logger = logging.getLogger(f"agent.{name}")
    
    # 使用OpenAI作为替代
    import openai
    self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    self.logger.info(f"Initialized {name} with OpenAI")
```

修改 `call_llm` 方法：

```python
async def call_llm(
    self,
    prompt: str,
    system_prompt: Optional[str] = None,
    max_tokens: int = 4000,
    temperature: float = 0.7
) -> str:
    """Call LLM through OpenAI"""
    try:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        self.logger.error(f"LLM call failed: {e}")
        raise
```

然后在 `.env` 中设置：

```env
OPENAI_API_KEY=your_openai_api_key_here
```

---

## 方案3: 手动克隆VeADK仓库

如果GitHub仓库可用：

```bash
# 克隆VeADK
cd /tmp
git clone https://github.com/volcengine/veadk-python.git
cd veadk-python
pip3 install -e .

# 克隆AgentKit
cd /tmp
git clone https://github.com/volcengine/agentkit-sdk-python.git
cd agentkit-sdk-python
pip3 install -e .

# 回到项目目录
cd Universal-SciAgent
pip3 install -r requirements.txt
```

---

## 方案4: 分步安装（逐个调试）

```bash
# 1. 先升级pip
python3 -m pip install --upgrade pip

# 2. 安装核心依赖（跳过VeADK）
pip3 install langchain>=0.1.0
pip3 install langchain-community>=0.1.0
pip3 install langchain-core>=0.1.0
pip3 install arxiv>=2.1.0
pip3 install requests>=2.31.0
pip3 install aiohttp>=3.9.0
pip3 install chromadb>=0.4.22
pip3 install pandas>=2.1.0
pip3 install numpy>=1.24.0
pip3 install pydantic>=2.5.0
pip3 install pyyaml>=6.0.1
pip3 install pypdf2>=3.0.0
pip3 install python-dotenv>=1.0.0
pip3 install tqdm>=4.66.0
pip3 install tenacity>=8.2.0

# 3. 安装Jupyter（如果需要）
pip3 install jupyter ipython ipywidgets

# 4. 安装替代LLM
pip3 install openai  # 或 anthropic
```

---

## 验证安装

安装完成后，运行测试：

```bash
python3 -c "import pandas; import chromadb; import arxiv; print('✅ 核心依赖安装成功')"
```

---

## 常见问题

### Q1: Anaconda 用户创建虚拟环境报错

**问题**: 使用 `python3 -m venv venv` 报错

**解决**:
```bash
# 使用 conda 创建虚拟环境
conda create -n sciagent python=3.10 -y
conda activate sciagent
pip install -r requirements.txt
```

### Q2: `from typing import override` 报错 ImportError

**问题**: Python 3.10/3.11 中 `typing.override` 不可用

**原因**: `override` 是 Python 3.12 新增的装饰器

**解决方案 A**: 升级到 Python 3.12
```bash
conda create -n sciagent python=3.12 -y
```

**解决方案 B**: 安装 typing_extensions（项目已自动包含）
```bash
pip install typing_extensions>=4.5.0
```

如果问题出现在 agentkit 库内部，需要修改库文件：
```python
# 修改 agentkit 库的 agent_server_app.py
# 将:
from typing import override
# 改为:
try:
    from typing import override
except ImportError:
    from typing_extensions import override
```

### Q3: API 认证错误 - The API key format is incorrect

**问题**:
```
AuthenticationError: litellm.AuthenticationError: OpenAIException - The API key format is incorrect
```

**原因**: 未配置或配置错误的火山引擎 API 密钥

**解决**:
1. 确保创建了 `.env` 文件：`cp .env.example .env`
2. 确保正确填写了以下配置：
   ```ini
   MODEL_AGENT_NAME=ep-xxxxxxxxxx-xxxxx   # 端点ID，格式以 ep- 开头
   MODEL_AGENT_API_KEY=your-actual-api-key
   MODEL_AGENT_API_BASE=https://ark.cn-beijing.volces.com/api/v3/
   ```
3. 如果没有火山引擎账号，请先注册并开通方舟大模型服务

### Q4: chromadb 安装失败

**解决**:
```bash
# 使用conda安装
conda install -c conda-forge chromadb

# 或降低版本
pip3 install chromadb==0.4.0
```

### Q5: langchain 版本冲突

**解决**:
```bash
pip3 install --upgrade langchain langchain-core langchain-community
```

### Q6: PyPDF2 找不到

**解决**:
```bash
# 使用pypdf代替
pip3 install pypdf
```

---

## 下一步

安装完成后，请查看：
- [QUICKSTART.md](QUICKSTART.md) - 快速开始指南
- [README.md](README.md) - 完整文档

---

**如有问题，请提交Issue**: https://github.com/your-org/Universal-SciAgent/issues

