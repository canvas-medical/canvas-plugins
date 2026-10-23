import certifi
import stripe
from stripe import StripeClient

# The Stripe SDK verifies TLS against its own bundled CA file, which trusts emSign ECC Root
# CA - G3, the root over the compromised eMudhra intermediate CAs. Every StripeClient a plugin
# builds reads this module setting per request, so it verifies against certifi instead.
stripe.ca_bundle_path = certifi.where()

__all__ = __exports__ = ("StripeClient",)
