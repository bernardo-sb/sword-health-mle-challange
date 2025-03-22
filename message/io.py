"""File I/O operations."""
import os
import json
import yaml
import pandas as pd
from pathlib import Path


def load_exercise_data(data_dir: str | Path) -> pd.DataFrame:
    """Load exercise results data from parquet file.
    
    Parameters
    ----------
    data_dir : str or Path
        Directory containing the exercise results data.
        
    Returns
    -------
    pd.DataFrame
        Raw exercise results data.
    """
    return pd.read_parquet(Path(data_dir, "exercise_results.parquet"))

def load_prompts() -> dict[str, str]:
    """Load prompts from YAML file.

    Returns
    -------
    dict[str, str]
        The prompts.
    """
    with open("prompts/prompts.yml", "r") as f:
        return yaml.safe_load(f)


def load_chat_history(chat_id: str) -> list[dict[str, str]]:
    """Load chat history from JSONL file.

    Parameters
    ----------
    chat_id : str
        The chat id.

    Returns
    -------
    list[dict[str, str]]
        The chat history.
    """
    os.makedirs(".chats", exist_ok=True)
    chat_file = os.path.join(".chats", f"{chat_id}.jsonl")

    if not os.path.exists(chat_file):
        with open(chat_file, "w") as f:
            return []

    with open(chat_file, "r") as f:
        return [json.loads(line) for line in f]

async def save_chat_history(chat_id: str, chat_history: list[dict[str, str]]):
    """Save chat history to JSONL file.

    Parameters
    ----------
    chat_id : str
        The chat id.
    chat_history : list[dict[str, str]]
        The chat history.
    """
    chat_file = os.path.join(".chats", f"{chat_id}.jsonl")
    with open(chat_file, "w") as f:
        for message in chat_history:
            f.write(json.dumps(message) + "\n")
