
from langgraph.graph import START
from langgraph.graph import StateGraph

from manifest.states import ManifestInputState
from manifest.states import ManifestState

from manifest.nodes.router import router_node
from manifest.nodes.initializer import initializer_node

from manifest.nodes.document_writer import document_writer_node

from manifest.nodes.service_extractor import service_extractor_node
from manifest.nodes.tech_stack_extractor import tech_stack_extractor_node
from manifest.nodes.task_decomposer import task_decomposer_node
from manifest.nodes.step_decomposer import step_decomposer_node

from manifest.nodes.implementation_planner import implementation_planner_node

from manifest.nodes.database_schema_generator import database_schema_generator_node
from manifest.nodes.api_endpoints_generator import api_endpoints_generator_node
from manifest.nodes.directory_structure_generator import directory_structure_generator_node

from manifest.nodes.implementor import implementor_node

from manifest.nodes.service_selector import service_selector_node
from manifest.nodes.tech_stack_selector import tech_stack_selector_node
from manifest.nodes.task_selector import task_selector_node
from manifest.nodes.step_selector import step_selector_node
from manifest.nodes.database_schema_consultant import database_schema_consultant_node
from manifest.nodes.api_endpoints_consultant import api_endpoints_consultant_node
from manifest.nodes.directory_structure_consultant import directory_structure_consultant_node
from manifest.nodes.coder import coder_node
from manifest.nodes.tester import tester_node
from manifest.nodes.validator import validator_node
from manifest.nodes.status_updater import status_updater_node


def build_graph():
    graph = StateGraph(ManifestState, input_schema=ManifestInputState)

    graph.add_node("router_node", router_node)

    graph.add_node("initializer_node", initializer_node)
    graph.add_edge(START, "initializer_node")
    graph.add_conditional_edges("initializer_node", router_node)

    # graph.add_node("document_writer_node", document_writer_node)
    # graph.add_conditional_edges("document_writer_node", router_node)
    # graph.add_edge("router_node", "document_writer_node")

    # graph.add_node("service_extractor_node", service_extractor_node)
    # graph.add_conditional_edges("service_extractor_node", router_node)
    # graph.add_edge("router_node", "service_extractor_node")

    # graph.add_node("tech_stack_extractor_node", tech_stack_extractor_node)
    # graph.add_conditional_edges("tech_stack_extractor_node", router_node)
    # graph.add_edge("router_node", "tech_stack_extractor_node")

    # graph.add_node("task_decomposer_node", task_decomposer_node)
    # graph.add_conditional_edges("task_decomposer_node", router_node)
    # graph.add_edge("router_node", "task_decomposer_node")

    # graph.add_node("step_decomposer_node", step_decomposer_node)
    # graph.add_conditional_edges("step_decomposer_node", router_node)
    # graph.add_edge("router_node", "step_decomposer_node")

    # graph.add_node("implementation_planner_node", implementation_planner_node)
    # graph.add_conditional_edges("implementation_planner_node", router_node)
    # graph.add_edge("router_node", "implementation_planner_node")

    # graph.add_node("database_schema_generator_node", database_schema_generator_node)
    # graph.add_conditional_edges("database_schema_generator_node", router_node)
    # graph.add_edge("router_node", "database_schema_generator_node")

    # graph.add_node("api_endpoints_generator_node", api_endpoints_generator_node)
    # graph.add_conditional_edges("api_endpoints_generator_node", router_node)
    # graph.add_edge("router_node", "api_endpoints_generator_node")

    # graph.add_node("directory_structure_generator_node", directory_structure_generator_node)
    # graph.add_conditional_edges("directory_structure_generator_node", router_node)
    # graph.add_edge("router_node", "directory_structure_generator_node")

    graph.add_node("implementor_node", implementor_node)
    graph.add_conditional_edges("implementor_node", router_node)
    graph.add_edge("router_node", "implementor_node")

    graph.add_node("service_selector_node", service_selector_node)
    graph.add_conditional_edges("service_selector_node", router_node)
    graph.add_edge("router_node", "service_selector_node")

    graph.add_node("tech_stack_selector_node", tech_stack_selector_node)
    graph.add_conditional_edges("tech_stack_selector_node", router_node)
    graph.add_edge("router_node", "tech_stack_selector_node")

    graph.add_node("task_selector_node", task_selector_node)
    graph.add_conditional_edges("task_selector_node", router_node)
    graph.add_edge("router_node", "task_selector_node")

    graph.add_node("step_selector_node", step_selector_node)
    graph.add_conditional_edges("step_selector_node", router_node)
    graph.add_edge("router_node", "step_selector_node")

    graph.add_node("database_schema_consultant_node", database_schema_consultant_node)
    graph.add_conditional_edges("database_schema_consultant_node", router_node)
    graph.add_edge("router_node", "database_schema_consultant_node")

    graph.add_node("directory_structure_consultant_node", directory_structure_consultant_node)
    graph.add_conditional_edges("directory_structure_consultant_node", router_node)
    graph.add_edge("router_node", "directory_structure_consultant_node")

    graph.add_node("api_endpoints_consultant_node", api_endpoints_consultant_node)
    graph.add_conditional_edges("api_endpoints_consultant_node", router_node)
    graph.add_edge("router_node", "api_endpoints_consultant_node")

    graph.add_node("coder_node", coder_node)
    graph.add_conditional_edges("coder_node", router_node)
    graph.add_edge("router_node", "coder_node")

    graph.add_node("tester_node", tester_node)
    graph.add_conditional_edges("tester_node", router_node)
    graph.add_edge("router_node", "tester_node")

    graph.add_node("validator_node", validator_node)
    graph.add_conditional_edges("validator_node", router_node)
    graph.add_edge("router_node", "validator_node")

    graph.add_node("status_updater_node", status_updater_node)
    graph.add_conditional_edges("status_updater_node", router_node)
    graph.add_edge("router_node", "status_updater_node")

    return graph.compile()