"""Data models fow view events"""
from faust import Record
from typing import List, Any, Iterable
from datetime import datetime
from faust.exceptions import ValidationError
from faust.models import FieldDescriptor


class ChoiceField(FieldDescriptor[str]):
    """A FieldDescriptor that checks for limited choices"""

    def __init__(self, choices: List[str], **kwargs: Any) -> None:
        """Initialise ChoiceField

        Args:
            choices: List of choices that should be possible.
            **kwargs:
        """
        self.choices = choices

        super().__init__(choices=choices, **kwargs)

    def validate(self, value: str) -> Iterable[ValidationError]:
        """Validate if the value is in the choices.

        Args:
            value: The value to check.

        Returns:
            Nothing if correct. Validation error if not correct.
        """
        if value not in self.choices:
            choices = ', '.join(self.choices)
            yield self.validation_error(
                f'{self.field} must be one of {choices}')


class ViewEvent(Record,  serializer='json', isodates=True):
    """Movel for a view event."""
    WAYPOINT = 'waypoint'
    STREAMSTART = 'streamstart'
    STREAMSTOP = 'streamstop'
    STREAMEND = 'streamend'

    VALID_EVENTS = [WAYPOINT, STREAMSTART, STREAMSTOP, STREAMEND]

    MediaId: int
    UserId: int
    Timestamp: int
    DateTime: datetime
    EventType: str = ChoiceField(VALID_EVENTS)


class MediaStats(Record):
    """Model for Media statistics."""
    view_time: int = 0
    starts: int = 0
    stops: int = 0
    ends: int = 0
    user_views: dict = {}
