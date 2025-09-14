from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.core.security import get_current_user
from app.schemas.user import NodeSeed, UserWithSeed
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/node_structure", response_model=UserWithSeed)
async def get_node_structure(current_user: User = Depends(get_current_user)):
    return {"firebase_uid": current_user.firebase_uid, "seed": current_user.node_structure_seed}

@router.post("/node_structure", response_model=UserWithSeed)
async def set_node_structure(
    payload: NodeSeed, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user),
):
    current_user.node_structure_seed = payload.seed # use model_dump instead
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return {"firebase_uid": current_user.firebase_uid, "seed": current_user.node_structure_seed}

# MIGHT IMPLEMENT SOON

# Profile endpoints
# GET /users/me → return profile info (UserOut).
# PATCH /users/me → update display name, email, etc.

# Admin endpoints
# GET /users/ → list all users (requires is_admin = True).
# DELETE /users/{id} → remove a user (again, admin-only).

# Settings endpoints
# (e.g. language preferences, notification preferences, etc.)