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

### 🧠 Advanced Task Analysis & Step-by-Step Execution
- **Smart Task Decomposition**: Breaks down complex tasks into actionable, sequential steps
- **Step-by-Step Execution**: Executes each step independently with real-time progress tracking
- **Intelligent Tool Detection**: Each step is analyzed to determine if external tools are needed
- **Visual Progress**: Shows task completion with checkmarks (✓) for completed steps

### 🛠️ Dynamic Tool Management
- **Vector-Based Search**: Uses embeddings to find similar existing tools
- **GitHub Integration**: Automatically searches and downloads tools from repositories
- **Universal Tool Generation**: Creates reusable, generic tools rather than task-specific ones
- **Smart Tool Descriptions**: Generates comprehensive descriptions for better tool discovery

### 🎨 Enhanced Code Generation
- **Generic Code Creation**: Generates reusable tools that work for multiple scenarios
- **Interactive Input Handling**: Tools request user input at runtime for maximum flexibility
- **Data Persistence**: Tools save results to JSON files for cross-step data sharing
- **Multi-API Support**: Intelligent fallback between different API providers

### 🔄 Self-Evolution & Learning
- **Continuous Learning**: Saves new tools with vectorized descriptions for future use
- **Knowledge Growth**: Builds an ever-expanding library of capabilities
- **Smart Reuse**: Prioritizes existing tools over creating new ones when possible

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

#### 📊 Stock Price Query with Step-by-Step Execution
```
💬 How can I help? (or type 'exit' to quit): 英伟达今天的股价怎么样？

🧠 Analyzing your request...

📋 Task Breakdown:
==================================================
  1. [ ] Fetch current stock price data for NVIDIA (NVDA)
  2. [ ] Analyze the stock price performance for today
  3. [ ] Summarize and present the NVIDIA stock price information to the user in Chinese
==================================================

🔄 Step 1: Fetch current stock price data for NVIDIA (NVDA)
✅ Found existing tool: stockkly_api
   🎯 Executing tool: stockkly_api

📊 股票价格查询需要 Alpha Vantage API 密钥
🆓 免费注册获取API密钥: https://www.alphavantage.co/support/#api-key

选择操作:
1. 输入我的API密钥
2. 使用Demo模式（仅支持部分股票）
请选择 (1/2): 2

📊 NVDA 股票数据
========================================
股票代码: NVDA
当前价格: $131.26
涨跌额: -$1.56
涨跌幅: -1.17%
数据来源: Alpha Vantage (Demo)

📋 Progress Update:
==================================================
  1. [✓] Fetch current stock price data for NVIDIA (NVDA)
  2. [ ] Analyze the stock price performance for today  
  3. [ ] Summarize and present the NVIDIA stock price information to the user in Chinese
==================================================

🔄 Step 2: Analyze the stock price performance for today
💭 Processing step...

📋 Progress Update:
==================================================
  1. [✓] Fetch current stock price data for NVIDIA (NVDA)
  2. [✓] Analyze the stock price performance for today
  3. [ ] Summarize and present the NVIDIA stock price information to the user in Chinese
==================================================

🔄 Step 3: Summarize and present the NVIDIA stock price information to the user in Chinese
💭 Processing step...

🎯 Generating final answer...

📋 根据今天的股票数据，英伟达(NVDA)的表现如下：

当前股价为 $131.26，相比前一交易日下跌了 $1.56，跌幅为 1.17%。
今天英伟达股票呈现小幅下跌趋势。虽然跌幅不大，但投资者可能需要关注市场动向和公司最新消息。
```

#### 🌤️ Weather Query Example
```
💬 How can I help? (or type 'exit' to quit): 北京今天的天气怎么样？

🧠 Analyzing your request...

📋 Task Breakdown:
==================================================
  1. [ ] Get current weather data for Beijing
  2. [ ] Summarize and present the weather information to the user
==================================================

🔄 Step 1: Get current weather data for Beijing
✅ Found existing tool: e_paper_weather_display
   🎯 Executing tool: e_paper_weather_display

请输入您的OpenWeatherMap API密钥: [your_api_key]
请输入城市名称 (例如: Shanghai): Beijing

城市: Beijing
天气状况: 晴
当前温度: 28.05°C
体感温度: 30.76°C
湿度: 70%
气压: 1003 hPa
风速: 2.06 m/s

🎯 Generating final answer...

📋 北京今天天气晴朗，当前温度28.05°C，体感温度30.76°C。
湿度为70%，气压1003 hPa，风速2.06米/秒。总体来说是个不错的天气！
```

#### 📚 Tool Management
```
💬 How can I help? list tools/

🛠️ Available Tools:
==================================================
⚙️ stockkly_api: Fetches real-time stock price data for any given stock ticker symbol
⚙️ e_paper_weather_display: Retrieves current weather conditions for a given city
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

### 1. Enhanced Task Analysis
```python
# User inputs: "北京今天的天气怎么样？"
analysis = analyze_task(user_input)
# Returns: {
#   steps: [
#     {description: "Get current weather data for Beijing", requires_tool: true, tool_type: "weather api"},
#     {description: "Summarize and present the weather information to the user", requires_tool: false}
#   ],
#   main_required_tool: "weather api",
#   tool_general_description: "A tool that fetches current weather data for any location"
# }
```

### 2. Step-by-Step Execution
```python
# Execute each step independently
for step in steps:
    print(f"🔄 Step {i}: {step['description']}")
    
    if step['requires_tool']:
        # Search for existing tools or create new ones
        existing_tool = search_similar_tool(step['tool_type'])
        if existing_tool:
            result = execute_existing_tool(existing_tool)
        else:
            result = create_and_execute_new_tool(step)
    else:
        # Process step using LLM
        result = process_step_with_llm(step)
    
    # Update progress visualization
    show_progress_update(steps, current_step)
```

### 3. Smart Tool Management
```python
# Generate universal, reusable tools
code = generate_code(
    language="python",
    usage_guide=tool_info['usage'],
    tool_general_description="A tool that fetches current weather data for any location",
    # Focus on generality, not specific user question
)

# Save tools with rich metadata
save_tool_with_description(code, tool_name, general_description)
vectorize_description(general_description, tool_name)
```

### 4. Data Flow & Final Answer
```python
# Tools save data for inter-step communication
with open('tool_output.json', 'w') as f:
    json.dump(tool_results, f)

# Generate comprehensive final answer
final_answer = generate_final_answer(
    user_question=user_input,
    all_step_results=step_results,
    console_outputs=captured_outputs
)
```

### 5. Real-time API Configuration
```python
# Tools handle API keys dynamically
def get_api_key():
    choice = input("1. Enter API key\n2. Use demo mode\nChoose: ")
    if choice == "1":
        api_key = input("Enter your API key: ")
        # Optionally save for future use
        save_to_env_file(api_key)
    return api_key or "demo"
```

## 🆕 Latest Updates (v2.0)

### ✨ Step-by-Step Task Execution
- **Visual Progress Tracking**: Real-time task breakdown with checkmark progress indicators
- **Independent Step Processing**: Each step is analyzed and executed separately
- **Smart Tool Detection**: Automatic determination of when tools are needed vs. LLM processing

### 🔧 Enhanced Tool Generation
- **Universal Tool Design**: Creates reusable tools that work for any similar request
- **Runtime API Configuration**: Tools prompt for API keys when needed, no pre-configuration required
- **Multi-API Support**: Intelligent fallback between different data providers
- **Cross-Step Data Sharing**: Tools save results for use by subsequent steps

### 📊 Advanced Examples
- **Stock Price Analysis**: Complete workflow from data fetching to Chinese summary
- **Weather Queries**: End-to-end weather information retrieval and presentation
- **Multi-Step Tasks**: Complex queries broken down into manageable, trackable steps

---

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
