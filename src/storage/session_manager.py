"""
Session management for conversation persistence.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
import json
from .database import Database


class SessionManager:
    """Manages conversation sessions and messages."""

    def __init__(self, db: Optional[Database] = None):
        """Initialize session manager.

        Args:
            db: Database instance (creates new if None)
        """
        self.db = db or Database()

    # Session Operations

    def create_session(self, title: str = None, metadata: Dict = None) -> int:
        """Create a new conversation session.

        Args:
            title: Session title (auto-generated if None)
            metadata: Additional session metadata

        Returns:
            Session ID
        """
        if not title:
            title = f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        metadata_json = json.dumps(metadata or {})

        cursor = self.db.execute(
            "INSERT INTO sessions (title, metadata) VALUES (?, ?)",
            (title, metadata_json),
        )
        return cursor.lastrowid

    def get_session(self, session_id: int) -> Optional[Dict[str, Any]]:
        """Get session by ID.

        Args:
            session_id: Session ID

        Returns:
            Session dictionary or None
        """
        session = self.db.fetchone("SELECT * FROM sessions WHERE id = ?", (session_id,))
        if session:
            session["metadata"] = json.loads(session.get("metadata", "{}"))
        return session

    def list_sessions(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """List all sessions ordered by most recent.

        Args:
            limit: Maximum number of sessions to return
            offset: Offset for pagination

        Returns:
            List of session dictionaries
        """
        sessions = self.db.fetchall(
            """
            SELECT s.*, COUNT(m.id) as message_count
            FROM sessions s
            LEFT JOIN messages m ON s.id = m.session_id
            GROUP BY s.id
            ORDER BY s.updated_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        )

        for session in sessions:
            session["metadata"] = json.loads(session.get("metadata", "{}"))

        return sessions

    def update_session(
        self, session_id: int, title: str = None, metadata: Dict = None
    ) -> bool:
        """Update session details.

        Args:
            session_id: Session ID
            title: New title (optional)
            metadata: New metadata (optional)

        Returns:
            True if successful
        """
        updates = []
        params = []

        if title is not None:
            updates.append("title = ?")
            params.append(title)

        if metadata is not None:
            updates.append("metadata = ?")
            params.append(json.dumps(metadata))

        if not updates:
            return False

        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(session_id)

        query = f"UPDATE sessions SET {', '.join(updates)} WHERE id = ?"
        self.db.execute(query, tuple(params))
        return True

    def delete_session(self, session_id: int) -> bool:
        """Delete a session and all its messages.

        Args:
            session_id: Session ID

        Returns:
            True if successful
        """
        self.db.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        return True

    def search_sessions(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search sessions by title or message content.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching sessions
        """
        search_pattern = f"%{query}%"

        sessions = self.db.fetchall(
            """
            SELECT DISTINCT s.*, COUNT(m.id) as message_count
            FROM sessions s
            LEFT JOIN messages m ON s.id = m.session_id
            WHERE s.title LIKE ? OR m.content LIKE ?
            GROUP BY s.id
            ORDER BY s.updated_at DESC
            LIMIT ?
            """,
            (search_pattern, search_pattern, limit),
        )

        for session in sessions:
            session["metadata"] = json.loads(session.get("metadata", "{}"))

        return sessions

    # Message Operations

    def add_message(
        self, session_id: int, role: str, content: str, metadata: Dict = None
    ) -> int:
        """Add a message to a session.

        Args:
            session_id: Session ID
            role: Message role (user/assistant/system)
            content: Message content
            metadata: Additional message metadata

        Returns:
            Message ID
        """
        metadata_json = json.dumps(metadata or {})

        cursor = self.db.execute(
            """
            INSERT INTO messages (session_id, role, content, metadata)
            VALUES (?, ?, ?, ?)
            """,
            (session_id, role, content, metadata_json),
        )

        # Update session timestamp
        self.db.execute(
            "UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (session_id,),
        )

        return cursor.lastrowid

    def get_messages(
        self, session_id: int, limit: int = None, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get messages for a session.

        Args:
            session_id: Session ID
            limit: Maximum messages to return (None for all)
            offset: Offset for pagination

        Returns:
            List of message dictionaries
        """
        query = """
            SELECT * FROM messages
            WHERE session_id = ?
            ORDER BY timestamp ASC
        """
        params = [session_id]

        if limit is not None:
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])

        messages = self.db.fetchall(query, tuple(params))

        for message in messages:
            message["metadata"] = json.loads(message.get("metadata", "{}"))

        return messages

    def get_message_count(self, session_id: int) -> int:
        """Get total message count for a session.

        Args:
            session_id: Session ID

        Returns:
            Message count
        """
        result = self.db.fetchone(
            "SELECT COUNT(*) as count FROM messages WHERE session_id = ?", (session_id,)
        )
        return result["count"] if result else 0

    def delete_message(self, message_id: int) -> bool:
        """Delete a specific message.

        Args:
            message_id: Message ID

        Returns:
            True if successful
        """
        self.db.execute("DELETE FROM messages WHERE id = ?", (message_id,))
        return True

    def clear_messages(self, session_id: int) -> bool:
        """Clear all messages from a session.

        Args:
            session_id: Session ID

        Returns:
            True if successful
        """
        self.db.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        return True

    # Export Operations

    def export_session_json(self, session_id: int) -> Optional[Dict[str, Any]]:
        """Export session to JSON-serializable dictionary.

        Args:
            session_id: Session ID

        Returns:
            Session data dictionary or None if session not found
        """
        session = self.get_session(session_id)
        if not session:
            return None

        messages = self.get_messages(session_id)

        return {
            "session": session,
            "messages": messages,
            "exported_at": datetime.now().isoformat(),
        }

    def export_session_markdown(self, session_id: int) -> Optional[str]:
        """Export session to Markdown format.

        Args:
            session_id: Session ID

        Returns:
            Markdown string or None if session not found
        """
        session = self.get_session(session_id)
        if not session:
            return None

        messages = self.get_messages(session_id)

        md = f"# {session['title']}\n\n"
        md += f"**Created:** {session['created_at']}\n\n"
        md += f"**Messages:** {len(messages)}\n\n"
        md += "---\n\n"

        for msg in messages:
            role = msg["role"].title()
            content = msg["content"]
            timestamp = msg["timestamp"]
            md += f"### {role} ({timestamp})\n\n{content}\n\n"

        return md

    # Statistics

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics.

        Returns:
            Statistics dictionary
        """
        total_sessions = self.db.fetchone("SELECT COUNT(*) as count FROM sessions")
        total_messages = self.db.fetchone("SELECT COUNT(*) as count FROM messages")

        return {
            "total_sessions": total_sessions["count"],
            "total_messages": total_messages["count"],
            "database_path": str(self.db.db_path),
        }
