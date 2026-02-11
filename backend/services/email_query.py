"""
Email Query Service
Provides search and query functionality for the email archive.
"""

import sqlite3
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailQueryService:
    """Handles querying and searching of indexed emails"""

    def __init__(self, db_path: str = "email_archive.db"):
        self.db_path = db_path
        self.conn = None

    async def connect(self):
        """Connect to SQLite database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    async def search_emails(
        self,
        query: Optional[str] = None,
        sender: Optional[str] = None,
        recipient: Optional[str] = None,
        subject: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        has_attachments: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search emails with various filters

        Args:
            query: Full-text search query
            sender: Filter by sender email
            recipient: Filter by recipient email
            subject: Filter by subject (partial match)
            date_from: Start date (ISO format)
            date_to: End date (ISO format)
            has_attachments: Filter by attachment presence
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            Dictionary with results and metadata
        """
        cursor = self.conn.cursor()
        params = []

        # Build SQL query
        if query:
            # Use full-text search
            sql = """
                SELECT e.*, emails_fts.rank
                FROM emails e
                JOIN emails_fts ON e.id = emails_fts.rowid
                WHERE emails_fts MATCH ?
            """
            params.append(query)
        else:
            sql = "SELECT * FROM emails WHERE 1=1"

        # Add filters
        if sender:
            sql += " AND sender_email LIKE ?"
            params.append(f"%{sender}%")

        if recipient:
            sql += " AND recipient_email LIKE ?"
            params.append(f"%{recipient}%")

        if subject:
            sql += " AND subject LIKE ?"
            params.append(f"%{subject}%")

        if date_from:
            sql += " AND date >= ?"
            params.append(date_from)

        if date_to:
            sql += " AND date <= ?"
            params.append(date_to)

        if has_attachments is not None:
            sql += " AND has_attachments = ?"
            params.append(1 if has_attachments else 0)

        # Get total count
        count_sql = f"SELECT COUNT(*) FROM ({sql})"
        cursor.execute(count_sql, params)
        total_count = cursor.fetchone()[0]

        # Add ordering and pagination
        sql += " ORDER BY date DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(sql, params)
        rows = cursor.fetchall()

        results = [dict(row) for row in rows]

        return {
            'results': results,
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
            'has_more': (offset + limit) < total_count
        }

    async def get_email_by_id(self, email_id: int) -> Optional[Dict[str, Any]]:
        """Get a single email by ID with attachments"""
        cursor = self.conn.cursor()

        # Get email
        cursor.execute("SELECT * FROM emails WHERE id = ?", (email_id,))
        row = cursor.fetchone()

        if not row:
            return None

        email_data = dict(row)

        # Get attachments
        cursor.execute(
            "SELECT * FROM attachments WHERE email_id = ?",
            (email_id,)
        )
        attachments = [dict(att_row) for att_row in cursor.fetchall()]
        email_data['attachments'] = attachments

        return email_data

    async def get_email_by_message_id(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get a single email by Message-ID"""
        cursor = self.conn.cursor()

        cursor.execute("SELECT * FROM emails WHERE message_id = ?", (message_id,))
        row = cursor.fetchone()

        if not row:
            return None

        email_data = dict(row)

        # Get attachments
        email_id = email_data['id']
        cursor.execute(
            "SELECT * FROM attachments WHERE email_id = ?",
            (email_id,)
        )
        attachments = [dict(att_row) for att_row in cursor.fetchall()]
        email_data['attachments'] = attachments

        return email_data

    async def get_senders(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get list of unique senders with email counts"""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT
                sender_email,
                sender,
                COUNT(*) as email_count,
                MIN(date) as first_email,
                MAX(date) as last_email
            FROM emails
            WHERE sender_email IS NOT NULL AND sender_email != ''
            GROUP BY sender_email
            ORDER BY email_count DESC
            LIMIT ?
        """, (limit,))

        return [dict(row) for row in cursor.fetchall()]

    async def get_recipients(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get list of unique recipients with email counts"""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT
                recipient_email,
                recipient,
                COUNT(*) as email_count,
                MIN(date) as first_email,
                MAX(date) as last_email
            FROM emails
            WHERE recipient_email IS NOT NULL AND recipient_email != ''
            GROUP BY recipient_email
            ORDER BY email_count DESC
            LIMIT ?
        """, (limit,))

        return [dict(row) for row in cursor.fetchall()]

    async def get_thread(self, message_id: str) -> List[Dict[str, Any]]:
        """
        Get email thread based on message ID
        (Simplified version - looks for In-Reply-To and References headers)
        """
        # Note: Full thread reconstruction would require parsing In-Reply-To
        # and References headers, which we could add in a future enhancement
        email = await self.get_email_by_message_id(message_id)
        if email:
            return [email]
        return []

    async def get_attachments_for_email(self, email_id: int) -> List[Dict[str, Any]]:
        """Get all attachments for a specific email"""
        cursor = self.conn.cursor()

        cursor.execute(
            "SELECT * FROM attachments WHERE email_id = ?",
            (email_id,)
        )

        return [dict(row) for row in cursor.fetchall()]

    async def search_by_attachment(self, filename_pattern: str) -> List[Dict[str, Any]]:
        """Search emails by attachment filename"""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT DISTINCT e.*
            FROM emails e
            JOIN attachments a ON e.id = a.email_id
            WHERE a.filename LIKE ?
            ORDER BY e.date DESC
        """, (f"%{filename_pattern}%",))

        return [dict(row) for row in cursor.fetchall()]

    async def get_email_stats(self) -> Dict[str, Any]:
        """Get overall statistics about the email archive"""
        cursor = self.conn.cursor()

        # Total emails
        cursor.execute("SELECT COUNT(*) FROM emails")
        total_emails = cursor.fetchone()[0]

        # Date range
        cursor.execute("SELECT MIN(date), MAX(date) FROM emails WHERE date IS NOT NULL")
        date_range = cursor.fetchone()

        # Unique senders
        cursor.execute("SELECT COUNT(DISTINCT sender_email) FROM emails WHERE sender_email IS NOT NULL")
        unique_senders = cursor.fetchone()[0]

        # Unique recipients
        cursor.execute("SELECT COUNT(DISTINCT recipient_email) FROM emails WHERE recipient_email IS NOT NULL")
        unique_recipients = cursor.fetchone()[0]

        # Emails with attachments
        cursor.execute("SELECT COUNT(*) FROM emails WHERE has_attachments = 1")
        with_attachments = cursor.fetchone()[0]

        # Total attachments
        cursor.execute("SELECT COUNT(*) FROM attachments")
        total_attachments = cursor.fetchone()[0]

        # Total size
        cursor.execute("SELECT SUM(size_bytes) FROM emails")
        total_size = cursor.fetchone()[0] or 0

        return {
            'total_emails': total_emails,
            'date_range': {
                'earliest': date_range[0],
                'latest': date_range[1]
            },
            'unique_senders': unique_senders,
            'unique_recipients': unique_recipients,
            'emails_with_attachments': with_attachments,
            'total_attachments': total_attachments,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2)
        }

    async def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
