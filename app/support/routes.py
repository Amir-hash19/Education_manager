from fastapi import status, HTTPException, Path, Request,Depends, APIRouter, Query
from fastapi.responses import JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy import and_
from sqlalchemy.orm import selectinload
from app.db.database import get_db
from app.auth.jwt_auth import get_authenticated_user
from datetime import datetime, timezone
from typing import Optional, List

from app.users.models import UserModel
from app.auth.jwt_auth import get_authenticated_user
from app.support.models import TicketModel, TicketMessageModel

from app.support.schemas import TicketBabseSchema, TicketResponseSchema


router = APIRouter(prefix="/api/v1")




@router.post("/support", status_code=status.HTTP_201_CREATED)
async def create_ticket(request:Request,ticket: TicketBabseSchema,current_user: UserModel = Depends(get_authenticated_user),db: AsyncSession = Depends(get_db)):
    try:
        ticket_obj = TicketModel(
            title=ticket.title,
            description=ticket.description,
            created_by=current_user.id,
            created_at=datetime.now(timezone.utc)
        )
        db.add(ticket_obj)
        await db.commit()
        await db.refresh(ticket_obj)

        return JSONResponse(
            content={"message":"ticket definded successfully",
                    "ticket_id":ticket_obj.id})
    
    except IntegrityError as ie:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error: " + str(ie.orig)
        )     
        
    



@router.get("/support", status_code=status.HTTP_200_OK, response_model=List[TicketResponseSchema])
async def list_ticket(db: AsyncSession = Depends(get_db),current_user: UserModel = Depends(get_authenticated_user)):
    tickets = (
        select(TicketModel)
        .where(TicketModel.created_by == current_user.id)
        .order_by(TicketModel.created_at.desc())
    )
    result = await db.execute(tickets)
    tickets = result.scalars().all()
    return tickets

    


@router.delete("/support/{ticket_id}", status_code=status.HTTP_200_OK)
async def delete_ticket(ticket_id: int, db: AsyncSession = Depends(get_db),current_user: UserModel = Depends(get_authenticated_user)):
    result = await db.execute(
        select(TicketModel).where(TicketModel.id==ticket_id)
    )
    ticket = result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ticket with ID {ticket_id} not found"
        )
    
    await db.delete(ticket)
    await db.commit()
    return {
        "message":"ticket deleted successfully"
    }



