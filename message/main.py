import typer
from message.data import transform_features_py  # noqa
from message.data import transform_features_sql  # noqa
from message.data import get_features
from prompts.prompt import SYSTEM, SYSTEM_FEEDBACK, EXTRA_FEEDBACK, TONE_PROMPT, GENERIC_PROMPT, ENGAGEMENT_PROMPT, FACTUALITY_PROMPT, OTHER_PROMPT
from enum import StrEnum

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


@app.command()
def get_message(
    session_group: str,
    chat_history: list[dict[str, str]] | None = None,
    session_group_limit: int | None = None,
    feedback_cat: FeedbackOption = FeedbackOption.OTHER,
    extra_feedback: str = None ) -> str:
    
    # Perform checks
    if extra_feedback and not chat_history:
        raise ValueError("'extra_feedback' can only be provided when 'chat_history' is provided")
    if session_group_limit and session_group_limit > 0:
        raise ValueError("'session_group_limit' must be greater than 0")
    FeedbackOption(feedback_cat) # raises ValueError if not valid option

    extra_feedback = extra_feedback if extra_feedback else ""   

    session_group_limit = session_group if not session_group_limit else session_group_limit[:session_group_limit]
    
    features = get_features(session_group=session_group_limit)  # noqa

    messages = [{"role": "system", "content": SYSTEM.format(session_data=features)}]

    if chat_history:
        messages.extend(chat_history)
    
    if extra_feedback:
        messages.append({"role": "system", "content": SYSTEM_FEEDBACK})
        messages.append({"role": "system", "content": FEEDBACK_PROMPT_MAP[feedback_cat]})
        messages.append({"role": "user", "content": EXTRA_FEEDBACK.format(extra_feedback=extra_feedback)})

    print("Sending:", messages)
    message = chat_model.get_completion(
            temperature=0,
            model="gpt-4o-mini",
            messages=messages
    )

    return message
