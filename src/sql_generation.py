from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI


class SQLQuery(BaseModel):
    """Schema for SQL query solutions to questions."""
    description: str = Field(description="Description of the SQL query")
    sql_code: str = Field(description="The SQL code block")

def get_sql_gen_chain():
    """Set up the SQL generation chain."""
    sql_gen_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a SQL assistant with expertise in SQL query generation. \n
Answer the user's question based on the provided documentation snippets and the database schema provided below. Ensure any SQL query you provide is valid and executable. \n
Structure your answer with a description of the query, followed by the SQL code block. Here are the documentation snippets:\n{retrieved_docs}\n\nDatabase Schema:\n{database_schema}""",
            ),
            ("placeholder", "{messages}"),
        ]
    )

    llm = ChatGoogleGenerativeAI(temperature=0, model='gemini-1.5-turbo')

    sql_gen_chain = sql_gen_prompt | llm.with_structured_output(SQLQuery)

    return sql_gen_chain
