# Security Policy | 安全策略

## Supported Versions | 支持的版本

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability | 报告漏洞

**Please do not report security vulnerabilities through public GitHub issues.**

请发送邮件至：[INSERT SECURITY EMAIL]

Please include:
- Type of issue (e.g., buffer overflow, SQL injection, etc.)
- Full paths of source file(s) related to the issue
- Step-by-step instructions to reproduce the issue
- Impact of the issue

## Security Best Practices | 安全最佳实践

### API Key Protection | API 密钥保护

1. **Never commit API keys to version control**
2. **Use environment variables or `.env` files**
3. **Ensure `.env` is in your `.gitignore`**
4. **Rotate API keys regularly**

### Configuration Files | 配置文件

- The `config.yaml` file may contain sensitive information
- Never commit `config.yaml` with real API keys
- Use `config.yaml.example` as a template
