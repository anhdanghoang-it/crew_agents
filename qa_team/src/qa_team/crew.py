from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters # For Stdio Server
from typing import List

@CrewBase
class QaTeam():
    """QaTeam crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    mcp_server_params = [
            # StdIO Server
            StdioServerParameters(
                command="npx",
                args=["@playwright/mcp@latest"],
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
