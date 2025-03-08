from langchain_ollama import OllamaLLM
from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from database import set_status, retrieve_haiku
from media import generate_image_description, generate_image, generate_audio_translation, generate_audio


class State(TypedDict):
    haiku_id: str
    haiku_line_1_en: str
    haiku_line_2_en: str
    haiku_line_3_en: str
    haiku_line_1_ja: str
    haiku_line_2_ja: str
    haiku_line_3_ja: str
    image_description_1: str
    image_description_2: str
    image_description_3: str
    audio_translation_1: str
    audio_translation_2: str
    audio_translation_3: str


def initialize_haiku(state: State):
    haiku = retrieve_haiku(state["haiku_id"])
    state["haiku_line_1_en"] = haiku["haiku_line_en_1"]
    state["haiku_line_2_en"] = haiku["haiku_line_en_2"]
    state["haiku_line_3_en"] = haiku["haiku_line_en_3"]
    state["haiku_line_1_ja"] = haiku["haiku_line_ja_1"]
    state["haiku_line_2_ja"] = haiku["haiku_line_ja_2"]
    state["haiku_line_3_ja"] = haiku["haiku_line_ja_3"]
    set_status(state["haiku_id"], "in_progress", "")
    return state

def generate_image_description_1(state: State):
    state["image_description_1"] = generate_image_description(state["haiku_id"], state["haiku_line_1_en"], 1)
    return state

def generate_image_description_2(state: State):
    state["image_description_2"] = generate_image_description(state["haiku_id"], state["haiku_line_2_en"], 2)
    return state

def generate_image_description_3(state: State):
    state["image_description_3"] = generate_image_description(state["haiku_id"], state["haiku_line_3_en"], 3)
    return state

def generate_image_1(state: State):
    state["image_link_1"] = generate_image(state["haiku_id"], state["image_description_1"], 1)
    return state

def generate_image_2(state: State):
    state["image_link_2"] = generate_image(state["haiku_id"], state["image_description_2"], 2)
    return state

def generate_image_3(state: State):
    state["image_link_3"] = generate_image(state["haiku_id"], state["image_description_3"], 3)
    return state

def generate_audio_translation_1(state: State):
    state["audio_translation_1"] = generate_audio_translation(state["haiku_id"], state["haiku_line_1_ja"], 1)
    return state

def generate_audio_translation_2(state: State):
    state["audio_translation_2"] = generate_audio_translation(state["haiku_id"], state["haiku_line_2_ja"], 2)
    return state

def generate_audio_translation_3(state: State):
    state["audio_translation_3"] = generate_audio_translation(state["haiku_id"], state["haiku_line_3_ja"], 3)
    return state

def generate_audio_1(state: State):
    state["audio_link_1"] = generate_audio(state["haiku_id"], state["audio_translation_1"], 1)
    return state

def generate_audio_2(state: State):
    state["audio_link_2"] = generate_audio(state["haiku_id"], state["audio_translation_2"], 2)
    return state

def generate_audio_3(state: State):
    state["audio_link_3"] = generate_audio(state["haiku_id"], state["audio_translation_3"], 3)
    return state

def check_state_and_set_error(state: State):
    required_fields = [
        'haiku_line_1_en',
        'haiku_line_2_en',
        'haiku_line_3_en',
        'haiku_line_1_ja',
        'haiku_line_2_ja',
        'haiku_line_3_ja',
        'image_description_1',
        'image_description_2',
        'image_description_3',
        'image_link_1',
        'image_link_2',
        'image_link_3',
        'audio_translation_1',
        'audio_translation_2',
        'audio_translation_3',
        'audio_link_1',
        'audio_link_2',
        'audio_link_3',
    ]

    status = 'completed'
    error_message = ''
    missing_fields = [field for field in required_fields if not getattr(state, field)]
    if missing_fields:
        status = 'failed'
        error_message = f'Missing fields: {', '.join(missing_fields)}'
    set_status(state['haiku_id'], status, error_message)
    return state

def define_workflow(generate_mermaid: bool = False):
    graph = StateGraph(State)

    graph.add_node("initialize_haiku", initialize_haiku)
    graph.add_node("generate_image_description_1", generate_image_description_1)
    graph.add_node("generate_image_description_2", generate_image_description_2)
    graph.add_node("generate_image_description_3", generate_image_description_3)
    graph.add_node("generate_image_1", generate_image_1)
    graph.add_node("generate_image_2", generate_image_2)
    graph.add_node("generate_image_3", generate_image_3)
    graph.add_node("generate_audio_translation_1", generate_audio_translation_1)
    graph.add_node("generate_audio_translation_2", generate_audio_translation_2)
    graph.add_node("generate_audio_translation_3", generate_audio_translation_3)
    graph.add_node("generate_audio_1", generate_audio_1)
    graph.add_node("generate_audio_2", generate_audio_2)
    graph.add_node("generate_audio_3", generate_audio_3)
    graph.add_node("check_state_and_set_error", check_state_and_set_error)
    
    graph.add_edge("initialize_haiku", "generate_image_description_1")
    graph.add_edge("generate_image_description_1", "generate_image_description_2")
    graph.add_edge("generate_image_description_2", "generate_image_description_3")
    graph.add_edge("generate_image_description_1", "generate_image_1")
    graph.add_edge("generate_image_description_2", "generate_image_2")
    graph.add_edge("generate_image_description_3", "generate_image_3")
    graph.add_edge("initialize_haiku", "generate_audio_translation_1")
    graph.add_edge("initialize_haiku", "generate_audio_translation_2")
    graph.add_edge("initialize_haiku", "generate_audio_translation_3")
    graph.add_edge("generate_audio_translation_1", "generate_audio_1")
    graph.add_edge("generate_audio_translation_2", "generate_audio_2")
    graph.add_edge("generate_audio_translation_3", "generate_audio_3")
    graph.add_edge("generate_image_1", "check_state_and_set_error")
    graph.add_edge("generate_image_2", "check_state_and_set_error")
    graph.add_edge("generate_image_3", "check_state_and_set_error")
    graph.add_edge("generate_audio_1", "check_state_and_set_error")
    graph.add_edge("generate_audio_2", "check_state_and_set_error")
    graph.add_edge("generate_audio_3", "check_state_and_set_error")

    graph.set_entry_point("initialize_haiku")
    graph.set_finish_point("check_state_and_set_error")

    workflow = graph.compile()

    if generate_mermaid:
        with open("media.mermaid", "w") as f:
            f.write(workflow.get_graph().draw_mermaid())
        with open("media-mermaid.png", "wb") as f:
            f.write(workflow.get_graph().draw_mermaid_png())

    return workflow

if __name__ == "__main__":
    define_workflow(True)