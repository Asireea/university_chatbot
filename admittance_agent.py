from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


# ========== Admittance Agent ==========

admittance_model = ChatOllama(model="llama3.2")

admittance_prompt = ChatPromptTemplate.from_template("""
You are an AI assistant specializing in university admissions.

Given the following document (scraped directly from the university website) and the user’s question,
summarize the admission criteria and provide a direct answer.

---
{prompt}
---

First, summarize the admission criteria in bullet points.
Then, explicitly answer the user question in 2-3 sentences.

If the document doesn't contain enough information, say what is missing.
""")

admittance_agent = admittance_prompt | admittance_model | StrOutputParser()

