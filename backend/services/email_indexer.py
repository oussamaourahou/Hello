"""
Email Indexer Service
Efficiently parses large mbox files and creates a searchable SQLite index.
"""

import mailbox
import sqlite3
import email
from email.utils import parsedate_to_datetime, parseaddr
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailIndexer:
    """Handles indexing of mbox files into SQLite database"""

    def __init__(self, db_path: str = "email_archive.db"):
        self.db_path = db_path
        self.conn = None

    async def connect(self):
        """Connect to SQLite database"""
        self.conn = sqlite3.connect(self.db_path)
        await self._create_tables()

    async def _create_tables(self):
        """Create database tables if they don't exist"""
        cursor = self.conn.cursor()

        # Main emails table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT UNIQUE,
                subject TEXT,
                sender TEXT,
                sender_email TEXT,
                recipient TEXT,
                recipient_email TEXT,
                date TIMESTAMP,
                body_text TEXT,
                body_html TEXT,
                has_attachments BOOLEAN,
                attachment_count INTEGER DEFAULT 0,
                size_bytes INTEGER,
                mbox_offset INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(message_id)
            )
        """)

        # Attachments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id INTEGER,
                filename TEXT,
                content_type TEXT,
                size_bytes INTEGER,
                FOREIGN KEY (email_id) REFERENCES emails(id)
            )
        """)

        # Create indexes for faster searching
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_emails_date ON emails(date DESC)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_emails_sender ON emails(sender_email)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_emails_subject ON emails(subject)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_emails_message_id ON emails(message_id)
        """)

        # Full-text search virtual table
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS emails_fts USING fts5(
                message_id UNINDEXED,
                subject,
                sender,
                recipient,
                body_text,
                content='emails',
                content_rowid='id'
            )
        """)

        self.conn.commit()

    def _extract_text_body(self, msg: email.message.Message) -> tuple[str, str]:
        """Extract text and HTML body from email message"""
        text_body = ""
        html_body = ""

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))

                if "attachment" not in content_disposition:
                    if content_type == "text/plain":
                        try:
                            text_body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        except:
                            pass
                    elif content_type == "text/html":
                        try:
                            html_body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        except:
                            pass
        else:
            content_type = msg.get_content_type()
            try:
                payload = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                if content_type == "text/plain":
                    text_body = payload
                elif content_type == "text/html":
                    html_body = payload
            except:
                pass

        return text_body, html_body

    def _extract_attachments(self, msg: email.message.Message) -> list[Dict[str, Any]]:
        """Extract attachment information from email message"""
        attachments = []

        if msg.is_multipart():
            for part in msg.walk():
                content_disposition = str(part.get("Content-Disposition", ""))

                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        attachments.append({
                            'filename': filename,
                            'content_type': part.get_content_type(),
                            'size_bytes': len(part.get_payload(decode=False))
                        })

        return attachments

    async def index_mbox(self, mbox_path: str, batch_size: int = 1000) -> Dict[str, Any]:
        """
        Index an mbox file into the database

        Args:
            mbox_path: Path to the mbox file
            batch_size: Number of emails to process before committing

        Returns:
            Dictionary with indexing statistics
        """
        if not Path(mbox_path).exists():
            raise FileNotFoundError(f"Mbox file not found: {mbox_path}")

        logger.info(f"Starting to index mbox file: {mbox_path}")

        mbox = mailbox.mbox(mbox_path)
        cursor = self.conn.cursor()

        total_indexed = 0
        total_skipped = 0
        errors = 0
        batch_count = 0

        try:
            for idx, message in enumerate(mbox):
                try:
                    # Extract message ID
                    message_id = message.get('Message-ID', f"generated-{idx}")

                    # Check if already indexed
                    cursor.execute("SELECT id FROM emails WHERE message_id = ?", (message_id,))
                    if cursor.fetchone():
                        total_skipped += 1
                        continue

                    # Extract headers
                    subject = message.get('Subject', '')
                    sender_name, sender_email = parseaddr(message.get('From', ''))
                    recipient_name, recipient_email = parseaddr(message.get('To', ''))

                    # Parse date
                    date_str = message.get('Date')
                    try:
                        date = parsedate_to_datetime(date_str) if date_str else None
                    except:
                        date = None

                    # Extract body
                    text_body, html_body = self._extract_text_body(message)

                    # Extract attachments
                    attachments = self._extract_attachments(message)

                    # Calculate size
                    size_bytes = len(str(message))

                    # Insert email
                    cursor.execute("""
                        INSERT INTO emails (
                            message_id, subject, sender, sender_email,
                            recipient, recipient_email, date, body_text, body_html,
                            has_attachments, attachment_count, size_bytes, mbox_offset
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        message_id, subject, sender_name, sender_email,
                        recipient_name, recipient_email, date, text_body, html_body,
                        len(attachments) > 0, len(attachments), size_bytes, idx
                    ))

                    email_id = cursor.lastrowid

                    # Insert attachments
                    for att in attachments:
                        cursor.execute("""
                            INSERT INTO attachments (email_id, filename, content_type, size_bytes)
                            VALUES (?, ?, ?, ?)
                        """, (email_id, att['filename'], att['content_type'], att['size_bytes']))

                    # Insert into FTS table
                    cursor.execute("""
                        INSERT INTO emails_fts (rowid, message_id, subject, sender, recipient, body_text)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (email_id, message_id, subject, sender_name, recipient_name, text_body[:10000]))

                    total_indexed += 1
                    batch_count += 1

                    # Commit in batches
                    if batch_count >= batch_size:
                        self.conn.commit()
                        logger.info(f"Indexed {total_indexed} emails so far...")
                        batch_count = 0

                except Exception as e:
                    logger.error(f"Error processing email {idx}: {str(e)}")
                    errors += 1
                    continue

            # Final commit
            self.conn.commit()
            logger.info(f"Indexing complete: {total_indexed} indexed, {total_skipped} skipped, {errors} errors")

        except Exception as e:
            logger.error(f"Fatal error during indexing: {str(e)}")
            raise

        return {
            'total_indexed': total_indexed,
            'total_skipped': total_skipped,
            'errors': errors,
            'status': 'completed'
        }

    async def get_index_status(self) -> Dict[str, Any]:
        """Get current indexing status and statistics"""
        cursor = self.conn.cursor()

        # Get total count
        cursor.execute("SELECT COUNT(*) FROM emails")
        total_emails = cursor.fetchone()[0]

        # Get date range
        cursor.execute("SELECT MIN(date), MAX(date) FROM emails WHERE date IS NOT NULL")
        date_range = cursor.fetchone()

        # Get top senders
        cursor.execute("""
            SELECT sender_email, COUNT(*) as count
            FROM emails
            WHERE sender_email IS NOT NULL AND sender_email != ''
            GROUP BY sender_email
            ORDER BY count DESC
            LIMIT 10
        """)
        top_senders = [{'email': row[0], 'count': row[1]} for row in cursor.fetchall()]

        # Get attachment stats
        cursor.execute("SELECT COUNT(*) FROM emails WHERE has_attachments = 1")
        emails_with_attachments = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM attachments")
        total_attachments = cursor.fetchone()[0]

        return {
            'total_emails': total_emails,
            'date_range': {
                'earliest': date_range[0],
                'latest': date_range[1]
            },
            'top_senders': top_senders,
            'emails_with_attachments': emails_with_attachments,
            'total_attachments': total_attachments
        }

    async def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
