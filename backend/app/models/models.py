from datetime import datetime
from enum import Enum as PyEnum
from typing import Dict, Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, ForeignKey,
    Integer, JSON, String, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base


class BookingStatus(str, PyEnum):
    '''Статусы бронирования'''
    ACTIVE = 'active'
    COMPLETD = 'completed'
    CANCELED = 'cancelled'


class User(Base):
    '''Модель пользователя'''
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    apartment = Column(String, nullable=False)
    is_verified = Column(Boolean)
    is_activate = Column(Boolean)
    is_admin = Column(Boolean, default=False)

    bookings = relationship('Booking', back_populates='user')
    booking_history = relationship('BookingHistory', back_populates='user')

    def __repr__(self):
        return f'User(id={self.id}, email={self.email}, email={self.apartment})'
    

class ParkingSpot(Base):
    '''Модель парковочного места'''
    number = Column(Integer, unique=True, nullable=False)
    coordinates = Column(JSON, nullable=False) #{x: float, y: float}

    bookings = relationship('Booking', back_populates='spot')
    booking_history = relationship('BookingHistory', back_populates='spot')

    def __repr__(self):
        return f'ParkingSpot(id={self.id}, number={self.number})'
    

class Booling(Base):
    '''Модель для текущего бронирования'''
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.id'), nullable=False)
    spot_id = Column(UUID(as_uuid=True), ForeignKey('parkingspot.id'), nullable=False)
    car_number = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(
        Enum(BookingStatus),
        nullable=False,
        default=BookingStatus.ACTIVE
    )

    user = relationship('User', back_populates='bookings')
    spot = relationship('ParkingSpot', back_populates='bookings')

    #ограничения
    __table_args__ = (
        #Пользователь не может иметь несколько активных броней
        UniqueConstraint(
            'user.id',
            name='unique_active_booking_per_user',
            postger_where=status==BookingStatus.ACTIVE
        ),
        UniqueConstraint(
            'spot_id',
            name='unique_activate_booking_per_spot',
            posgresql_where=status==BookingStatus.ACTIVE
        ),
    )

    def __repr__(self):
        return (
            f"Booking(id={self.id}, user_id={self.user_id}, "
            f"spot_id={self.spot_id}, status={self.status})"
        )


class BookingHistory(Base):
    """Модель истории бронирований"""
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    spot_id = Column(UUID(as_uuid=True), ForeignKey("parkingspot.id"), nullable=False)
    car_number = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(Enum(BookingStatus), nullable=False)

    user = relationship("User", back_populates="booking_history")
    spot = relationship("ParkingSpot", back_populates="booking_history")

    def __repr__(self):
        return (
            f"BookingHistory(id={self.id}, user_id={self.user_id}, "
            f"spot_id={self.spot_id}, status={self.status})"
        )