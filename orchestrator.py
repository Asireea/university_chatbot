from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# TODO: if the user gave a general task the the orchestrator is in trouble choosing one agent, ask the user for more input (details)

# simple LLM router
router_model = ChatOllama(model="mistral") # employ a general reasoning model here (maybe it has better results :)) )

router_prompt = ChatPromptTemplate.from_template("""
You are the Orchestrator. Your job is to decide which agent should handle the user's request.
Options:
- "research" for finding or summarizing information
- "therapist" — for guiding students through academic, career, or personal study-related decisions and challenges
- "reviewer" for checking and critiquing work

User request: {user_input}

Return only one word: research, therapist, or reviewer.
""")

router = router_prompt | router_model | StrOutputParser()
