# 🚀 Universal-SciAgent 部署指南

## 部署方式概览

Universal-SciAgent支持三种部署方式：

1. **本地部署** - 开发和测试
2. **Docker部署** - 容器化部署
3. **AgentKit部署** - 部署到Volcengine AgentKit Runtime（推荐）

---

## 方式1: 本地部署

### 适用场景
- 本地开发和测试
- 小规模使用
- 学习和研究

### 部署步骤

#### 1. 克隆仓库

```bash
git clone https://github.com/your-org/Universal-SciAgent.git
cd Universal-SciAgent
```

#### 2. 创建虚拟环境

```bash
# 使用venv
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 或使用conda
conda create -n sciagent python=3.10
conda activate sciagent
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

#### 4. 配置环境变量

```bash
cp .env.example .env
# 编辑.env，设置VEADK_API_KEY
```

#### 5. 运行测试

```bash
python examples/simple_example.py
```

---

## 方式2: Docker部署

### 适用场景
- 生产环境部署
- 多实例部署
- 云服务器部署

### 部署步骤

#### 1. 创建Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY backend/ backend/
COPY config/ config/
COPY .env .env

# 创建数据目录
RUN mkdir -p data/chromadb data/logs

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 暴露端口（如果需要API服务）
EXPOSE 8000

# 启动命令
CMD ["python", "-m", "backend.api.server"]
```

#### 2. 构建镜像

```bash
docker build -t universal-sciagent:latest .
```

#### 3. 运行容器

```bash
docker run -d \
  --name sciagent \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e VEADK_API_KEY=your_api_key \
  universal-sciagent:latest
```

#### 4. Docker Compose（推荐）

创建`docker-compose.yml`：

```yaml
version: '3.8'

services:
  sciagent:
    build: .
    container_name: universal-sciagent
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./config:/app/config
    environment:
      - VEADK_API_KEY=${VEADK_API_KEY}
      - VEADK_API_BASE=${VEADK_API_BASE}
      - VEADK_MODEL=${VEADK_MODEL}
    restart: unless-stopped
```

启动：

```bash
docker-compose up -d
```

---

## 方式3: AgentKit部署（推荐）

### 适用场景
- 生产环境
- 需要高可用性
- 需要监控和日志
- 自动扩缩容

### 前提条件

1. **安装AgentKit CLI**

```bash
pip install agentkit-sdk-python
```

2. **配置火山引擎凭证**

```bash
# 设置访问凭证
export VOLCENGINE_ACCESS_KEY_ID=your_access_key
export VOLCENGINE_SECRET_ACCESS_KEY=your_secret_key
```

### 部署步骤

#### 1. 初始化配置

```bash
# 在项目根目录
agentkit init
```

这会创建`agentkit.yaml`配置文件（我们已经提供了`agentkit_deploy.yaml`模板）。

#### 2. 检查配置

确保`agentkit_deploy.yaml`配置正确：

```yaml
name: universal-sciagent
version: 1.0.0

runtime:
  python_version: "3.10"
  memory: 2048
  timeout: 600

environment:
  VEADK_API_KEY: ${VEADK_API_KEY}
  VEADK_MODEL: "doubao-pro-32k"

entrypoint:
  module: backend.agents.master_agent
  class: MasterAgent
  method: run
```

#### 3. 部署

```bash
# 使用默认配置
agentkit deploy

# 或指定配置文件
agentkit deploy -f agentkit_deploy.yaml
```

#### 4. 查看状态

```bash
# 查看部署状态
agentkit status

# 查看日志
agentkit logs

# 查看指标
agentkit metrics
```

#### 5. 调用API

部署成功后，AgentKit会提供API端点：

```bash
# 文献综述
curl -X POST https://your-endpoint.volces.com/literature-review \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["Transformer", "Computer Vision"],
    "domain": ["computer_science"],
    "max_papers": 15
  }'

# 假设生成
curl -X POST https://your-endpoint.volces.com/hypothesis-generation \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["perovskite", "solar cell"],
    "domain": ["materials_science"],
    "num_hypotheses": 3
  }'
```

#### 6. 更新部署

```bash
# 修改代码后重新部署
agentkit deploy --force

# 或使用版本管理
agentkit deploy --version 1.0.1
```

#### 7. 扩缩容

```bash
# 手动扩容
agentkit scale --instances 5

# 或在配置文件中设置自动扩缩容
```

#### 8. 回滚

```bash
# 回滚到上一个版本
agentkit rollback

# 回滚到指定版本
agentkit rollback --version 1.0.0
```

#### 9. 删除部署

```bash
agentkit delete
```

---

## 监控与日志

### 本地部署

日志存储在`data/logs/`目录：

```bash
tail -f data/logs/agent.log
```

### Docker部署

查看容器日志：

```bash
docker logs -f sciagent
```

### AgentKit部署

使用AgentKit内置监控：

```bash
# 实时日志
agentkit logs --follow

# 查看错误日志
agentkit logs --level error

# 查看性能指标
agentkit metrics --window 1h
```

---

## 性能优化

### 1. 缓存配置

在`.env`中配置Redis缓存（可选）：

```env
REDIS_HOST=localhost
REDIS_PORT=6379
ENABLE_CACHE=true
```

### 2. 并发控制

在`agentkit_deploy.yaml`中配置：

```yaml
scaling:
  min_instances: 2
  max_instances: 10
  target_cpu_utilization: 70
```

### 3. 超时设置

```yaml
runtime:
  timeout: 600  # 10分钟
```

### 4. 内存优化

```yaml
resources:
  cpu: 2
  memory: 2048  # MB
```

---

## 安全配置

### 1. API密钥管理

**不要**将API密钥硬编码在代码中。使用环境变量：

```bash
export VEADK_API_KEY=your_secret_key
```

### 2. 网络隔离

Docker部署时使用自定义网络：

```bash
docker network create sciagent-network
docker run --network sciagent-network ...
```

### 3. 访问控制

AgentKit部署支持IP白名单：

```yaml
security:
  allowed_ips:
    - "10.0.0.0/8"
    - "172.16.0.0/12"
```

---

## 故障排查

### 问题1: API密钥无效

**错误**: `ValueError: VEADK_API_KEY is required`

**解决**:
```bash
# 检查环境变量
echo $VEADK_API_KEY

# 重新设置
export VEADK_API_KEY=your_key
```

### 问题2: 内存不足

**错误**: `MemoryError` 或容器被OOM Kill

**解决**:
- 增加Docker内存限制：`docker run -m 4g ...`
- 或在AgentKit配置中增加内存：`memory: 4096`

### 问题3: ChromaDB初始化失败

**错误**: `Failed to initialize ChromaDB`

**解决**:
```bash
# 检查目录权限
chmod -R 755 data/chromadb

# 或重新创建目录
rm -rf data/chromadb
mkdir -p data/chromadb
```

### 问题4: PDF解析超时

**错误**: `aiohttp.ClientTimeout`

**解决**:
增加超时设置（在`backend/tools/literature_tools.py`中）：
```python
timeout=aiohttp.ClientTimeout(total=60)  # 增加到60秒
```

---

## 生产环境检查清单

- [ ] API密钥已配置且有效
- [ ] 日志目录已创建且可写
- [ ] 数据库目录已创建且可写
- [ ] 防火墙规则已配置
- [ ] 监控告警已设置
- [ ] 备份策略已制定
- [ ] 负载测试已通过
- [ ] 文档已更新

---

## 成本估算

### 按使用量计费（基于豆包模型）

| 任务类型 | 单次成本 | 月100次 | 月1000次 |
|---------|---------|---------|----------|
| 文献综述 | $1.20 | $120 | $1,200 |
| 假设生成 | $1.80 | $180 | $1,800 |
| 跨学科任务 | $2.10 | $210 | $2,100 |

### AgentKit运行时成本

- 计算资源：约$0.05/小时（2核2G）
- 存储：约$0.01/GB/月
- 网络：按流量计费

---

## 技术支持

- **文档**: [README.md](README.md), [QUICKSTART.md](QUICKSTART.md)
- **GitHub Issues**: https://github.com/your-org/Universal-SciAgent/issues
- **Email**: your-email@example.com

---

**部署愉快！🚀**

