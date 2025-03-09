from langgraph.graph import StateGraph
from typing import TypedDict
from database import set_status, retrieve_haiku
from media import generate_image_description, generate_image, generate_audio_translation, generate_audio


class State(TypedDict):
    haiku_id: str
    haiku_line_en_1: str
    haiku_line_en_2: str
    haiku_line_en_3: str
    image_description_1: str
    image_description_2: str
    image_description_3: str
    image_link_1: str
    image_link_2: str
    image_link_3: str
    haiku_line_ja_1: str
    haiku_line_ja_2: str
    haiku_line_ja_3: str
    audio_link_1: str
    audio_link_2: str
    audio_link_3: str


def initialize_haiku(state: State):
    haiku = retrieve_haiku(state["haiku_id"])
    set_status(state["haiku_id"], "in_progress", "")
    return {
        "haiku_line_en_1": haiku["haiku_line_en_1"],
        "haiku_line_en_2": haiku["haiku_line_en_2"],
        "haiku_line_en_3": haiku["haiku_line_en_3"],
    }

def generate_image_description_1(state: State):
    description = generate_image_description(state["haiku_id"], state["haiku_line_en_1"], 1)
    return {
        "image_description_1": description
    }

def generate_image_description_2(state: State):
    description = generate_image_description(state["haiku_id"], state["haiku_line_en_2"], 2)
    return {
        "image_description_2": description
    }

def generate_image_description_3(state: State):
    description = generate_image_description(state["haiku_id"], state["haiku_line_en_3"], 3)
    return {
        "image_description_3": description
    }

def generate_image_1(state: State):
    link = generate_image(state["haiku_id"], state["image_description_1"], 1)
    return {
        "image_link_1": link
    }

def generate_image_2(state: State):
    link = generate_image(state["haiku_id"], state["image_description_2"], 2)
    return {
        "image_link_2": link
    }

def generate_image_3(state: State):
    link = generate_image(state["haiku_id"], state["image_description_3"], 3)
    return {
        "image_link_3": link
    }

def generate_audio_translation_1(state: State):
    translation = generate_audio_translation(state["haiku_id"], state["haiku_line_en_1"], 1)
    return {
        "haiku_line_ja_1": translation
    }

def generate_audio_translation_2(state: State):
    translation = generate_audio_translation(state["haiku_id"], state["haiku_line_en_2"], 2)
    return {
        "haiku_line_ja_2": translation
    }

def generate_audio_translation_3(state: State):
    translation = generate_audio_translation(state["haiku_id"], state["haiku_line_en_3"], 3)
    return {
        "haiku_line_ja_3": translation
    }

def generate_audio_1(state: State):
    link = generate_audio(state["haiku_id"], state["haiku_line_ja_1"], 1)
    return {
        "audio_link_1": link
    }

def generate_audio_2(state: State):
    link = generate_audio(state["haiku_id"], state["haiku_line_ja_2"], 2)
    return {
        "audio_link_2": link
    }

def generate_audio_3(state: State):
    link = generate_audio(state["haiku_id"], state["haiku_line_ja_3"], 3)
    return {
        "audio_link_3": link
    }

def check_status(state: State):
    missing_fields = []
    if not state['haiku_line_en_1']:
        missing_fields.append('haiku_line_en_1')
    if not state['haiku_line_en_2']:
        missing_fields.append('haiku_line_en_2')
    if not state['haiku_line_en_3']:
        missing_fields.append('haiku_line_en_3')
    if not state['image_description_1']:
        missing_fields.append('image_description_1')
    if not state['image_description_2']:
        missing_fields.append('image_description_2')
    if not state['image_description_3']:
        missing_fields.append('image_description_3')
    if not state['image_link_1']:
        missing_fields.append('image_link_1')
    if not state['image_link_2']:
        missing_fields.append('image_link_2')
    if not state['image_link_3']:
        missing_fields.append('image_link_3')
    if not state['haiku_line_ja_1']:
        missing_fields.append('haiku_line_ja_1')
    if not state['haiku_line_ja_2']:
        missing_fields.append('haiku_line_ja_2')
    if not state['haiku_line_ja_3']:
        missing_fields.append('haiku_line_ja_3')
    if not state['audio_link_1']:
        missing_fields.append('audio_link_1')
    if not state['audio_link_2']:
        missing_fields.append('audio_link_2')
    if not state['audio_link_3']:
        missing_fields.append('audio_link_3')

    status = 'completed'
    error_message = ''
    if missing_fields:
        status = 'failed'
        error_message = f'Missing fields: {', '.join(missing_fields)}'
    set_status(state['haiku_id'], status, error_message)
    return state


def create_workflow():
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
    graph.add_node("check_status", check_status)
    
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
    graph.add_edge("generate_image_1", "check_status")
    graph.add_edge("generate_image_2", "check_status")
    graph.add_edge("generate_image_3", "check_status")
    graph.add_edge("generate_audio_1", "check_status")
    graph.add_edge("generate_audio_2", "check_status")
    graph.add_edge("generate_audio_3", "check_status")

    graph.set_entry_point("initialize_haiku")
    graph.set_finish_point("check_status")

    workflow = graph.compile()

    return workflow


workflow = create_workflow()


def start_workflow(haiku_id: str):
    workflow.invoke({"haiku_id": haiku_id})

if __name__ == "__main__":
    with open("media.mermaid", "w") as f:
        f.write(workflow.get_graph().draw_mermaid())
    with open("media-mermaid.png", "wb") as f:
        f.write(workflow.get_graph().draw_mermaid_png())
