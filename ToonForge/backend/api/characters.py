from fastapi import APIRouter, HTTPException
from models.schemas import Character

router = APIRouter()

_characters_db: dict[str, Character] = {}


@router.get("/", response_model=list[Character])
async def list_characters():
    return list(_characters_db.values())


@router.get("/{character_id}", response_model=Character)
async def get_character(character_id: str):
    char = _characters_db.get(character_id)
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")
    return char


@router.put("/{character_id}", response_model=Character)
async def update_character(character_id: str, character: Character):
    _characters_db[character_id] = character
    return character
