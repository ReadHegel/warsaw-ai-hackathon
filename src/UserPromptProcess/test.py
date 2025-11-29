import sys
from pathlib import Path

# Dodajemy bieżący katalog do ścieżki, aby zaimportować chat.py
sys.path.append(str(Path(__file__).parent))

import chat

# Ścieżka do obrazka testowego (zmień na istniejący plik .jpg/.png)
IMG_PATH = "src/Images/ortho.png" 

def test_suggest_classes():
    print("\n=== TEST: suggest_classes ===")
    
    # Symulacja pustego pliku, jeśli nie istnieje, aby test się nie wywalił od razu
    if not Path(IMG_PATH).exists():
        print(f"BŁĄD: Brak pliku {IMG_PATH}. Utwórz go lub zmień ścieżkę w kodzie.")
        return

    history = [{"role": "user", "content": "Co widzisz na tym placu budowy?"}]
    proposed = ["hełm", "koparka"]
    
    print(f"Input proposed: {proposed}")
    
    try:
        # Wywołanie funkcji
        result = chat.suggest_classes(IMG_PATH, history, proposed)
        
        print(f"\n[RAW RESULT LIST]: {result}")
        print(f"Liczba klas: {len(result)}")
        assert isinstance(result, list)
        assert len(result) <= 10
    except Exception as e:
        print(f"BŁĄD PODCZAS TESTU: {e}")

def test_chat_answer():
    print("\n=== TEST: chat_answer ===")
    
    if not Path(IMG_PATH).exists():
        return

    history = [{"role": "user", "content": "Czy pracownicy mają kaski?"}]
    classes = ["kask", "osoba", "drabina"]
    
    # Symulacja outputu z detektora
    mock_answer_json = {
        "detections": [
            {"label": "person", "score": 0.95, "box": [10, 10, 100, 200]},
            {"label": "helmet", "score": 0.88, "box": [15, 15, 50, 50]}
        ],
        "segmentations": [{}, {}] # 2 maski
    }
    
    try:
        # Wywołanie funkcji
        raw_response = chat._MODEL.predict([chat._load_image(IMG_PATH)], "Opisz krótko co jest na zdjęciu (test RAW).")
        print(f"\n[PODGLĄD SUROWEJ ODPOWIEDZI MODELU NA PROSTY PROMPT]:\n{raw_response}\n")

        print("-" * 20)
        
        # Wywołanie właściwej funkcji chat_answer
        final_answer = chat.chat_answer(history, classes, IMG_PATH, mock_answer_json)
        
        print(f"\n[FINALNA ODPOWIEDŹ CHATU]:\n{final_answer}")
        assert isinstance(final_answer, str)
        assert len(final_answer) > 0
    except Exception as e:
        print(f"BŁĄD PODCZAS TESTU: {e}")

def main():
    print("Rozpoczynam testy...")
    test_suggest_classes()
    test_chat_answer()
    print("\nTesty zakończone.")

if __name__ == "__main__":
    main()