"""Application use cases for Jira task management."""
import json
import subprocess
import os
from pathlib import Path
from typing import Optional
import traceback

from app.domain.jira.entities import JiraTask, JiraBatchConfig
from app.infrastructure.logging.logging_config import get_logger

logger = get_logger(__name__)


class CreateJiraBatch:
    """Use case for creating Jira tasks via batch file."""

    def __init__(self, working_directory: Optional[str] = None):
        """Initialize use case with optional working directory."""
        self.working_directory = working_directory or os.getcwd()

    def execute(self, tasks: list[dict], last_env: str = "prod") -> dict:
        """
        Create jira.json file and execute jirabatch.py script.
        
        Args:
            tasks: List of task dictionaries with jira fields
            last_env: Environment setting (default: "prod")
            
        Returns:
            dict with status, message, and command output
        """
        logger.info(f"[CreateJiraBatch] Starting execution with {len(tasks)} tasks, env={last_env}")
        logger.debug(f"[CreateJiraBatch] Working directory: {self.working_directory}")
        
        try:
            # Convert dictionaries to domain entities
            jira_tasks = [
                JiraTask(
                    summary=task["summary"],
                    brief=task["brief"],
                    outcome=task["outcome"],
                    assignee=task["assignee"],
                    stakeholder=task["stakeholder"],
                    labels=task["labels"],
                    due_date=task["due_date"]
                )
                for task in tasks
            ]
            logger.debug(f"[CreateJiraBatch] Converted {len(jira_tasks)} tasks to domain entities")

            # Create batch config
            batch_config = JiraBatchConfig(
                last_env=last_env,
                tasks=jira_tasks
            )

            # Write jira.json file
            json_path = Path(self.working_directory) / "jira.json"
            logger.info(f"[CreateJiraBatch] Writing JSON to: {json_path}")
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(batch_config.to_dict(), f, indent=2)
            
            logger.info(f"[CreateJiraBatch] JSON file created successfully")

            # Execute jirabatch.py script
            script_path = "bin/python/my_app/taskmanager/jirabatch.py"
            command = f"{script_path} {json_path}"
            
            logger.info(f"[CreateJiraBatch] Executing command: {command}")
            logger.debug(f"[CreateJiraBatch] CWD: {self.working_directory}")
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.working_directory
            )
            
            logger.info(f"[CreateJiraBatch] Command completed with return code: {result.returncode}")
            if result.stdout:
                logger.info(f"[CreateJiraBatch] STDOUT: {result.stdout}")
            if result.stderr:
                logger.warning(f"[CreateJiraBatch] STDERR: {result.stderr}")

            return {
                "success": result.returncode == 0,
                "message": "Jira batch created and executed successfully" if result.returncode == 0 else f"Execution failed with return code {result.returncode}",
                "json_path": str(json_path),
                "command": command,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "working_directory": self.working_directory
            }

        except Exception as e:
            error_traceback = traceback.format_exc()
            logger.error(f"[CreateJiraBatch] Error: {str(e)}")
            logger.error(f"[CreateJiraBatch] Traceback:\n{error_traceback}")
            
            return {
                "success": False,
                "message": f"Error creating Jira batch: {str(e)}",
                "error": str(e),
                "traceback": error_traceback,
                "working_directory": self.working_directory
            }
