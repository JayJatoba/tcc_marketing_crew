import sys
import warnings
import json
from dotenv import load_dotenv

from datetime import datetime

from marketing_cc.crew import InstagramAutomationCrew

warnings.filterwarnings(
    "ignore",
    category=SyntaxWarning,
    module="pysbd"
)

_ = load_dotenv()

def get_default_inputs():
    return {
        "research_topic": "The boom invloving hyrox",
        "target_audience": "Amateur athletes and sports enthusiasts",
        "brand_tone": "inspiring, informative",
        "current_year": str(datetime.now().year)
    }

def run():
    """
    Run the crew.
    """

    inputs = get_default_inputs()

    try:
        result = (
            InstagramAutomationCrew()
            .crew()
            .kickoff(inputs=inputs)
        )

        print(result)

    except Exception as e:
        print(e)
        raise Exception(
            f"An error occurred while running the crew: {e}"
        )

def train():
    """
    Train the crew.
    """

    inputs = get_default_inputs()

    try:
        (
            InstagramAutomationCrew()
            .crew()
            .train(
                n_iterations=int(sys.argv[1]),
                filename=sys.argv[2],
                inputs=inputs
            )
        )

    except Exception as e:
        raise Exception(
            f"An error occurred while training the crew: {e}"
        )

def replay():
    """
    Replay a previous crew execution.
    """

    try:
        (
            InstagramAutomationCrew()
            .crew()
            .replay(task_id=sys.argv[1])
        )

    except Exception as e:
        raise Exception(
            f"An error occurred while replaying the crew: {e}"
        )

def test():
    """
    Test the crew.
    """

    inputs = get_default_inputs()

    try:
        (
            InstagramAutomationCrew()
            .crew()
            .test(
                n_iterations=int(sys.argv[1]),
                eval_llm=sys.argv[2],
                inputs=inputs
            )
        )

    except Exception as e:
        raise Exception(
            f"An error occurred while testing the crew: {e}"
        )

def run_with_trigger():
    """
    Run the crew using an external trigger payload.
    """

    if len(sys.argv) < 2:
        raise Exception(
            "No trigger payload provided. "
            "Please provide JSON payload as argument."
        )

    try:
        trigger_payload = json.loads(sys.argv[1])

    except json.JSONDecodeError:
        raise Exception(
            "Invalid JSON payload provided as argument."
        )

    inputs = {
        "crewai_trigger_payload": trigger_payload,

        "research_topic": trigger_payload.get(
            "research_topic",
            "AI automation"
        ),

        "target_audience": trigger_payload.get(
            "target_audience",
            "entrepreneurs"
        ),

        "brand_tone": trigger_payload.get(
            "brand_tone",
            "professional"
        ),

        "current_year": str(datetime.now().year)
    }

    try:
        result = (
            InstagramAutomationCrew()
            .crew()
            .kickoff(inputs=inputs)
        )

        print(result)

        return result

    except Exception as e:
        raise Exception(
            f"An error occurred while running the crew "
            f"with trigger: {e}"
        )

run()