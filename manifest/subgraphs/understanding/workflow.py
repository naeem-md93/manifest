from langgraph.graph import END
from langgraph.graph import START
from langgraph.graph import StateGraph

from manifest.subgraphs.understanding import states
from manifest.subgraphs.understanding import nodes


def build_graph():

    graph = StateGraph(
        states.UnderstandingState,
        input_schema=states.UnderstandingInputState
    )

    graph.add_node("draft_writer_node", nodes.draft_writer_node)
    graph.add_node("functional_domain_extractor_node", nodes.functional_domain_extractor_node)
    graph.add_node("technical_layer_extractor_node", nodes.technical_layer_extractor_node)
    graph.add_node("database_schema_generator_node", nodes.database_schema_generator_node)
    graph.add_node("api_endpoints_generator_node", nodes.api_endpoints_generator_node)
    graph.add_node("directory_structure_generator_node", nodes.directory_structure_generator_node)
    graph.add_node("synthesizer_node", nodes.synthesizer_node)

    graph.add_edge(START, "draft_writer_node")

    graph.add_edge("draft_writer_node", "functional_domain_extractor_node")
    graph.add_edge("draft_writer_node", "technical_layer_extractor_node")
    graph.add_edge("draft_writer_node", "database_schema_generator_node")
    graph.add_edge("draft_writer_node", "api_endpoints_generator_node")
    graph.add_edge("draft_writer_node", "directory_structure_generator_node")

    graph.add_edge("functional_domain_extractor_node", "synthesizer_node")
    graph.add_edge("technical_layer_extractor_node", "synthesizer_node")
    graph.add_edge("database_schema_generator_node", "synthesizer_node")
    graph.add_edge("api_endpoints_generator_node", "synthesizer_node")
    graph.add_edge("directory_structure_generator_node", "synthesizer_node")

    graph.add_edge("synthesizer_node", END)

    return graph.compile()
