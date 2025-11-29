from typing import List, Dict, Any

def generate_classes_with_llm(chat_history: List[Dict[str, Any]],
                               proposed_classes: List[str], 
                               current_image_path: Any) -> List[str]:
    pass


def generate_chat_answer(chat_history: List[Dict[str, Any]], classes: List[str], current_image_path: Any,
                         anwser: json ) -> str:
    """Simplistic chat summarizer that references requested classes.
    Replace with your LLM or rule-based system.
    """
    last_user = ""
    for msg in reversed(chat_history or []):
        if msg.get("role") == "user":
            last_user = msg.get("content", "")
            break
    return f"Zamierzam wykonać segmentację dla klas: {', '.join(classes)}. Ostatnia wiadomość: {last_user}"
