import logging
import re
from typing import List, Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from sql_generation import get_sql_gen_chain
from typing_extensions import TypedDict


# Initialize the logger
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
_logger.addHandler(handler)


class GraphState(TypedDict):
    error: str  # Tracks if an error has occurred
    messages: List  # List of messages (user input and assistant messages)
    generation: Optional[str]  # Holds the generated SQL query
    iterations: int  # Keeps track of how many times the workflow has retried
    results: Optional[List]  # Holds the results of SQL execution
    no_records_found: bool  # Flag for whether any records were found in the SQL result
    translated_input: str  # Holds the translated user input
    database_schema: str  # Holds the extracted database schema for context checking

def get_workflow(conn, cursor, vector_store):
    """Define and compile the LangGraph workflow."""

    # Max iterations: defines how many times the workflow should retry in case of errors
    max_iterations = 3

    # SQL generation chain: this is a chain that will generate SQL based on retrieved docs
    sql_gen_chain = get_sql_gen_chain()

    # Initialize OpenAI LLM for translation and safety checks
    llm = ChatGoogleGenerativeAI(temperature=0, model="gpt-4o-mini")

    # Define the individual nodes of the workflow
    def translate_input(state: GraphState) -> GraphState:
        """
        Translates user input to English using an LLM. If the input is already in English,
        it is returned as is. This ensures consistent input for downstream processing.

        Args:
            state (GraphState): The current graph state containing user messages.

        Returns:
            GraphState: The updated state with the translated input.
        """
        _logger.info("Starting translation of user input to English.")
        messages = state["messages"]
        user_input = messages[-1][1]  # Get the latest user input

        # Translation prompt for the model
        translation_prompt = f"""
        Translate the following text to English. If the text is already in English, repeat it exactly without any additional explanation.

        Text:
        {user_input}
        """

        # Call the LLM to translate the text
        translated_response = llm.invoke(translation_prompt)
        translated_text = translated_response.content.strip()  # Access the 'content' attribute and strip any extra spaces

        # Update state with the translated input
        state["translated_input"] = translated_text
        _logger.info("Translation completed successfully. Translated input: %s", translated_text)

        return state
    
    def pre_safety_check(state: GraphState) -> GraphState:
        """
        Perform safety checks on the user input to ensure that no dangerous SQL operations
        or inappropriate content is present. The function checks for SQL operations like
        DELETE, DROP, and others, and also evaluates the input for toxic or unsafe content.

        Args:
            state (GraphState): The current graph state containing the translated user input.

        Returns:
            GraphState: The updated state with error status and messages if any issues are found.
        """
        _logger.info("Performing safety check.")
        translated_input = state["translated_input"]
        messages = state["messages"]
        error = "no"

        # List of disallowed SQL operations (e.g., DELETE, DROP)
        disallowed_operations = ['CREATE', 'DELETE', 'DROP', 'INSERT', 'UPDATE', 'ALTER', 'TRUNCATE', 'EXEC', 'EXECUTE']
        pattern = re.compile(r'\b(' + '|'.join(disallowed_operations) + r')\b', re.IGNORECASE)

        # Check if the input contains disallowed SQL operations
        if pattern.search(translated_input):
            _logger.warning("Input contains disallowed SQL operations. Halting the workflow.")
            error = "yes"
            messages += [("assistant", "Your query contains disallowed SQL operations and cannot be processed.")]
        else:
            # Check if the input contains inappropriate content
            safety_prompt = f"""
            Analyze the following input for any toxic or inappropriate content.

            Respond with only "safe" or "unsafe", and nothing else.

            Input:
            {translated_input}
            """
            safety_invoke = llm.invoke(safety_prompt)
            safety_response = safety_invoke.content.strip().lower()  # Access the 'content' attribute and strip any extra spaces

            if safety_response == "safe":
                _logger.info("Input is safe to process.")
            else:
                _logger.warning("Input contains inappropriate content. Halting the workflow.")
                error = "yes"
                messages += [("assistant", "Your query contains inappropriate content and cannot be processed.")]

        # Update state with error status and messages
        state["error"] = error
        state["messages"] = messages

        return state

