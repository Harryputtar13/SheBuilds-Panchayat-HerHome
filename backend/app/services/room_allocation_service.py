import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)

class RoomAllocationService:
    """
    Service for intelligent room allocation and assignment
    """
    
    def __init__(self):
        self.allocation_strategies = {
            'compatibility_first': self._allocate_by_compatibility,
            'budget_first': self._allocate_by_budget,
            'location_first': self._allocate_by_location,
            'balanced': self._allocate_balanced
        }
    
    async def allocate_rooms(
        self, 
        users: List[Dict[str, Any]], 
        rooms: List[Dict[str, Any]], 
        strategy: str = 'balanced'
    ) -> Dict[str, Any]:
        """
        Allocate rooms to users based on specified strategy
        
        Args:
            users: List of users to allocate
            rooms: List of available rooms
            strategy: Allocation strategy ('compatibility_first', 'budget_first', 'location_first', 'balanced')
            
        Returns:
            Dictionary with allocation results
        """
        try:
            logger.info(f"Starting room allocation with strategy: {strategy}")
            
            if not users:
                return {
                    "success": False,
                    "message": "No users to allocate",
                    "allocations": []
                }
            
            if not rooms:
                return {
                    "success": False,
                    "message": "No rooms available",
                    "allocations": []
                }
            
            # Get allocation function
            allocation_func = self.allocation_strategies.get(strategy)
            if not allocation_func:
                return {
                    "success": False,
                    "message": f"Unknown allocation strategy: {strategy}",
                    "allocations": []
                }
            
            # Perform allocation
            allocations = await allocation_func(users, rooms)
            
            return {
                "success": True,
                "strategy": strategy,
                "allocations": allocations,
                "total_users": len(users),
                "total_rooms": len(rooms),
                "allocated_users": len([a for a in allocations if a['assigned']]),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in room allocation: {e}")
            return {
                "success": False,
                "message": str(e),
                "allocations": []
            }
    
    async def _allocate_by_compatibility(
        self, 
        users: List[Dict[str, Any]], 
        rooms: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Allocate rooms prioritizing user compatibility
        """
        allocations = []
        
        # Group users by compatibility
        user_groups = await self._group_users_by_compatibility(users)
        
        # Sort rooms by capacity (larger rooms first for groups)
        sorted_rooms = sorted(rooms, key=lambda r: r['capacity'], reverse=True)
        
        # Allocate groups to rooms
        room_index = 0
        for group in user_groups:
            if room_index >= len(sorted_rooms):
                break
                
            room = sorted_rooms[room_index]
            
            # Check if room can accommodate the group
            if room['capacity'] >= len(group):
                # Assign all users in group to this room
                for user in group:
                    allocations.append({
                        "user_id": user['id'],
                        "user_name": user['name'],
                        "room_id": room['id'],
                        "room_number": room['room_number'],
                        "assigned": True,
                        "group_size": len(group),
                        "reason": "compatibility_group"
                    })
                
                room_index += 1
            else:
                # Room too small for group, try to split
                for user in group:
                    if room_index < len(sorted_rooms):
                        room = sorted_rooms[room_index]
                        allocations.append({
                            "user_id": user['id'],
                            "user_name": user['name'],
                            "room_id": room['id'],
                            "room_number": room['room_number'],
                            "assigned": True,
                            "group_size": 1,
                            "reason": "compatibility_split"
                        })
                        room_index += 1
                    else:
                        allocations.append({
                            "user_id": user['id'],
                            "user_name": user['name'],
                            "room_id": None,
                            "room_number": None,
                            "assigned": False,
                            "group_size": 1,
                            "reason": "no_rooms_available"
                        })
        
        # Handle remaining users
        for user in users:
            if not any(a['user_id'] == user['id'] for a in allocations):
                if room_index < len(sorted_rooms):
                    room = sorted_rooms[room_index]
                    allocations.append({
                        "user_id": user['id'],
                        "user_name": user['name'],
                        "room_id": room['id'],
                        "room_number": room['room_number'],
                        "assigned": True,
                        "group_size": 1,
                        "reason": "remaining_user"
                    })
                    room_index += 1
                else:
                    allocations.append({
                        "user_id": user['id'],
                        "user_name": user['name'],
                        "room_id": None,
                        "room_number": None,
                        "assigned": False,
                        "group_size": 1,
                        "reason": "no_rooms_available"
                    })
        
        return allocations
    
    async def _allocate_by_budget(
        self, 
        users: List[Dict[str, Any]], 
        rooms: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Allocate rooms prioritizing budget constraints
        """
        allocations = []
        
        # Sort users by budget (ascending) and rooms by price (ascending)
        sorted_users = sorted(users, key=lambda u: self._extract_budget_value(u.get('budget_range', '')))
        sorted_rooms = sorted(rooms, key=lambda r: r.get('monthly_rent', 0))
        
        user_index = 0
        room_index = 0
        
        while user_index < len(sorted_users) and room_index < len(sorted_rooms):
            user = sorted_users[user_index]
            room = sorted_rooms[room_index]
            
            user_budget = self._extract_budget_value(user.get('budget_range', ''))
            room_price = room.get('monthly_rent', 0)
            
            if room_price <= user_budget:
                allocations.append({
                    "user_id": user['id'],
                    "user_name": user['name'],
                    "room_id": room['id'],
                    "room_number": room['room_number'],
                    "assigned": True,
                    "budget_match": True,
                    "user_budget": user_budget,
                    "room_price": room_price,
                    "reason": "budget_match"
                })
                user_index += 1
                room_index += 1
            else:
                # User can't afford this room, try next room
                room_index += 1
        
        # Handle remaining users
        for i in range(user_index, len(sorted_users)):
            user = sorted_users[i]
            allocations.append({
                "user_id": user['id'],
                "user_name": user['name'],
                "room_id": None,
                "room_number": None,
                "assigned": False,
                "reason": "budget_too_low"
            })
        
        return allocations
    
    async def _allocate_by_location(
        self, 
        users: List[Dict[str, Any]], 
        rooms: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Allocate rooms prioritizing location preferences
        """
        allocations = []
        
        # Group users by location preference
        location_groups = {}
        for user in users:
            location = user.get('location_preference', 'any')
            if location not in location_groups:
                location_groups[location] = []
            location_groups[location].append(user)
        
        # Sort rooms by floor (assuming floor indicates location)
        sorted_rooms = sorted(rooms, key=lambda r: r.get('floor_number', 0))
        
        room_index = 0
        
        # Allocate by location preference
        for location, users_in_location in location_groups.items():
            for user in users_in_location:
                if room_index < len(sorted_rooms):
                    room = sorted_rooms[room_index]
                    allocations.append({
                        "user_id": user['id'],
                        "user_name": user['name'],
                        "room_id": room['id'],
                        "room_number": room['room_number'],
                        "assigned": True,
                        "location_preference": location,
                        "room_floor": room.get('floor_number'),
                        "reason": "location_match"
                    })
                    room_index += 1
                else:
                    allocations.append({
                        "user_id": user['id'],
                        "user_name": user['name'],
                        "room_id": None,
                        "room_number": None,
                        "assigned": False,
                        "location_preference": location,
                        "reason": "no_rooms_available"
                    })
        
        return allocations
    
    async def _allocate_balanced(
        self, 
        users: List[Dict[str, Any]], 
        rooms: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Balanced allocation considering multiple factors
        """
        allocations = []
        
        # Calculate scores for each user-room combination
        user_room_scores = []
        
        for user in users:
            for room in rooms:
                score = await self._calculate_user_room_score(user, room)
                user_room_scores.append({
                    "user": user,
                    "room": room,
                    "score": score
                })
        
        # Sort by score (descending)
        user_room_scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Greedy allocation
        assigned_users = set()
        assigned_rooms = set()
        
        for user_room in user_room_scores:
            user = user_room['user']
            room = user_room['room']
            
            if (user['id'] not in assigned_users and 
                room['id'] not in assigned_rooms):
                
                allocations.append({
                    "user_id": user['id'],
                    "user_name": user['name'],
                    "room_id": room['id'],
                    "room_number": room['room_number'],
                    "assigned": True,
                    "score": user_room['score'],
                    "reason": "balanced_allocation"
                })
                
                assigned_users.add(user['id'])
                assigned_rooms.add(room['id'])
        
        # Handle unassigned users
        for user in users:
            if user['id'] not in assigned_users:
                allocations.append({
                    "user_id": user['id'],
                    "user_name": user['name'],
                    "room_id": None,
                    "room_number": None,
                    "assigned": False,
                    "reason": "no_rooms_available"
                })
        
        return allocations
    
    async def _group_users_by_compatibility(self, users: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """
        Group users by compatibility scores
        """
        if len(users) <= 1:
            return [users] if users else []
        
        groups = []
        used_users = set()
        
        for i, user1 in enumerate(users):
            if user1['id'] in used_users:
                continue
                
            group = [user1]
            used_users.add(user1['id'])
            
            for j, user2 in enumerate(users):
                if (j != i and user2['id'] not in used_users and 
                    await self._are_users_compatible(user1, user2)):
                    group.append(user2)
                    used_users.add(user2['id'])
                    
                    # Limit group size to 4 for practical room sharing
                    if len(group) >= 4:
                        break
            
            groups.append(group)
        
        return groups
    
    async def _are_users_compatible(self, user1: Dict[str, Any], user2: Dict[str, Any]) -> bool:
        """
        Check if two users are compatible for room sharing
        """
        compatibility_score = 0.0
        
        # Sleep schedule compatibility
        if user1.get('sleep_schedule') == user2.get('sleep_schedule'):
            compatibility_score += 0.3
        elif user1.get('sleep_schedule') == 'flexible' or user2.get('sleep_schedule') == 'flexible':
            compatibility_score += 0.15
        
        # Cleanliness compatibility
        if user1.get('cleanliness_level') == user2.get('cleanliness_level'):
            compatibility_score += 0.3
        elif abs(self._cleanliness_to_number(user1.get('cleanliness_level')) - 
                self._cleanliness_to_number(user2.get('cleanliness_level'))) <= 1:
            compatibility_score += 0.15
        
        # Noise tolerance compatibility
        if user1.get('noise_tolerance') == user2.get('noise_tolerance'):
            compatibility_score += 0.2
        elif abs(self._noise_to_number(user1.get('noise_tolerance')) - 
                self._noise_to_number(user2.get('noise_tolerance'))) <= 1:
            compatibility_score += 0.1
        
        # Pet preference compatibility
        if user1.get('pet_preference') == user2.get('pet_preference'):
            compatibility_score += 0.2
        
        return compatibility_score >= 0.6  # Threshold for compatibility
    
    async def _calculate_user_room_score(self, user: Dict[str, Any], room: Dict[str, Any]) -> float:
        """
        Calculate compatibility score between user and room
        """
        score = 0.0
        
        # Budget compatibility
        user_budget = self._extract_budget_value(user.get('budget_range', ''))
        room_price = room.get('monthly_rent', 0)
        
        if room_price <= user_budget:
            score += 0.4
        elif room_price <= user_budget * 1.2:  # 20% tolerance
            score += 0.2
        
        # Location preference
        user_location = user.get('location_preference', '').lower()
        room_location = str(room.get('floor_number', '')).lower()
        
        if user_location in room_location or room_location in user_location:
            score += 0.3
        elif user_location == 'any':
            score += 0.15
        
        # Room amenities (basic check)
        if room.get('amenities'):
            score += 0.1
        
        # Room type preference (assuming shared rooms are preferred for social users)
        if user.get('social_preference') in ['social', 'very_social'] and room.get('room_type') == 'shared':
            score += 0.2
        
        return score
    
    def _extract_budget_value(self, budget_range: str) -> float:
        """
        Extract numerical budget value from budget range string
        """
        try:
            # Handle different budget range formats
            budget_range = budget_range.lower().replace('$', '').replace(',', '')
            
            if 'under' in budget_range:
                return 500.0
            elif '500-750' in budget_range or '500-800' in budget_range:
                return 625.0
            elif '750-1000' in budget_range or '800-1000' in budget_range:
                return 875.0
            elif '1000-1500' in budget_range:
                return 1250.0
            elif '1500+' in budget_range or 'over' in budget_range:
                return 2000.0
            else:
                # Try to extract any number
                import re
                numbers = re.findall(r'\d+', budget_range)
                if numbers:
                    return float(numbers[0])
                return 1000.0  # Default
        except:
            return 1000.0  # Default
    
    def _cleanliness_to_number(self, level: str) -> int:
        """Convert cleanliness level to number"""
        mapping = {
            'very_clean': 4,
            'clean': 3,
            'moderate': 2,
            'relaxed': 1,
            'very_relaxed': 0
        }
        return mapping.get(level, 2)
    
    def _noise_to_number(self, level: str) -> int:
        """Convert noise tolerance to number"""
        mapping = {
            'very_quiet': 0,
            'quiet': 1,
            'moderate': 2,
            'tolerant': 3,
            'very_tolerant': 4
        }
        return mapping.get(level, 2)

# Global room allocation service instance
room_allocation_service = RoomAllocationService() 