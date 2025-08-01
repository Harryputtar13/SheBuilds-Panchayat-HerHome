from fastapi import APIRouter, HTTPException, Depends
import asyncpg
import logging
from typing import List, Dict, Any, Optional

from ..database.db import get_db
from ..services.room_allocation_service import room_allocation_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/allocate-rooms/")
async def allocate_rooms(
    strategy: str = "balanced",
    db: asyncpg.Connection = Depends(get_db)
):
    """
    Allocate rooms to all available users
    
    Strategies:
    - compatibility_first: Prioritize user compatibility
    - budget_first: Prioritize budget constraints
    - location_first: Prioritize location preferences
    - balanced: Consider all factors equally
    """
    try:
        # Get all users without room assignments
        users = await db.fetch("""
            SELECT u.id, u.name, u.age, u.gender, u.occupation, u.sleep_schedule,
                   u.cleanliness_level, u.noise_tolerance, u.social_preference,
                   u.hobbies, u.dietary_restrictions, u.pet_preference,
                   u.smoking_preference, u.budget_range, u.location_preference
            FROM users u
            LEFT JOIN room_assignments ra ON u.id = ra.user_id AND ra.status = 'active'
            WHERE ra.id IS NULL
        """)
        
        # Get all available rooms
        rooms = await db.fetch("""
            SELECT id, room_number, floor_number, room_type, capacity, 
                   monthly_rent, amenities, is_occupied
            FROM rooms 
            WHERE is_occupied = FALSE
        """)
        
        if not users:
            return {
                "success": False,
                "message": "No users available for allocation",
                "allocations": []
            }
        
        if not rooms:
            return {
                "success": False,
                "message": "No rooms available for allocation",
                "allocations": []
            }
        
        # Convert to dictionaries
        users_list = [dict(user) for user in users]
        rooms_list = [dict(room) for room in rooms]
        
        # Perform allocation
        result = await room_allocation_service.allocate_rooms(users_list, rooms_list, strategy)
        
        if result["success"]:
            # Store allocations in database
            await _store_allocations(result["allocations"], db)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in room allocation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/allocate-room/{user_id}")
async def allocate_single_user(
    user_id: int,
    strategy: str = "balanced",
    db: asyncpg.Connection = Depends(get_db)
):
    """
    Allocate a room for a specific user
    """
    try:
        # Check if user already has an active room assignment
        existing_assignment = await db.fetchrow("""
            SELECT ra.id, r.room_number
            FROM room_assignments ra
            JOIN rooms r ON ra.room_id = r.id
            WHERE ra.user_id = $1 AND ra.status = 'active'
        """, user_id)
        
        if existing_assignment:
            return {
                "success": False,
                "message": f"User already assigned to room {existing_assignment['room_number']}",
                "existing_assignment": {
                    "room_number": existing_assignment['room_number']
                }
            }
        
        # Get user data
        user = await db.fetchrow("""
            SELECT id, name, age, gender, occupation, sleep_schedule,
                   cleanliness_level, noise_tolerance, social_preference,
                   hobbies, dietary_restrictions, pet_preference,
                   smoking_preference, budget_range, location_preference
            FROM users WHERE id = $1
        """, user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get available rooms
        rooms = await db.fetch("""
            SELECT id, room_number, floor_number, room_type, capacity, 
                   monthly_rent, amenities, is_occupied
            FROM rooms 
            WHERE is_occupied = FALSE
        """)
        
        if not rooms:
            return {
                "success": False,
                "message": "No rooms available for allocation",
                "allocations": []
            }
        
        # Convert to lists
        users_list = [dict(user)]
        rooms_list = [dict(room) for room in rooms]
        
        # Perform allocation
        result = await room_allocation_service.allocate_rooms(users_list, rooms_list, strategy)
        
        if result["success"] and result["allocations"]:
            # Store allocation in database
            await _store_allocations(result["allocations"], db)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error allocating room for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/allocation-status/")
async def get_allocation_status(db: asyncpg.Connection = Depends(get_db)):
    """
    Get current room allocation status
    """
    try:
        # Get total users
        total_users = await db.fetchval("SELECT COUNT(*) FROM users")
        
        # Get users with active room assignments
        assigned_users = await db.fetchval("""
            SELECT COUNT(DISTINCT user_id) 
            FROM room_assignments 
            WHERE status = 'active'
        """)
        
        # Get total rooms
        total_rooms = await db.fetchval("SELECT COUNT(*) FROM rooms")
        
        # Get occupied rooms
        occupied_rooms = await db.fetchval("""
            SELECT COUNT(*) FROM rooms WHERE is_occupied = TRUE
        """)
        
        # Get available rooms
        available_rooms = total_rooms - occupied_rooms
        
        # Get allocation statistics by strategy
        strategy_stats = await db.fetch("""
            SELECT 
                COUNT(*) as count,
                CASE 
                    WHEN ra.id IS NULL THEN 'unassigned'
                    ELSE 'assigned'
                END as status
            FROM users u
            LEFT JOIN room_assignments ra ON u.id = ra.user_id AND ra.status = 'active'
            GROUP BY ra.id IS NULL
        """)
        
        return {
            "total_users": total_users,
            "assigned_users": assigned_users,
            "unassigned_users": total_users - assigned_users,
            "total_rooms": total_rooms,
            "occupied_rooms": occupied_rooms,
            "available_rooms": available_rooms,
            "occupancy_rate": round((occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0, 2),
            "assignment_rate": round((assigned_users / total_users * 100) if total_users > 0 else 0, 2)
        }
        
    except Exception as e:
        logger.error(f"Error getting allocation status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/room-details/{room_id}")
async def get_room_details(room_id: int, db: asyncpg.Connection = Depends(get_db)):
    """
    Get detailed information about a specific room and its occupants
    """
    try:
        # Get room information
        room = await db.fetchrow("""
            SELECT id, room_number, floor_number, room_type, capacity, 
                   monthly_rent, amenities, is_occupied, created_at
            FROM rooms WHERE id = $1
        """, room_id)
        
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        
        # Get room occupants
        occupants = await db.fetch("""
            SELECT u.id, u.name, u.age, u.gender, u.occupation, u.hobbies,
                   ra.assigned_at, ra.status
            FROM room_assignments ra
            JOIN users u ON ra.user_id = u.id
            WHERE ra.room_id = $1 AND ra.status = 'active'
            ORDER BY ra.assigned_at
        """, room_id)
        
        return {
            "room": dict(room),
            "occupants": [dict(occupant) for occupant in occupants],
            "occupancy_count": len(occupants),
            "available_spots": room['capacity'] - len(occupants)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting room details for room {room_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/remove-assignment/{user_id}")
async def remove_room_assignment(user_id: int, db: asyncpg.Connection = Depends(get_db)):
    """
    Remove a user's room assignment
    """
    try:
        # Check if user has an active assignment
        assignment = await db.fetchrow("""
            SELECT ra.id, ra.room_id, r.room_number
            FROM room_assignments ra
            JOIN rooms r ON ra.room_id = r.id
            WHERE ra.user_id = $1 AND ra.status = 'active'
        """, user_id)
        
        if not assignment:
            return {
                "success": False,
                "message": "User has no active room assignment"
            }
        
        # Update assignment status
        await db.execute("""
            UPDATE room_assignments 
            SET status = 'inactive' 
            WHERE id = $1
        """, assignment['id'])
        
        # Check if room is now empty
        remaining_occupants = await db.fetchval("""
            SELECT COUNT(*) 
            FROM room_assignments 
            WHERE room_id = $1 AND status = 'active'
        """, assignment['room_id'])
        
        # Update room occupancy status
        if remaining_occupants == 0:
            await db.execute("""
                UPDATE rooms 
                SET is_occupied = FALSE 
                WHERE id = $1
            """, assignment['room_id'])
        
        return {
            "success": True,
            "message": f"Removed assignment from room {assignment['room_number']}",
            "room_id": assignment['room_id'],
            "room_number": assignment['room_number']
        }
        
    except Exception as e:
        logger.error(f"Error removing assignment for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def _store_allocations(allocations: List[Dict[str, Any]], db: asyncpg.Connection):
    """
    Store room allocations in the database
    """
    try:
        for allocation in allocations:
            if allocation.get('assigned') and allocation.get('room_id'):
                # Insert room assignment
                await db.execute("""
                    INSERT INTO room_assignments (user_id, room_id, status)
                    VALUES ($1, $2, 'active')
                    ON CONFLICT (user_id, room_id) 
                    DO UPDATE SET status = 'active', assigned_at = CURRENT_TIMESTAMP
                """, allocation['user_id'], allocation['room_id'])
                
                # Update room occupancy
                await db.execute("""
                    UPDATE rooms 
                    SET is_occupied = TRUE 
                    WHERE id = $1
                """, allocation['room_id'])
                
                logger.info(f"Assigned user {allocation['user_id']} to room {allocation['room_id']}")
        
    except Exception as e:
        logger.error(f"Error storing allocations: {e}")
        raise 