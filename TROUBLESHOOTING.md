# 🔧 常见问题解决指南 (Troubleshooting)

> 本文档收集了用户在安装和使用过程中可能遇到的常见问题及解决方案

---

## 📦 安装问题

### 问题 1: SSL 证书验证失败 (macOS)

**症状**:
```bash
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate
ERROR: Could not find a version that satisfies the requirement veadk-python>=0.5.3
```

**影响用户**: macOS 用户（尤其是首次安装 Python 3.10+）

**根本原因**: macOS Python 安装后 SSL 证书未自动配置（这是 Python 官方安装包的已知问题）

#### ✅ 解决方案（3选1）

**方案 1: 使用国内镜像源（推荐，最快）**

```bash
pip3 install -r requirements.txt \
  -i https://pypi.tuna.tsinghua.edu.cn/simple \
  --trusted-host pypi.tuna.tsinghua.edu.cn
```

其他可用镜像：
- 阿里云: `https://mirrors.aliyun.com/pypi/simple/`
- 豆瓣: `https://pypi.douban.com/simple`
- 中科大: `https://pypi.mirrors.ustc.edu.cn/simple/`

**方案 2: 安装 SSL 证书（一次性解决）**

```bash
# 双击运行（推荐）
open "/Applications/Python 3.12/Install Certificates.command"

# 或终端运行
sudo "/Applications/Python 3.12/Install Certificates.command"

# 然后正常安装
pip3 install -r requirements.txt
```

**方案 3: 永久配置镜像源**

```bash
# 创建 pip 配置
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << 'EOF'
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF

# 以后所有 pip install 都自动使用镜像
pip3 install -r requirements.txt
```

---

### 问题 2: 找不到 Python 或 pip

**症状**:
```bash
command not found: python
command not found: pip
```

**解决方案**:

```bash
# 使用 python3 和 pip3
python3 --version
pip3 --version

# 或创建别名
echo "alias python=python3" >> ~/.zshrc
echo "alias pip=pip3" >> ~/.zshrc
source ~/.zshrc
```

---

### 问题 3: 权限错误

**症状**:
```bash
ERROR: Could not install packages due to an OSError: [Errno 13] Permission denied
```

**解决方案**:

```bash
# 方案 1: 使用 --user 安装到用户目录
pip3 install -r requirements.txt --user

# 方案 2: 使用虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

---

### 问题 4: 依赖冲突

**症状**:
```bash
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed
```

**解决方案**:

```bash
# 创建干净的虚拟环境
python3 -m venv venv_clean
source venv_clean/bin/activate
pip3 install --upgrade pip
pip3 install -r requirements.txt
```

---

## 🚀 运行问题

### 问题 5: 导入错误 `ModuleNotFoundError`

**症状**:
```python
ModuleNotFoundError: No module named 'veadk'
```

**原因**: 依赖未正确安装或虚拟环境未激活

**解决方案**:

```bash
# 1. 确认依赖已安装
pip3 list | grep veadk

# 2. 如果未安装，重新安装
pip3 install veadk-python>=0.5.3

# 3. 如果使用虚拟环境，确保已激活
source venv/bin/activate
```

---

### 问题 6: API Key 错误

**症状**:
```python
AuthenticationError: The API key format is incorrect
```

**解决方案**:

```bash
# 1. 检查 .env 文件是否存在
ls -la .env

# 2. 检查配置内容
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
key = os.getenv('MODEL_AGENT_API_KEY')
endpoint = os.getenv('MODEL_AGENT_NAME')
print(f'API Key: {key[:10] if key else None}...')
print(f'Endpoint: {endpoint}')
"

# 3. 确认格式正确
# MODEL_AGENT_NAME 应该以 'ep-' 开头
# MODEL_AGENT_API_KEY 应该是长字符串
```

---

### 问题 7: Agent 无响应或超时

**症状**: Agent 运行时无响应或超时

**可能原因**:
1. 网络连接问题
2. API 配额用完
3. 模型端点不可用

**解决方案**:

```bash
# 1. 测试网络连接
curl https://ark.cn-beijing.volces.com/api/v3/

# 2. 检查 API 配额（登录火山引擎控制台查看）

# 3. 尝试更换模型端点

# 4. 查看日志
tail -f /tmp/logs/agent.log
```

---

## 💻 Jupyter Notebook 问题

### 问题 8: Jupyter 无法找到模块

**症状**: Notebook 中导入失败，但终端可以

**解决方案**:

```bash
# 确保 Jupyter 使用正确的 Python
which python3
which jupyter

# 在虚拟环境中安装 Jupyter
source venv/bin/activate
pip3 install jupyter ipykernel
python3 -m ipykernel install --user --name=sciagent

# 启动 Jupyter，选择 'sciagent' kernel
jupyter notebook
```

---

## ☁️ AgentKit 部署问题

### 问题 9: agentkit 命令找不到

**症状**:
```bash
command not found: agentkit
```

**解决方案**:

```bash
# 安装 AgentKit CLI
pip3 install agentkit-sdk-python

# 验证安装
agentkit --version

# 如果仍然找不到，添加到 PATH
export PATH="$HOME/.local/bin:$PATH"
```

---

### 问题 10: AgentKit 初始化失败

**症状**: `agentkit init` 报错

**解决方案**:

```bash
# 1. 确认 agent.py 存在
ls -la agent.py

# 2. 确认 root_agent 定义正确
python3 -c "from agent import root_agent; print(root_agent.name)"

# 3. 使用完整路径
agentkit init --from-agent $(pwd)/agent.py --agent-var root_agent
```

---

## 🔍 其他问题

### 问题 11: 找不到配置文件

**症状**: 
```python
FileNotFoundError: [Errno 2] No such file or directory: 'config.yaml'
```

**解决方案**:

```bash
# 复制配置模板
cp config.yaml.example config.yaml

# 编辑配置
nano config.yaml
```

---

### 问题 12: ChromaDB 错误

**症状**:
```python
RuntimeError: Your system has an unsupported version of sqlite3
```

**解决方案**:

```bash
# 方案 1: 升级 ChromaDB
pip3 install --upgrade chromadb

# 方案 2: 使用兼容版本
pip3 install chromadb==0.4.22

# 方案 3: 清理旧数据
rm -rf /tmp/chromadb
```

---

## 📊 性能问题

### 问题 13: 响应速度慢

**可能原因**:
1. 网络延迟
2. 模型选择（大模型更慢）
3. 搜索论文数量过多

**优化方案**:

```python
# 1. 减少搜索结果数量
results = await arxiv_search("query", max_results=5)  # 从 20 减到 5

# 2. 使用更快的模型
# 编辑 .env 文件，选择更小的模型

# 3. 启用缓存（VeADK 自动缓存）
# 重复相同问题会使用缓存
```

---

## 🆘 获取帮助

如果以上方案都无法解决您的问题：

1. **查看详细日志**:
   ```bash
   # Agent 日志
   tail -f /tmp/logs/agent.log
   
   # Python 错误详情
   python3 agent.py 2>&1 | tee debug.log
   ```

2. **运行诊断脚本**:
   ```bash
   python3 verify_installation.py
   ```

3. **提交 Issue**:
   - 访问: https://github.com/wanghui2323/Universal-SciAgent/issues
   - 提供: Python 版本、错误信息、完整日志

4. **查看官方文档**:
   - VeADK: https://volcengine.github.io/veadk-python/
   - AgentKit: https://volcengine.github.io/agentkit-sdk-python/

---

## 📝 问题反馈

如果您遇到了新的问题并成功解决，欢迎提交 PR 补充本文档！

**贡献格式**:
```markdown
### 问题 X: [问题标题]

**症状**: [错误信息或现象]

**解决方案**:
```bash
[解决命令]
```
```

---

**最后更新**: 2026-01-04  
**维护者**: Universal-SciAgent Team

