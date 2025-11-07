from langgraph.graph import StateGraph, END
from orchestrator import router
from agents import research_agent, therapist_agent, reviewer_agent, cazare_agent, taxations_agent
from search_agent import invoke_search_agent
from admittance_agent import admittance_agent
from admittance_bot import get_admission_criteria_text

# define a dictionary object that holds information as the workflow proceeds
# the original user text input
# the agent which the orchestrator chose
# the result/response from the chosen agent
class AgentState(dict):
    user_input: str
    agent_selected: str
    agent_output: str


# ----------------------- define graph nodes -----------------------

# calls the router to decide the agent, prints the chosen agent and saves the decision into a state

def orchestrator_node(state: AgentState):
    user_text = state["user_input"].lower()

    # 1. Define Search Triggers (Explicitly external resource requests)
    search_triggers = ["search for", "look up", "pdf", "document", "website", "latest", "article", "news"]

    # 2. Define Research Triggers (Explicitly conceptual/knowledge requests)
    # These often indicate the need for a conceptual answer or deep dive.
    research_triggers = ["explain", "define", "meaning", "difference between"]

    # Define Admittance agent triggers
    admittance_triggers = ["admittance", "admission", "admitted"]

    cazare_triggers =["accomodation", "cazare", "housing", "camin", "dormitory", "canteen", "cantina", "administrator", "address", "adresa", "colina", "memo"]

    taxations_triggers = ["taxes", "tax", "fees", "fee", "taxa"]

    # 3. Check for Search-Specific Keywords
    if any(keyword in user_text for keyword in search_triggers):
        decision = "search"
    
    # 4. Check for Research-Specific Keywords (Give this agent high priority)
    elif any(keyword in user_text for keyword in research_triggers):
        decision = "research" # <-- Directly invoke the Research Agent

    elif any(keyword in user_text for keyword in admittance_triggers):
        decision = "admittance"
    
    elif any(keyword in user_text for keyword in cazare_triggers):
        decision = "cazare"

    elif any(keyword in user_text for keyword in taxations_triggers):
        decision = "taxations"
    
    # 5. Fallback to LLM Router for everything else (or default to research/core agent)
    else:
        # If the query is complex but doesn't hit a keyword, let the LLM decide, 
        # or just default to your Research Agent for maximum invocation.
        # decision = router.invoke({"user_input": state["user_input"]}) 
        decision = "research" # <-- Assuming "research" is your desired default agent for conceptual questions
        
    print(f"Orchestrator selected: {decision}")
    state["agent_selected"] = decision.strip().lower()
    return state

# -----------------------------------------------------------------------------------------------------------------------
def admittance_agent_wrapper(user_input: str, admittance_agent_chain):
    # 1. Get the raw admission text and metadata
    scrape_result = get_admission_criteria_text(user_input)

    if "error" in scrape_result:
        return scrape_result["error"]

    extracted_text = scrape_result["text"]
    metadata = scrape_result["metadata"]

    # 2. Inject the extracted text into the prompt context for the LLM
    # This structure is necessary because your existing template only accepts {prompt}
    # and expects the criteria document to be part of the prompt.
    final_prompt_for_llm = (
        f"DOCUMENT (Admission Criteria for {metadata['faculty']} - {metadata['program'].capitalize()}):\n\n"
        f"--- START DOCUMENT ---\n{extracted_text}\n--- END DOCUMENT ---\n\n"
        f"USER QUESTION: {user_input}"
    )

    # 3. Invoke the LangChain Agent
    summary = admittance_agent_chain.invoke({
        "prompt": final_prompt_for_llm 
    })

    # Optionally, you can append the source URL to the end of the summary
    summary += f"\n\nSource of information: {metadata['source_url']}"

    return summary
# -----------------------------------------------------------------------------------------------------------------------

# execute the chosen agent

def agent_executor_node(state: AgentState):
    agents = {
        "search": invoke_search_agent,
        "research": research_agent,
        "therapist": therapist_agent,
        "reviewer": reviewer_agent,
        "admittance": admittance_agent,
        "cazare": cazare_agent,
        "taxations": taxations_agent
    }

    agent_key = state["agent_selected"]
    agent = agents.get(agent_key, research_agent)
    user_input = state["user_input"]

    # --- MODIFICATION HERE ---
    if agent_key == "admittance":
        # Call the custom wrapper function, passing the user input
        # and the LangChain pipeline itself.
        result = admittance_agent_wrapper(user_input, admittance_agent)
    elif callable(agent):
        result = agent(user_input)
    else:
        # Existing logic for other LangChain pipelines
        result = agent.invoke({
            "topic": user_input,
            "problem": user_input,
            "output": state.get("agent_output", ""),
            "prompt": user_input,
            "input": user_input
        })

    print(f"{state['agent_selected'].capitalize()} Agent Output:\n{result}\n")
    state["agent_output"] = result
    return state



# -------------- Build LangGraph --------------

# creates a new state graph using AgentState as the data structure that flows between nodes
graph = StateGraph(AgentState)

# adds the two nodes to the graph
graph.add_node("orchestrator", orchestrator_node) # orchestrator node for deciding the agent
graph.add_node("agent_executor", agent_executor_node) # agent executor for running the agent

# the entry point (point of start) should be the orchestrator node
graph.set_entry_point("orchestrator")

# after the orchestrator runs, go to agent executor 
# after agent executor runs, end the workflow
graph.add_edge("orchestrator", "agent_executor")
graph.add_edge("agent_executor", END)

# converts the defined nodes and edges into a ready-to-run workflow object
workflow = graph.compile()


# ----------------------- helper functions for Flask -----------------------

def workflow_invoke(user_input: str) -> dict:
    """
    Runs the workflow and returns the full result dictionary.
    """
    result = workflow.invoke({"user_input": user_input})
    return result


def run_workflow(request_data: dict) -> dict:
    """
    Flask-friendly function that receives JSON (with 'user_input'),
    invokes the workflow, and returns a JSON-ready dict.
    """
    user_input = request_data.get("user_input", "").strip()
    if not user_input:
        return {"error": "Missing 'user_input' field."}

    try:
        result = workflow_invoke(user_input)
        return {"agent_output": result.get("agent_output", "No output produced.")}
    except Exception as e:
        return {"error": str(e)}

# ------------------------------------------- main (for CLI use only) -------------------------------------------

if __name__ == "__main__":
    user_request = input("Enter your request: ")
    result = workflow_invoke(user_request)
    print("\nFinal Output:\n", result["agent_output"])