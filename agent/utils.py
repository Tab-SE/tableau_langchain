import os
import getpass

from IPython.display import Image, display


def _set_env(var: str):
    """
    if environment variable not set, safely prompts user for value returns the newly resolved variable
    """
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")


def _visualize_graph(graph):
    """
    Creates a mermaid visualization of the State Graph .png format
    """
    try:
        display(Image(graph.get_graph().draw_mermaid_png()))
    except Exception:
        # This requires some extra dependencies and is optional
        pass


def stream_graph_updates(user_input: str, graph):
    """
    Processes the given user input and streams updates from the state graph.

    This function takes a string input from the user and passes it to the state graph's streaming interface.
    Each event generated by the graph is iterated over, and within each event, the function looks for values
    associated with the 'messages' key.

    For each message found, the function prints the content of the last message in the sequence, which is assumed
    to be the response from the assistant. This allows for a dynamic conversation-like interaction where the
    assistant's responses are generated and displayed in real-time based on the user's input.

    Parameters:
    - user_input (str): The input string from the user that will be processed by the state graph.

    Returns:
    None. The function's primary side effect is to print the assistant's response to the console.
    """
    for event in graph.stream({"messages": [("user", user_input)]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)
