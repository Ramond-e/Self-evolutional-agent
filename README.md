# 🤖  Self-Evolutional AI Agent

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-Self--evolutional--agent-black.svg)](https://github.com/Ramond-e/Self-evolutional-agent)

> 🌟 **A self-evolving AI agent that can analyze tasks, search for relevant tools, generate code, and execute solutions autonomously.**

## 🚀 Overview

This is an intelligent AI agent that combines task analysis, tool management, and code generation to provide dynamic solutions to user queries. It can:

- 🧠 **Analyze complex tasks** and break them down into actionable steps
- 🔍 **Search GitHub** for relevant tools and libraries
- 🛠️ **Generate and validate code** automatically
- 📦 **Install dependencies** and execute solutions
- 💾 **Learn and save tools** for future reuse
- 🎯 **Execute existing tools** from its growing knowledge base

## ✨ Key Features

### 🤖 Intelligent Task Analysis
- Uses advanced language models to understand user requests
- Breaks down complex tasks into manageable steps
- Determines whether existing tools can be used or new ones need to be created

### 🛠️ Dynamic Tool Management
- Searches for similar existing tools using vector embeddings
- Automatically downloads and integrates tools from GitHub
- Saves and vectorizes tool descriptions for efficient retrieval

### 🎨 Code Generation & Validation
- Generates Python code based on user requirements
- Validates and cleans generated code for safety and correctness
- Handles dependency installation automatically

### 🔄 Self-Evolution
- Learns from each interaction by saving new tools
- Builds a growing knowledge base of capabilities
- Improves over time through accumulated experience

## 📁 Project Structure

```
alita/
├── 🧠 manager.py                   # Main AI agent controller
├── 🔍 task_analyzer.py             # Task analysis and LLM interface
├── 🛠️ tools_managing.py           # Tool storage and retrieval
├── 🎨 code_generating.py          # Code generation and validation
├── ⚡ code_executing.py           # Code execution and dependency management
├── 🔎 tool_searching.py           # GitHub tool search functionality
├── 📁 tools/                      # Saved tool implementations
│   ├── stockkly_api.py           # Stock price fetching tool
│   └── e_paper_weather_display.py # Weather display tool
├── 🧮 vectorized_tools/           # Tool embeddings for similarity search
├── 📝 .env.example               # Environment variable template
└── 🚫 .gitignore                 # Git ignore rules
```

## 🛠️ Installation

### Prerequisites
- Python 3.7 or higher
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/Ramond-e/Self-evolutional-agent.git
cd Self-evolutional-agent
```

### 2. Set Up Environment
```bash
# Copy environment template
cp .env.example .env
```

### 3. Configure API Keys
Edit the `.env` file and add your API keys:

```env
# OpenRouter API Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_API_BASE_URL=https://openrouter.ai/api/v1/chat/completions

# GitHub API Configuration
GITHUB_API_TOKEN=your_github_api_token_here
```

> **⚠️ Security Note**: Never commit your actual API keys to version control. 

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

> **💡 Tip**: Use a virtual environment to avoid conflicts:
```bash
# Create virtual environment
python -m venv alita-env

# Activate (Windows)
alita-env\Scripts\activate

# Activate (macOS/Linux)
source alita-env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

> **🔑 API Keys Setup**:
> - **OpenRouter**: Required for AI model access
> - **GitHub**: Required for searching and downloading tools
> - Keep your API keys secure and never share them publicly

## 🎮 Usage

### Starting the Agent
```bash
python manager.py
```

### Example Interactions

```
💬 How can I help? (or type 'exit' to quit): Get NVIDIA stock price

🔍 Searching for existing tools...
✅ Found existing tool: stockkly_api
🎯 Executing tool: stockkly_api
股票代码: NVDA
当前价格: $131.26
涨跌额: $-1.56
涨跌幅: -1.17%
✅ Tool execution completed successfully!
```

```
💬 How can I help? list tools/

🛠️ Available Tools:
==================================================
⚙️ stockkly_api: Fetches real-time NVIDIA stock price data
⚙️ e_paper_weather_display: Weather display functionality
==================================================
```

### Special Commands

| Command | Description |
|---------|-------------|
| `list tools/` | Display all available tools |
| `exit` | Quit the application |

## 🔧 API Configuration

### Required APIs

1. **OpenRouter API** - For language model access
   - Sign up at [OpenRouter.ai](https://openrouter.ai/)
   - Get your API key from the dashboard
   - Used for accessing various AI models through a unified interface

2. **GitHub API** - For tool searching and repository access
   - Create a personal access token at [GitHub Settings](https://github.com/settings/tokens)
   - No special permissions required for public repository access
   - Used to search for and download relevant tools from GitHub repositories

## 🏗️ How It Works

### 1. Task Analysis
```python
# User inputs: "Get weather data for Tokyo"
analysis = analyze_task(user_input)
# Returns: {steps: [...], required_tool: "weather_api"}
```

### 2. Tool Search
```python
# Search for existing tools
existing_tool = search_similar_tool("weather_api")
# Or search GitHub for new tools
tool_info = find_best_tool(user_input, steps, required_tool)
```

### 3. Code Generation
```python
# Generate code for the task
code = generate_code(language="python", usage_guide=tool_info['usage'])
# Validate and clean the code
code = clean_and_validate_code(code, language="python")
```

### 4. Execution
```python
# Execute the generated/existing tool
success, output = execute_python_code(f"{tool_name}.py")
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Include error handling
- Test new features thoroughly
- Update documentation as needed

## 🔒 Security & Privacy

- **Environment Variables**: All sensitive API keys are stored in `.env` (not tracked by git)
- **Code Validation**: All generated code is validated before execution
- **Sandboxing**: Consider running in a virtual environment
- **API Limits**: Be mindful of API rate limits and costs

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenRouter** for providing access to advanced language models
- **GitHub** for hosting and API access
- **Anthropic** for Claude models
- The open-source community for tools and inspiration

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/Ramond-e/Self-evolutional-agent/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/Ramond-e/Self-evolutional-agent/discussions)
- 📧 **Contact**: [Create an issue](https://github.com/Ramond-e/Self-evolutional-agent/issues/new) for direct support

---

<div align="center">


⭐ **Star this repo if you find it useful!** ⭐

</div>
