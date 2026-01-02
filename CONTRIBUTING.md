# 贡献指南

感谢您对Universal-SciAgent的关注！我们欢迎任何形式的贡献。

## 🎯 贡献方向

### 1. 新领域配置

添加新的研究领域（如地球科学、经济学等）：

1. 在`config/domains/`创建新的YAML文件
2. 定义领域专用Prompt和方法论模板
3. 添加领域关键词
4. 更新`backend/utils/domain_manager.py`中的`SUPPORTED_DOMAINS`

示例：
```yaml
name: "地球科学"
description: "涵盖气候学、地质学、海洋学等"

tools:
  - arxiv_search
  - semantic_scholar_search

keywords:
  - climate
  - geology
  - oceanography

prompts:
  hypothesis_generation: |
    你是地球科学领域的资深研究员...
```

### 2. 新工具集成

添加新的外部工具（如Google Scholar、专利检索等）：

1. 在`backend/tools/`创建新的工具模块
2. 使用装饰器注册工具：
```python
@tool_registry.register(
    name="google_scholar_search",
    description="Search Google Scholar",
    required_params=["query"]
)
async def google_scholar_search(query: str, max_results: int = 10):
    # Implementation
    pass
```
3. 在领域配置中引用新工具

### 3. Agent改进

- 优化现有Agent的Prompt
- 改进解析逻辑
- 增强错误处理
- 添加缓存机制

### 4. 性能优化

- 并行化工具调用
- 实现结果缓存
- 优化LLM调用（减少token消耗）
- 改进PDF解析速度

### 5. 测试用例

- 为核心模块添加单元测试
- 添加集成测试
- 性能基准测试

## 📝 开发流程

### 1. Fork仓库

点击右上角的"Fork"按钮

### 2. 克隆到本地

```bash
git clone https://github.com/your-username/Universal-SciAgent.git
cd Universal-SciAgent
```

### 3. 创建分支

```bash
git checkout -b feature/your-feature-name
```

### 4. 开发与测试

```bash
# 安装依赖
pip install -r requirements.txt

# 运行测试
pytest tests/ -v

# 代码格式化
black backend/
isort backend/
```

### 5. 提交代码

```bash
git add .
git commit -m "Add: your feature description"
git push origin feature/your-feature-name
```

### 6. 创建Pull Request

在GitHub上创建PR，描述您的改动。

## ✅ 代码规范

- 使用Python 3.10+特性
- 遵循PEP 8代码风格
- 添加类型注解
- 编写docstring（Google风格）
- 变量和函数命名使用英文

示例：
```python
async def search_papers(
    query: str,
    max_results: int = 10
) -> List[Paper]:
    """
    Search papers from multiple sources.
    
    Args:
        query: Search query string
        max_results: Maximum number of results
        
    Returns:
        List of Paper objects
        
    Raises:
        ValueError: If query is empty
    """
    pass
```

## 🧪 测试要求

- 新功能必须包含测试用例
- 保持测试覆盖率>80%
- 测试文件命名：`test_*.py`

## 📄 文档要求

- 更新README（如果添加新功能）
- 添加注释说明复杂逻辑
- 更新配置文件示例

## 🐛 报告Bug

使用[GitHub Issues](https://github.com/your-org/Universal-SciAgent/issues)报告Bug，请包含：

- Bug描述
- 重现步骤
- 预期行为
- 实际行为
- 环境信息（Python版本、操作系统等）

## 💡 功能建议

使用[GitHub Issues](https://github.com/your-org/Universal-SciAgent/issues)提交功能建议，请描述：

- 功能描述
- 使用场景
- 预期效果
- （可选）实现思路

## 📮 联系我们

- Issues: [GitHub Issues](https://github.com/your-org/Universal-SciAgent/issues)
- Email: your-email@example.com

---

再次感谢您的贡献！🎉

