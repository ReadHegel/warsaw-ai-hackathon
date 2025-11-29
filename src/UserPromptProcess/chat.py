import torch
from PIL import Image
from typing import List, Dict, Any, Union
from pathlib import Path
import json

from google import genai
from google.genai import types 
from google.genai.errors import APIError

_MODEL = None

class Model:
    def __init__(self, model_id: str = "gemini-2.5-flash"):
        print(f"--> Inicjalizacja klienta Google GenAI dla modelu {model_id}...")
        try:
            # KLUCZ API: Upewnij się, że zmienna środowiskowa GEMINI_API_KEY jest ustawiona
            self.client = genai.Client()
            self.model_id = model_id
            print("--> Klient Gemini API zainicjalizowany pomyślnie.")
        except Exception as e:
            raise RuntimeError(f"Nie udało się zainicjalizować klienta Gemini: {e}")

    def predict(self, images_list: List[Image.Image], prompt: str) -> str:
        """
        Metoda inferencji. Wysyła prompt i obrazy do Gemini API.
        Zachowuje interfejs predict(images_list, prompt).
        """
        if not self.client:
            raise RuntimeError("Klient Gemini nie został poprawnie zainicjalizowany.")

        # 1. Przygotowanie wejścia (List[Image.Image] + str)
        # Gemini API oczekuje listy obiektów (TextPart, ImagePart)
        
        contents = []
        
        # Dodawanie obrazów
        for img in images_list:
             # Upewniamy się, że obraz ma poprawny format (RGB)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            contents.append(img)
            
        # Dodawanie tekstu promptu
        contents.append(prompt)

        # 2. Wywołanie API
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=contents,
                config=types.GenerateContentConfig(
                    # Ustawienia kreatywności i maksymalnej długości (odpowiednik temperatury i max_new_tokens)
                    temperature=0.2,
                    max_output_tokens=2048, # Wyższa wartość dla bezpieczeństwa
                )
            )

            # print(f"[DEBUG] Gemini API response: {response}")
            # 3. Zwracanie wyniku
            return response.text.strip()
        
        except APIError as e:
            raise RuntimeError(f"Błąd Gemini API: {e}")
        except Exception as e:
            raise RuntimeError(f"Nieoczekiwany błąd podczas predykcji: {e}")

# Inicjalizacja Singletona przy imporcie
if _MODEL is None:
    _MODEL = Model()


# --- Funkcje pomocnicze ---

def _load_image(path_or_obj: Any) -> Image.Image:
    if isinstance(path_or_obj, Image.Image):
        return path_or_obj.convert("RGB")
    return Image.open(str(path_or_obj)).convert("RGB")


def _extract_last_user_message(chat_history: List[Dict[str, Any]]) -> str:
    for msg in reversed(chat_history or []):
        if msg.get("role") == "user":
            return msg.get("content", "")
    return ""


# --- Główne funkcje API ---

def suggest_classes(
    image_path: Any, 
    chat_history: List[Dict[str, Any]], 
    proposed_classes: List[str]
) -> List[str]:
    """
    Analizuje obraz i zwraca listę max 10 klas obiektów (po polsku).
    Uwzględnia klasy zaproponowane (proposed_classes).
    """
    image = _load_image(image_path)
    user_context = _extract_last_user_message(chat_history)
    proposed_str = ", ".join(proposed_classes) if proposed_classes else "brak"

    # Duży preprompt systemowy
    system_instruction = (
        "Jesteś ekspertem wizyjnym na placu budowy. Twoim zadaniem jest stworzenie listy "
        "kategorii obiektów widocznych na zdjęciu, które są istotne dla bezpieczeństwa i logistyki "
        "(np. kask, koparka, rura, pracownik, rusztowanie).\n"
        "ZASADY:\n"
        "1. Przeanalizuj obraz i kontekst rozmowy.\n"
        f"2. Uwzględnij te sugerowane klasy, jeśli faktycznie są na zdjęciu: [{proposed_str}].\n"
        "3. Wypisz MAKSYMALNIE 10 najważniejszych klas.\n"
        "4. Używaj języka polskiego.\n"
        "5. Wynik ma być WYŁĄCZNIE listą oddzieloną przecinkami, bez numeracji i zbędnego tekstu."
    )

    prompt = f"{system_instruction}\nKontekst rozmowy: '{user_context}'\nJakie obiekty widzisz?"

    # Wywołanie modelu
    raw_response = _MODEL.predict([image], prompt)
    print(f"[DEBUG] Raw response for suggest_classes: {raw_response}")
    
    # Proste parsowanie wyniku na listę
    # Usuwamy ewentualne kropki na końcu i dzielimy po przecinkach
    clean_text = raw_response.replace(".", "").replace("\n", ",")
    items = [x.strip().lower() for x in clean_text.split(",") if x.strip()]
    
    # Ograniczenie do 10 unikalnych
    unique_items = list(dict.fromkeys(items))[:10]
    
    return unique_items


def chat_answer(
    chat_history: List[Dict[str, Any]], 
    classes: List[str], 
    current_image_path: Any, 
    answer_json: Any
) -> str:
    """
    Generuje odpowiedź dla użytkownika na podstawie obrazu, historii czatu i metadanych detekcji.
    """
    image = _load_image(current_image_path)
    last_user_question = _extract_last_user_message(chat_history)
    
    # Parsowanie metadanych z detekcji
    try:
        data = answer_json if isinstance(answer_json, dict) else json.loads(answer_json)
    except:
        data = {}

    detections = data.get("detections", [])
    det_summary = ", ".join([f"{d.get('label')} (pewność: {d.get('score', 0):.2f})" for d in detections[:10]])
    if not det_summary:
        det_summary = "Brak wyraźnych detekcji w metadanych."
    
    classes_str = ", ".join(classes)

    # Duży preprompt systemowy
    system_instruction = (
        "Jesteś inteligentnym asystentem BHP i inżynierem budownictwa. "
        "Odpowiadasz na pytania użytkownika na podstawie dostarczonego zdjęcia oraz wyników detekcji obiektów.\n"
        "ZASADY:\n"
        "1. Odpowiadaj krótko, rzeczowo i po polsku.\n"
        "2. Opieraj się na tym co widzisz na zdjęciu ORAZ na dostarczonych danych detekcji.\n"
        "3. Jeśli pytanie dotyczy bezpieczeństwa, zwróć uwagę na brak kasków lub kamizelek.\n"
        "4. Bądź pomocny i profesjonalny."
    )

    data_context = (
        f"Dane z detektora obiektów: [{det_summary}].\n"
        f"Lista wykrytych klas ogólnych: [{classes_str}].\n"
        f"Segmentacja: wykryto {len(data.get('segmentations', []))} masek obiektów."
    )

    prompt = (
        f"{system_instruction}\n\n"
        f"DANE TECHNICZNE:\n{data_context}\n\n"
        f"PYTANIE UŻYTKOWNIKA: '{last_user_question}'\n"
        "ODPOWIEDŹ:"
    )

    # Wywołanie modelu
    response = _MODEL.predict([image], prompt)
    
    return response