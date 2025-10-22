from langgraph.graph import StateGraph, END
from orchestrator import router
from agents import research_agent, therapist_agent, reviewer_agent

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
    # calls the router and passes the user input to it
    decision = router.invoke({"user_input": state["user_input"]})
    # print the chosen agent -- used for debug purposes
    print(f"Orchestrator selected: {decision}")
    # cleans and stores the orchestrator’s decision (which agent called) in the workflow state
    state["agent_selected"] = decision.strip().lower()
    # return the updated state for the next node
    return state


# execute the chosen agent

def agent_executor_node(state: AgentState):
    # create a dictionary of all available agents
    agents = {
        "research": research_agent,
        "therapist": therapist_agent,
        "reviewer": reviewer_agent,
        }
    # retrieves the agent object based on the orchestrator’s decision
    # if no valid key is found, the default is research_agent 
    # TODO: idk what could the default be? maybe smth else?
    agent = agents.get(state["agent_selected"], research_agent)
    # invoke the chosen agent
    # the input dictionary consists of:
        # topic - the original user input - the agent treats it as subject or context
        # problem - also the original user input - a task to solve
        # output - any previous agent output already stored in the state
    # TODO: get rid of redundancy (see what agents use - either topic or problem - and clean it up to feed it to the agent)
    result = agent.invoke({
        "topic": state["user_input"],
        "problem": state["user_input"],
        "output": state.get("agent_output", "")
    })

    # prints the output and stores it in the state dictionary.
    print(f"{state['agent_selected'].capitalize()} Agent Output:\n{result}\n")
    state["agent_output"] = result

    # return updated state
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