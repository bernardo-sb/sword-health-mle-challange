import typer
from message.data import transform_features_py  # noqa
from message.data import transform_features_sql  # noqa
from message.chat import run_chat
import asyncio

app = typer.Typer()


@app.command()
def transform():
    # Uncomment the function you want to run
    # transform_features_sql()
    transform_features_py()

    return


@app.command()
def get_message(session_group: str):
    """Get a message from the chat.

    Parameters
    ----------
    session_group : str
        The session group to load from file.
    """
    asyncio.run(run_chat(session_group))
