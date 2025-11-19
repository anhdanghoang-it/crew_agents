#!/usr/bin/env python
import sys
import warnings
import time

from datetime import datetime

from qa_team.crew import QaTeam

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    with open(f"output/user_stories.md", "r", encoding="utf-8") as f:
        user_stories = f.read()
    
    with open(f"output/snapshot.md", "r", encoding="utf-8") as f:
        snapshot = f.read()   

    with open(f"output/test_plan.md", "r", encoding="utf-8") as f:
        test_plan = f.read()     

    with open(f"output/simulation.spec.ts", "r", encoding="utf-8") as f:
        test_scripts = f.read()        

    with open(f"e2e/test-files.json", "r", encoding="utf-8") as f:
        test_files_json = f.read()   
    
    inputs = {
        'given_url': 'http://127.0.0.1:7860/',
        'userstories': user_stories,
        'snapshot': snapshot,
        'test_plan': test_plan,
        'test_scripts': test_scripts,
        'test_files_json': test_files_json,
        'time_stamp': int(time.time())
    }

    try:
        QaTeam().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        QaTeam().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        QaTeam().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }

    try:
        QaTeam().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

def run_with_trigger():
    """
    Run the crew with trigger payload.
    """
    import json

    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    inputs = {
        "crewai_trigger_payload": trigger_payload,
        "topic": "",
        "current_year": ""
    }

    try:
        result = QaTeam().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")
