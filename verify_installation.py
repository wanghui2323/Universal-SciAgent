#!/usr/bin/env python3
"""
Universal-SciAgent 1.0.2 安装验证脚本

此脚本验证所有依赖是否正确安装，以及代码是否可以正常运行。
"""

import sys
from pathlib import Path

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def test_import(module_name, from_module=None, description=""):
    """测试模块导入"""
    try:
        if from_module:
            exec(f"from {from_module} import {module_name}")
            print_success(f"{description or f'{from_module}.{module_name}'} 导入成功")
        else:
            exec(f"import {module_name}")
            print_success(f"{description or module_name} 导入成功")
        return True
    except ImportError as e:
        print_error(f"{description or module_name} 导入失败: {e}")
        return False
    except Exception as e:
        print_error(f"{description or module_name} 导入错误: {e}")
        return False

def main():
    print_info("=" * 70)
    print_info("Universal-SciAgent 1.0.2 安装验证")
    print_info("=" * 70)
    print()
    
    total_tests = 0
    passed_tests = 0
    
    # 测试 1: Python 版本
    print_info("测试 1: Python 版本检查")
    python_version = sys.version_info
    print(f"   当前 Python 版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    if python_version >= (3, 10):
        print_success("Python 版本兼容 (>= 3.10)")
        passed_tests += 1
    else:
        print_error("Python 版本过低，需要 >= 3.10")
    total_tests += 1
    print()
    
    # 测试 2: 核心依赖
    print_info("测试 2: 核心依赖检查")
    core_deps = [
        ("veadk", None, "VeADK"),
        ("Agent", "veadk", "VeADK Agent"),
        ("Runner", "veadk", "VeADK Runner"),
        ("FunctionTool", "google.adk.tools", "Google ADK FunctionTool"),
        ("SequentialAgent", "veadk.agents.sequential_agent", "VeADK SequentialAgent"),
        ("ParallelAgent", "veadk.agents.parallel_agent", "VeADK ParallelAgent"),
        ("ShortTermMemory", "veadk.memory.short_term_memory", "VeADK ShortTermMemory"),
        ("LongTermMemory", "veadk.memory.long_term_memory", "VeADK LongTermMemory"),
    ]
    
    for module, from_module, desc in core_deps:
        if test_import(module, from_module, desc):
            passed_tests += 1
        total_tests += 1
    print()
    
    # 测试 3: AgentKit
    print_info("测试 3: AgentKit 检查")
    agentkit_deps = [
        ("agentkit", None, "AgentKit SDK"),
        ("AgentkitAgentServerApp", "agentkit.apps", "AgentKit Server App"),
    ]
    
    for module, from_module, desc in agentkit_deps:
        if test_import(module, from_module, desc):
            passed_tests += 1
        total_tests += 1
    print()
    
    # 测试 4: 学术搜索工具
    print_info("测试 4: 学术搜索工具检查")
    tool_deps = [
        ("arxiv", None, "arXiv API"),
        ("requests", None, "HTTP Requests"),
        ("aiohttp", None, "Async HTTP"),
    ]
    
    for module, from_module, desc in tool_deps:
        if test_import(module, from_module, desc):
            passed_tests += 1
        total_tests += 1
    print()
    
    # 测试 5: PDF 处理
    print_info("测试 5: PDF 处理库检查")
    pdf_deps = [
        ("pypdf", None, "pypdf (已修复)"),
        ("PdfReader", "pypdf", "PDF Reader"),
        ("pdfplumber", None, "PDF Plumber"),
    ]
    
    for module, from_module, desc in pdf_deps:
        if test_import(module, from_module, desc):
            passed_tests += 1
        total_tests += 1
    print()
    
    # 测试 6: 数据处理
    print_info("测试 6: 数据处理库检查")
    data_deps = [
        ("pandas", None, "Pandas"),
        ("numpy", None, "NumPy"),
        ("pydantic", None, "Pydantic"),
        ("yaml", None, "PyYAML"),
    ]
    
    for module, from_module, desc in data_deps:
        if test_import(module, from_module, desc):
            passed_tests += 1
        total_tests += 1
    print()
    
    # 测试 7: 向量数据库
    print_info("测试 7: 向量数据库检查")
    if test_import("chromadb", None, "ChromaDB"):
        passed_tests += 1
    total_tests += 1
    print()
    
    # 测试 8: 配置文件
    print_info("测试 8: 配置文件检查")
    config_files = [
        Path("agent.py"),
        Path("requirements.txt"),
        Path("config.yaml.example"),
        Path(".env.example"),
        Path("backend/agents/sci_agent_system.py"),
        Path("backend/tools/veadk_tools.py"),
        Path("backend/core/config.py"),
    ]
    
    for config_file in config_files:
        if config_file.exists():
            print_success(f"{config_file} 存在")
            passed_tests += 1
        else:
            print_error(f"{config_file} 不存在")
        total_tests += 1
    print()
    
    # 测试 9: 导入项目模块
    print_info("测试 9: 项目模块导入检查")
    try:
        # 测试配置模块
        from backend.core.config import settings
        print_success("backend.core.config 导入成功")
        passed_tests += 1
    except Exception as e:
        print_error(f"backend.core.config 导入失败: {e}")
    total_tests += 1
    
    try:
        # 测试工具模块
        from backend.tools.veadk_tools import arxiv_search, semantic_scholar_search
        print_success("backend.tools.veadk_tools 导入成功")
        passed_tests += 1
    except Exception as e:
        print_error(f"backend.tools.veadk_tools 导入失败: {e}")
    total_tests += 1
    
    try:
        # 测试 agent 模块
        import agent
        print_success("agent.py 导入成功")
        passed_tests += 1
    except Exception as e:
        print_error(f"agent.py 导入失败: {e}")
    total_tests += 1
    print()
    
    # 测试 10: 环境配置
    print_info("测试 10: 环境配置检查")
    import os
    
    api_key = os.getenv("MODEL_AGENT_API_KEY") or os.getenv("model_agent_api_key")
    if api_key:
        print_success("API Key 已配置")
        passed_tests += 1
    else:
        print_warning("API Key 未配置 (请在 .env 文件中设置)")
        print_info("   提示: cp .env.example .env && 编辑 .env 填入 API Key")
    total_tests += 1
    print()
    
    # 总结
    print_info("=" * 70)
    print_info(f"验证完成: {passed_tests}/{total_tests} 项测试通过")
    print_info("=" * 70)
    print()
    
    if passed_tests == total_tests:
        print_success("🎉 所有测试通过！项目可以正常运行。")
        print()
        print_info("下一步:")
        print("   1. 如果未配置 API Key，请编辑 .env 文件")
        print("   2. 运行: python3 agent.py")
        print("   3. 访问: http://localhost:8000")
        return 0
    elif passed_tests >= total_tests * 0.8:
        print_warning("⚠️  大部分测试通过，但有些问题需要解决。")
        print()
        print_info("建议:")
        if not api_key:
            print("   1. 配置 API Key: cp .env.example .env && 编辑 .env")
        print("   2. 安装缺失的依赖: pip install -r requirements.txt")
        print("   3. 查看详细报告: CODE_REVIEW_REPORT.md")
        return 1
    else:
        print_error("❌ 多项测试失败，需要修复关键问题。")
        print()
        print_info("请执行:")
        print("   1. pip install --upgrade pip")
        print("   2. pip install -r requirements.txt")
        print("   3. 重新运行此验证脚本")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print()
        print_warning("用户中断")
        sys.exit(1)
    except Exception as e:
        print_error(f"验证过程出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

