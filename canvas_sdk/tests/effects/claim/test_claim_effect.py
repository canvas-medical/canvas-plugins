from collections.abc import Generator
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.claim import BannerAlertIntent, ClaimEffect


@pytest.fixture
def mock_db_queries() -> Generator[dict[str, MagicMock], None, None]:
    """Mock all database queries to return True/exist by default."""
    with patch("canvas_sdk.effects.claim.claim_banner_alert.Claim.objects") as mock_claim:
        mock_claim.filter.return_value.exists.return_value = True
        yield {"claim": mock_claim}


class TestClaimEffect:
    """Tests for ClaimEffect class."""

    def test_claim_effect_creation_with_uuid(self) -> None:
        """Test creating a ClaimEffect with a UUID."""
        claim_id = uuid4()
        effect = ClaimEffect(claim_id=claim_id)
        assert effect.claim_id == claim_id

    def test_claim_effect_creation_with_string(self) -> None:
        """Test creating a ClaimEffect with a string ID."""
        claim_id = "test-claim-id"
        effect = ClaimEffect(claim_id=claim_id)
        assert effect.claim_id == claim_id


class TestAddBanner:
    """Tests for ClaimEffect.add_banner method."""

    def test_add_banner_with_all_fields(self, mock_db_queries: dict[str, MagicMock]) -> None:
        """Test add_banner with all fields including optional href."""
        claim_id = "test-claim-id"
        effect = ClaimEffect(claim_id=claim_id)

        result = effect.add_banner(
            key="test-key",
            narrative="Test banner message",
            intent=BannerAlertIntent.INFO,
            href="https://example.com",
        )

        assert isinstance(result, Effect)
        assert result.type == EffectType.ADD_CLAIM_BANNER_ALERT
        assert '"claim_id": "test-claim-id"' in result.payload
        assert '"key": "test-key"' in result.payload
        assert '"narrative": "Test banner message"' in result.payload
        assert '"intent": "info"' in result.payload
        assert '"href": "https://example.com"' in result.payload

    def test_add_banner_without_href(self, mock_db_queries: dict[str, MagicMock]) -> None:
        """Test add_banner without the optional href."""
        claim_id = "test-claim-id"
        effect = ClaimEffect(claim_id=claim_id)

        result = effect.add_banner(
            key="test-key",
            narrative="Test banner message",
            intent=BannerAlertIntent.WARNING,
        )

        assert isinstance(result, Effect)
        assert result.type == EffectType.ADD_CLAIM_BANNER_ALERT
        assert '"href": null' in result.payload

    def test_add_banner_with_info_intent(self, mock_db_queries: dict[str, MagicMock]) -> None:
        """Test add_banner with INFO intent."""
        effect = ClaimEffect(claim_id="claim-id")
        result = effect.add_banner(key="key", narrative="message", intent=BannerAlertIntent.INFO)
        assert '"intent": "info"' in result.payload

    def test_add_banner_with_warning_intent(self, mock_db_queries: dict[str, MagicMock]) -> None:
        """Test add_banner with WARNING intent."""
        effect = ClaimEffect(claim_id="claim-id")
        result = effect.add_banner(key="key", narrative="message", intent=BannerAlertIntent.WARNING)
        assert '"intent": "warning"' in result.payload

    def test_add_banner_with_alert_intent(self, mock_db_queries: dict[str, MagicMock]) -> None:
        """Test add_banner with ALERT intent."""
        effect = ClaimEffect(claim_id="claim-id")
        result = effect.add_banner(key="key", narrative="message", intent=BannerAlertIntent.ALERT)
        assert '"intent": "alert"' in result.payload

    def test_add_banner_with_uuid_claim_id(self, mock_db_queries: dict[str, MagicMock]) -> None:
        """Test add_banner converts UUID to string in payload."""
        claim_id = uuid4()
        effect = ClaimEffect(claim_id=claim_id)

        result = effect.add_banner(
            key="test-key",
            narrative="Test message",
            intent=BannerAlertIntent.INFO,
        )

        assert f'"claim_id": "{claim_id}"' in result.payload

    def test_add_banner_requires_existing_claim(
        self, mock_db_queries: dict[str, MagicMock]
    ) -> None:
        """Test that add_banner validates claim exists."""
        mock_db_queries["claim"].filter.return_value.exists.return_value = False
        effect = ClaimEffect(claim_id="nonexistent-claim")

        with pytest.raises(ValidationError) as exc_info:
            effect.add_banner(
                key="test-key",
                narrative="Test message",
                intent=BannerAlertIntent.INFO,
            )

        err_msg = repr(exc_info.value)
        assert "Claim with id nonexistent-claim does not exist" in err_msg

    def test_add_banner_narrative_max_length(self, mock_db_queries: dict[str, MagicMock]) -> None:
        """Test that narrative has a maximum length of 90 characters."""
        effect = ClaimEffect(claim_id="claim-id")
        long_narrative = "x" * 91

        with pytest.raises(ValidationError) as exc_info:
            effect.add_banner(
                key="test-key",
                narrative=long_narrative,
                intent=BannerAlertIntent.INFO,
            )

        err_msg = repr(exc_info.value)
        assert "String should have at most 90 characters" in err_msg

    def test_add_banner_narrative_at_max_length(
        self, mock_db_queries: dict[str, MagicMock]
    ) -> None:
        """Test that narrative at exactly 90 characters is valid."""
        effect = ClaimEffect(claim_id="claim-id")
        max_narrative = "x" * 90

        result = effect.add_banner(
            key="test-key",
            narrative=max_narrative,
            intent=BannerAlertIntent.INFO,
        )

        assert isinstance(result, Effect)
        assert max_narrative in result.payload


class TestRemoveBanner:
    """Tests for ClaimEffect.remove_banner method."""

    def test_remove_banner(self, mock_db_queries: dict[str, MagicMock]) -> None:
        """Test remove_banner returns correct effect."""
        claim_id = "test-claim-id"
        effect = ClaimEffect(claim_id=claim_id)

        result = effect.remove_banner(key="test-key")

        assert isinstance(result, Effect)
        assert result.type == EffectType.REMOVE_CLAIM_BANNER_ALERT
        assert '"claim_id": "test-claim-id"' in result.payload
        assert '"key": "test-key"' in result.payload

    def test_remove_banner_with_uuid_claim_id(self, mock_db_queries: dict[str, MagicMock]) -> None:
        """Test remove_banner converts UUID to string in payload."""
        claim_id = uuid4()
        effect = ClaimEffect(claim_id=claim_id)

        result = effect.remove_banner(key="test-key")

        assert f'"claim_id": "{claim_id}"' in result.payload

    def test_remove_banner_does_not_validate_claim_exists(
        self, mock_db_queries: dict[str, MagicMock]
    ) -> None:
        """Test that remove_banner does not check if claim exists."""
        mock_db_queries["claim"].filter.return_value.exists.return_value = False
        effect = ClaimEffect(claim_id="nonexistent-claim")

        # Should not raise - remove_banner doesn't validate claim existence
        result = effect.remove_banner(key="test-key")

        assert isinstance(result, Effect)
        assert result.type == EffectType.REMOVE_CLAIM_BANNER_ALERT


class TestBannerAlertIntent:
    """Tests for BannerAlertIntent enum."""

    def test_banner_alert_intent_values(self) -> None:
        """Test that BannerAlertIntent has correct values."""
        assert BannerAlertIntent.INFO.value == "info"
        assert BannerAlertIntent.WARNING.value == "warning"
        assert BannerAlertIntent.ALERT.value == "alert"

    def test_banner_alert_intent_members(self) -> None:
        """Test that BannerAlertIntent has exactly three members."""
        members = list(BannerAlertIntent)
        assert len(members) == 3
        assert BannerAlertIntent.INFO in members
        assert BannerAlertIntent.WARNING in members
        assert BannerAlertIntent.ALERT in members
