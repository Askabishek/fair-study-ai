from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from agents.multimodal_processor import MultimodalAgent
from database.drive_db import DriveDatabase

# 1. State Definition
class StudyState(TypedDict):
    session_id: str
    user_input_path: str
    text_prompt: str
    extracted_notes: str
    quiz_data: list
    next_node: str

def orchestrator_node(state: StudyState):
    """Router agent that determines user goal and fetches user history from Drive."""
    # Logic to route to specialized generator nodes based on text_prompt intent
    if "quiz" in state['text_prompt'].lower():
        return {"next_node": "quiz_designer"}
    return {"next_node": "material_generator"}

def material_generator_node(state: StudyState):
    """Processes multimodal inputs (PDFs, Images, Audio) into clean markdown summaries."""
    import os
    api_key = os.environ.get("GEMINI_API_KEY")
    
    # Try to load .env manually if not in environment
    if not api_key and os.path.exists(".env"):
        try:
            with open(".env") as f:
                for line in f:
                    if line.strip() and not line.startswith("#"):
                        parts = line.strip().split("=", 1)
                        if len(parts) == 2 and parts[0].strip() == "GEMINI_API_KEY":
                            api_key = parts[1].strip()
        except Exception:
            pass
            
    if not api_key:
        try:
            import streamlit as st
            api_key = st.session_state.get("gemini_api_key", None)
        except Exception:
            pass

    processor = MultimodalAgent(api_key=api_key or "YOUR_GEMINI_API_KEY")
    prompt = "Extract key educational themes and provide structured clear study notes."
    
    notes = processor.process_study_input(state['user_input_path'], prompt)
    return {"extracted_notes": notes, "next_node": "save_to_drive"}

def quiz_designer_node(state: StudyState):
    """Generates structured multiple-choice quiz questions from the study materials."""
    import os
    api_key = os.environ.get("GEMINI_API_KEY")
    
    # Try to load .env manually if not in environment
    if not api_key and os.path.exists(".env"):
        try:
            with open(".env") as f:
                for line in f:
                    if line.strip() and not line.startswith("#"):
                        parts = line.strip().split("=", 1)
                        if len(parts) == 2 and parts[0].strip() == "GEMINI_API_KEY":
                            api_key = parts[1].strip()
        except Exception:
            pass
            
    if not api_key:
        try:
            import streamlit as st
            api_key = st.session_state.get("gemini_api_key", None)
        except Exception:
            pass

    processor = MultimodalAgent(api_key=api_key or "YOUR_GEMINI_API_KEY")
    
    import json
    try:
        json_prompt = (
            "Generate a multiple-choice quiz based on the study material. "
            "Return ONLY a JSON array of 3 questions. Each question must be an object with: "
            "'question': 'string', 'options': ['string', 'string', 'string', 'string'], 'answer': 'string' (e.g. 'A'). "
            "Do not include markdown blocks like ```json or any other text, just the raw JSON array."
        )
        response_text = processor.process_study_input(state['user_input_path'], json_prompt)
        # Clean response if markdown blocks are included
        cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
        quiz_list = json.loads(cleaned_text)
    except Exception as e:
        # Fallback quiz
        quiz_list = [
            {
                "question": "What is the primary topic of the uploaded study material?",
                "options": ["Computer Science", "Artificial Intelligence", "General Study", "Unknown"],
                "answer": "C"
            }
        ]
    return {"quiz_data": quiz_list, "next_node": "save_to_drive"}

def save_to_drive_node(state: StudyState):
    """Saves session snapshot directly back into user's personal Google Drive file with local fallback."""
    creds = None
    try:
        import streamlit as st
        creds = st.session_state.get("google_creds", None)
    except Exception:
        pass
        
    # Serialize state and drop non-serializable elements
    import json
    import os
    serializable_state = {k: v for k, v in state.items() if k not in ['voice_parts']}
    
    if creds is None:
        os.makedirs("sandbox_data", exist_ok=True)
        with open(f"sandbox_data/{state['session_id']}.json", "w") as f:
            json.dump(serializable_state, f, indent=4)
        return {"next_node": END}
        
    try:
        db = DriveDatabase(credentials=creds) 
        db.save_state(state['session_id'], dict(state))
    except Exception as e:
        # Fallback to local sandbox if Google Drive fails
        os.makedirs("sandbox_data", exist_ok=True)
        with open(f"sandbox_data/{state['session_id']}.json", "w") as f:
            json.dump(serializable_state, f, indent=4)
            
    return {"next_node": END}

# 2. Graph Construction
workflow = StateGraph(StudyState)

workflow.add_node("orchestrator", orchestrator_node)
workflow.add_node("material_generator", material_generator_node)
workflow.add_node("quiz_designer", quiz_designer_node)
workflow.add_node("save_to_drive", save_to_drive_node)

workflow.set_entry_point("orchestrator")

# Rules guiding progression path
workflow.add_conditional_edges(
    "orchestrator",
    lambda state: state["next_node"],
    {
        "material_generator": "material_generator",
        "quiz_designer": "quiz_designer",
        "save_to_drive": "save_to_drive"
    }
)
workflow.add_edge("material_generator", "save_to_drive")
workflow.add_edge("quiz_designer", "save_to_drive")

app = workflow.compile()

