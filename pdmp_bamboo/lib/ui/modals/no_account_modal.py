"""
No Bamboo Health Account Modal.

Modal displayed when user doesn't have a Bamboo Health account configured.
"""

from canvas_sdk.effects import Effect
from logger import log
from pdmp_bamboo.lib.ui.modals.base_modal import BaseModal


class NoAccountModal(BaseModal):
    """Modal for users without Bamboo Health account."""

    def create_no_account_modal(self) -> Effect:
        """
        Create a modal for users without Bamboo Health account.

        Returns:
            LaunchModalEffect for the no account modal
        """
        log.info("NoAccountModal: Creating no Bamboo Health account modal")

        # Build modal content
        content = self._build_modal_content()

        # Create modal title
        title = "⚠️ Bamboo Health Account Required"

        return self.create_modal(title, content)

    def _build_modal_content(self) -> str:
        """Build the complete modal content."""
        from canvas_sdk.templates import render_to_string

        return render_to_string("templates/modals/no_account_modal_content.html", {})
