from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import json
from pathlib import Path

app = FastAPI()

# Load word groups and words from JSON files
def load_data():
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    groups_file = data_dir / "groups.json"
    words_file = data_dir / "words.json"
    
    # Create default data if files don't exist
    if not groups_file.exists():
        default_groups = {
            "items": [
                {"id": "hiragana", "name": "Hiragana"},
                {"id": "katakana", "name": "Katakana"}
            ]
        }
        groups_file.write_text(json.dumps(default_groups, indent=2))
    
    if not words_file.exists():
        default_words = {
            "hiragana": [
                {"japanese": "あ", "english": "a"},
                {"japanese": "い", "english": "i"},
                {"japanese": "う", "english": "u"},
                {"japanese": "え", "english": "e"},
                {"japanese": "お", "english": "o"}
            ],
            "katakana": [
                {"japanese": "ア", "english": "a"},
                {"japanese": "イ", "english": "i"},
                {"japanese": "ウ", "english": "u"},
                {"japanese": "エ", "english": "e"},
                {"japanese": "オ", "english": "o"}
            ]
        }
        words_file.write_text(json.dumps(default_words, indent=2))
    
    return (
        json.loads(groups_file.read_text()),
        json.loads(words_file.read_text())
    )

groups_data, words_data = load_data()

@app.get("/api/groups")
async def get_groups():
    return groups_data

@app.get("/api/groups/{group_id}/words")
async def get_words(group_id: str):
    if group_id not in words_data:
        raise HTTPException(status_code=404, detail="Group not found")
    return {"items": words_data[group_id]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
