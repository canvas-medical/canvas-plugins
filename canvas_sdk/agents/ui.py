"""One stylesheet for agent plugin pages, so every agent looks the same in the chart.

Components follow the Studio onboarding chat; neutrals, cards and the Lato font follow
the chart. Purple marks what the agent made, blue what the reader can act on, and
green, amber and red mark status beside a word. Every text color clears WCAG AA.

:data:`AGENT_UI_CSS` is marked safe, so a template outputs it intact::

    render_to_string("templates/chat.html", {"agent_ui_css": AGENT_UI_CSS})

    <style>{{ agent_ui_css }}</style>
    <div class="adk-panel">...</div>

:data:`TOKENS` holds the same values for code that draws its own colors, such as a chart.
"""

from collections.abc import Mapping
from types import MappingProxyType

from django.utils.safestring import SafeString, mark_safe

# The chart loads Lato from this URL on every page, so the pane adds no new party.
LATO_IMPORT = (
    "https://fonts.googleapis.com/css?family=Lato:400,700,400italic,700italic&subset=latin"
)

TOKENS: Mapping[str, str] = MappingProxyType(
    {
        "font": "Lato, 'Helvetica Neue', Arial, Helvetica, sans-serif",
        "mono": "'SF Mono', Menlo, Consolas, monospace",
        "font-size": "14px",
        "font-size-sm": "12.5px",
        "font-size-xs": "11px",
        "radius-sm": "8px",
        "radius": "12px",
        "radius-pill": "999px",
        "bg": "#ffffff",
        "bg-secondary": "#f9fafb",
        "bg-elevated": "#ffffff",
        "bg-hover": "#f3f4f6",
        "border": "#e5e7eb",
        "input-bg": "#ffffff",
        "input-border": "#6a7282",
        "text": "#101828",
        "text-secondary": "#4a5565",
        "agent": "#8041d0",
        "agent-fg": "#ffffff",
        "agent-soft": "#f0e8f9",
        "action": "#155dfc",
        "action-fg": "#ffffff",
        "action-soft": "#e8efff",
        "good": "#047857",
        "warning": "#8a5a00",
        "warning-soft": "#f3eee6",
        "critical": "#b42323",
        "critical-soft": "#f8e9e9",
        "shadow": "0 1px 3px rgb(0 0 0 / 10%), 0 1px 2px -1px rgb(0 0 0 / 10%)",
        "shadow-raised": "0 4px 12px rgb(0 0 0 / 10%), 0 2px 4px -2px rgb(0 0 0 / 10%)",
    }
)

_COMPONENTS = """
.adk-panel { font-family: var(--adk-font); font-size: var(--adk-font-size); line-height: 1.5;
  color: var(--adk-text); background: var(--adk-bg); display: flex; flex-direction: column;
  min-height: 100%; container-type: inline-size; }
.adk-panel *, .adk-panel *::before, .adk-panel *::after { box-sizing: border-box; }
.adk-panel button, .adk-panel input, .adk-panel textarea, .adk-panel select { font-family: inherit; }
.adk-panel a { color: var(--adk-action); text-decoration: none; }
.adk-panel a:hover { text-decoration: underline; }
.adk-panel :focus-visible { outline: 2px solid var(--adk-action); outline-offset: 2px; }
.adk-panel svg { flex-shrink: 0; }

.adk-header { padding: 14px 16px 10px; display: flex; flex-direction: column; gap: 10px;
  border-bottom: 1px solid var(--adk-border); }
.adk-title { font-size: calc(var(--adk-font-size) + 2px); font-weight: 700; }
.adk-tabs { display: inline-flex; gap: 2px; padding: 3px; align-self: flex-start;
  border: 1px solid var(--adk-border); border-radius: var(--adk-radius-sm);
  background: var(--adk-bg-secondary); }
.adk-tab { border: 0; background: transparent; color: var(--adk-text-secondary); cursor: pointer;
  font-size: var(--adk-font-size-sm); font-weight: 700; padding: 5px 12px;
  border-radius: calc(var(--adk-radius-sm) - 3px); }
.adk-tab[aria-selected="true"] { background: var(--adk-bg); color: var(--adk-text);
  box-shadow: var(--adk-shadow); }
.adk-body { flex: 1; padding: 12px 12px 8px; display: flex; flex-direction: column; gap: 6px;
  overflow-y: auto; }
.adk-section-label { display: flex; align-items: center; gap: 6px; margin: 12px 0 6px;
  font-size: var(--adk-font-size-xs); font-weight: 700; letter-spacing: .05em;
  text-transform: uppercase; color: var(--adk-text-secondary); }
.adk-count { font-variant-numeric: tabular-nums; letter-spacing: 0; text-transform: none; }

/* Transcript rows: an icon column and a body. The agent's dot is purple; a person's
   row shows their initials in --adk-author, set inline per person. */
.adk-msg { display: flex; gap: 14px; align-items: flex-start; padding: 8px 12px; border-radius: 6px; }
.adk-msg-icon { flex-shrink: 0; width: 20px; display: flex; justify-content: center;
  padding-top: 3px; font-size: 11px; line-height: 1.5; user-select: none; }
.adk-msg-body { flex: 1; min-width: 0; }
.adk-msg-user { background: var(--adk-bg-secondary); white-space: pre-wrap; }
.adk-msg-agent .adk-msg-icon { color: var(--adk-agent); }
.adk-msg-agent + .adk-msg-agent .adk-msg-icon { visibility: hidden; }
.adk-msg-agent p { margin: 0 0 8px; }
.adk-msg-agent p:last-child { margin-bottom: 0; }
.adk-msg-agent h4 { margin: 10px 0 4px; font-size: var(--adk-font-size); font-weight: 700; }
.adk-msg-agent h4:first-child { margin-top: 0; }
.adk-msg-agent ul, .adk-msg-agent ol { margin: 0 0 6px 18px; padding: 0; }
.adk-msg-agent code { font-family: var(--adk-mono); font-size: var(--adk-font-size-sm); }
.adk-author { width: 18px; height: 18px; margin-top: 1px; padding: 0; border-radius: 50%;
  align-items: center; font-size: 9px; font-weight: 700; color: #ffffff;
  background: var(--adk-author, var(--adk-text-secondary)); }
.adk-answer { font-size: calc(var(--adk-font-size) + .5px); }

.adk-cite { display: inline-flex; align-items: center; justify-content: center; min-width: 17px;
  height: 17px; padding: 0 4px; margin: 0 1px; border: 0; border-radius: 5px; cursor: pointer;
  vertical-align: 1px; font-size: var(--adk-font-size-xs); font-weight: 700; line-height: 1;
  font-variant-numeric: tabular-nums; color: var(--adk-agent); background: var(--adk-agent-soft); }
.adk-cite:hover, .adk-cite[aria-current="true"] { color: var(--adk-agent-fg); background: var(--adk-agent); }

/* Record card: one card for a keyword result and for a reference an answer cites. */
.adk-records { display: flex; flex-direction: column; gap: 8px; }
.adk-record { flex-shrink: 0; overflow: hidden; border: 1px solid var(--adk-border);
  border-radius: var(--adk-radius); background: var(--adk-bg-elevated); box-shadow: var(--adk-shadow); }
.adk-record[aria-current="true"] { border-color: var(--adk-agent);
  box-shadow: 0 0 0 3px var(--adk-agent-soft); }
.adk-record-head { display: flex; align-items: center; gap: 8px; padding: 10px 12px 0; }
.adk-kind { flex-shrink: 0; padding: 1px 7px; border-radius: var(--adk-radius-pill);
  font-size: var(--adk-font-size-xs); font-weight: 700; letter-spacing: .03em; text-transform: uppercase;
  color: var(--adk-text-secondary); background: var(--adk-bg-hover); }
.adk-record-title { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  font-weight: 700; }
.adk-record-state { margin-left: auto; flex-shrink: 0; font-size: var(--adk-font-size-xs);
  font-weight: 700; color: var(--adk-text-secondary); }
.adk-record-summary { padding: 4px 12px 0; }
.adk-record-why { padding: 4px 12px 0; font-size: var(--adk-font-size-sm); color: var(--adk-text-secondary); }
.adk-record-details { display: grid; grid-template-columns: max-content 1fr; gap: 2px 12px;
  margin: 6px 12px 0; font-size: var(--adk-font-size-sm); }
.adk-record-details dt { color: var(--adk-text-secondary); }
.adk-record-details dd { margin: 0; }
.adk-record-foot { display: flex; align-items: center; gap: 8px; padding: 8px 12px 10px;
  font-size: var(--adk-font-size-sm); color: var(--adk-text-secondary); }
.adk-record-foot .adk-open { margin-left: auto; }
.adk-good { color: var(--adk-good); }
.adk-warning { color: var(--adk-warning); }
.adk-critical { color: var(--adk-critical); }

.adk-btn { display: inline-flex; align-items: center; gap: 6px; height: 32px; padding: 0 13px;
  border: 1px solid var(--adk-border); border-radius: var(--adk-radius-sm); cursor: pointer;
  background: var(--adk-bg); color: var(--adk-text); font-size: var(--adk-font-size-sm); font-weight: 700; }
.adk-btn:hover { border-color: var(--adk-text-secondary); }
.adk-btn:disabled { opacity: .5; cursor: not-allowed; }
.adk-btn-primary { background: var(--adk-action); border-color: var(--adk-action); color: var(--adk-action-fg); }
.adk-btn-sm { height: 26px; padding: 0 9px; font-size: var(--adk-font-size-xs); }
.adk-open { display: inline-flex; align-items: center; gap: 3px; padding: 3px 8px; border-radius: 6px;
  border: 1px solid transparent; background: none; cursor: pointer; color: var(--adk-action);
  font-size: var(--adk-font-size-sm); font-weight: 700; }
.adk-open:hover { border-color: var(--adk-action); background: var(--adk-action-soft); }
.adk-link-btn { border: 0; background: none; padding: 0; cursor: pointer; font-size: inherit;
  font-weight: 700; color: var(--adk-text-secondary); }
.adk-link-btn:hover { color: var(--adk-text); }
.adk-icon-btn { display: inline-flex; align-items: center; justify-content: center; width: 28px;
  height: 28px; border: 0; border-radius: 6px; background: none; cursor: pointer;
  color: var(--adk-text-secondary); }
.adk-icon-btn:hover { background: var(--adk-bg-hover); color: var(--adk-text); }
.adk-icon-btn[aria-pressed="true"] { color: var(--adk-action); background: var(--adk-action-soft); }
.adk-icon-btn svg { width: 16px; height: 16px; }
.adk-reply-actions { display: flex; align-items: center; gap: 2px; margin: 6px 0 0 -6px; }
.adk-feedback-reason { display: flex; gap: 6px; margin-top: 6px; }
.adk-feedback-reason .adk-text-input { flex: 1; }

.adk-chips { display: flex; flex-wrap: wrap; gap: 6px; }
.adk-chip { padding: 5px 12px; border-radius: var(--adk-radius-pill); cursor: pointer; background: transparent;
  border: 1px dashed var(--adk-text-secondary); color: var(--adk-text-secondary); font-size: var(--adk-font-size-sm); }
.adk-chip:hover { color: var(--adk-action); border: 1px solid var(--adk-action); background: var(--adk-action-soft); }

.adk-greet { padding: 8px 4px 4px; }
.adk-greet-title { margin-bottom: 4px; font-size: calc(var(--adk-font-size) + 6px); font-weight: 700; }
.adk-greet-sub { margin-bottom: 14px; color: var(--adk-text-secondary); }
.adk-starters { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.adk-starter { display: flex; flex-direction: column; gap: 6px; padding: 11px 12px; text-align: left;
  cursor: pointer; color: var(--adk-text); background: var(--adk-bg-elevated); border: 1px solid var(--adk-border);
  border-radius: var(--adk-radius); box-shadow: var(--adk-shadow); transition: border-color .14s, box-shadow .14s; }
.adk-starter:hover { border-color: var(--adk-action); box-shadow: var(--adk-shadow-raised); }
.adk-starter-top { display: flex; align-items: center; gap: 9px; font-size: var(--adk-font-size-sm); font-weight: 700; }
.adk-starter-desc { font-size: var(--adk-font-size-xs); color: var(--adk-text-secondary); }
.adk-ico { display: flex; align-items: center; justify-content: center; flex-shrink: 0; width: 26px;
  height: 26px; border-radius: 8px; color: var(--adk-text-secondary); background: var(--adk-bg-hover); }
.adk-ico svg { width: 15px; height: 15px; }

/* Run status. The thinking dot and a running step pulse in the agent's purple. */
.adk-thinking { display: flex; align-items: center; gap: 14px; padding: 8px 12px;
  font-size: var(--adk-font-size-sm); color: var(--adk-text-secondary); font-variant-numeric: tabular-nums; }
.adk-thinking-dot { width: 20px; display: flex; justify-content: center; }
.adk-thinking-dot::before, .adk-steps li.adk-running::before { content: ""; width: 8px; height: 8px;
  border-radius: 50%; background: var(--adk-agent); animation: adk-pulse 1.2s ease-in-out infinite; }
.adk-steps li.adk-running::before { width: 6px; height: 6px; }
.adk-steps { margin: 2px 0 0; padding: 0 0 0 58px; list-style: none; font-size: var(--adk-font-size-sm);
  color: var(--adk-text-secondary); }
.adk-steps li { display: flex; align-items: center; gap: 6px; padding: 1px 0; }
.adk-steps li.adk-done::before { content: "\\2713"; color: var(--adk-good); font-size: 11px; }
@keyframes adk-pulse { 0%, 100% { opacity: .35; transform: scale(.8); } 50% { opacity: 1; transform: scale(1); } }
@media (prefers-reduced-motion: reduce) {
  .adk-thinking-dot::before, .adk-steps li.adk-running::before { animation: none; }
}
.adk-status { display: flex; gap: 11px; align-items: flex-start; padding: 12px 14px;
  border: 1px solid var(--adk-border); border-radius: var(--adk-radius); background: var(--adk-bg-elevated); }
.adk-status-title { font-weight: 700; }
.adk-status-sub { margin-top: 1px; font-size: var(--adk-font-size-sm); color: var(--adk-text-secondary); }
.adk-status-actions { display: flex; gap: 8px; margin-top: 10px; }
.adk-status.adk-critical { color: var(--adk-text); border-color: var(--adk-critical); }
.adk-status.adk-critical .adk-ico { color: var(--adk-critical); background: var(--adk-critical-soft); }
.adk-status.adk-warning { color: var(--adk-text); }
.adk-status.adk-warning .adk-ico { color: var(--adk-warning); background: var(--adk-warning-soft); }

/* A note the agent wrote, such as a draft to review before it is used. */
.adk-note { display: flex; gap: 10px; padding: 10px 12px; border-radius: var(--adk-radius-sm);
  font-size: var(--adk-font-size-sm); border: 1px solid var(--adk-border); background: var(--adk-bg-secondary); }
.adk-note-agent { border-color: var(--adk-agent); background: var(--adk-agent-soft); }

.adk-sources { margin-top: 8px; }
.adk-sources-head { display: inline-flex; align-items: center; gap: 6px; padding: 2px 0; border: 0;
  background: none; cursor: pointer; color: var(--adk-text-secondary); font-size: var(--adk-font-size-sm); }
.adk-sources-head:hover { color: var(--adk-text); }
.adk-sources-chev { transition: transform .15s; }
.adk-sources[aria-expanded="true"] .adk-sources-chev { transform: rotate(90deg); }
.adk-sources .adk-records { margin-top: 6px; }

.adk-actions { display: flex; gap: 5px; padding: 8px 16px 0; overflow-x: auto; }
.adk-action { display: inline-flex; align-items: center; gap: 6px; flex-shrink: 0; height: 28px;
  padding: 0 9px; border-radius: var(--adk-radius-pill); border: 1px solid var(--adk-border); cursor: pointer;
  background: var(--adk-bg-elevated); color: var(--adk-text); font-size: var(--adk-font-size-sm);
  font-weight: 700; box-shadow: var(--adk-shadow); }
.adk-action:hover { border-color: var(--adk-action); }
.adk-action svg { width: 14px; height: 14px; color: var(--adk-text-secondary); }

.adk-input-area { display: flex; align-items: flex-end; gap: 8px; padding: 10px 16px 6px; }
.adk-input-wrap { flex: 1; display: flex; align-items: flex-end; border: 1px solid var(--adk-input-border);
  border-radius: 10px; background: var(--adk-input-bg); }
.adk-input-wrap:focus-within { border-color: var(--adk-action); }
.adk-input { flex: 1; min-height: 38px; max-height: 140px; padding: 9px 12px; resize: none; border: 0;
  outline: 0; background: transparent; color: var(--adk-text); font-size: var(--adk-font-size); }
.adk-input::placeholder { color: var(--adk-text-secondary); }
.adk-send { display: flex; align-items: center; justify-content: center; flex-shrink: 0; width: 38px;
  height: 38px; border: 0; border-radius: 10px; cursor: pointer; background: var(--adk-action); color: var(--adk-action-fg); }
.adk-send:disabled { opacity: .45; cursor: not-allowed; }
.adk-send svg { width: 17px; height: 17px; }
.adk-disclaimer { display: flex; justify-content: space-between; gap: 8px; padding: 0 16px 10px;
  font-size: var(--adk-font-size-xs); color: var(--adk-text-secondary); }

.adk-search-row { display: flex; gap: 8px; }
.adk-field { flex: 1; display: flex; align-items: center; gap: 8px; height: 36px; padding: 0 10px;
  border: 1px solid var(--adk-input-border); border-radius: var(--adk-radius-sm);
  background: var(--adk-input-bg); color: var(--adk-text-secondary); }
.adk-field:focus-within { border-color: var(--adk-action); }
.adk-field input { flex: 1; min-width: 0; border: 0; outline: 0; background: transparent; color: var(--adk-text); }
.adk-field svg { width: 16px; height: 16px; }
.adk-text-input { height: 32px; padding: 0 9px; border: 1px solid var(--adk-input-border);
  border-radius: var(--adk-radius-sm); background: var(--adk-input-bg); color: var(--adk-text);
  font-size: var(--adk-font-size-sm); }
.adk-badge { display: inline-flex; align-items: center; justify-content: center; min-width: 17px;
  height: 17px; padding: 0 5px; border-radius: var(--adk-radius-pill); font-size: 10.5px; font-weight: 700;
  background: var(--adk-action); color: var(--adk-action-fg); }
.adk-filters { display: flex; flex-direction: column; gap: 10px; padding: 10px 12px 12px;
  border: 1px solid var(--adk-border); border-radius: var(--adk-radius); background: var(--adk-bg-elevated); }
.adk-filter-label { display: block; margin-bottom: 5px; font-size: var(--adk-font-size-xs); font-weight: 700;
  letter-spacing: .04em; text-transform: uppercase; color: var(--adk-text-secondary); }
.adk-filter-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.adk-toggle-chip { padding: 3px 10px; border-radius: var(--adk-radius-pill); border: 1px solid var(--adk-border);
  cursor: pointer; background: var(--adk-bg); color: var(--adk-text-secondary); font-size: var(--adk-font-size-sm); }
.adk-toggle-chip[aria-pressed="true"] { font-weight: 700; color: var(--adk-action);
  border-color: var(--adk-action); background: var(--adk-action-soft); }
.adk-results-bar { display: flex; align-items: center; justify-content: space-between; padding: 2px 2px 0;
  font-size: var(--adk-font-size-sm); color: var(--adk-text-secondary); }
.adk-empty { padding: 36px 16px; text-align: center; color: var(--adk-text-secondary); }
.adk-empty .adk-ico { width: 36px; height: 36px; margin: 0 auto 10px; border-radius: 10px; }
.adk-empty-title { margin-bottom: 2px; font-weight: 700; color: var(--adk-text); }

/* RIGHT_CHART_PANE is a quarter of the page, 360px on a 1440px screen. */
@container (max-width: 400px) {
  .adk-record-head { flex-wrap: wrap; row-gap: 2px; }
  .adk-record-title { order: 3; flex-basis: 100%; white-space: normal; }
  .adk-actions { flex-wrap: wrap; overflow: visible; }
  .adk-starters { grid-template-columns: 1fr; }
}
"""


def _stylesheet(tokens: Mapping[str, str]) -> str:
    """The font import, the tokens as --adk-* custom properties, and the components."""
    properties = "\n".join(f"  --adk-{name}: {value};" for name, value in tokens.items())
    return f"@import url({LATO_IMPORT});\n:root {{\n{properties}\n}}\n{_COMPONENTS.strip()}\n"


AGENT_UI_CSS: SafeString = mark_safe(_stylesheet(TOKENS))

__exports__ = ("AGENT_UI_CSS", "TOKENS")
