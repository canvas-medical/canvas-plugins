from pathlib import Path

import certifi
import stripe

import canvas_sdk.clients.third_party  # noqa: F401  (points stripe at certifi on import)

# emSign ECC Root CA - G3 issued the eight eMudhra intermediate CAs whose private keys are
# public; certifi 2026.10.19 dropped it. AAA Certificate Services, which cross-signed the same
# keys, left certifi earlier, and the assertion keeps it from coming back.
DISTRUSTED_ROOTS = ("emSign ECC Root CA - G3", "AAA Certificate Services")


def test_certifi_distrusts_the_roots_over_the_compromised_emudhra_intermediates() -> None:
    """Certifi trusts neither root over the compromised eMudhra intermediate CAs."""
    bundle = Path(certifi.where()).read_text()

    for root in DISTRUSTED_ROOTS:
        assert f"CN={root}" not in bundle, f"certifi trusts {root}; upgrade to certifi>=2026.10.19"


def test_stripe_clients_verify_tls_against_certifi() -> None:
    """StripeClient verifies against certifi, not the CA file bundled with the Stripe SDK."""
    assert stripe.ca_bundle_path == certifi.where()
