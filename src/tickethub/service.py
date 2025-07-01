import logging
from typing import Dict, List, Optional

from .external_client import dummy_client
from .models import Ticket, TicketDetail, TicketPriority, TicketStats, TicketStatus, User

logger = logging.getLogger(__name__)


class TicketService:
    def __init__(self):
        self._users_cache: Optional[Dict[int, User]] = None
    
    async def _get_users_cache(self) -> Dict[int, User]:
        if self._users_cache is None:
            users = await dummy_client.get_users()
            self._users_cache = {user.id: user for user in users}
        return self._users_cache
    
    def _calculate_priority(self, todo_id: int) -> TicketPriority:
        priority_map = {
            0: TicketPriority.LOW,
            1: TicketPriority.MEDIUM,
            2: TicketPriority.HIGH
        }
        return priority_map[todo_id % 3]
    
    def _truncate_description(self, text: str, max_length: int = 100) -> str:
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."
    
    async def _transform_todo_to_ticket(self, todo_data: Dict) -> Ticket:
        users_cache = await self._get_users_cache()
        user_id = todo_data.get("userId", 1)
        assignee_user = users_cache.get(user_id)
        assignee = assignee_user.username if assignee_user else f"user{user_id}"
        
        return Ticket(
            id=todo_data["id"],
            title=todo_data["todo"],
            status=TicketStatus.CLOSED if todo_data["completed"] else TicketStatus.OPEN,
            priority=self._calculate_priority(todo_data["id"]),
            assignee=assignee,
            description=self._truncate_description(todo_data["todo"])
        )
    
    async def _transform_todo_to_ticket_detail(self, todo_data: Dict) -> TicketDetail:
        users_cache = await self._get_users_cache()
        user_id = todo_data.get("userId", 1)
        assignee_user = users_cache.get(user_id)
        assignee = assignee_user.username if assignee_user else f"user{user_id}"
        
        return TicketDetail(
            id=todo_data["id"],
            title=todo_data["todo"],
            status=TicketStatus.CLOSED if todo_data["completed"] else TicketStatus.OPEN,
            priority=self._calculate_priority(todo_data["id"]),
            assignee=assignee,
            description=self._truncate_description(todo_data["todo"]),
            source_data=todo_data
        )
    
    async def get_tickets(
        self, 
        skip: int = 0, 
        limit: int = 20,
        status: Optional[TicketStatus] = None,
        priority: Optional[TicketPriority] = None,
        search: Optional[str] = None
    ) -> List[Ticket]:
        todos = await dummy_client.get_todos()
        
        tickets = []
        for todo in todos:
            ticket = await self._transform_todo_to_ticket(todo)
            
            # Apply filters
            if status and ticket.status != status:
                continue
            if priority and ticket.priority != priority:
                continue
            if search and search.lower() not in ticket.title.lower():
                continue
            
            tickets.append(ticket)
        
        # Apply pagination
        return tickets[skip:skip + limit]
    
    async def get_ticket_by_id(self, ticket_id: int) -> Optional[TicketDetail]:
        todo_data = await dummy_client.get_todo_by_id(ticket_id)
        if not todo_data:
            return None
        
        return await self._transform_todo_to_ticket_detail(todo_data)
    
    async def get_total_tickets_count(
        self,
        status: Optional[TicketStatus] = None,
        priority: Optional[TicketPriority] = None,
        search: Optional[str] = None
    ) -> int:
        todos = await dummy_client.get_todos()
        
        count = 0
        for todo in todos:
            ticket = await self._transform_todo_to_ticket(todo)
            
            # Apply filters
            if status and ticket.status != status:
                continue
            if priority and ticket.priority != priority:
                continue
            if search and search.lower() not in ticket.title.lower():
                continue
            
            count += 1
        
        return count
    
    async def get_ticket_stats(self) -> TicketStats:
        todos = await dummy_client.get_todos()
        
        total_tickets = len(todos)
        open_tickets = 0
        closed_tickets = 0
        low_priority = 0
        medium_priority = 0
        high_priority = 0
        assignee_distribution = {}
        
        for todo in todos:
            ticket = await self._transform_todo_to_ticket(todo)
            
            if ticket.status == TicketStatus.OPEN:
                open_tickets += 1
            else:
                closed_tickets += 1
            
            if ticket.priority == TicketPriority.LOW:
                low_priority += 1
            elif ticket.priority == TicketPriority.MEDIUM:
                medium_priority += 1
            else:
                high_priority += 1
            
            assignee_distribution[ticket.assignee] = assignee_distribution.get(ticket.assignee, 0) + 1
        
        return TicketStats(
            total_tickets=total_tickets,
            open_tickets=open_tickets,
            closed_tickets=closed_tickets,
            low_priority=low_priority,
            medium_priority=medium_priority,
            high_priority=high_priority,
            assignee_distribution=assignee_distribution
        )


# Global service instance
ticket_service = TicketService()