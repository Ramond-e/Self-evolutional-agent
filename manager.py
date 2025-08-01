import os
import subprocess
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
            steps = analysis['steps']
            main_required_tool = analysis.get('main_required_tool', 'no_extra_tools_needed')
            tool_general_description = analysis.get('tool_general_description', '')

            # Display task breakdown
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
                    
                    # Check for existing tool
                    print("🔍 Searching for required tool...")
                    existing_tool = search_similar_tool(tool_type)
                    
                    # Reset stdout to show tool execution
                    sys.stdout = old_stdout
                    
                    if existing_tool:
                        print(f"✅ Found existing tool: {existing_tool}")
                        result = self._execute_existing_tool(existing_tool, user_input)
                        results.append(result)
                    else:
                        # Need to create new tool
                        print("🚀 Creating new tool...")
                        result = self._create_and_execute_new_tool(
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
            return f"❌ An error occurred: {str(e)}"

    def _generate_direct_response(self, question: str) -> str:
        """Generate direct response using LLM when no tool is needed."""
        prompt = f"""
        Provide a clear and concise answer to this question:
        {question}
        """
        return get_model_response(prompt)

    def _execute_tool_with_capture(self, tool_filename: str, tool_name: str) -> str:
        """Execute a tool and capture its output using a wrapper script."""
        import tempfile
        import json
        
        # Create a wrapper script that captures output
        wrapper_code = f"""
import sys
import io
import subprocess

# Run the tool and capture output
result = subprocess.run(
    [sys.executable, "tools/{tool_filename}"],
    capture_output=True,
    text=True
)

# Save the output
output_data = {{
    "stdout": result.stdout,
    "stderr": result.stderr,
    "returncode": result.returncode
}}

# Print for capture
print("===OUTPUT_START===")
print(result.stdout)
print("===OUTPUT_END===")
"""
        
        # Write wrapper to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(wrapper_code)
            wrapper_path = f.name
        
        try:
            # Execute wrapper
            result = subprocess.run(
                [sys.executable, wrapper_path],
                capture_output=True,
                text=True
            )
            
            # Extract output
            if "===OUTPUT_START===" in result.stdout and "===OUTPUT_END===" in result.stdout:
                start = result.stdout.find("===OUTPUT_START===") + len("===OUTPUT_START===")
                end = result.stdout.find("===OUTPUT_END===")
                captured_output = result.stdout[start:end].strip()
                return captured_output
            else:
                # Fallback: just run interactively
                success, output = execute_python_code(tool_filename, capture_output=False)
                return "Tool executed (interactive mode). Check console for output."
                
        finally:
            # Clean up temp file
            if os.path.exists(wrapper_path):
                os.unlink(wrapper_path)
    
    def _execute_existing_tool(self, tool_name: str, user_input: str) -> str:
        """Execute an existing tool and return its output."""
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
                return f"Tool '{tool_name}' not found"
            
            print(f"   🎯 Executing tool: {matching_tool['name']}")
            
            # Remove any existing output file
            output_file = 'tool_output.json'
            if os.path.exists(output_file):
                os.remove(output_file)
            
            # Execute the tool interactively (for user input)
            success, output = execute_python_code(matching_tool['filename'], capture_output=False)
            
            if not success:
                return f"Failed to execute tool: {output}"
            
            # Try to read output from file if tool saved it
            result_message = f"Tool {matching_tool['name']} executed successfully."
            if os.path.exists(output_file):
                try:
                    import json
                    with open(output_file, 'r', encoding='utf-8') as f:
                        tool_output = json.load(f)
                    result_message += f" Output data: {json.dumps(tool_output, ensure_ascii=False)}"
                    # Don't remove the file yet, let other steps use it if needed
                except Exception as e:
                    result_message += f" (Note: Could not read structured output: {str(e)})"
            else:
                result_message += " Please check the console output above for results."
            
            return result_message
            
        except Exception as e:
            return f"Error executing tool: {str(e)}"

    def _generate_final_answer(self, user_input: str, steps: List[dict], results: List[str], step_outputs: List[str] = None) -> str:
        """Generate final answer based on all step results."""
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
        
        prompt += """
        Please provide a comprehensive answer IN CHINESE that:
        1. Directly addresses the user's question
        2. Extracts and uses any specific data from "Output data:" in the results if available
        3. Is clear, natural, and conversational
        4. Includes all relevant details from the tool execution
        
        IMPORTANT: 
        - Look for "Output data:" in the results above - it may contain JSON data
        - If there was an error during tool execution, explain what happened
        - Focus ONLY on what the user asked about, not other topics
        - Use the actual data in your response if available
        - If data retrieval failed, explain why and provide alternatives
        """
        
        return get_model_response(prompt)

    def _create_and_execute_new_tool(self, user_input: str, steps: List[dict], required_tool: str, tool_general_description: str) -> str:
        """Search for, create, and execute a new tool."""
        try:
            # Find best tool on GitHub
            print("   🔎 Searching GitHub for suitable tools...")
            # Convert steps to string list for find_best_tool
            step_descriptions = [step['description'] for step in steps] if isinstance(steps[0], dict) else steps
            tool_info = find_best_tool(user_input, step_descriptions, required_tool)
            if tool_info['score'] == 0:
                return "❌ Could not find a suitable tool for this task."

            # Generate installation commands
            install_cmds = generate_install_commands(tool_info['installation'])
            install_cmds = clean_and_validate_commands(install_cmds)

            # Ask user for installation approval
            print(f"\n   🎉 Found tool: {tool_info['name']}")
            print(f"   📝 Description: {tool_info['description']}")
            print("\n   📦 Installation commands:")
            for cmd in install_cmds:
                print(f"      🔧 {cmd}")
            approval = input("\n   ❓ Proceed with installation? (y/n): ")
            
            if approval.lower() != 'y':
                return "Tool installation cancelled."

            # Install dependencies
            print("   ⚡ Installing dependencies...")
            for cmd in install_cmds:
                print(f"      ⬇️ Running: {cmd}")
                success, output = install_dependencies(cmd)
                if not success:
                    return f"Failed to install dependencies: {output}"

            # Generate and validate code
            print("   🎨 Generating code...")
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

            # Generate tool description and save
            print("   📝 Generating tool description...")
            description = generate_code_description(
                user_question=user_input,
                required_tool=required_tool,
                code=code,
                tool_name=tool_info['name'],
                tool_general_description=tool_general_description
            )

            # Save and vectorize tool
            print("   💾 Saving tool...")
            tool_name = save_tool_code(description, code, tool_info['name'])
            print("   🧠 Vectorizing tool for future use...")
            vectorize_description(description, tool_info['name'])

            # Execute new tool
            print(f"   🚀 Executing new tool: {tool_name}")
            success, output = execute_python_code(f"{tool_name}.py")
            
            if not success:
                return f"Failed to execute new tool: {output}"
                
            # Return execution result
            return f"New tool {tool_name} created and executed successfully. Output captured."

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
