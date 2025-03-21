import os
import typer
from message.data import transform_features_py  # noqa
from message.data import transform_features_sql  # noqa
from message.data import get_features
from message.config import get_settings
from message.model import ChatModel
from message.prompts import SYSTEM_BASE, SYSTEM_FEEDBACK, EXTRA_FEEDBACK, TONE_PROMPT, GENERIC_PROMPT, ENGAGEMENT_PROMPT, FACTUALITY_PROMPT, OTHER_PROMPT
from enum import StrEnum
from uuid import uuid4
import json
import asyncio

settings = get_settings()
chat_model = ChatModel()

class FeedbackOption(StrEnum):
    TONE = "tone"
    GENERIC = "generic"
    ENGAGEMENT = "engagement"
    FACTUALITY = "factuality"
    OTHER = "other"

FEEDBACK_PROMPT_MAP = {
    FeedbackOption.TONE: TONE_PROMPT,
    FeedbackOption.GENERIC: GENERIC_PROMPT,
    FeedbackOption.ENGAGEMENT: ENGAGEMENT_PROMPT,
    FeedbackOption.FACTUALITY: FACTUALITY_PROMPT,
    FeedbackOption.OTHER: OTHER_PROMPT,
}


app = typer.Typer()


@app.command()
def transform():

    # Uncomment the function you want to run
    # transform_features_sql()
    transform_features_py()

    return

def load_chat_history(chat_id: str) -> list[dict[str, str]]:
    """Load chat history from JSONL file."""
    os.makedirs(".chats", exist_ok=True)
    chat_file = os.path.join(".chats", f"{chat_id}.jsonl")

    if not os.path.exists(chat_file):
        with open(chat_file, "w") as f:
            return []

    with open(chat_file, "r") as f:
        return [json.loads(line) for line in f]

def prompt_for_acceptance() -> str:
    """Prompt user for message acceptance."""
    response = None
    while not response:
        response = input("Accept | Edit | Reject: ").strip().lower()
        if response not in ["accept", "edit", "reject"]:
            print("Invalid response. Please enter 'accept', 'edit', or 'reject'.")
            response = None

    return response
    
def prompt_for_feedback() -> tuple[str, str]:
    """Prompt user for feedback."""
    category = None
    while not category:
        category = input("Editing Reasons (optional) - [tone, generic, engagement, factuality, other]: ").lower().strip()
        try:
            category = "other" if not category else category
            category = FeedbackOption(category)
        except ValueError:
            print("Invalid category. Please enter 'tone', 'generic', 'engagement', 'factuality', or 'other'.")
    
    feedback = None
    while not feedback:
        feedback = input("Feedback: ").strip().lower()
        if not feedback:
            print("Feedback cannot be empty.")
    return category, feedback

def llm(messages: list[dict[str, str]]) -> str:
    return chat_model.get_completion(
            temperature=0,
            model="gpt-4o-mini",
            messages=messages
    )

async def save_chat_history(chat_id: str, chat_history: list[dict[str, str]]):
    chat_file = os.path.join(".chats", f"{chat_id}.jsonl")
    with open(chat_file, "w") as f:
        for message in chat_history:
            f.write(json.dumps(message) + "\n")

async def _run(session_group: str) -> str:
    try:
        print("Loading session group:", session_group)

        features = get_features(session_group=session_group)  # noqa

        chat_id = str(uuid4())
        print("Starting chat with id:", chat_id)

        chat_history = load_chat_history(chat_id)

        if not chat_history:
            chat_history.append({"role": "system", "content": SYSTEM_BASE.format(session_data=features)})

        print("="*50)
        while True:
            message = llm(chat_history)
            
            print("Message:", message)

            acceptance = prompt_for_acceptance()

            if acceptance == "accept":
                chat_history.append({"role": "assistant", "content": message})
                _ = asyncio.create_task(save_chat_history(chat_id, chat_history))
            if acceptance == "edit":
                category, feedback = prompt_for_feedback()
                
                # TODO: only save accepted messages (e.g. use tem_chat_history)
                chat_history.append({"role": "system", "content": SYSTEM_FEEDBACK.format(feedback_prompt=FEEDBACK_PROMPT_MAP[FeedbackOption(category)])})
                chat_history.append({"role": "user", "content": EXTRA_FEEDBACK.format(extra_feedback=feedback)})

                message = llm(chat_history)

                print("Message:", message)
                print("-"*50)
            if acceptance == "reject":
                message = input("Write your answer: ")
                chat_history.append({"role": "assistant", "content": message})
                asyncio.create_task(save_chat_history(chat_id, chat_history))
    except:
        print()
        print("="*50)
        print("\nShutting down...")
        await save_chat_history(chat_id, chat_history)
        
        raise typer.Exit()

@app.command()
def get_message(session_group: str) -> str:
    asyncio.run(_run(session_group))
