"""
Email Analytics Service
Provides analytics and insights for the email archive.
"""

import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailAnalyticsService:
    """Handles analytics and insights for email archive"""

    def __init__(self, db_path: str = "email_archive.db"):
        self.db_path = db_path
        self.conn = None

    async def connect(self):
        """Connect to SQLite database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    async def get_emails_by_year(self) -> List[Dict[str, Any]]:
        """Get email count grouped by year"""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT
                strftime('%Y', date) as year,
                COUNT(*) as count
            FROM emails
            WHERE date IS NOT NULL
            GROUP BY year
            ORDER BY year
        """)

        return [dict(row) for row in cursor.fetchall()]

    async def get_emails_by_month(self, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get email count grouped by month"""
        cursor = self.conn.cursor()

        if year:
            cursor.execute("""
                SELECT
                    strftime('%Y-%m', date) as month,
                    COUNT(*) as count
                FROM emails
                WHERE date IS NOT NULL AND strftime('%Y', date) = ?
                GROUP BY month
                ORDER BY month
            """, (str(year),))
        else:
            cursor.execute("""
                SELECT
                    strftime('%Y-%m', date) as month,
                    COUNT(*) as count
                FROM emails
                WHERE date IS NOT NULL
                GROUP BY month
                ORDER BY month
            """)

        return [dict(row) for row in cursor.fetchall()]

    async def get_emails_by_day_of_week(self) -> List[Dict[str, Any]]:
        """Get email count grouped by day of week"""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT
                CASE CAST(strftime('%w', date) AS INTEGER)
                    WHEN 0 THEN 'Sunday'
                    WHEN 1 THEN 'Monday'
                    WHEN 2 THEN 'Tuesday'
                    WHEN 3 THEN 'Wednesday'
                    WHEN 4 THEN 'Thursday'
                    WHEN 5 THEN 'Friday'
                    WHEN 6 THEN 'Saturday'
                END as day_of_week,
                strftime('%w', date) as day_number,
                COUNT(*) as count
            FROM emails
            WHERE date IS NOT NULL
            GROUP BY day_number
            ORDER BY day_number
        """)

        return [dict(row) for row in cursor.fetchall()]

    async def get_emails_by_hour(self) -> List[Dict[str, Any]]:
        """Get email count grouped by hour of day"""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT
                strftime('%H', date) as hour,
                COUNT(*) as count
            FROM emails
            WHERE date IS NOT NULL
            GROUP BY hour
            ORDER BY hour
        """)

        return [dict(row) for row in cursor.fetchall()]

    async def get_top_senders(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get top senders by email count"""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT
                sender_email,
                sender,
                COUNT(*) as email_count,
                SUM(size_bytes) as total_size,
                MIN(date) as first_email,
                MAX(date) as last_email,
                SUM(CASE WHEN has_attachments = 1 THEN 1 ELSE 0 END) as emails_with_attachments
            FROM emails
            WHERE sender_email IS NOT NULL AND sender_email != ''
            GROUP BY sender_email
            ORDER BY email_count DESC
            LIMIT ?
        """, (limit,))

        return [dict(row) for row in cursor.fetchall()]

    async def get_top_recipients(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get top recipients by email count"""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT
                recipient_email,
                recipient,
                COUNT(*) as email_count,
                SUM(size_bytes) as total_size,
                MIN(date) as first_email,
                MAX(date) as last_email
            FROM emails
            WHERE recipient_email IS NOT NULL AND recipient_email != ''
            GROUP BY recipient_email
            ORDER BY email_count DESC
            LIMIT ?
        """, (limit,))

        return [dict(row) for row in cursor.fetchall()]

    async def get_top_domains(self, limit: int = 20, direction: str = 'sender') -> List[Dict[str, Any]]:
        """
        Get top email domains

        Args:
            limit: Number of results to return
            direction: 'sender' or 'recipient'
        """
        cursor = self.conn.cursor()

        email_field = 'sender_email' if direction == 'sender' else 'recipient_email'

        cursor.execute(f"""
            SELECT
                SUBSTR({email_field}, INSTR({email_field}, '@') + 1) as domain,
                COUNT(*) as count
            FROM emails
            WHERE {email_field} IS NOT NULL
                AND {email_field} != ''
                AND {email_field} LIKE '%@%'
            GROUP BY domain
            ORDER BY count DESC
            LIMIT ?
        """, (limit,))

        return [dict(row) for row in cursor.fetchall()]

    async def get_attachment_statistics(self) -> Dict[str, Any]:
        """Get detailed attachment statistics"""
        cursor = self.conn.cursor()

        # Total attachments
        cursor.execute("SELECT COUNT(*) FROM attachments")
        total_attachments = cursor.fetchone()[0]

        # Attachments by type
        cursor.execute("""
            SELECT
                content_type,
                COUNT(*) as count,
                SUM(size_bytes) as total_size
            FROM attachments
            GROUP BY content_type
            ORDER BY count DESC
            LIMIT 20
        """)
        by_type = [dict(row) for row in cursor.fetchall()]

        # Most common filenames
        cursor.execute("""
            SELECT
                filename,
                COUNT(*) as count
            FROM attachments
            WHERE filename IS NOT NULL
            GROUP BY filename
            ORDER BY count DESC
            LIMIT 20
        """)
        common_filenames = [dict(row) for row in cursor.fetchall()]

        # Total attachment size
        cursor.execute("SELECT SUM(size_bytes) FROM attachments")
        total_size = cursor.fetchone()[0] or 0

        return {
            'total_attachments': total_attachments,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'by_content_type': by_type,
            'common_filenames': common_filenames
        }

    async def get_conversation_statistics(self, email_address: str) -> Dict[str, Any]:
        """Get statistics for conversations with a specific email address"""
        cursor = self.conn.cursor()

        # Sent to this address
        cursor.execute("""
            SELECT COUNT(*) FROM emails
            WHERE recipient_email = ?
        """, (email_address,))
        sent_count = cursor.fetchone()[0]

        # Received from this address
        cursor.execute("""
            SELECT COUNT(*) FROM emails
            WHERE sender_email = ?
        """, (email_address,))
        received_count = cursor.fetchone()[0]

        # First and last email
        cursor.execute("""
            SELECT MIN(date), MAX(date) FROM emails
            WHERE sender_email = ? OR recipient_email = ?
        """, (email_address, email_address))
        date_range = cursor.fetchone()

        # Emails by month with this address
        cursor.execute("""
            SELECT
                strftime('%Y-%m', date) as month,
                SUM(CASE WHEN sender_email = ? THEN 1 ELSE 0 END) as received,
                SUM(CASE WHEN recipient_email = ? THEN 1 ELSE 0 END) as sent
            FROM emails
            WHERE (sender_email = ? OR recipient_email = ?)
                AND date IS NOT NULL
            GROUP BY month
            ORDER BY month
        """, (email_address, email_address, email_address, email_address))
        by_month = [dict(row) for row in cursor.fetchall()]

        return {
            'email_address': email_address,
            'sent_count': sent_count,
            'received_count': received_count,
            'total_count': sent_count + received_count,
            'first_email': date_range[0],
            'last_email': date_range[1],
            'by_month': by_month
        }

    async def search_keywords(self, keywords: List[str], limit: int = 100) -> Dict[str, Any]:
        """
        Search for keywords in email body and return frequency statistics

        Args:
            keywords: List of keywords to search for
            limit: Maximum results per keyword
        """
        cursor = self.conn.cursor()
        results = {}

        for keyword in keywords:
            cursor.execute("""
                SELECT COUNT(*) FROM emails
                WHERE body_text LIKE ?
            """, (f"%{keyword}%",))
            count = cursor.fetchone()[0]

            cursor.execute("""
                SELECT
                    id,
                    subject,
                    sender_email,
                    date
                FROM emails
                WHERE body_text LIKE ?
                ORDER BY date DESC
                LIMIT ?
            """, (f"%{keyword}%", limit))

            matches = [dict(row) for row in cursor.fetchall()]

            results[keyword] = {
                'count': count,
                'matches': matches
            }

        return results

    async def get_size_statistics(self) -> Dict[str, Any]:
        """Get email size distribution statistics"""
        cursor = self.conn.cursor()

        # Average size
        cursor.execute("SELECT AVG(size_bytes) FROM emails")
        avg_size = cursor.fetchone()[0] or 0

        # Size distribution
        cursor.execute("""
            SELECT
                CASE
                    WHEN size_bytes < 1024 THEN '< 1KB'
                    WHEN size_bytes < 10240 THEN '1-10KB'
                    WHEN size_bytes < 102400 THEN '10-100KB'
                    WHEN size_bytes < 1048576 THEN '100KB-1MB'
                    WHEN size_bytes < 10485760 THEN '1-10MB'
                    ELSE '> 10MB'
                END as size_range,
                COUNT(*) as count
            FROM emails
            GROUP BY size_range
        """)
        size_distribution = [dict(row) for row in cursor.fetchall()]

        # Largest emails
        cursor.execute("""
            SELECT
                id,
                subject,
                sender_email,
                date,
                size_bytes,
                has_attachments
            FROM emails
            ORDER BY size_bytes DESC
            LIMIT 20
        """)
        largest_emails = [dict(row) for row in cursor.fetchall()]

        return {
            'average_size_bytes': round(avg_size, 2),
            'average_size_kb': round(avg_size / 1024, 2),
            'size_distribution': size_distribution,
            'largest_emails': largest_emails
        }

    async def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
