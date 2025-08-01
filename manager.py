import os
from typing import Dict, Union, List, Optional
from task_analyzer import analyze_task, get_model_response
from tools_managing import search_similar_tool, list_available_tools, save_tool_code, vectorize_description, generate_code_description
from code_generating import generate_install_commands, generate_code, clean_and_validate_code, clean_and_validate_commands
from code_executing import install_dependencies, execute_python_code
from tool_searching import find_best_tool

class AlitaManager:
    def __init__(self):
        """Initialize the Alita AI agent manager."""
        self.welcome_message = """
🤖 Welcome to Alita AI Agent! ✨

🌟 I can help you with various tasks. Here are some things you can do:
💡 Ask me questions and I'll analyze if we need any special tools
🔧 Type 'list tools/' to see available tools  
💬 Let me know what you'd like help with!
"""

    def display_tools(self) -> str:
        """Display list of available tools."""
        tools = list_available_tools()
        if not tools:
            return "🚫 No tools are currently available."
            
        tool_list = "\n🛠️ Available Tools:\n"
        tool_list += "=" * 50 + "\n"
        for tool in tools:
            tool_list += f"⚙️ {tool['name']}: {tool['description']}\n"
        tool_list += "=" * 50
        return tool_list

    def handle_task(self, user_input: str) -> str:
        """
        Main method to handle user tasks.
        
        Args:
            user_input (str): User's question or command
            
        Returns:
            str: Response to user
        """
        try:
            # Check for special commands
            if user_input.lower() == 'list tools/':
                return self.display_tools()

            # Analyze the task
            analysis = analyze_task(user_input)
            steps = analysis['steps']
            required_tool = analysis['required_tool']

            # If no tool needed, use LLM directly
            if required_tool == "no_extra_tools_needed":
                print("💭 Analyzing your question...")
                return self._generate_direct_response(user_input)

            # Check if we have a similar tool
            print("🔍 Searching for existing tools...")
            existing_tool = search_similar_tool(required_tool)
            if existing_tool:
                print(f"✅ Found existing tool: {existing_tool}")
                return self._execute_existing_tool(existing_tool, user_input)

            # Search for and create new tool
            print("🚀 Creating new tool for your task...")
            return self._create_and_execute_new_tool(user_input, steps, required_tool)

        except Exception as e:
            return f"❌ An error occurred: {str(e)}"

    def _generate_direct_response(self, question: str) -> str:
        """Generate direct response using LLM when no tool is needed."""
        prompt = f"""
        Provide a clear and concise answer to this question:
        {question}
        """
        return get_model_response(prompt)

    def _execute_existing_tool(self, tool_name: str, user_input: str) -> str:
        """Execute an existing tool."""
        try:
            # Get the actual tool information
            tools = list_available_tools()
            matching_tool = None
            
            # Find the tool that matches the sanitized name
            for tool in tools:
                # Check if the tool_name matches the sanitized version of this tool's name
                from tools_managing import sanitize_tool_name
                if tool_name == sanitize_tool_name(tool['name']):
                    matching_tool = tool
                    break
            
            if not matching_tool:
                return f"❌ Tool '{tool_name}' not found in available tools"
            
            print(f"🎯 Executing tool: {matching_tool['name']}")
            print(f"📝 Description: {matching_tool['description']}")
            
            # Execute the tool using the actual filename
            success, output = execute_python_code(matching_tool['filename'])
            
            if not success:
                return f"❌ Failed to execute tool: {output}"
                
            # Tool output has been printed directly to console
            return "✅ Tool execution completed successfully!"
            
        except Exception as e:
            return f"❌ Error executing tool: {str(e)}"

    def _create_and_execute_new_tool(self, user_input: str, steps: List[str], required_tool: str) -> str:
        """Search for, create, and execute a new tool."""
        try:
            # Find best tool on GitHub
            print("🔎 Searching GitHub for suitable tools...")
            tool_info = find_best_tool(user_input, steps, required_tool)
            if tool_info['score'] == 0:
                return "❌ Could not find a suitable tool for this task."

            # Generate installation commands
            install_cmds = generate_install_commands(tool_info['installation'])
            install_cmds = clean_and_validate_commands(install_cmds)

            # Ask user for installation approval
            print(f"\n🎉 Found tool: {tool_info['name']}")
            print(f"📝 Description: {tool_info['description']}")
            print("\n📦 Installation commands:")
            for cmd in install_cmds:
                print(f"   🔧 {cmd}")
            approval = input("\n❓ Proceed with installation? (y/n): ")
            
            if approval.lower() != 'y':
                return "❌ Tool installation cancelled."

            # Install dependencies
            print("⚡ Installing dependencies...")
            for cmd in install_cmds:
                print(f"   ⬇️ Running: {cmd}")
                success, output = install_dependencies(cmd)
                if not success:
                    return f"❌ Failed to install dependencies: {output}"

            # Generate and validate code
            print("🎨 Generating code...")
            code = generate_code(
                language="python",
                usage_guide=tool_info['usage'],
                user_question=user_input,
                search_keyword=required_tool
            )
            
            print("🔍 Validating code...")
            code = clean_and_validate_code(
                code=code,
                language="python",
                user_question=user_input,
                search_keyword=required_tool,
                usage_guide=tool_info['usage']
            )

            if not code:
                return "❌ Failed to generate valid code."

            # Generate tool description and save
            print("📝 Generating tool description...")
            description = generate_code_description(
                user_question=user_input,
                required_tool=required_tool,
                code=code,
                tool_name=tool_info['name']
            )

            # Save and vectorize tool
            print("💾 Saving tool...")
            tool_name = save_tool_code(description, code, tool_info['name'])
            print("🧠 Vectorizing tool for future use...")
            vectorize_description(description, tool_info['name'])

            # Execute new tool
            print(f"🚀 Executing new tool: {tool_name}")
            success, _ = execute_python_code(f"{tool_name}.py")
            
            if not success:
                return "❌ Failed to execute new tool"
                
            # Tool output has been printed directly to console
            return "✅ Tool execution completed successfully!"

        except Exception as e:
            return f"❌ Error creating/executing tool: {str(e)}"

def main():
    """Main entry point for the Alita AI agent."""
    manager = AlitaManager()
    print(manager.welcome_message)
    
    while True:
        try:
            user_input = input("\n💬 How can I help? (or type 'exit' to quit): ")
            
            if user_input.lower() == 'exit':
                print("\n👋 Goodbye! Thanks for using Alita AI Agent! ✨")
                break
                
            response = manager.handle_task(user_input)
            print("\n📋 " + response)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Thanks for using Alita AI Agent! ✨")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
