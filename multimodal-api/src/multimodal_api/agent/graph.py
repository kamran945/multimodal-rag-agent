from functools import lru_cache

from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.runnables import RunnableConfig

from multimodal_api.agent.state import (
    VideoAgentState,
    VideoAgentInputState,
    VideoAgentOutputState,
    Context,
)
from multimodal_api.agent.nodes.summarizer import summarization_node
from multimodal_api.agent.nodes.router import routing_node
from multimodal_api.agent.nodes.tool_selector import tool_selector_node
from multimodal_api.agent.nodes.tool_executor import tool_executor_node
from multimodal_api.agent.nodes.general_response import general_response_node


class AIAgent:
    def __init__(self):
        self._checkpointer = InMemorySaver()
        self._graph = self._build_and_compile_graph()

    @lru_cache(maxsize=1)
    def _build_and_compile_graph(self):
        builder = StateGraph(
            state_schema=VideoAgentState,
            input_schema=VideoAgentInputState,
            output_schema=VideoAgentOutputState,
        )
        builder.add_node("summarization_node", summarization_node)
        builder.add_node("routing_node", routing_node)
        builder.add_node("general_response_node", general_response_node)
        builder.add_node("tool_selector_node", tool_selector_node)
        builder.add_node("tool_executor_node", tool_executor_node)
        builder.add_edge(START, "summarization_node")
        builder.add_edge("summarization_node", "routing_node")
        builder.add_edge("tool_selector_node", "tool_executor_node")
        builder.add_edge("tool_executor_node", "general_response_node")
        builder.add_edge("general_response_node", END)
        # builder.add_edge("tool_executor_node", END)
        # builder.add_edge("tool_selector_node", END)
        return builder.compile(checkpointer=self._checkpointer)

    async def ainvoke(
        self, input: VideoAgentInputState, context: Context, config: RunnableConfig
    ) -> VideoAgentOutputState:
        return await self._graph.ainvoke(input=input, context=context, config=config)
