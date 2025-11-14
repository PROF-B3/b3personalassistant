"""
Gmail Integration for B3PersonalAssistant

Provides email management through Gmail API including reading, sending,
searching, and organizing emails.
"""

import logging
import base64
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import pickle

logger = logging.getLogger(__name__)


@dataclass
class Email:
    """Email message representation."""
    id: str
    thread_id: str
    subject: str
    sender: str
    recipient: str
    date: datetime
    body: str
    snippet: str
    labels: List[str]
    is_read: bool = False
    has_attachments: bool = False
    importance: str = "normal"  # "low", "normal", "high"


class GmailIntegration:
    """
    Gmail API integration for email management.

    Features:
    - Read emails with filters
    - Send emails
    - Search emails semantically
    - Mark as read/unread
    - Apply labels
    - Archive/delete emails
    - Extract action items
    - Auto-categorize
    - Smart replies

    Example:
        >>> gmail = GmailIntegration()
        >>> gmail.authenticate()
        >>>
        >>> # Get unread emails
        >>> emails = gmail.get_emails(unread_only=True, max_results=10)
        >>> for email in emails:
        ...     print(f"{email.subject} from {email.sender}")
        >>>
        >>> # Send email
        >>> gmail.send_email(
        ...     to="user@example.com",
        ...     subject="Hello",
        ...     body="Test email from B3Assistant"
        ... )
    """

    def __init__(self, credentials_path: Optional[str] = None, token_path: Optional[str] = None):
        """
        Initialize Gmail integration.

        Args:
            credentials_path: Path to OAuth credentials.json
            token_path: Path to store token.pickle
        """
        if credentials_path is None:
            credentials_path = os.environ.get("GMAIL_CREDENTIALS_PATH", "credentials.json")
        if token_path is None:
            token_path = os.environ.get("GMAIL_TOKEN_PATH", "token.pickle")

        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self._check_dependencies()

    def _check_dependencies(self):
        """Check if required libraries are installed."""
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
            self.dependencies_available = True
            logger.info("Gmail API dependencies available")
        except ImportError:
            self.dependencies_available = False
            logger.warning(
                "Gmail API dependencies not installed. "
                "Install with: pip install -e '.[integrations]'"
            )

    def authenticate(self, scopes: Optional[List[str]] = None) -> bool:
        """
        Authenticate with Gmail API.

        Args:
            scopes: OAuth scopes (defaults to read/send/modify)

        Returns:
            True if authentication successful

        Example:
            >>> gmail = GmailIntegration()
            >>> if gmail.authenticate():
            ...     print("Authenticated successfully")
        """
        if not self.dependencies_available:
            logger.error("Gmail dependencies not available")
            return False

        if scopes is None:
            scopes = [
                'https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/gmail.send',
                'https://www.googleapis.com/auth/gmail.modify'
            ]

        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build

            creds = None

            # Load existing token
            if Path(self.token_path).exists():
                with open(self.token_path, 'rb') as token:
                    creds = pickle.load(token)

            # Refresh or get new token
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not Path(self.credentials_path).exists():
                        logger.error(f"Credentials file not found: {self.credentials_path}")
                        logger.info("Download credentials.json from Google Cloud Console")
                        return False

                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, scopes
                    )
                    creds = flow.run_local_server(port=0)

                # Save token
                with open(self.token_path, 'wb') as token:
                    pickle.dump(creds, token)

            # Build service
            self.service = build('gmail', 'v1', credentials=creds)
            logger.info("Gmail API authenticated successfully")
            return True

        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False

    def get_emails(
        self,
        query: Optional[str] = None,
        unread_only: bool = False,
        max_results: int = 20,
        label_ids: Optional[List[str]] = None
    ) -> List[Email]:
        """
        Get emails with optional filters.

        Args:
            query: Gmail search query (e.g., "from:user@example.com")
            unread_only: Only get unread emails
            max_results: Maximum number of emails
            label_ids: Filter by label IDs

        Returns:
            List of Email objects

        Example:
            >>> emails = gmail.get_emails(
            ...     query="subject:urgent",
            ...     unread_only=True,
            ...     max_results=5
            ... )
        """
        if not self.service:
            logger.error("Not authenticated. Call authenticate() first.")
            return []

        try:
            # Build query
            search_query = query or ""
            if unread_only:
                search_query = "is:unread " + search_query

            # Get message list
            response = self.service.users().messages().list(
                userId='me',
                q=search_query.strip(),
                maxResults=max_results,
                labelIds=label_ids
            ).execute()

            messages = response.get('messages', [])
            emails = []

            # Get full message details
            for msg in messages:
                email = self._get_email_details(msg['id'])
                if email:
                    emails.append(email)

            logger.info(f"Retrieved {len(emails)} emails")
            return emails

        except Exception as e:
            logger.error(f"Failed to get emails: {e}")
            return []

    def _get_email_details(self, message_id: str) -> Optional[Email]:
        """Get full email details."""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            headers = message['payload']['headers']
            header_dict = {h['name']: h['value'] for h in headers}

            # Extract body
            body = self._get_email_body(message['payload'])

            # Parse date
            date_str = header_dict.get('Date', '')
            try:
                from email.utils import parsedate_to_datetime
                date = parsedate_to_datetime(date_str)
            except:
                date = datetime.now()

            # Check if read
            is_read = 'UNREAD' not in message.get('labelIds', [])

            # Determine importance
            importance = self._determine_importance(header_dict, message)

            return Email(
                id=message['id'],
                thread_id=message['threadId'],
                subject=header_dict.get('Subject', '(No Subject)'),
                sender=header_dict.get('From', ''),
                recipient=header_dict.get('To', ''),
                date=date,
                body=body,
                snippet=message.get('snippet', ''),
                labels=message.get('labelIds', []),
                is_read=is_read,
                has_attachments='ATTACHMENT' in message.get('labelIds', []),
                importance=importance
            )

        except Exception as e:
            logger.error(f"Failed to get email details: {e}")
            return None

    def _get_email_body(self, payload: Dict) -> str:
        """Extract email body from payload."""
        body = ""

        if 'body' in payload and 'data' in payload['body']:
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

        elif 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
                elif part['mimeType'] == 'text/html' and not body:
                    if 'data' in part['body']:
                        # Fallback to HTML
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')

        return body

    def _determine_importance(self, headers: Dict, message: Dict) -> str:
        """Determine email importance."""
        # Check priority headers
        priority = headers.get('X-Priority', '3')
        importance_header = headers.get('Importance', 'normal').lower()

        if priority == '1' or importance_header == 'high':
            return "high"
        elif priority == '5' or importance_header == 'low':
            return "low"

        # Check for IMPORTANT label
        if 'IMPORTANT' in message.get('labelIds', []):
            return "high"

        return "normal"

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
        html: bool = False
    ) -> Optional[str]:
        """
        Send an email.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            cc: CC recipients (comma-separated)
            bcc: BCC recipients (comma-separated)
            html: Whether body is HTML

        Returns:
            Message ID if successful, None otherwise

        Example:
            >>> message_id = gmail.send_email(
            ...     to="user@example.com",
            ...     subject="Meeting Tomorrow",
            ...     body="Let's meet at 2pm"
            ... )
        """
        if not self.service:
            logger.error("Not authenticated")
            return None

        try:
            message = MIMEMultipart() if html else MIMEText(body)
            message['to'] = to
            message['subject'] = subject

            if cc:
                message['cc'] = cc
            if bcc:
                message['bcc'] = bcc

            if html:
                message.attach(MIMEText(body, 'html'))

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

            result = self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()

            logger.info(f"Email sent successfully: {result['id']}")
            return result['id']

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return None

    def mark_as_read(self, message_id: str) -> bool:
        """Mark email as read."""
        if not self.service:
            return False

        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to mark as read: {e}")
            return False

    def mark_as_unread(self, message_id: str) -> bool:
        """Mark email as unread."""
        if not self.service:
            return False

        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': ['UNREAD']}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to mark as unread: {e}")
            return False

    def archive_email(self, message_id: str) -> bool:
        """Archive an email (remove INBOX label)."""
        if not self.service:
            return False

        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['INBOX']}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to archive: {e}")
            return False

    def delete_email(self, message_id: str) -> bool:
        """Move email to trash."""
        if not self.service:
            return False

        try:
            self.service.users().messages().trash(
                userId='me',
                id=message_id
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to delete: {e}")
            return False

    def summarize_emails(self, emails: List[Email]) -> Dict[str, Any]:
        """
        Create a summary of emails.

        Args:
            emails: List of emails to summarize

        Returns:
            Dictionary with summary statistics

        Example:
            >>> emails = gmail.get_emails(unread_only=True)
            >>> summary = gmail.summarize_emails(emails)
            >>> print(f"Unread: {summary['total']}, High priority: {summary['high_priority']}")
        """
        if not emails:
            return {
                "total": 0,
                "high_priority": 0,
                "senders": {},
                "subjects": []
            }

        # Count by sender
        senders = {}
        for email in emails:
            sender = email.sender
            senders[sender] = senders.get(sender, 0) + 1

        # Get subjects
        subjects = [email.subject for email in emails[:10]]

        # Count high priority
        high_priority = sum(1 for e in emails if e.importance == "high")

        return {
            "total": len(emails),
            "high_priority": high_priority,
            "senders": senders,
            "subjects": subjects,
            "oldest": min(emails, key=lambda e: e.date).date.isoformat() if emails else None,
            "newest": max(emails, key=lambda e: e.date).date.isoformat() if emails else None
        }

    def extract_action_items(self, email: Email) -> List[str]:
        """
        Extract action items from email using simple heuristics.

        In production, this would use NLP/LLM for better extraction.

        Args:
            email: Email to analyze

        Returns:
            List of potential action items
        """
        action_items = []

        # Simple keyword-based extraction
        action_keywords = [
            "please ", "could you ", "can you ", "need you to ",
            "action required", "todo:", "to do:", "task:",
            "deadline:", "due date:", "by "
        ]

        body_lower = email.body.lower()
        lines = email.body.split('\n')

        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in action_keywords):
                action_items.append(line.strip())

        return action_items[:5]  # Limit to 5


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Initialize
    gmail = GmailIntegration()

    # Authenticate
    if gmail.authenticate():
        print("✅ Authenticated with Gmail")

        # Get unread emails
        print("\nFetching unread emails...")
        emails = gmail.get_emails(unread_only=True, max_results=5)

        for i, email in enumerate(emails, 1):
            print(f"\n{i}. {email.subject}")
            print(f"   From: {email.sender}")
            print(f"   Date: {email.date}")
            print(f"   Importance: {email.importance}")
            print(f"   Snippet: {email.snippet[:100]}...")

            # Extract action items
            actions = gmail.extract_action_items(email)
            if actions:
                print(f"   Action items: {len(actions)}")
                for action in actions:
                    print(f"     - {action[:80]}")

        # Get summary
        print("\n📊 Email Summary:")
        summary = gmail.summarize_emails(emails)
        print(f"   Total: {summary['total']}")
        print(f"   High Priority: {summary['high_priority']}")
        print(f"   Top senders: {list(summary['senders'].keys())[:3]}")

    else:
        print("❌ Authentication failed")
        print("1. Download credentials.json from Google Cloud Console")
        print("2. Enable Gmail API in your Google Cloud project")
        print("3. Set GMAIL_CREDENTIALS_PATH environment variable")
