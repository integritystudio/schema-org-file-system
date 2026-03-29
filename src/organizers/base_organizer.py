"""Base organizer with shared configuration."""

from pathlib import Path


class BaseOrganizer:
    """Stores shared configuration for all organizer subclasses."""

    def __init__(
        self,
        base_path: Path,
        organize_by_date: bool = False,
        organize_by_location: bool = False,
        enable_cost_tracking: bool = False,
        db_path: str | None = None,
    ) -> None:
        self.base_path = Path(base_path).expanduser()
        self.organize_by_date = organize_by_date
        self.organize_by_location = organize_by_location
        self.enable_cost_tracking = enable_cost_tracking
        self.db_path = db_path
