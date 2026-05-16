# SPDX-FileCopyrightText: 2026 Subramania Raja <dhanpraja231@gmail.com>
# SPDX-FileCopyrightText: 2026 Hari Srinivasan <harisrini21@gmail.com>
# SPDX-FileCopyrightText: 2026 Shaan Narendran <shaannaren06@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-only

"""Insights plugin loader.

Controlled by the INSIGHTS_ENABLED env var (defaults to True when
DEPLOYMENT_MODE=enterprise). Set INSIGHTS_ENABLED=false to disable explicitly.

If enabled but the ee/ package is missing the import will fail loudly at
startup rather than silently returning 402s.
"""

from config import settings

INSIGHTS_AVAILABLE: bool = settings.INSIGHTS_AVAILABLE

if INSIGHTS_AVAILABLE:
    from ee.observal_insights import generate_report_content as _generate
    from ee.observal_insights import render_report_html as _render
else:
    _generate = None  # type: ignore[assignment]
    _render = None  # type: ignore[assignment]


def _not_available():
    raise RuntimeError("Insights is not enabled. Set INSIGHTS_ENABLED=true (or DEPLOYMENT_MODE=enterprise).")


async def generate_report_content(*args, **kwargs):
    if not INSIGHTS_AVAILABLE:
        _not_available()
    return await _generate(*args, **kwargs)  # type: ignore[misc]


def render_report_html(*args, **kwargs):
    if not INSIGHTS_AVAILABLE:
        _not_available()
    return _render(*args, **kwargs)  # type: ignore[misc]


def configure_insights():
    """Wire up dependencies from the host app into the insights package.

    Called once at server startup. No-op if not enabled.
    """
    if not INSIGHTS_AVAILABLE:
        return

    from database import async_session
    from ee.observal_insights import configure
    from models.insight_meta_cache import InsightMetaCache
    from models.insight_session_facets import InsightSessionFacets
    from models.insight_session_meta import InsightSessionMeta
    from services.clickhouse import _query
    from services.eval.eval_service import call_eval_model

    configure(
        settings=settings,
        query_fn=_query,
        call_model_fn=call_eval_model,
        db_session_factory=async_session,
        meta_model=InsightSessionMeta,
        facets_model=InsightSessionFacets,
        meta_cache_model=InsightMetaCache,
    )
