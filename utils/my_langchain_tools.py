#import duckdb
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
import utils.embedding as embedding
import yaml
import os
import langchain
from langchain_community.vectorstores import FAISS
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
#from operator import itemgetter
from langchain_core.prompts import PromptTemplate
#from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from sqlalchemy import create_engine
from langchain_core.tools import tool
from langchain_core.prompts import FewShotPromptTemplate
from langchain.chains import create_sql_query_chain
#from langchain_core.messages import AIMessage
# from langchain_core.runnables import (
#     Runnable,
#     RunnableLambda,
#     RunnableMap,
#     RunnablePassthrough,
# )
import my_db_specifics as my_db_specifics

with open("config.yaml", "r") as stream:
    try:
        PARAM = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

langchain.debug = False
engine = create_engine('duckdb:///' + PARAM['drugdb_path'])
db = SQLDatabase(engine=engine, view_support=True)
#print(db.dialect)
print(db.get_usable_table_names())

for c in my_db_specifics.initialization_commands:
    db.run(c)


# Set up your OpenAI API key
os.environ["OPENAI_API_KEY"] = PARAM['openai_api']
llm = ChatOpenAI(model_name="gpt-4o-mini")
# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
# os.environ["LANGCHAIN_API_KEY"] = PARAM['langsmith_api']
# os.environ["LANGCHAIN_PROJECT"] = "default"

@tool
def SQL_QueryTool(my_question: str, limit: int = 20) -> str:
    """Use the SQL route to get the answer from the database"""
    print ("my_question", my_question)
    print ("limit", limit)

    database_description = my_db_specifics.sql_database_prompt
    
    examples = my_db_specifics.sql_examples


    example_selector = SemanticSimilarityExampleSelector.from_examples(
        examples,
        OpenAIEmbeddings(),
        FAISS,
        k=5,
        input_keys=["input"],
    )

    example_prompt = PromptTemplate.from_template("User input: {input}\nSQL query: {query}")
    sql_generation_prompt = FewShotPromptTemplate(
        example_selector=example_selector,
        example_prompt=example_prompt,
        prefix="You are a {dialect} expert. Given an input question, create a syntactically correct DuckDB query to run. Unless otherwise specificed, do not return more than {top_k} rows.\n\nHere is the relevant table info: {table_info}\n\nBelow are a number of examples of questions and their corresponding SQL queries.",
        suffix="User input: {input}\nSQL query: ",
        input_variables=["input", "top_k", "table_info"],
    )

    write_query = create_sql_query_chain(llm, db, sql_generation_prompt)
    #write_query = create_sql_query_chain(llm, db)
    print ("write_query", write_query)



    system = f"""
    Double check the user's {db.dialect} query for common mistakes, including:
    - If the search term contains a single quote, it should be escaped with another single quote. For example, 'Alzheimer's Disease' should be 'Alzheimer''s Disease'.
    - Only return SQL Query not anything else like ```sql ... ```
    - Using NOT IN with NULL values
    - Using UNION when UNION ALL should have been used
    - Using BETWEEN for exclusive ranges
    - Data type mismatch in predicates\
    - Using the correct number of arguments for functions
    - Casting to the correct data type
    - Using the proper columns for joins
    - Write a LIMIT {limit} clause at the end of the query.
    - Never write 'LIMIT 0', instead, remove the LIMIT clause entirely.
    - Make sure all parentheses are balanced.
    - Ends with a semicolon

    If there are any of the above mistakes, rewrite the query.
    If there are no mistakes, just reproduce the original query with no further commentary.

    Output the final SQL query only."""


    validation_prompt = ChatPromptTemplate.from_messages(
        [("system", system), ("human", "{query}")]
    )


    generate_query = (
        write_query
        | validation_prompt | llm | StrOutputParser()
    )
    
    sql_query = generate_query.invoke({"question": my_question, "top_k": limit, "table_info": database_description})
    
    return sql_query

@tool
def Graph_QueryTool(my_question: str, limit: int = 20) -> str:
    """Use the graph query language route to get the answer from the database. Only suitable for questions that involve the interrelationship between the Drugs, Disorders, and MOA tables."""

    print ("my_question", my_question)
    print ("limit", limit)
    database_description = my_db_specifics.graph_database_prompt
    
    examples = my_db_specifics.graph_examples

    example_selector = SemanticSimilarityExampleSelector.from_examples(
        examples,
        OpenAIEmbeddings(),
        FAISS,
        k=5,
        input_keys=["input"],
    )

    example_prompt = PromptTemplate.from_template("User input: {input}\graph query: {query}")

    pgq_generation_prompt = FewShotPromptTemplate(
        example_selector=example_selector,
        example_prompt=example_prompt,
        prefix="Forget the previous answer. You are a graph expert. Given an input question, create a syntactically correct graph query to run. \n\nHere is the relevant table info: {table_info}\n\nBelow are a number of examples of questions and their corresponding graph queries.",
        suffix="User input: {input}\ngraph query: ",
        input_variables=["input", "table_info", "top_k"],
    )

    system = f"""
    DuckPGQ is very similar to Cypher. But there are some differences.
    Double check the user's DuckPGQ graph query for common mistakes, including:
    - If the search term contains a single quote, it should be escaped with another single quote. For example, 'Alzheimer's Disease' should be 'Alzheimer''s Disease'.
    - It must start with "FROM GRAPH_TABLE (drug_graph" before the MATCH clause. It ends with a closing parenthesis before the LIMIT clause.
    - Only return graph qery not anything else like ```sql ... ```
    - Every variable in the graph pattern has to be bound by a variable. For example, (i:Drug)-[:MAY_TREAT]->(c:Disorder WHERE c.name = 'Alzheimer''s Disease') is not correct because :MAY_TREAT is not bound to a variable. Instead, it should be (i:Drug)-[m:MAY_TREAT]->(c:Disorder WHERE c.name = 'Alzheimer''s Disease').
    - Use "COLUMNS" as the return statement in the graph query.
    - Replace all '\n' with a space.
    - Write a LIMIT {limit} clause at the end of the query.
    - Never write 'LIMIT 0', instead, remove the LIMIT clause entirely but not the closing parenthesis before it, because that closing parenthesis belongs to the COLUMNS () clause.
    - Make sure all parentheses are balanced.

    - Ends with a semicolon

    If there are any of the above mistakes, rewrite the query.
    If there are no mistakes, just reproduce the original query with no further commentary.

    Output the final graph query only."""

    validation_prompt = ChatPromptTemplate.from_messages(
        [("system", system), ("human", "{query}")]
    )

    generate_query = (
        pgq_generation_prompt
        | validation_prompt
        | llm | StrOutputParser()
    )

    graph_query = generate_query.invoke({"input": my_question, "table_info": database_description, "top_k": limit})
    print ("graph_query", graph_query)
    return graph_query


@tool
def Fulltext_QueryTool(my_question: str, original_query: str, limit: int = 20) -> str:
    """Use the full text search to get the trials from the database. Only suitable for questions that involve the StudyTitle. Use this tool when users question does not read like a sentence and looks like some keywords instead. Keep the original query for the user's reference. And keep all the operators such as &, |, and ! in the query."""
    print ("original_query", original_query)
    field_with_full_text_search = "StudyTitle"

    generate_query = my_db_specifics.full_text_search_query_template.format(original_query=original_query.replace("'", "''"), field=field_with_full_text_search, limit=limit)

    # print ("Fulltext_QueryTool, query", query)
    # system = """
    # Forget the previous answer.
    # Double check the user's DuckPGQ graph query for common mistakes, including:
    # - If the search term contains a single quote, it should be escaped with another single quote. For example, 'Alzheimer's Disease' should be 'Alzheimer''s Disease'.

    # If there are any of the above mistakes, rewrite the query.
    # If there are no mistakes, just reproduce the original query with no further commentary.

    # Output the final graph query only."""

    # validation_prompt = ChatPromptTemplate.from_messages(
    #     [("system", system), ("human", "{query}")]
    # )

    # validation_chain = validation_prompt | llm | StrOutputParser()

    #generate_query = validation_chain.invoke({"query": query})

    #print ("Fulltext_QueryTool, generate_query", generate_query)
    
    return generate_query




@tool
def Vector_QueryTool(my_question: str, limit: int = 20) -> str:
    """Use the vector search to get the disorder from the database. Only suitable for questions that involve the definition of disorder."""
    
    question_embedding = embedding.get_embedding(my_question)
    
    vector_response = my_db_specifics.vector_search_query_template.format(question_embedding=question_embedding, limit=limit)
    
    return vector_response



def execute_query(my_question, confirmed_query):
    execute_result = db.run(confirmed_query)
    #print (execute_result)
    #print (len(execute_result))

    if len(execute_result) == 0:
        return "No results found."

    answer_prompt = PromptTemplate.from_template(
        """Given the Question {question} and the query_result {query_result}, format the results into sentences or a table for the human to understand. 
        Don't add any data or facts outside of the query_result. 
    """
    )

    formulate_human_readable_answer = (
      answer_prompt
      | llm
      | StrOutputParser()
    )

    final_response = formulate_human_readable_answer.invoke({"question": my_question, "query_result": execute_result})

    return final_response