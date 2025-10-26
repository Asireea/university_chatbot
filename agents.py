from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ========== Research Agent ==========
# creates an instance of Mistral model to handle the research tasks
research_model = ChatOllama(model="qwen")  # this should be a general reasoning model

# text instructions the LLM receives
research_prompt = ChatPromptTemplate.from_template("""
You are a research assistant. Find and summarize key information about this topic:
{topic}
""")

# combines the pieces into a LangChain pipeline using the pipe ('|')
# so that the output of one feeds into the input of the next
# research_prompt -> takes in a dictionary like {"topic": "[user's query]"} and produces a structured prompt (a chat ready for the model)
# research_model -> receives the prompt and generates a model response (text output)
# StrOutputParser() -> takes the model's response and parses it to plain text string

research_agent = research_prompt | research_model | StrOutputParser()


# ========== Therapist Agent ==========
therapist_model = ChatOllama(model="qwen")

therapist_prompt = ChatPromptTemplate.from_template("""
You are a university school counselor. You will counsel the student about the following problem:
{problem}

Your objectives are to listen carefully and show empathy and understanding, provide thoughtful, supportive, 
and evidence-based guidance related to the issue, help the student reflect on their goals, strengths, 
and interests before making decisions and suggest realistic next steps or resources (academic, personal, or career).
""")

therapist_agent = therapist_prompt | therapist_model | StrOutputParser()


# ========== Reviewer Agent ==========
reviewer_model = ChatOllama(model="llama3") # idk, maybe general reasoning again??

reviewer_prompt = ChatPromptTemplate.from_template("""
You are a paper reviewer. Read the following input and provide constructive feedback:
{output}
""")

reviewer_agent = reviewer_prompt | reviewer_model | StrOutputParser()



