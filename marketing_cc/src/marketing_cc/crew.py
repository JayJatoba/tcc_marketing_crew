from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent


@CrewBase
class InstagramAutomationCrew():
    """Instagram Automation Crew"""
    
    agents: list[BaseAgent]
    tasks: list[Task]
    
    # Agents section
    @agent
    def research_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['research_agent'],
            verbose=True,
            allow_delegation=True
        )

    @agent
    def content_selection_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['content_selection_agent'],
            verbose=True
        )

    @agent
    def editorial_planning_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['editorial_planning_agent'],
            verbose=True
        )

    @agent
    def content_creation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['content_creation_agent'],
            verbose=True
        )

    @agent
    def review_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['review_agent'],
            verbose=True
        )

    @agent
    def automation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['automation_agent'],
            verbose=True
        )

    @agent
    def monitoring_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['monitoring_agent'],
            verbose=True
        )

    @agent
    def learning_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['learning_agent'],
            verbose=True
        )

    # Tasks section
    @task
    def market_research(self) -> Task:
        return Task(
            config=self.tasks_config['market_research']
        )

    @task
    def content_selection(self) -> Task:
        return Task(
            config=self.tasks_config['content_selection'],
            output_file='selection_output.md'
        )

    @task
    def editorial_planning(self) -> Task:
        return Task(
            config=self.tasks_config['editorial_planning'],
            context=[self.market_research()],
            output_file='planning_output.md'
        )

    @task
    def content_creation(self) -> Task:
        return Task(
            config=self.tasks_config['content_creation'],
            context=[self.content_selection()],
            output_file='creation_result.md'
        )

    @task
    def content_review(self) -> Task:
        return Task(
            config=self.tasks_config['content_review'],
            output_file='review_result.md'
        )

    @task
    def post_automation(self) -> Task:
        return Task(
            config=self.tasks_config['post_automation'],
            context=[self.editorial_planning(),
                     self.content_review()],
            output_file='automation_report.md'
        )

    @task
    def monitoring_and_analysis(self) -> Task:
        return Task(
            config=self.tasks_config['monitoring_and_analysis'],
            context=[self.post_automation()],
            output_file='performance_report.md'
        )

    @task
    def strategy_learning(self) -> Task:
        return Task(
            config=self.tasks_config['strategy_learning'],
            context=[ 
                self.monitoring_and_analysis(), 
                self.content_review(), 
                self.market_research()
                ],
            output_file='strategy_report.md'
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
