"""
Session Manager - Conversation Memory & Multi-turn Dialogue Support

This module manages conversation sessions and message history for the eligibility agent.

=== PURPOSE ===

Without session management:
- Each query is independent (agent has no memory)
- User must repeat context every time
- No conversation flow

With session management:
- Agent remembers previous messages
- Natural multi-turn conversations
- Context persists across page reloads

=== ARCHITECTURE ===

SessionManager handles:
1. Creating new sessions
2. Retrieving session history
3. Adding messages to sessions
4. Converting DB messages to LangChain format
5. Session lifecycle (expiration, cleanup)

=== DATABASE ===

Uses PostgreSQL with:
- sessions table: conversation metadata
- messages table: full message history

Created: Day 6 - Conversation Memory Implementation
"""

import os
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from dotenv import load_dotenv

# LangChain message types for conversation history
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
    ToolMessage
)

load_dotenv()


class SessionManager:
    """
    Manages conversation sessions and message history.

    === USAGE EXAMPLE ===

    ```python
    # Initialize
    manager = SessionManager()

    # Create new session
    session_id, session_key = manager.create_session(
        user_identifier="user@example.com"
    )

    # Add user message
    manager.add_message(
        session_id=session_id,
        role="user",
        content="Can I get life insurance?"
    )

    # Get conversation history (for agent)
    history = manager.get_conversation_history(session_id)

    # Add agent response
    manager.add_message(
        session_id=session_id,
        role="assistant",
        content="Let me check your eligibility..."
    )
    ```

    === WHY PostgreSQL? ===

    PostgreSQL is perfect for this because:
    - JSONB support (flexible metadata storage)
    - Transaction support (data consistency)
    - UUID support (secure session IDs)
    - Full-text search (future: search conversations)
    - Mature, production-ready
    """

    def __init__(self, db_url: Optional[str] = None):
        """
        Initialize SessionManager with database connection.

        Args:
            db_url: PostgreSQL connection string
                   Format: postgresql://user:pass@host:port/db
                   If None, reads from DATABASE_URL env var
        """
        self.db_url = db_url or os.getenv(
            'DATABASE_URL',
            'postgresql://postgres:postgres@localhost:5432/eligibility_agent'
        )

        # Test connection on initialization
        try:
            conn = self._get_connection()
            conn.close()
        except Exception as e:
            print(f"⚠️  Database connection failed: {e}")
            print(f"📝 Make sure PostgreSQL is running and DATABASE_URL is set")
            print(f"   Current DATABASE_URL: {self.db_url}")

    def _get_connection(self):
        """
        Get a database connection.

        Returns:
            psycopg2 connection object

        === WHY A SEPARATE METHOD? ===

        We don't keep a persistent connection because:
        - Connections can timeout
        - Connection pools handle this better
        - Easier to test and mock
        - Thread-safe by default
        """
        return psycopg2.connect(
            self.db_url,
            cursor_factory=RealDictCursor  # Return dicts instead of tuples
        )

    def create_session(
        self,
        user_identifier: Optional[str] = None,
        customer_profile: Optional[Dict[str, Any]] = None,
        initial_query: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, str]:
        """
        Create a new conversation session.

        Args:
            user_identifier: Optional user ID/email
            customer_profile: Optional customer data (age, health, etc.)
            initial_query: Optional first question
            metadata: Optional additional metadata (user_agent, ip, etc.)

        Returns:
            Tuple of (session_id, session_key)
            - session_id: UUID for internal use
            - session_key: Client-facing key for reconnection

        === SESSION KEY vs SESSION ID ===

        session_id (UUID):
        - Internal database primary key
        - Never exposed to client directly
        - Used for all DB operations

        session_key (string):
        - Client-facing identifier
        - Stored in browser (localStorage/cookie)
        - User provides this to reconnect
        - More secure than exposing UUID
        """
        # Generate unique session key (UUID4 is cryptographically random)
        session_key = str(uuid.uuid4())

        # Extract metadata if provided
        user_agent = metadata.get('user_agent') if metadata else None
        ip_address = metadata.get('ip_address') if metadata else None

        # Insert into database
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO sessions (
                    session_key,
                    user_identifier,
                    user_agent,
                    ip_address,
                    initial_query,
                    customer_profile
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                session_key,
                user_identifier,
                user_agent,
                ip_address,
                initial_query,
                Json(customer_profile) if customer_profile else None
            ))

            session_id = cursor.fetchone()['id']
            conn.commit()

            return str(session_id), session_key

        finally:
            cursor.close()
            conn.close()

    def get_session_by_key(self, session_key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session by client-facing session key.

        Args:
            session_key: The session key provided by client

        Returns:
            Session dict or None if not found/expired

        === TYPICAL FLOW ===

        1. Client sends session_key with request
        2. Backend calls get_session_by_key(session_key)
        3. If valid, continue conversation
        4. If expired/not found, create new session
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT *
                FROM sessions
                WHERE session_key = %s
                AND status = 'active'
                AND expires_at > NOW()
            """, (session_key,))

            session = cursor.fetchone()
            return dict(session) if session else None

        finally:
            cursor.close()
            conn.close()

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        tool_name: Optional[str] = None,
        tool_input: Optional[Dict] = None,
        tool_output: Optional[Dict] = None
    ) -> int:
        """
        Add a message to the conversation.

        Args:
            session_id: Session UUID
            role: Message role ('user', 'assistant', 'tool', 'system')
            content: Message content
            metadata: Optional metadata (processing_time, model_used, etc.)
            tool_name: If role='tool', the tool name
            tool_input: If role='tool', the tool input params
            tool_output: If role='tool', the tool result

        Returns:
            Message ID

        === MESSAGE ROLES ===

        'user': Human message
            Example: "Can I get life insurance?"

        'assistant': Agent response
            Example: "Let me check your eligibility..."

        'tool': Tool call result (internal)
            Example: calculate_age('1985-05-15') -> 39

        'system': System notification (rare)
            Example: "Session restored from 2 hours ago"

        === WHY STORE TOOL CALLS? ===

        Storing tool calls allows us to:
        - Debug agent reasoning
        - Understand which tools are used most
        - Reproduce conversations exactly
        - Improve prompts based on tool usage patterns
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO messages (
                    session_id,
                    role,
                    content,
                    message_metadata,
                    tool_name,
                    tool_input,
                    tool_output
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                session_id,
                role,
                content,
                Json(metadata) if metadata else None,
                tool_name,
                Json(tool_input) if tool_input else None,
                Json(tool_output) if tool_output else None
            ))

            message_id = cursor.fetchone()['id']
            conn.commit()

            return message_id

        finally:
            cursor.close()
            conn.close()

    def get_messages(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all messages for a session.

        Args:
            session_id: Session UUID
            limit: Optional limit (e.g., last 20 messages)

        Returns:
            List of message dicts ordered by created_at ASC

        === MESSAGE FORMAT ===

        Each message dict contains:
        {
            'id': 123,
            'role': 'user',
            'content': 'Can I get insurance?',
            'created_at': datetime(...),
            'tool_name': None,  # or tool name if role='tool'
            ...
        }
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            query = """
                SELECT *
                FROM messages
                WHERE session_id = %s
                ORDER BY created_at ASC
            """

            if limit:
                query += f" LIMIT {limit}"

            cursor.execute(query, (session_id,))
            messages = cursor.fetchall()

            return [dict(msg) for msg in messages]

        finally:
            cursor.close()
            conn.close()

    def get_conversation_history(
        self,
        session_id: str,
        include_tool_messages: bool = False
    ) -> List:
        """
        Get conversation history in LangChain message format.

        This is the KEY method for agent integration!

        Args:
            session_id: Session UUID
            include_tool_messages: Whether to include tool calls in history

        Returns:
            List of LangChain message objects (HumanMessage, AIMessage, etc.)

        === WHY LANGCHAIN MESSAGE FORMAT? ===

        LangChain agents expect conversation history as:
        [
            HumanMessage(content="..."),
            AIMessage(content="..."),
            HumanMessage(content="..."),
            ...
        ]

        This method converts our database format to LangChain format.

        === USAGE WITH AGENT ===

        ```python
        # Get history
        history = session_manager.get_conversation_history(session_id)

        # Pass to agent
        result = agent_executor.invoke({
            "input": "New question here",
            "chat_history": history  # Agent now has context!
        })
        ```
        """
        messages = self.get_messages(session_id)

        langchain_messages = []

        for msg in messages:
            role = msg['role']
            content = msg['content']

            # Convert to appropriate LangChain message type
            if role == 'user':
                langchain_messages.append(HumanMessage(content=content))

            elif role == 'assistant':
                langchain_messages.append(AIMessage(content=content))

            elif role == 'system':
                langchain_messages.append(SystemMessage(content=content))

            elif role == 'tool' and include_tool_messages:
                # Tool messages are more complex - include tool name and result
                langchain_messages.append(ToolMessage(
                    content=content,
                    tool_call_id=str(msg['id']),  # Use message ID as tool call ID
                    name=msg.get('tool_name', 'unknown_tool')
                ))

        return langchain_messages

    def update_session_status(
        self,
        session_id: str,
        status: str
    ) -> bool:
        """
        Update session status.

        Args:
            session_id: Session UUID
            status: New status ('active', 'completed', 'abandoned')

        Returns:
            True if updated successfully

        === STATUS MEANINGS ===

        'active': Conversation ongoing
        'completed': User explicitly ended conversation
        'abandoned': User left without completing (auto-detected)
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE sessions
                SET status = %s
                WHERE id = %s
            """, (status, session_id))

            conn.commit()
            return cursor.rowcount > 0

        finally:
            cursor.close()
            conn.close()

    def extend_session_expiry(
        self,
        session_id: str,
        hours: int = 24
    ) -> bool:
        """
        Extend session expiration time.

        Useful when user is actively using the session.

        Args:
            session_id: Session UUID
            hours: Hours to extend from now

        Returns:
            True if updated successfully
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE sessions
                SET expires_at = NOW() + INTERVAL '%s hours'
                WHERE id = %s
            """, (hours, session_id))

            conn.commit()
            return cursor.rowcount > 0

        finally:
            cursor.close()
            conn.close()

    def cleanup_expired_sessions(self) -> int:
        """
        Delete expired sessions and their messages.

        Returns:
            Number of sessions deleted

        === WHEN TO CALL ===

        Call this from:
        - Cron job (daily cleanup)
        - Background task (every hour)
        - Admin endpoint (manual cleanup)

        Messages are automatically deleted via CASCADE.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT cleanup_expired_sessions()")
            deleted_count = cursor.fetchone()['cleanup_expired_sessions']
            conn.commit()

            return deleted_count

        finally:
            cursor.close()
            conn.close()


# === CONVENIENCE FUNCTION ===
def create_session_manager() -> SessionManager:
    """
    Create and return a SessionManager instance.

    Example:
        manager = create_session_manager()
        session_id, key = manager.create_session()
    """
    return SessionManager()
