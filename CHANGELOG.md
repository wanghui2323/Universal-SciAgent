# Changelog | 更新日志

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] | 未发布

### Added | 新增
- Project structure optimization for open source release
- Added `.env.example` template
- Added GitHub Actions CI/CD workflow
- Added `CODE_OF_CONDUCT.md`
- Added `SECURITY.md`
- Added `pyproject.toml` for modern Python packaging
- Added unit tests

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

[Unreleased]: https://github.com/your-org/Universal-SciAgent/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/your-org/Universal-SciAgent/releases/tag/v1.0.0
