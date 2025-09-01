from langchain.agents import initialize_agent, Tool, AgentType
from tools_agentic import registry as tools_registry
from llm_router import LLMRouter

# Build tools from registry
_tools = tools_registry()
TOOLS = [
    # Minimal set focused on saving JSON and exporting when needed
    Tool(name=name, func=cfg["func"], description=cfg["desc"]) for name, cfg in _tools.items()
]

router = LLMRouter()
llm = router.get_chat_model()

# Prefer agent only when provider supports instruction-following chat well (OpenAI),
# but we also expose a simple agent for HF to allow tool calls when text suggests.
agent = initialize_agent(
    TOOLS,
    llm,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)


def run_agent_task(instruction: str) -> str:
    """Generic agent runner with tools available."""
    return agent.run(instruction)


def run_agent(domain: str) -> str:
    """Backwards-compat: generate a text survey (plain)."""
    instruction = (
        f"Design a survey for {domain} with a clear title and 6-8 questions (mix open-ended and choice). "
        f"Return concise plain text."
    )
    return run_agent_task(instruction)


if __name__ == "__main__":
    print(run_agent("Agriculture"))