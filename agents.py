from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
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

# ========== Cazare Agent ==========

cazare_model = ChatOllama(
    model="llama3.2",
    temperature=0,          # fully deterministic, no creativity
    top_p=0,                # disables nucleus sampling
    num_predict=200,        # equivalent to max_new_tokens
    repeat_penalty=1.5      # discourages model from looping or expanding
)

cazare_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are an assistant for student accommodations at Transilvania University of Brașov (UNITBV).

**RULES (MANDATORY):**
1. If the user asks about anything **not listed below**, reply exactly:  
   "I don't have information about that in my dataset. Would you like contact details for the dorm administrator?"
2. Use only the facts below. Do not add, infer, or assume anything.
3. Answer only what exists in the facts; use the fallback phrase for all missing info.
4. Be concise and factual. No creativity or extras.

---

### FACTS

**GENERAL**
- there are only 2 complexes accomodations: Memo (8 dorms + canteen) and Colina (5 dorms + canteen).
- Both have laundry rooms with washers/dryers and video surveillance.

**MEMO COMPLEX**
- Rooms: 3- or 4-bed. Shared bathrooms per floor. Study rooms. Some small kitchens.
- Dorms: 1, 2, 3, 4, 5, 8, 9, 10.
- Contacts:
  - Dorm 1 — 15 Memorandului — Mihaela Chircă — 0751 990 418 — camin1@unitbv.ro
  - Dorm 2 — 16 Memorandului — Mihaela Negruțiu — 0751 990 419 — camin2@unitbv.ro
  - Dorm 3 — 18 Memorandului — Felicia Tinca — 0751 990 420 — camin3@unitbv.ro
  - Dorm 4 — 17 Memorandului — Viola Bordoș — 0759 031 098 — camin4@unitbv.ro
  - Dorm 5 — 26 Memorandului — Luminița Gheorghe — 0751 990 421 — camin5@unitbv.ro
  - Dorm 8 — 32 Memorandului — Nicoleta Potecă — 0751 990 422 — camin8@unitbv.ro
  - Dorm 9 — 34 Memorandului — Cristina Văsui — 0751 990 423 — camin9@unitbv.ro
  - Dorm 10 — 43 Memorandului — Adrian Prepeliță — 0751 990 424 — camin10@unitbv.ro

**COLINA COMPLEX**
- Rooms: 4-bed. Shared bathrooms per two-room module.
- Exception: Dorm 16 has private bathrooms per room.
- Amenities: Colina Arena (sports field), Colina Club (billiards/table tennis), grocery store, terrace.
- Dorms: 11, 12, 14, 15, 16.
- Contacts:
  - Dorm 11 — 1 Universității — Mihai Cojoc — 0751 990 425 — camin11@unitbv.ro
  - Dorm 12 — 1 Universității — Cristina Neamțu — 0751 990 426 — camin12@unitbv.ro
  - Dorm 14 — 1 Universității — Cătălin Lazăr — 0751 990 427 — camin14@unitbv.ro
  - Dorm 15 — 1 Universității — Sorin Enache — 0751 990 428 — camin15@unitbv.ro
  - Dorm 16 — 1 Universității — (Not specified) — 0751 990 429 — camin16@unitbv.ro
    - Note: Only Dorm 16 has private bathrooms.

**Accommodation fees and taxes**
- Fee-paying: 730 RON/month  
- Budgeted: 510 RON/month  
- Budgeted (special categories): 350 RON/month
---
    """),
    ("human", "{input}")
])

cazare_agent = cazare_prompt | cazare_model | StrOutputParser()

# ========== Taxes Agent ==========

taxations_model = ChatOllama(
    model="llama3.2",
    temperature=0,
    top_p=0,
    num_predict=200,
    repeat_penalty=1.5
)

taxations_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are an assistant for tuition and academic fees at Transilvania University of Brașov (UNITBV).

**RULES:**
1. If asked about anything not listed, reply exactly:  
   "I don't have information about that in my dataset. Would you like contact details for the university administration?"
2. Use only the facts below. No assumptions or creativity.
3. Be short and factual.

---

### FACTS

**General rule (most faculties):**
- Bachelor’s degree: 3,850 RON/year  
- Master’s degree: 3,850 RON/year  
- Applies to: Mechanical Engineering, Technological Engineering, Materials Science, Electrical Engineering, Forestry, Furniture Design, Civil Engineering, Food and Tourism, Product Design, Mathematics and Computer Science, Psychology, Physical Education, Letters, Law, Sociology and Communication.

**Faculty of Economic Sciences and Business Administration**
- Bachelor’s: 3,850 RON/year  
- Master’s: 3,850 RON/year  
- Master’s in Business Strategies (English): 4,800 RON/year

**Faculty of Music**
- Bachelor’s – Instruments: 6,000 RON/year  
- Bachelor’s – Singing: 6,000 RON/year  
- Bachelor’s – Music: 3,850 RON/year  
- Master’s – SPIIV: 6,000 RON/year  
- Master’s – TAM: 3,850 RON/year  
- Master’s – MELO: 3,850 RON/year

**Faculty of Medicine**
- Bachelor’s – Medicine: 7,750 RON/year  
- Bachelor’s – General Nursing: 5,100 RON/year  
- Bachelor’s – Balneophysiokinetotherapy: 5,100 RON/year  
- Bachelor’s – Clinical Laboratory: 3,850 RON/year  
- Master’s: 4,400 RON/year

**Psychopedagogical Training**
- Level I+II: 700 RON/year  
- Postgraduate Level I: 2,000 RON/year  
- Postgraduate Level II: 1,300 RON/year

---

    """),
    ("human", "{input}")
])

taxations_agent = taxations_prompt | taxations_model | StrOutputParser()



