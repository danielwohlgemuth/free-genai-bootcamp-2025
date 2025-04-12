from database import set_status, retrieve_haiku
from langgraph.graph import StateGraph
from media import generate_image_description, generate_image, generate_translation, generate_audio
from typing import TypedDict


class State(TypedDict):
    user_id: str
    haiku_id: str
    haiku_line_en_1: str
    haiku_line_en_2: str
    haiku_line_en_3: str
    topic: str
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
    haiku = retrieve_haiku(state["user_id"], state["haiku_id"])
    set_status(state["user_id"], state["haiku_id"], "in progress", "")
    new_state = {}
    if haiku.haiku_line_en_1:
        new_state["haiku_line_en_1"] = haiku.haiku_line_en_1
    if haiku.haiku_line_en_2:
        new_state["haiku_line_en_2"] = haiku.haiku_line_en_2
    if haiku.haiku_line_en_3:
        new_state["haiku_line_en_3"] = haiku.haiku_line_en_3
    if haiku.topic:
        new_state["topic"] = haiku.topic
    if haiku.image_description_1:
        new_state["image_description_1"] = haiku.image_description_1
    if haiku.image_description_2:
        new_state["image_description_2"] = haiku.image_description_2
    if haiku.image_description_3:
        new_state["image_description_3"] = haiku.image_description_3
    if haiku.image_link_1:
        new_state["image_link_1"] = haiku.image_link_1
    if haiku.image_link_2:
        new_state["image_link_2"] = haiku.image_link_2
    if haiku.image_link_3:
        new_state["image_link_3"] = haiku.image_link_3
    if haiku.haiku_line_ja_1:
        new_state["haiku_line_ja_1"] = haiku.haiku_line_ja_1
    if haiku.haiku_line_ja_2:
        new_state["haiku_line_ja_2"] = haiku.haiku_line_ja_2
    if haiku.haiku_line_ja_3:
        new_state["haiku_line_ja_3"] = haiku.haiku_line_ja_3
    if haiku.audio_link_1:
        new_state["audio_link_1"] = haiku.audio_link_1
    if haiku.audio_link_2:
        new_state["audio_link_2"] = haiku.audio_link_2
    if haiku.audio_link_3:
        new_state["audio_link_3"] = haiku.audio_link_3
    return new_state

def generate_image_description_1(state: State):
    if state.get("image_description_1"):
        return {}

    description = generate_image_description(state["user_id"], state["haiku_id"], state["topic"], state["haiku_line_en_1"], 1)
    return {
        "image_description_1": description
    }

def generate_image_description_2(state: State):
    if state.get("image_description_2"):
        return {}
    
    description = generate_image_description(state["user_id"], state["haiku_id"], state["topic"], state["haiku_line_en_2"], 2)
    return {
        "image_description_2": description
    }

def generate_image_description_3(state: State):
    if state.get("image_description_3"):
        return {}
    
    description = generate_image_description(state["user_id"], state["haiku_id"], state["topic"], state["haiku_line_en_3"], 3)
    return {
        "image_description_3": description
    }

def generate_image_1(state: State):
    if state.get("image_link_1"):
        return {}
    
    link = generate_image(state["user_id"], state["haiku_id"], state["image_description_1"], 1)
    return {
        "image_link_1": link
    }

def generate_image_2(state: State):
    if state.get("image_link_2"):
        return {}
    
    link = generate_image(state["user_id"], state["haiku_id"], state["image_description_2"], 2)
    return {
        "image_link_2": link
    }

def generate_image_3(state: State):
    if state.get("image_link_3"):
        return {}
    
    link = generate_image(state["user_id"], state["haiku_id"], state["image_description_3"], 3)
    return {
        "image_link_3": link
    }

def generate_translation_1(state: State):
    if state.get("haiku_line_ja_1"):
        return {}
    
    translation = generate_translation(state["user_id"], state["haiku_id"], state["topic"], state["haiku_line_en_1"], 1)
    return {
        "haiku_line_ja_1": translation
    }

def generate_translation_2(state: State):
    if state.get("haiku_line_ja_2"):
        return {}
    
    translation = generate_translation(state["user_id"], state["haiku_id"], state["topic"], state["haiku_line_en_2"], 2)
    return {
        "haiku_line_ja_2": translation
    }

def generate_translation_3(state: State):
    if state.get("haiku_line_ja_3"):
        return {}
    
    translation = generate_translation(state["user_id"], state["haiku_id"], state["topic"], state["haiku_line_en_3"], 3)
    return {
        "haiku_line_ja_3": translation
    }

def generate_audio_1(state: State):
    if state.get("audio_link_1"):
        return {}
    
    link = generate_audio(state["user_id"], state["haiku_id"], state["haiku_line_ja_1"], 1)
    return {
        "audio_link_1": link
    }

def generate_audio_2(state: State):
    if state.get("audio_link_2"):
        return {}
    
    link = generate_audio(state["user_id"], state["haiku_id"], state["haiku_line_ja_2"], 2)
    return {
        "audio_link_2": link
    }

def generate_audio_3(state: State):
    if state.get("audio_link_3"):
        return {}
    
    link = generate_audio(state["user_id"], state["haiku_id"], state["haiku_line_ja_3"], 3)
    return {
        "audio_link_3": link
    }

def check_status(state: State):
    missing_fields = []
    if not state.get('haiku_line_en_1'):
        missing_fields.append('haiku_line_en_1')
    if not state.get('haiku_line_en_2'):
        missing_fields.append('haiku_line_en_2')
    if not state.get('haiku_line_en_3'):
        missing_fields.append('haiku_line_en_3')
    if not state.get('image_description_1'):
        missing_fields.append('image_description_1')
    if not state.get('image_description_2'):
        missing_fields.append('image_description_2')
    if not state.get('image_description_3'):
        missing_fields.append('image_description_3')
    if not state.get('image_link_1'):
        missing_fields.append('image_link_1')
    if not state.get('image_link_2'):
        missing_fields.append('image_link_2')
    if not state.get('image_link_3'):
        missing_fields.append('image_link_3')
    if not state.get('haiku_line_ja_1'):
        missing_fields.append('haiku_line_ja_1')
    if not state.get('haiku_line_ja_2'):
        missing_fields.append('haiku_line_ja_2')
    if not state.get('haiku_line_ja_3'):
        missing_fields.append('haiku_line_ja_3')
    if not state.get('audio_link_1'):
        missing_fields.append('audio_link_1')
    if not state.get('audio_link_2'):
        missing_fields.append('audio_link_2')
    if not state.get('audio_link_3'):
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
    graph.add_node("generate_translation_1", generate_translation_1)
    graph.add_node("generate_translation_2", generate_translation_2)
    graph.add_node("generate_translation_3", generate_translation_3)
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
    graph.add_edge("initialize_haiku", "generate_translation_1")
    graph.add_edge("initialize_haiku", "generate_translation_2")
    graph.add_edge("initialize_haiku", "generate_translation_3")
    graph.add_edge("generate_translation_1", "generate_audio_1")
    graph.add_edge("generate_translation_2", "generate_audio_2")
    graph.add_edge("generate_translation_3", "generate_audio_3")
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


def start_workflow(user_id: str, haiku_id: str):
    workflow.invoke({"user_id": user_id, "haiku_id": haiku_id})

if __name__ == "__main__":
    with open("media.mermaid", "w") as f:
        f.write(workflow.get_graph().draw_mermaid())
    with open("media-mermaid.png", "wb") as f:
        f.write(workflow.get_graph().draw_mermaid_png())
