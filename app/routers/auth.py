from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.core.firebase import verify_id_token
from app.core.db import get_db
from app import crud
from app.core.security import get_current_user
from app.schemas.user import UserOut
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["auth"])

class TokenIn(BaseModel):
    id_token: str

@router.post("/firebase")
async def firebase_login(token_in: TokenIn, db: AsyncSession = Depends(get_db)):
    # 1️⃣ Verify Firebase token
    decoded = verify_id_token(token_in.id_token)
    uid = decoded.get("uid")
    if not uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload."
        )

    # 2️⃣ Find or create user
    user = await crud.user.get_by_firebase_uid(db, uid)
    is_new_user = False
    if not user:
        # Do NOT assign a default display_name
        user = await crud.user.create_from_firebase(
            db, uid, decoded.get("email"), decoded.get("name")  # can be None
        )
        is_new_user = True

    # 3️⃣ Decide if profile completion is needed
    # first_login is True if this is a new user OR they have no display_name yet
    first_login = is_new_user or not user.display_name

    return {
        "user": UserOut.model_validate(user),  # serialize with Pydantic
        "first_login": first_login,
    }


@router.get("/me", response_model=UserOut)
async def me(current_user=Depends(get_current_user)):
    return current_user
