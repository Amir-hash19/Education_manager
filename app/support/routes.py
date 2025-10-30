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
from app.support.models import TicketModel, TicketMessageModel, MessageStatusEnum

from app.support.schemas import TicketBabseSchema, TicketResponseSchema, TicketMessageBaseSchema, TicketMessageResponseSchema, TicketMessageUpdateSchema
from app.users.permissions import get_current_admin

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





@router.post("/support/{ticket_id}/message", status_code=status.HTTP_201_CREATED)
async def create_message(data:TicketMessageBaseSchema,current_user: UserModel = Depends(get_authenticated_user),db: AsyncSession = Depends(get_db), ticket_id: int = Path(..., description="ID of the ticket")):
    try:
        result = await db.execute(
            select(TicketModel).where(TicketModel.id==ticket_id)
        )
        ticket_obj = result.scalar_one_or_none()

        if not ticket_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ticket with given ID {ticket_id} not found"
            )
        
        ticket_message = TicketMessageModel(
            ticket_id=ticket_id,
            sender_id=current_user.id,
            user_phone=data.user_phone,
            message_status=data.message_status if data.message_status else MessageStatusEnum.pending,
            message=data.message,
            date_created=datetime.now(timezone.utc)
        )
        db.add(ticket_message)
        await db.commit()
        await db.refresh(ticket_message)

        return JSONResponse(
            content={"message":"ticket message created successfully",
                    "message_id":ticket_message.id}
        )
    
    except IntegrityError as ie:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error: " + str(ie.orig)
        )  
        

                        




@router.put("/support/{ticket_id}/message/{message_id}", status_code=status.HTTP_200_OK)
async def update_message(ticket_id: int, message_id: int, data: TicketMessageBaseSchema, current_user: UserModel = Depends(get_authenticated_user), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(TicketMessageModel).where(TicketMessageModel.id == message_id, TicketMessageModel.ticket_id == ticket_id)
        )
        message_obj = result.scalar_one_or_none()

        if not message_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Message with ID {message_id} not found"
            )

        # Update the message fields
        message_obj.user_phone = data.user_phone
        message_obj.message_status = data.message_status if data.message_status else MessageStatusEnum.pending
        message_obj.message = data.message
        message_obj.date_updated = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(message_obj)

        return JSONResponse(
            content={"message": "Message updated successfully",
                      "message_id": message_obj.id}
        )

    except IntegrityError as ie:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error: " + str(ie.orig)
        )





@router.put("/support/message/{message_id}", status_code=status.HTTP_200_OK)
async def update_message(message_id: int, data: TicketMessageUpdateSchema, current_admin: UserModel = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(TicketMessageModel).where(TicketMessageModel.id == message_id)
        )
        message_obj = result.scalar_one_or_none()

        if not message_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Message with ID {message_id} not found"
            )

        message_obj.message_status = data.message_status
        message_obj.admin_response = data.admin_response

        db.add(message_obj)
        await db.commit()
        await db.refresh(message_obj)

        return JSONResponse(
            content={"message": "Message updated successfully",
                      "message_id": message_obj.id}
        )

    except IntegrityError as ie:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error: " + str(ie.orig)
        )




