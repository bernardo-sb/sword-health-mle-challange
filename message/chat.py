"""Chat"""

from enum import StrEnum
from message.io import load_chat_history, load_prompts, save_chat_history
from uuid import uuid4
from message.config import get_settings
from message.model import ChatModel
from message.data import get_features
import typer

prompts = load_prompts()
settings = get_settings()
chat_model = ChatModel()


class FeedbackOption(StrEnum):
    TONE = "tone"
    GENERIC = "generic"
    ENGAGEMENT = "engagement"
    FACTUALITY = "factuality"
    OTHER = "other"

FEEDBACK_PROMPT_MAP = {
    FeedbackOption.TONE: prompts["TONE_PROMPT"],
    FeedbackOption.GENERIC: prompts["GENERIC_PROMPT"],
    FeedbackOption.ENGAGEMENT: prompts["ENGAGEMENT_PROMPT"],
    FeedbackOption.FACTUALITY: prompts["FACTUALITY_PROMPT"],
    FeedbackOption.OTHER: prompts["OTHER_PROMPT"],
}

def prompt_for_acceptance() -> str:
    """Prompt user for message acceptance.

    Returns
    -------
    str
        The response.
    """
    response = None
    while not response:
        response = input("Accept | Edit | Reject: ").strip().lower()
        if response not in ["accept", "edit", "reject"]:
            print("Invalid response. Please enter 'accept', 'edit', or 'reject'.")
            response = None

    return response
    
def prompt_for_feedback() -> tuple[str, str]:
    """Prompt user for feedback.

    Returns
    -------
    tuple[str, str]
        The category and feedback.
    """
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
    """Get a chat completion from the LLM.

    Parameters
    ----------
    messages : list[dict[str, str]]
        The messages to send to the LLM.

    Returns
    -------
    str
        The chat completion response.
    """
    return chat_model.get_completion(
            temperature=0,
            model="gpt-4o-mini",
            messages=messages
    )

async def run_chat(session_group: str):
    """Run the chat.

    Parameters
    ----------
    session_group : str
        The session group to load from file.
    """
    try:
        print("[INFO] Loading session group:", session_group)

        features = get_features(session_group=session_group)  # noqa

        chat_id = str(uuid4())
        print("[INFO] Starting chat with id:", chat_id)

        chat_history = load_chat_history(chat_id)

        if not chat_history:
            chat_history.append(
                {
                    "role": "system",
                    "content": prompts["SYSTEM_BASE"].format(session_data=features)
                }
            )

        print("[INFO] Starting chat...")
        print("="*50)

        acceptance = None
        while acceptance not in ["accept", "reject"]:
            message = llm(chat_history)
            
            print("Message:", message)

            acceptance = prompt_for_acceptance()

            if acceptance == "accept":
                chat_history.append({"role": "assistant", "content": message})
            if acceptance == "edit":
                category, feedback = prompt_for_feedback()
                
                # NOTE: could only save accepted messages instead (e.g. use temp_chat_history)
                chat_history.append({"role": "system", "content": SYSTEM_FEEDBACK.format(feedback_prompt=FEEDBACK_PROMPT_MAP[FeedbackOption(category)])})
                chat_history.append({"role": "user", "content": EXTRA_FEEDBACK.format(extra_feedback=feedback)})

                message = llm(chat_history)

                print("Message:", message)
                print("-"*50)
            if acceptance == "reject":
                message = input("Write your answer: ")
                chat_history.append({"role": "assistant", "content": message})

        print()
        print("="*50)
        print("[INFO] Shutting down...")
        await save_chat_history(chat_id, chat_history)
        return
    except Exception as e:
        print(e)
        print()
        print("="*50)
        print("[INFO] Shutting down...")

        await save_chat_history(chat_id, chat_history)

        raise typer.Exit()
