from datetime import datetime 
from typing import List
from pydantic import BaseModel, Field
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import SerperDevTool
from src.marketing_cc.tools.image_hosting_tool import ImageHostingTool
from src.marketing_cc.tools.image_generation_tool import ImageGenerationTool
from src.marketing_cc.tools.instagram_api_tool import InstagramAPITool

class ContentCreationOutput(BaseModel):
    caption: str = Field(..., description="The fully written Instagram caption, including hashtags.")
    image_paths: List[str] = Field(..., description="A strict list of local file paths for the 3 to 5 generated images.")

class HostedImagesOutput(BaseModel):
    image_urls: List[str] = Field(..., description="A strict list of public ImgBB URLs for the uploaded images.")

@CrewBase
class InstagramAutomationCrew():
    """Instagram Automation Crew"""
    
    agents: list[BaseAgent]
    tasks: list[Task]
    
    TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S") 
    OUTPUT_DIR = f"output/{TIMESTAMP}"
    
    # Agents section
    @agent
    def research_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['research_agent'],
            verbose=True,
            allow_delegation=False, 
            tools=[SerperDevTool()] 
        )

    @agent
    def content_selection_agent(self) -> Agent:
        return Agent(config=self.agents_config['content_selection_agent'], verbose=True)

    @agent
    def editorial_planning_agent(self) -> Agent:
        return Agent(config=self.agents_config['editorial_planning_agent'], verbose=True)

    @agent
    def content_creation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['content_creation_agent'],
            verbose=True,
            tools=[ImageGenerationTool()]
        )

    @agent
    def review_agent(self) -> Agent:
        return Agent(config=self.agents_config['review_agent'], verbose=True)

    @agent
    def image_hosting_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['image_hosting_agent'], 
            verbose=True,
            tools=[ImageHostingTool()] 
        )

    @agent
    def instagram_publishing_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['instagram_publishing_agent'], 
            verbose=True,
            tools=[InstagramAPITool()]
        )

    @agent
    def monitoring_agent(self) -> Agent:
        return Agent(config=self.agents_config['monitoring_agent'], verbose=True)

    @agent
    def learning_agent(self) -> Agent:
        return Agent(config=self.agents_config['learning_agent'], verbose=True)

    # Tasks section
    @task
    def market_research(self) -> Task:
        return Task(config=self.tasks_config['market_research'])

    @task
    def content_selection(self) -> Task:
        return Task(
            config=self.tasks_config['content_selection'],
            context=[self.market_research()],
            output_file=f'{self.OUTPUT_DIR}/selection_output.md'
        )

    @task
    def editorial_planning(self) -> Task:
        return Task(
            config=self.tasks_config['editorial_planning'],
            context=[self.content_selection()],
            output_file=f'{self.OUTPUT_DIR}/planning_output.md'
        )

    @task
    def content_creation(self) -> Task:
        return Task(
            config=self.tasks_config['content_creation'],
            context=[self.editorial_planning()],
            output_pydantic=ContentCreationOutput,
            output_file=f'{self.OUTPUT_DIR}/creation_result.md'
        )

    @task
    def content_review(self) -> Task:
        return Task(
            config=self.tasks_config['content_review'],
            context=[self.content_creation()],
            output_file=f'{self.OUTPUT_DIR}/review_result.md'
        )

    @task
    def image_hosting(self) -> Task:
        return Task(
            config=self.tasks_config['image_hosting'],
            context=[self.content_creation()],
            output_pydantic=HostedImagesOutput,
            output_file=f'{self.OUTPUT_DIR}/hosted_urls.md'
        )

    @task
    def instagram_publishing(self) -> Task:
        return Task(
            config=self.tasks_config['instagram_publishing'],
            context=[self.content_review(), self.image_hosting()],
            output_file=f'{self.OUTPUT_DIR}/publish_report.md'
        )

    @task
    def monitoring_and_analysis(self) -> Task:
        return Task(
            config=self.tasks_config['monitoring_and_analysis'],
            output_file=f'{self.OUTPUT_DIR}/performance_report.md'
        )

    @task
    def strategy_learning(self) -> Task:
        return Task(
            config=self.tasks_config['strategy_learning'],
            context=[self.monitoring_and_analysis()],
            output_file=f'{self.OUTPUT_DIR}/strategy_report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Instagram Automation Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )