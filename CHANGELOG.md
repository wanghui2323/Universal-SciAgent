# Changelog | 更新日志

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] | 未发布

### Planned | 计划中
- 待添加...

---

## [1.0.1] - 2026-01-03

### Added | 新增
- 基于 v1.0.0 创建优化分支
- 项目结构优化，为开源发布做准备
- 添加 `.env.example` 模板
- 添加 GitHub Actions CI/CD 工作流
- 添加 `CODE_OF_CONDUCT.md`
- 添加 `SECURITY.md`
- 添加 `pyproject.toml` 现代 Python 打包配置
- 添加单元测试
- 添加 `typing_extensions` 依赖解决 Python 3.10/3.11 兼容性问题

### Changed | 变更
- 版本号更新至 1.0.1
- 优化 README 安装说明，添加 Conda 环境创建方式
- 完善 API 密钥配置说明，增加详细获取步骤

### Fixed | 修复
- 修复 Anaconda 用户创建虚拟环境的文档问题
- 解决 `typing.override` 在 Python 3.10/3.11 中的 ImportError 问题
- 改进 API 认证错误的排查指南

---

## [1.0.0] - 2026-01-02

### Added | 新增

#### Multi-Agent System | 多智能体系统
- Master Agent for task coordination and quality control
- Literature Agent with arXiv, Semantic Scholar, PubMed integration
- Hypothesis Agent for research hypothesis generation
- Experiment Design Agent for experiment planning
- Writing Agent for report generation

#### VeADK Integration | VeADK 集成
- Native VeADK Agent integration
- VeADK Tool system with `@Tool` decorator
- VeADK Memory system (short-term + long-term)
- VeADK workflow orchestration

#### AgentKit Deployment | AgentKit 部署
- AgentKit deployment configuration
- HTTP server entry point for VeFaaS
- API endpoints: `/literature-review`, `/hypothesis-generation`, `/experiment-design`, `/write-report`

#### Domain Support | 领域支持
- Computer Science (计算机科学)
- Materials Science (材料科学)
- Biomedical (生物医学)
- Physics (物理学)
- Chemistry (化学)

#### Tools | 工具
- `arxiv_search`: Search papers on arXiv
- `semantic_scholar_search`: Search with citation metrics
- `pubmed_search`: Search biomedical papers
- `parse_pdf`: Extract text from PDF files

### Dependencies | 依赖
- veadk-python >= 0.2.27
- agentkit-sdk-python >= 0.2.0
- chromadb >= 0.4.22
- arxiv >= 2.1.0
- pydantic >= 2.5.0

---

[Unreleased]: https://github.com/wanghui2323/Universal-SciAgent/compare/v1.0.1...HEAD
[1.0.1]: https://github.com/wanghui2323/Universal-SciAgent/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/wanghui2323/Universal-SciAgent/releases/tag/v1.0.0
