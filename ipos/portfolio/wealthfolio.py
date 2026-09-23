"""Truthful boundary for the not-yet-connected Wealthfolio product.

E01 deliberately removes the previous local JSON and dictionary functions
that were labeled as Wealthfolio backup/MCP behavior without invoking the
product. E02 will replace this boundary only after exercising a supported
native Wealthfolio import/export interface.
"""

INTEGRATION_STATUS = "NOT_CONNECTED"


class WealthfolioIntegrationUnavailable(RuntimeError):
    """Raised when code attempts to use Wealthfolio before native proof."""


def require_real_wealthfolio() -> None:
    """Fail closed instead of substituting a local Wealthfolio facade."""
    raise WealthfolioIntegrationUnavailable(
        "Wealthfolio is not connected; complete E02 native product validation first"
    )
