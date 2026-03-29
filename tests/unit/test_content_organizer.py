"""Unit tests for ContentOrganizer."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.organizers.base_organizer import BaseOrganizer
from src.organizers.content_organizer import ContentOrganizer


@pytest.fixture()
def mock_classifier() -> MagicMock:
    clf = MagicMock()
    clf.extract_company_names.return_value = []
    clf.extract_people_names.return_value = []
    clf.sanitize_company_name.side_effect = lambda name: name
    clf.classify_content.return_value = ("uncategorized", "other", None, [])
    return clf


@pytest.fixture()
def organizer(tmp_path: Path, mock_classifier: MagicMock) -> ContentOrganizer:
    return ContentOrganizer(base_path=tmp_path, content_classifier=mock_classifier)


# ------------------------------------------------------------------ #
# BaseOrganizer                                                        #
# ------------------------------------------------------------------ #

class TestBaseOrganizer:
    def test_stores_attrs(self, tmp_path: Path) -> None:
        base = BaseOrganizer(
            base_path=tmp_path,
            organize_by_date=True,
            organize_by_location=False,
            enable_cost_tracking=True,
            db_path="results/test.db",
        )
        assert base.base_path == tmp_path
        assert base.organize_by_date is True
        assert base.organize_by_location is False
        assert base.enable_cost_tracking is True
        assert base.db_path == "results/test.db"

    def test_expands_home(self) -> None:
        base = BaseOrganizer(base_path=Path("~/Documents"))
        assert "~" not in str(base.base_path)

    def test_defaults(self, tmp_path: Path) -> None:
        base = BaseOrganizer(base_path=tmp_path)
        assert base.organize_by_date is False
        assert base.organize_by_location is False
        assert base.enable_cost_tracking is False
        assert base.db_path is None


# ------------------------------------------------------------------ #
# classify_by_filepath                                                 #
# ------------------------------------------------------------------ #

class TestClassifyByFilepath:
    def test_python_file(self, organizer: ContentOrganizer) -> None:
        result = organizer.classify_by_filepath(Path("/some/project/script.py"))
        assert result is not None
        assert "Technical/Python" in result

    def test_typescript_file(self, organizer: ContentOrganizer) -> None:
        result = organizer.classify_by_filepath(Path("/home/user/src/index.ts"))
        assert result is not None
        assert "Technical/TypeScript" in result

    def test_exact_filename_match(self, organizer: ContentOrganizer) -> None:
        result = organizer.classify_by_filepath(Path("/project/Makefile"))
        assert result == "Technical/Build"

    def test_double_extension(self, organizer: ContentOrganizer) -> None:
        result = organizer.classify_by_filepath(Path("/logs/output.log.gz"))
        assert result == "Technical/Logs"

    def test_unknown_extension_returns_none(self, organizer: ContentOrganizer) -> None:
        result = organizer.classify_by_filepath(Path("/files/data.xyz123"))
        assert result is None

    def test_json_file(self, organizer: ContentOrganizer) -> None:
        result = organizer.classify_by_filepath(Path("/home/user/config/settings.json"))
        assert result is not None
        assert "Technical/Config" in result


# ------------------------------------------------------------------ #
# classify_game_asset                                                  #
# ------------------------------------------------------------------ #

class TestClassifyGameAsset:
    def test_ogg_game_music(self, organizer: ContentOrganizer) -> None:
        result = organizer.classify_game_asset(Path("/sounds/dungeon.ogg"))
        assert result == ('game_assets', 'music')

    def test_wav_game_sfx(self, organizer: ContentOrganizer) -> None:
        result = organizer.classify_game_asset(Path("/sounds/sword_attack.wav"))
        assert result == ('game_assets', 'audio')

    def test_png_sprite_frame(self, organizer: ContentOrganizer) -> None:
        result = organizer.classify_game_asset(Path("/sprites/frame_1.png"))
        assert result == ('game_assets', 'sprites')

    def test_ttf_font(self, organizer: ContentOrganizer) -> None:
        result = organizer.classify_game_asset(Path("/fonts/arial.ttf"))
        assert result == ('fonts', 'truetype')

    def test_otf_font(self, organizer: ContentOrganizer) -> None:
        result = organizer.classify_game_asset(Path("/fonts/comic.otf"))
        assert result == ('fonts', 'opentype')

    def test_regular_jpg_returns_none(self, organizer: ContentOrganizer) -> None:
        result = organizer.classify_game_asset(Path("/photos/vacation.jpg"))
        assert result is None

    def test_mp3_non_game_returns_none(self, organizer: ContentOrganizer) -> None:
        # "song.mp3" has extension .mp3 but no game keywords — classify_game_asset returns None
        result = organizer.classify_game_asset(Path("/music/vacation_song.mp3"))
        assert result is None


# ------------------------------------------------------------------ #
# should_skip_file                                                     #
# ------------------------------------------------------------------ #

class TestShouldSkipFile:
    def test_ds_store(self, organizer: ContentOrganizer) -> None:
        assert organizer.should_skip_file(Path("/docs/.DS_Store")) is True

    def test_thumbs_db(self, organizer: ContentOrganizer) -> None:
        assert organizer.should_skip_file(Path("/docs/Thumbs.db")) is True

    def test_hidden_file(self, organizer: ContentOrganizer) -> None:
        assert organizer.should_skip_file(Path("/docs/.hidden_file")) is True

    def test_gitignore_not_skipped(self, organizer: ContentOrganizer) -> None:
        assert organizer.should_skip_file(Path("/project/.gitignore")) is False

    def test_env_example_not_skipped(self, organizer: ContentOrganizer) -> None:
        assert organizer.should_skip_file(Path("/project/.env.example")) is False

    def test_pycache_dir(self, organizer: ContentOrganizer) -> None:
        assert organizer.should_skip_file(Path("/project/__pycache__/module.pyc")) is True

    def test_node_modules(self, organizer: ContentOrganizer) -> None:
        assert organizer.should_skip_file(Path("/project/node_modules/lib/index.js")) is True

    def test_regular_file_not_skipped(self, organizer: ContentOrganizer) -> None:
        assert organizer.should_skip_file(Path("/project/report.pdf")) is False


# ------------------------------------------------------------------ #
# get_destination_path                                                 #
# ------------------------------------------------------------------ #

class TestGetDestinationPath:
    def test_returns_path(self, organizer: ContentOrganizer, tmp_path: Path) -> None:
        result = organizer.get_destination_path(
            file_path=Path("/src/report.pdf"),
            category="financial",
            subcategory="invoices",
        )
        assert isinstance(result, Path)

    def test_uncategorized_fallback(self, organizer: ContentOrganizer, tmp_path: Path) -> None:
        result = organizer.get_destination_path(
            file_path=Path("/src/unknown.xyz"),
            category="unknown_cat",
            subcategory="unknown_sub",
        )
        assert "Uncategorized" in str(result)

    def test_organization_with_company(self, organizer: ContentOrganizer, tmp_path: Path) -> None:
        result = organizer.get_destination_path(
            file_path=Path("/src/invoice.pdf"),
            category="organization",
            subcategory="vendors",
            company_name="Acme Corp",
        )
        assert "Acme Corp" in str(result)
        assert "Organization" in str(result)

    def test_person_with_name(self, organizer: ContentOrganizer, tmp_path: Path) -> None:
        result = organizer.get_destination_path(
            file_path=Path("/src/resume.pdf"),
            category="person",
            subcategory="contacts",
            people_names=["Jane Doe"],
        )
        assert "Jane Doe" in str(result)
        assert "Person" in str(result)

    def test_person_without_name_uses_unknown(self, organizer: ContentOrganizer, tmp_path: Path) -> None:
        result = organizer.get_destination_path(
            file_path=Path("/src/resume.pdf"),
            category="person",
            subcategory="contacts",
        )
        assert "Unknown" in str(result)

    def test_filepath_category_uses_subcategory_as_path(
        self, organizer: ContentOrganizer, tmp_path: Path
    ) -> None:
        result = organizer.get_destination_path(
            file_path=Path("/src/script.py"),
            category="filepath",
            subcategory="Technical/Python/MyProject",
        )
        assert "Technical/Python/MyProject" in str(result)

    def test_media_photos_travel(self, organizer: ContentOrganizer, tmp_path: Path) -> None:
        result = organizer.get_destination_path(
            file_path=Path("/photos/img.jpg"),
            category="media",
            subcategory="photos_travel",
        )
        assert "Travel" in str(result)

    def test_date_organization_overrides_path(
        self, tmp_path: Path, mock_classifier: MagicMock
    ) -> None:
        org = ContentOrganizer(
            base_path=tmp_path,
            content_classifier=mock_classifier,
            organize_by_date=True,
        )
        result = org.get_destination_path(
            file_path=Path("/photos/img.jpg"),
            category="media",
            subcategory="photos_other",
            image_metadata={"year": 2024, "month": 6},
        )
        assert "Photos/2024/06" in str(result)


# ------------------------------------------------------------------ #
# classify_by_filename_patterns                                        #
# ------------------------------------------------------------------ #

class TestClassifyByFilenamePatterns:
    def test_log_file(self, organizer: ContentOrganizer) -> None:
        result = organizer.classify_by_filename_patterns(Path("/logs/system.log"))
        assert result is not None
        assert result[0] == 'technical'
        assert result[1] == 'logs'

    def test_timestamped_duplicate_skipped(self, organizer: ContentOrganizer) -> None:
        result = organizer.classify_by_filename_patterns(
            Path("/docs/report_20241201_123456.pdf")
        )
        assert result is not None
        assert result[0] == 'skip'

    def test_screenshot_detected(self, organizer: ContentOrganizer) -> None:
        result = organizer.classify_by_filename_patterns(Path("/photos/screenshot_2024.png"))
        assert result is not None
        assert 'screenshot' in result[1]

    def test_resume_pdf_with_name(self, organizer: ContentOrganizer) -> None:
        result = organizer.classify_by_filename_patterns(
            Path("/docs/Alyshia_Ledlie_Resume.pdf")
        )
        assert result is not None
        assert result[0] == 'person'
        assert len(result[3]) > 0  # people_names

    def test_nda_document(self, organizer: ContentOrganizer) -> None:
        result = organizer.classify_by_filename_patterns(Path("/docs/nda_2024.pdf"))
        assert result is not None
        assert result[0] == 'legal'
        assert result[1] == 'contracts'

    def test_unknown_returns_none(self, organizer: ContentOrganizer) -> None:
        result = organizer.classify_by_filename_patterns(Path("/random/xyzxyz_unique_file.pdf"))
        assert result is None
