import os
import subprocess
import json
from typing import Dict, Union, List, Optional, Set
from task_analyzer import analyze_task, get_model_response
from tools_managing import (
    search_tool_by_keywords, list_available_tools_v2, save_tool_as_json,
    generate_tool_keywords, generate_code_description_v2, load_tool_by_id,
    extract_keywords
)
from code_generating import generate_install_commands, generate_code, clean_and_validate_code, clean_and_validate_commands
from code_executing import install_dependencies, execute_python_code
from tool_searching import find_best_tool, find_best_tools_with_exclusion

class AlitaManagerV2:
    def __init__(self):
        """Initialize the Alita AI agent manager V2."""
        self.welcome_message = """
🤖 Welcome to Alita AI Agent V2! ✨

🌟 I can help you with various tasks. Here are some things you can do:
💡 Ask me questions and I'll analyze if we need any special tools
🔧 Type 'list tools/' to see available tools  
💬 Let me know what you'd like help with!

✨ NEW: Faster keyword-based tool search and dependency management!
"""

    def display_tools(self) -> str:
        """Display list of available tools."""
        tools = list_available_tools_v2()
        if not tools:
            return "🚫 No tools are currently available."
            
        tool_list = "\n🛠️ Available Tools:\n"
        tool_list += "=" * 70 + "\n"
        for tool in tools:
            tool_list += f"⚙️ {tool['name']}: {tool['description']}\n"
            tool_list += f"   📌 Keywords: {tool['keywords'][:50]}...\n"
        tool_list += "=" * 70
        return tool_list

    def handle_task(self, user_input: str) -> str:
        """
        Main method to handle user tasks step by step.
        
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
            print("🧠 Analyzing your request...")
            analysis = analyze_task(user_input)
            needs_external_tool = analysis.get('needs_external_tool', False)
            steps = analysis['steps']
            main_required_tool = analysis.get('main_required_tool', 'no_extra_tools_needed')
            tool_general_description = analysis.get('tool_general_description', '')

            # If no external tools needed, provide direct response
            if not needs_external_tool:
                print("💬 Generating response...")
                response = self._generate_direct_response(user_input)
                return response

            # Display task breakdown only if tools are needed
            print("\n📋 Task Breakdown:")
            print("=" * 50)
            for i, step in enumerate(steps, 1):
                print(f"  {i}. [ ] {step['description']}")
            print("=" * 50)

            # Store all console output for reference
            step_outputs = []
            
            # Execute each step
            results = []
            for i, step in enumerate(steps, 1):
                print(f"\n🔄 Step {i}: {step['description']}")
                
                # Capture console output for this step
                import io
                import sys
                old_stdout = sys.stdout
                sys.stdout = mystdout = io.StringIO()
                
                if step['requires_tool']:
                    # This step needs a tool
                    tool_type = step.get('tool_type', main_required_tool)
                    
                    # Extract keywords for better search
                    task_keywords = extract_keywords(user_input)
                    
                    # Check for existing tool using keyword search
                    print("🔍 Searching for required tool using keywords...")
                    existing_tool = search_tool_by_keywords(tool_type, task_keywords)
                    
                    # Reset stdout to show tool execution
                    sys.stdout = old_stdout
                    
                    if existing_tool:
                        print(f"✅ Found existing tool: {existing_tool['original_name']}")
                        print(f"   📊 Match score: {existing_tool.get('match_score', 0):.2%}")
                        print(f"   🔤 Matching keywords: {', '.join(existing_tool.get('matching_keywords', []))}")
                        result = self._execute_existing_tool_v2(existing_tool, user_input)
                        results.append(result)
                    else:
                        # Need to create new tool
                        print("🚀 No existing tool found. Creating new tool...")
                        result = self._create_and_execute_new_tool_v2(
                            user_input, [step], tool_type, tool_general_description
                        )
                        results.append(result)
                else:
                    # Reset stdout
                    sys.stdout = old_stdout
                    # This step doesn't need a tool, just process it
                    print("💭 Processing step...")
                    results.append(f"Step {i} completed")
                
                # Store the console output
                step_outputs.append(mystdout.getvalue())
                
                # Update progress
                print(f"\n📋 Progress Update:")
                print("=" * 50)
                for j, s in enumerate(steps, 1):
                    if j <= i:
                        print(f"  {j}. [✓] {s['description']}")
                    else:
                        print(f"  {j}. [ ] {s['description']}")
                print("=" * 50)

            # Final step: Summarize results
            print("\n🎯 Generating final answer...")
            final_answer = self._generate_final_answer(user_input, steps, results, step_outputs)
            
            # Clean up output file after processing
            output_file = 'tool_output.json'
            if os.path.exists(output_file):
                try:
                    os.remove(output_file)
                except:
                    pass
            
            return final_answer

        except Exception as e:
            import traceback
            return f"❌ An error occurred: {str(e)}\n{traceback.format_exc()}"

    def _generate_direct_response(self, question: str) -> str:
        """Generate direct response using LLM when no tool is needed."""
        prompt = f"""
        Provide a clear, helpful, and conversational answer to this question IN CHINESE:
        {question}
        
        Instructions:
        - Be friendly and natural
        - Provide accurate and helpful information
        - Use Chinese for the response
        - Do not mention that you're not using tools or external resources
        - Just answer the question directly
        """
        return get_model_response(prompt)

    def _execute_existing_tool_v2(self, tool_data: Dict, user_input: str) -> str:
        """Execute an existing tool loaded from JSON format."""
        try:
            tool_id = tool_data['id']
            tool_name = tool_data.get('original_name', tool_id)
            dependencies = tool_data.get('install_dependencies', [])
            
            print(f"\n   🎯 Preparing to execute tool: {tool_name}")
            
            # Check if we need to install dependencies
            if dependencies:
                print(f"\n   📦 This tool requires the following dependencies:")
                for dep in dependencies:
                    print(f"      🔧 {dep}")
                
                approval = input("\n   ❓ Install dependencies? (y/n): ")
                if approval.lower() == 'y':
                    print("\n   ⚡ Installing dependencies...")
                    for cmd in dependencies:
                        print(f"      ⬇️ Running: {cmd}")
                        success, output = install_dependencies(cmd)
                        if not success:
                            print(f"      ❌ Failed: {output}")
                            return f"Failed to install dependencies: {output}"
                        print(f"      ✅ Success")
                else:
                    print("   ⚠️ Skipping dependency installation. Tool may not work properly.")
            
            # Remove any existing output file
            output_file = 'tool_output.json'
            if os.path.exists(output_file):
                os.remove(output_file)
            
            # Execute the tool's Python code
            print(f"\n   🚀 Executing tool code...")
            
            # Write Python code to a temporary file with proper structure
            temp_filename = f"temp_{tool_id}.py"
            
            # Ensure the code has proper structure
            code_content = tool_data['python_code']
            
            # Check if the code already has if __name__ == "__main__": block
            if 'if __name__ == "__main__":' not in code_content:
                # Find the main function call
                if 'def main()' in code_content:
                    code_content += '\n\nif __name__ == "__main__":\n    main()'
                elif 'def fetch_data()' in code_content:
                    code_content += '\n\nif __name__ == "__main__":\n    fetch_data()'
                else:
                    # Try to find any function definition and call it
                    import re
                    func_match = re.search(r'def\s+(\w+)\s*\(', code_content)
                    if func_match:
                        func_name = func_match.group(1)
                        code_content += f'\n\nif __name__ == "__main__":\n    {func_name}()'
            
            with open(temp_filename, 'w', encoding='utf-8') as f:
                f.write(code_content)
            
            try:
                # Execute the tool
                success, output = execute_python_code(temp_filename, capture_output=False)
                
                if not success:
                    return f"Failed to execute tool: {output}"
                
                # Try to read output from file if tool saved it
                result_message = f"Tool {tool_name} executed successfully."
                if os.path.exists(output_file):
                    try:
                        with open(output_file, 'r', encoding='utf-8') as f:
                            tool_output = json.load(f)
                        result_message += f" Output data: {json.dumps(tool_output, ensure_ascii=False)}"
                    except Exception as e:
                        result_message += f" (Note: Could not read structured output: {str(e)})"
                else:
                    result_message += " Please check the console output above for results."
                
                return result_message
                
            finally:
                # Clean up temp file
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
                
        except Exception as e:
            return f"Error executing tool: {str(e)}"

    def _create_and_execute_new_tool_v2(self, user_input: str, steps: List[dict], required_tool: str, tool_general_description: str) -> str:
        """Search for, create, and execute a new tool with JSON storage."""
        try:
            # Track tried tools to avoid repetition
            tried_tools = set()
            max_search_attempts = 3
            current_attempt = 0
            
            while current_attempt < max_search_attempts:
                # Find best tools on GitHub
                print(f"\n   🔎 Searching GitHub for suitable tools (Attempt {current_attempt + 1}/{max_search_attempts})...")
                
                # Convert steps to string list
                step_descriptions = [step['description'] for step in steps] if isinstance(steps[0], dict) else steps
                
                # Get multiple tool options
                tool_options = find_best_tools_with_exclusion(
                    question=user_input,
                    steps=step_descriptions,
                    search_keyword=required_tool,
                    excluded_tools=tried_tools,
                    max_tools=3
                )
                
                if not tool_options:
                    return "❌ Could not find any suitable tools for this task."
                
                # Display tool options
                print(f"\n   🎯 Found {len(tool_options)} potential tools:")
                print("   " + "=" * 60)
                for i, tool in enumerate(tool_options, 1):
                    print(f"\n   📦 Option {i}: {tool['name']}")
                    print(f"   ⭐ Stars: {tool['stars']} | Score: {tool['score']:.1f}/100")
                    print(f"   📝 Description: {tool['description'][:100]}...")
                    print(f"   🔗 URL: {tool['url']}")
                print("   " + "=" * 60)
                
                # Let user choose
                while True:
                    choice = input(f"\n   ❓ Select a tool (1-{len(tool_options)}), 's' to search again, or 'c' to cancel: ")
                    
                    if choice.lower() == 'c':
                        return "Tool installation cancelled."
                    
                    if choice.lower() == 's':
                        # Add all shown tools to tried list
                        for tool in tool_options:
                            tried_tools.add(tool['name'])
                        current_attempt += 1
                        break
                    
                    try:
                        tool_index = int(choice) - 1
                        if 0 <= tool_index < len(tool_options):
                            tool_info = tool_options[tool_index]
                            
                            # Generate installation commands
                            install_cmds = generate_install_commands(tool_info['installation'])
                            install_cmds = clean_and_validate_commands(install_cmds)

                            # Ask user for installation approval
                            print(f"\n   🎉 Selected tool: {tool_info['name']}")
                            print(f"   📝 Full Description: {tool_info['description']}")
                            print("\n   📦 Installation commands:")
                            for cmd in install_cmds:
                                print(f"      🔧 {cmd}")
                            
                            approval = input("\n   ❓ Proceed with installation and tool creation? (y/n): ")
                            
                            if approval.lower() != 'y':
                                # Add to tried tools and continue searching
                                tried_tools.add(tool_info['name'])
                                print("\n   ↩️ Going back to tool selection...")
                                break
                            
                            # Proceed with installation and tool creation
                            return self._install_and_execute_tool_v2(
                                tool_info, install_cmds, user_input, 
                                required_tool, tool_general_description
                            )
                        
                        else:
                            print("   ❌ Invalid selection. Please try again.")
                    except ValueError:
                        print("   ❌ Invalid input. Please enter a number.")
            
            return "❌ Maximum search attempts reached. Could not find a suitable tool."

        except Exception as e:
            import traceback
            return f"❌ Error creating/executing tool: {str(e)}\n{traceback.format_exc()}"

    def _install_and_execute_tool_v2(self, tool_info: Dict, install_cmds: List[str], 
                                    user_input: str, required_tool: str, 
                                    tool_general_description: str) -> str:
        """Install dependencies and execute the selected tool."""
        try:
            # Install dependencies
            print("\n   ⚡ Installing dependencies...")
            for cmd in install_cmds:
                print(f"      ⬇️ Running: {cmd}")
                success, output = install_dependencies(cmd)
                if not success:
                    print(f"      ❌ Failed: {output}")
                    return f"Failed to install dependencies: {output}"
                print(f"      ✅ Success")

            # Generate and validate code
            print("\n   🎨 Generating code...")
            code = generate_code(
                language="python",
                usage_guide=tool_info['usage'],
                user_question=user_input,
                search_keyword=required_tool,
                tool_general_description=tool_general_description
            )
            
            print("   🔍 Validating code...")
            code = clean_and_validate_code(
                code=code,
                language="python",
                user_question=user_input,
                search_keyword=required_tool,
                usage_guide=tool_info['usage'],
                tool_general_description=tool_general_description
            )

            if not code:
                return "Failed to generate valid code."

            # Generate tool description
            print("   📝 Generating tool description...")
            description = generate_code_description_v2(
                user_question=user_input,
                required_tool=required_tool,
                code=code,
                tool_name=tool_info['name'],
                tool_general_description=tool_general_description
            )

            # Generate keywords
            print("   🔤 Generating search keywords...")
            keywords = generate_tool_keywords(
                tool_name=tool_info['name'],
                tool_description=description,
                required_tool=required_tool,
                code=code
            )

            # Save tool in JSON format
            print("   💾 Saving tool...")
            tool_id = save_tool_as_json(
                tool_name=tool_info['name'],
                tool_description=description,
                keywords=keywords,
                install_dependencies=install_cmds,
                python_code=code
            )

            print(f"   ✅ Tool saved with ID: {tool_id}")

            # Execute new tool
            print(f"\n   🚀 Executing new tool: {tool_info['name']}")
            
            # Write code to temp file for execution
            temp_filename = f"temp_{tool_id}.py"
            
            # Ensure the code has proper structure
            code_content = code
            
            # Check if the code already has if __name__ == "__main__": block
            if 'if __name__ == "__main__":' not in code_content:
                # Find the main function call
                if 'def main()' in code_content:
                    code_content += '\n\nif __name__ == "__main__":\n    main()'
                elif 'def fetch_data()' in code_content:
                    code_content += '\n\nif __name__ == "__main__":\n    fetch_data()'
                else:
                    # Try to find any function definition and call it
                    import re
                    func_match = re.search(r'def\s+(\w+)\s*\(', code_content)
                    if func_match:
                        func_name = func_match.group(1)
                        code_content += f'\n\nif __name__ == "__main__":\n    {func_name}()'
            
            with open(temp_filename, 'w', encoding='utf-8') as f:
                f.write(code_content)
            
            try:
                success, output = execute_python_code(temp_filename, capture_output=False)
                
                if not success:
                    return f"Failed to execute new tool: {output}"
                    
                # Return execution result
                return f"New tool {tool_info['name']} created and executed successfully. Output captured."
                
            finally:
                # Clean up temp file
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)

        except Exception as e:
            import traceback
            return f"❌ Error: {str(e)}\n{traceback.format_exc()}"

    def _generate_final_answer(self, user_input: str, steps: List[dict], 
                             results: List[str], step_outputs: List[str] = None) -> str:
        """Generate final answer based on all step results."""
        # Try to read the tool output file for the most recent data
        tool_output_data = None
        output_file = 'tool_output.json'
        if os.path.exists(output_file):
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    tool_output_data = json.load(f)
            except Exception as e:
                print(f"Warning: Could not read tool output file: {e}")
        
        prompt = f"""
        Based on the following task execution results, provide a clear and concise answer to the user's question.
        
        User Question: {user_input}
        
        Executed Steps and Results:
        """
        
        for i, (step, result) in enumerate(zip(steps, results), 1):
            prompt += f"\nStep {i}: {step['description']}"
            prompt += f"\nResult: {result}"
            
            # Include console output if available
            if step_outputs and i-1 < len(step_outputs) and step_outputs[i-1]:
                prompt += f"\nConsole Output: {step_outputs[i-1]}"
            
            prompt += "\n"
        
        # Add the actual tool output data if available
        if tool_output_data:
            prompt += f"\nACTUAL TOOL OUTPUT DATA:\n{json.dumps(tool_output_data, ensure_ascii=False, indent=2)}\n"
        
        prompt += """
        Please provide a comprehensive answer IN CHINESE that:
        1. Directly addresses the user's question
        2. Uses the specific data from the execution results
        3. Is clear, natural, and conversational
        4. Includes all relevant details from the tool execution
        
        CRITICAL INSTRUCTIONS FOR DATA EXTRACTION:
        - Look for "Output data:" in the Step Results above
        - ALSO look for "ACTUAL TOOL OUTPUT DATA:" section which contains the real data
        - This contains JSON data with actual values (temperature, weather, stock prices, etc.)
        - USE THESE EXACT VALUES in your response - they are the real data!
        
        For stock price queries:
        - Mention the current price, high, low, previous close
        - Calculate and mention the price change (current - previous close)
        - Include market cap, P/E ratio if available
        - Mention the data retrieval time
        - Example: "英伟达(NVDA)今天的股价是$170.92，最高$177.26，最低$170.89..."
        
        For weather queries:
        - Temperature, weather condition, humidity, wind speed should all be mentioned
        - Use natural language like "今天北京天气晴朗，温度34.09°C..."
        
        IMPORTANT: The data HAS been successfully retrieved if you see "ACTUAL TOOL OUTPUT DATA" section.
        DO NOT say data is unavailable if it appears in the output above!
        """
        
        return get_model_response(prompt)

def main():
    """Main entry point for the Alita AI agent V2."""
    manager = AlitaManagerV2()
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
