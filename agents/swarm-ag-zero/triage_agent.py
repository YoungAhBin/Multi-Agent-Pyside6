# 创建分流代理（Triage Agent）
from swarm import Agent
from agents.fabric_agent import fabric_agent
from agents.rail_agent import rail_agent
from agents.installation_agent import installation_agent

def transfer_back_to_triage():
    """Call this function if a user is asking about a topic that is not handled by the current agent."""
    return triage_agent

def transfer_to_fabric():
    return fabric_agent

def transfer_to_rail():
    return rail_agent

def transfer_to_installation():
    return installation_agent

triage_agent = Agent(
    name="分流代理",
    instructions="Determine which agent is best suited to handle the user's request, and transfer the conversation to that agent.",
    functions=[transfer_to_fabric, transfer_to_rail, transfer_to_installation],
)

fabric_agent.functions.append(transfer_back_to_triage)
rail_agent.functions.append(transfer_back_to_triage)
installation_agent.functions.append(transfer_back_to_triage)
