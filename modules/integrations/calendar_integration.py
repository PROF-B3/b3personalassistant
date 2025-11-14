"""
Google Calendar Integration for B3PersonalAssistant

Provides calendar management including creating, reading, updating events,
and smart scheduling suggestions.
"""

import logging
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path
import pickle

logger = logging.getLogger(__name__)


@dataclass
class CalendarEvent:
    """Calendar event representation."""
    id: str
    summary: str
    description: Optional[str]
    start: datetime
    end: datetime
    location: Optional[str] = None
    attendees: Optional[List[str]] = None
    reminders: Optional[List[int]] = None  # Minutes before
    recurrence: Optional[str] = None
    calendar_id: str = "primary"


class CalendarIntegration:
    """
    Google Calendar API integration.

    Features:
    - Create/update/delete events
    - List events with filters
    - Find free time slots
    - Smart scheduling suggestions
    - Meeting conflict detection
    - Automatic reminder creation
    - Sync with tasks

    Example:
        >>> calendar = CalendarIntegration()
        >>> calendar.authenticate()
        >>>
        >>> # Get today's events
        >>> events = calendar.get_events(
        ...     start_date=datetime.now(),
        ...     end_date=datetime.now() + timedelta(days=1)
        ... )
        >>>
        >>> # Create event
        >>> event_id = calendar.create_event(
        ...     summary="Team Meeting",
        ...     start=datetime.now() + timedelta(hours=2),
        ...     duration_minutes=60,
        ...     attendees=["team@example.com"]
        ... )
    """

    def __init__(self, credentials_path: Optional[str] = None, token_path: Optional[str] = None):
        """
        Initialize Calendar integration.

        Args:
            credentials_path: Path to OAuth credentials.json
            token_path: Path to store token.pickle
        """
        if credentials_path is None:
            credentials_path = os.environ.get("CALENDAR_CREDENTIALS_PATH", "credentials.json")
        if token_path is None:
            token_path = os.environ.get("CALENDAR_TOKEN_PATH", "calendar_token.pickle")

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
            logger.info("Calendar API dependencies available")
        except ImportError:
            self.dependencies_available = False
            logger.warning(
                "Calendar API dependencies not installed. "
                "Install with: pip install -e '.[integrations]'"
            )

    def authenticate(self, scopes: Optional[List[str]] = None) -> bool:
        """
        Authenticate with Google Calendar API.

        Args:
            scopes: OAuth scopes

        Returns:
            True if authentication successful
        """
        if not self.dependencies_available:
            logger.error("Calendar dependencies not available")
            return False

        if scopes is None:
            scopes = ['https://www.googleapis.com/auth/calendar']

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
                        return False

                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, scopes
                    )
                    creds = flow.run_local_server(port=0)

                # Save token
                with open(self.token_path, 'wb') as token:
                    pickle.dump(creds, token)

            # Build service
            self.service = build('calendar', 'v3', credentials=creds)
            logger.info("Calendar API authenticated successfully")
            return True

        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False

    def get_events(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        max_results: int = 50,
        calendar_id: str = "primary"
    ) -> List[CalendarEvent]:
        """
        Get calendar events.

        Args:
            start_date: Start of time range (defaults to now)
            end_date: End of time range (defaults to 7 days from now)
            max_results: Maximum number of events
            calendar_id: Calendar ID

        Returns:
            List of CalendarEvent objects
        """
        if not self.service:
            logger.error("Not authenticated")
            return []

        try:
            if start_date is None:
                start_date = datetime.now()
            if end_date is None:
                end_date = start_date + timedelta(days=7)

            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=start_date.isoformat() + 'Z',
                timeMax=end_date.isoformat() + 'Z',
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])
            calendar_events = []

            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))

                # Parse datetime
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))

                # Extract attendees
                attendees = None
                if 'attendees' in event:
                    attendees = [a['email'] for a in event['attendees']]

                # Extract reminders
                reminders = None
                if 'reminders' in event and 'overrides' in event['reminders']:
                    reminders = [r['minutes'] for r in event['reminders']['overrides']]

                calendar_events.append(CalendarEvent(
                    id=event['id'],
                    summary=event.get('summary', '(No title)'),
                    description=event.get('description'),
                    start=start_dt,
                    end=end_dt,
                    location=event.get('location'),
                    attendees=attendees,
                    reminders=reminders,
                    recurrence=event.get('recurrence'),
                    calendar_id=calendar_id
                ))

            logger.info(f"Retrieved {len(calendar_events)} events")
            return calendar_events

        except Exception as e:
            logger.error(f"Failed to get events: {e}")
            return []

    def create_event(
        self,
        summary: str,
        start: datetime,
        duration_minutes: int = 60,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        reminders: Optional[List[int]] = None,
        calendar_id: str = "primary"
    ) -> Optional[str]:
        """
        Create a calendar event.

        Args:
            summary: Event title
            start: Start datetime
            duration_minutes: Event duration in minutes
            description: Event description
            location: Event location
            attendees: List of attendee emails
            reminders: List of reminder times (minutes before)
            calendar_id: Calendar ID

        Returns:
            Event ID if successful

        Example:
            >>> event_id = calendar.create_event(
            ...     summary="Team Standup",
            ...     start=datetime(2024, 1, 15, 9, 0),
            ...     duration_minutes=30,
            ...     attendees=["team@example.com"],
            ...     reminders=[10, 5]
            ... )
        """
        if not self.service:
            logger.error("Not authenticated")
            return None

        try:
            end = start + timedelta(minutes=duration_minutes)

            event = {
                'summary': summary,
                'start': {
                    'dateTime': start.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end.isoformat(),
                    'timeZone': 'UTC',
                },
            }

            if description:
                event['description'] = description
            if location:
                event['location'] = location

            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]

            if reminders:
                event['reminders'] = {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': minutes}
                        for minutes in reminders
                    ]
                }

            result = self.service.events().insert(
                calendarId=calendar_id,
                body=event
            ).execute()

            logger.info(f"Event created: {result['id']}")
            return result['id']

        except Exception as e:
            logger.error(f"Failed to create event: {e}")
            return None

    def update_event(
        self,
        event_id: str,
        summary: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        description: Optional[str] = None,
        calendar_id: str = "primary"
    ) -> bool:
        """Update an existing event."""
        if not self.service:
            return False

        try:
            # Get existing event
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()

            # Update fields
            if summary:
                event['summary'] = summary
            if description:
                event['description'] = description
            if start:
                event['start'] = {'dateTime': start.isoformat(), 'timeZone': 'UTC'}
            if end:
                event['end'] = {'dateTime': end.isoformat(), 'timeZone': 'UTC'}

            # Update event
            self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event
            ).execute()

            logger.info(f"Event updated: {event_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to update event: {e}")
            return False

    def delete_event(self, event_id: str, calendar_id: str = "primary") -> bool:
        """Delete an event."""
        if not self.service:
            return False

        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            logger.info(f"Event deleted: {event_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete event: {e}")
            return False

    def find_free_slots(
        self,
        start_date: datetime,
        end_date: datetime,
        duration_minutes: int = 60,
        calendar_id: str = "primary"
    ) -> List[Dict[str, datetime]]:
        """
        Find free time slots.

        Args:
            start_date: Start of search range
            end_date: End of search range
            duration_minutes: Desired slot duration
            calendar_id: Calendar ID

        Returns:
            List of dicts with 'start' and 'end' datetimes

        Example:
            >>> slots = calendar.find_free_slots(
            ...     start_date=datetime.now(),
            ...     end_date=datetime.now() + timedelta(days=1),
            ...     duration_minutes=60
            ... )
            >>> for slot in slots[:3]:
            ...     print(f"{slot['start']} - {slot['end']}")
        """
        # Get all events in range
        events = self.get_events(start_date, end_date, calendar_id=calendar_id)

        # Sort by start time
        events.sort(key=lambda e: e.start)

        free_slots = []
        current_time = start_date

        for event in events:
            # Check if there's a gap before this event
            if current_time < event.start:
                gap_duration = (event.start - current_time).total_seconds() / 60

                if gap_duration >= duration_minutes:
                    free_slots.append({
                        'start': current_time,
                        'end': event.start
                    })

            # Move current time to end of this event
            if event.end > current_time:
                current_time = event.end

        # Check if there's time after last event
        if current_time < end_date:
            gap_duration = (end_date - current_time).total_seconds() / 60
            if gap_duration >= duration_minutes:
                free_slots.append({
                    'start': current_time,
                    'end': end_date
                })

        return free_slots

    def check_conflicts(
        self,
        start: datetime,
        end: datetime,
        calendar_id: str = "primary"
    ) -> List[CalendarEvent]:
        """
        Check for conflicting events.

        Args:
            start: Proposed event start
            end: Proposed event end
            calendar_id: Calendar ID

        Returns:
            List of conflicting events
        """
        events = self.get_events(start, end, calendar_id=calendar_id)

        conflicts = []
        for event in events:
            # Check if events overlap
            if not (event.end <= start or event.start >= end):
                conflicts.append(event)

        return conflicts

    def get_daily_summary(
        self,
        date: Optional[datetime] = None,
        calendar_id: str = "primary"
    ) -> Dict[str, Any]:
        """
        Get summary of day's events.

        Args:
            date: Date to summarize (defaults to today)
            calendar_id: Calendar ID

        Returns:
            Dictionary with day summary
        """
        if date is None:
            date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        start = date
        end = date + timedelta(days=1)

        events = self.get_events(start, end, calendar_id=calendar_id)

        total_duration = sum(
            (e.end - e.start).total_seconds() / 60
            for e in events
        )

        return {
            "date": date.date().isoformat(),
            "total_events": len(events),
            "total_duration_minutes": int(total_duration),
            "events": [
                {
                    "time": e.start.strftime("%H:%M"),
                    "summary": e.summary,
                    "duration": int((e.end - e.start).total_seconds() / 60)
                }
                for e in events
            ],
            "first_event": events[0].start.strftime("%H:%M") if events else None,
            "last_event": events[-1].end.strftime("%H:%M") if events else None
        }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Initialize
    calendar = CalendarIntegration()

    # Authenticate
    if calendar.authenticate():
        print("✅ Authenticated with Google Calendar")

        # Get today's events
        print("\n📅 Today's Events:")
        today_start = datetime.now().replace(hour=0, minute=0, second=0)
        today_end = today_start + timedelta(days=1)

        events = calendar.get_events(today_start, today_end)

        for event in events:
            print(f"  {event.start.strftime('%H:%M')} - {event.end.strftime('%H:%M')}: {event.summary}")
            if event.location:
                print(f"    Location: {event.location}")

        # Get daily summary
        print("\n📊 Daily Summary:")
        summary = calendar.get_daily_summary()
        print(f"  Total events: {summary['total_events']}")
        print(f"  Total time: {summary['total_duration_minutes']} minutes")

        # Find free slots tomorrow
        print("\n🕐 Free Slots Tomorrow:")
        tomorrow = datetime.now() + timedelta(days=1)
        tomorrow_start = tomorrow.replace(hour=9, minute=0, second=0)
        tomorrow_end = tomorrow.replace(hour=17, minute=0, second=0)

        free_slots = calendar.find_free_slots(
            tomorrow_start,
            tomorrow_end,
            duration_minutes=60
        )

        for i, slot in enumerate(free_slots[:5], 1):
            duration = int((slot['end'] - slot['start']).total_seconds() / 60)
            print(f"  {i}. {slot['start'].strftime('%H:%M')} - {slot['end'].strftime('%H:%M')} ({duration} min)")

    else:
        print("❌ Authentication failed")
