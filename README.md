# 🤖  Self-Evolving AI Agent

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> 🌟 **A self-evolving AI agent that analyzes tasks, searches tools, generates code, and executes solutions autonomously.**

## 🚀 What's New in V2

- **⚡ 1000x Faster Search**: Keyword-based search replaces embeddings (5-10s → <5ms)
- **🌏 Chinese Support**: Full support for Chinese queries and responses
- **📦 Smart Dependencies**: Prompts before installing packages with clear feedback
- **🔍 Better Tool Discovery**: 100% search accuracy with enhanced keyword matching

## ✨ Key Features

- 🧠 **Smart Task Analysis** - Breaks complex tasks into actionable steps
- 🔍 **GitHub Tool Search** - Finds and integrates relevant tools automatically
- 🛠️ **Code Generation** - Creates reusable, generic tools
- 💾 **Tool Memory** - Learns and saves tools for future use
- 🌏 **Bilingual** - Works seamlessly with English and Chinese

## 🛠️ Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/Ramond-e/Self-evolutional-agent
cd Self-evolutional-agent
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file with at least ONE LLM key. You can add both (OpenRouter优先):
```env
OPENROUTER_API_KEY=your_openrouter_key_here        # (优先使用)
OPENROUTER_API_BASE_URL=https://openrouter.ai/api/v1/chat/completions
OPENAI_API_KEY=your_openai_key_here                # (如未填OpenRouter则用此)
OPENAI_API_BASE_URL=https://api.openai.com/v1/chat/completions
GITHUB_API_TOKEN=your_github_token_here
```

**API KEY与BASE URL优先级与变量说明：**
- `OPENROUTER_API_KEY` 和 `OPENROUTER_API_BASE_URL` 均需设置才能使用 OpenRouter。
- `OPENAI_API_KEY` 和 `OPENAI_API_BASE_URL` 均需设置才能使用 OpenAI（API BASE URL默认即可，需特殊代理等可自定义）。
- 两类 key & base url 都填写时，优先调用 OpenRouter。
- 只填写其中一组就用填写的。
- 都没填会报错。


### 3. Run
```bash
python manager.py
```

## 🎮 Usage Examples

### Stock Price Query
```
💬 User: 查看英伟达的股票价格

📋 Alita breaks it down:
  1. [✓] Fetch NVIDIA stock data
  2. [✓] Analyze price performance  
  3. [✓] Present results in Chinese

📊 Result: 英伟达(NVDA)当前股价为$131.26，较昨日下跌1.17%...
```

### Weather Query
```
💬 User: 北京今天的天气怎么样？

🌤️ Result: 北京今天天气晴朗，温度28°C，湿度70%...
```

### Special Commands
- `list tools/` - Show all available tools
- `exit` - Quit the application

## 🏗️ Architecture

```
alita/
├── manager.py          # Main controller
├── task_analyzer.py    # Task decomposition
├── tools_managing.py   # Tool storage (JSON + keywords)
├── code_generating.py  # Code generation
├── code_executing.py   # Execution engine
├── tool_searching.py   # GitHub integration
└── tools/             # Saved tools (JSON format)
```

## 📊 Technical Improvements

### Tool Storage Format
```json
{
  "id": "weather_tool_1234567890",
  "tool_description": "Fetches weather data for any location",
  "keywords": "weather temperature forecast climate 天气 温度",
  "install_dependencies": ["pip install requests"],
  "python_code": "..."
}
```

### Search Algorithm
- **Keyword Matching**: Direct keyword intersection (40%)
- **Description Matching**: Keywords in description (20%)
- **Partial Matching**: Substring matches (20%)
- **Domain Boost**: Weather/Stock specific bonuses

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenRouter for AI model access
- GitHub for code repository hosting
- Open source community for inspiration

---

⭐ **Star this repo if you find it useful!**
