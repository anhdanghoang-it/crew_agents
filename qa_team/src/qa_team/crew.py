from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters # For Stdio Server
from typing import List
import json
import os
from pathlib import Path

@CrewBase
class QaTeam():
    """QaTeam crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # mcp_server_params = [
    #         # StdIO Server
    #         StdioServerParameters(
    #             command="npx",
    #             args=["@playwright/mcp@latest"],
    #         )
    #     ]

    mcp_server_params = [
        # StdIO Server
        StdioServerParameters(
            command="npx",
            args=["playwright", "run-test-mcp-server"],
        )
    ]

    @agent
    def snapshot_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['snapshot_agent'], # type: ignore[index]
            tools=self.get_mcp_tools(),
            verbose=True
        )
    
    @agent
    def test_plan_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['test_plan_agent'], # type: ignore[index]
            verbose=True
        )    
    
    @agent
    def test_generator_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['test_generator_agent'], # type: ignore[index]
            verbose=True
        )    
    
    @agent
    def test_healer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['test_healer_agent'], # type: ignore[index]
            tools=self.get_mcp_tools(),
            verbose=True
        )  

    @task
    def take_snapshot_task(self) -> Task:
        return Task(
            config=self.tasks_config['take_snapshot_task'], # type: ignore[index]
        )
    
    @task
    def generate_test_plan_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_test_plan_task'], # type: ignore[index]
        )    
    
    @task
    def generate_playwright_tests_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_playwright_tests_task'], # type: ignore[index]
            callback=self._process_test_files_callback
        )

    def _process_test_files_callback(self, task_output):
        """
        Callback to process the JSON output and write individual test files to e2e folder.
        Works for both test generation and test healing outputs.
        """
        try:
            # Get the output content
            content = task_output.raw if hasattr(task_output, 'raw') else str(task_output)
            
            # Clean up markdown code fences if present
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]  # Remove ```json
            elif content.startswith('```'):
                content = content[3:]  # Remove ```
            
            if content.endswith('```'):
                content = content[:-3]  # Remove trailing ```
            
            content = content.strip()
            
            # Parse JSON
            test_files = json.loads(content)
            
            # Ensure e2e directory exists
            e2e_dir = Path("e2e")
            e2e_dir.mkdir(exist_ok=True)
            
            # Write each test file
            for test_file in test_files:
                filename = test_file.get("filename")
                file_content = test_file.get("content")
                
                if filename and file_content:
                    file_path = e2e_dir / filename
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(file_content)
                    print(f"✅ Written: {file_path}")
            
            print(f"\n🎉 Successfully processed {len(test_files)} test files in e2e/ folder")
            print(f"📁 Files are ready for execution: npx playwright test")
            
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON output: {e}")
            print(f"Raw output (first 500 chars):\n{content[:500] if 'content' in locals() else 'N/A'}...")
            print(f"\nPlease ensure the agent outputs pure JSON without markdown code fences.")
        except Exception as e:
            print(f"❌ Error processing test files: {e}")

    @task
    def heal_playwright_tests_task(self) -> Task:
        return Task(
            config=self.tasks_config['heal_playwright_tests_task'], # type: ignore[index]
            callback=self._process_test_files_callback  # Reuse same callback to write healed files
        )

    @crew
    def crew(self) -> Crew:
        """Creates the QaTeam crew"""

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            memory=True,
            verbose=True,
        )
