"""Analytics and reporting commands."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import click

from ..core.formatters import format_output
from ..utils import load_json_payload
from .common import auth_kwargs, auth_option, format_option, make_client


def _format_percent(value: Any, decimals: int = 1) -> str:
    """Format numeric values as percentages with sensible fallbacks."""
    if value in (None, ""):
        return "0%"
    try:
        return f"{float(value):.{decimals}f}%"
    except (TypeError, ValueError):
        return str(value)


def _format_number(value: Any, decimals: int = 2) -> str:
    """Format numeric values while preserving integers as-is."""
    if value in (None, ""):
        return "0"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if number.is_integer():
        return str(int(number))
    return f"{number:.{decimals}f}"


def _format_bool(value: Any) -> str:
    """Format booleans and fallback to string for other values."""
    if isinstance(value, bool):
        return "Yes" if value else "No"
    return "0" if value == 0 else (str(value) if value is not None else "")


def _humanize_key(key: str) -> str:
    """Turn snake_case keys into human readable labels."""
    if not key:
        return ""
    return key.replace("_", " ").replace("-", " ").title()


def _dict_to_rows(
    mapping: Optional[Dict[str, Any]],
    *,
    key_label: str,
    value_label: str,
    formatter: Optional[callable] = None,
) -> List[Dict[str, Any]]:
    """Convert a dictionary mapping into table rows."""
    if not isinstance(mapping, dict) or not mapping:
        return []
    rows: List[Dict[str, Any]] = []
    for key, value in mapping.items():
        formatted = formatter(value) if formatter else value
        rows.append({key_label: _humanize_key(str(key)), value_label: formatted})
    return rows


def _append_section(
    sections: List[Tuple[str, List[Dict[str, Any]]]],
    title: str,
    rows: List[Dict[str, Any]],
) -> None:
    """Append a section if it contains at least one row with data."""
    filtered: List[Dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        cleaned = {key: ("" if value is None else value) for key, value in row.items()}
        if any(value not in ("", [], {}) for value in cleaned.values()):
            filtered.append(cleaned)
    if filtered:
        sections.append((f"== {title} ==", filtered))


def _build_lead_analytics_sections(payload: Dict[str, Any]) -> List[Tuple[str, List[Dict[str, Any]]]]:
    """Transform raw analytics payload into titled table sections."""
    sections: List[Tuple[str, List[Dict[str, Any]]]] = []

    summary = payload.get("lead_summary")
    if isinstance(summary, dict):
        _append_section(sections, "Lead Summary", [
            {"Metric": "Total Leads", "Value": summary.get("total_leads", 0)},
            {"Metric": "Qualified Leads", "Value": summary.get("qualified_leads", 0)},
            {"Metric": "Contacted Leads", "Value": summary.get("contacted_leads", 0)},
            {"Metric": "Converted Leads", "Value": summary.get("converted_leads", 0)},
            {"Metric": "Lost Leads", "Value": summary.get("lost_leads", 0)},
        ])

    conv = payload.get("conversation_engagement")
    if isinstance(conv, dict):
        _append_section(sections, "Conversation Engagement", [
            {"Metric": "Avg Messages / Conversation", "Value": _format_number(conv.get("avg_messages_per_conversation"))},
            {"Metric": "Avg Satisfaction", "Value": _format_number(conv.get("avg_satisfaction"))},
            {"Metric": "Leads with Conversations", "Value": conv.get("leads_with_conversations", 0)},
            {"Metric": "Total Conversations", "Value": conv.get("total_conversations", 0)},
        ])

    funnel = payload.get("conversion_funnel")
    if isinstance(funnel, dict):
        _append_section(sections, "Conversion Funnel", [
            {"Metric": "Contact Rate", "Value": _format_percent(funnel.get("contact_rate_percent"))},
            {"Metric": "Qualification Rate", "Value": _format_percent(funnel.get("qualification_rate_percent"))},
            {"Metric": "Conversion Rate", "Value": _format_percent(funnel.get("conversion_rate_percent"))},
            {"Metric": "Overall Conversion Rate", "Value": _format_percent(funnel.get("overall_conversion_rate_percent"))},
        ])

    quality = payload.get("lead_quality")
    if isinstance(quality, dict):
        _append_section(sections, "Lead Quality", [
            {"Metric": "Avg Engagement Days", "Value": _format_number(quality.get("avg_engagement_days"))},
            {"Metric": "Marketing Consent Rate", "Value": _format_percent(quality.get("marketing_consent_rate_percent"))},
            {"Metric": "Phone Completion Rate", "Value": _format_percent(quality.get("phone_completion_rate_percent"))},
        ])

    date_range = payload.get("date_range")
    if isinstance(date_range, dict):
        _append_section(sections, "Date Range", [
            {"Metric": "Start Date", "Value": date_range.get("start_date", "")},
            {"Metric": "End Date", "Value": date_range.get("end_date", "")},
        ])

    sources = payload.get("source_analysis")
    if isinstance(sources, list) and sources:
        _append_section(sections, "Lead Sources", [
            {"Source": item.get("source", "Unknown"), "Lead Count": item.get("count", 0)}
            for item in sources
        ])

    statuses = payload.get("status_distribution")
    if isinstance(statuses, list) and statuses:
        _append_section(sections, "Status Distribution", [
            {"Status": item.get("status", "Unknown"), "Lead Count": item.get("count", 0)}
            for item in statuses
        ])

    top_sources = payload.get("top_performing_sources")
    if isinstance(top_sources, list) and top_sources:
        _append_section(sections, "Top Performing Sources", [
            {
                "Source": item.get("source", "Unknown"),
                "Total Leads": item.get("total_leads", 0),
                "Conversions": item.get("conversions", 0),
                "Conversion Rate": _format_percent(item.get("conversion_rate_percent")),
            }
            for item in top_sources
        ])

    daily_trend = payload.get("daily_trend")
    if isinstance(daily_trend, list) and daily_trend:
        _append_section(sections, "Daily Trend", [
            {
                "Date": item.get("date", ""),
                "Lead Count": item.get("lead_count", 0),
                "Conversions": item.get("conversions", 0),
                "Daily Conversion Rate": _format_percent(item.get("daily_conversion_rate")),
            }
            for item in daily_trend
        ])

    return sections


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    """Parse an ISO datetime string into a datetime object."""
    if not value:
        return None
    try:
        normalized = value.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def _format_date_value(value: Optional[str]) -> str:
    """Format ISO datetime strings for display."""
    dt_value = _parse_datetime(value)
    if dt_value:
        return dt_value.strftime("%Y-%m-%d %H:%M")
    return value or "N/A"


def _format_range_duration(start: Optional[str], end: Optional[str]) -> str:
    """Return a friendly duration between two ISO timestamps."""
    start_dt = _parse_datetime(start)
    end_dt = _parse_datetime(end)
    if not (start_dt and end_dt):
        return ""
    delta = end_dt - start_dt
    if delta.total_seconds() <= 0:
        return ""
    days = delta.days
    if days >= 1:
        return f"{days} day{'s' if days != 1 else ''}"
    hours = delta.seconds // 3600
    if hours >= 1:
        return f"{hours} hour{'s' if hours != 1 else ''}"
    minutes = (delta.seconds % 3600) // 60
    if minutes >= 1:
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    return f"{delta.seconds} seconds"


def _format_metric_label(metric_key: str) -> str:
    """Map raw metric keys to display labels."""
    mapping = {
        "conversations": "Conversations",
        "conversions": "Conversions",
        "response_time": "Avg Response Time (s)",
        "satisfaction_rating": "Avg Satisfaction",
        "total_messages": "Total Messages",
    }
    return mapping.get(metric_key, metric_key.replace("_", " ").title())


def _format_metric_value(value: Any) -> str:
    """Format metric values while preserving blanks."""
    if value in (None, ""):
        return "N/A"
    return _format_number(value)


def _format_relative_percent(value: Any) -> str:
    """Format percent deltas with explicit signs."""
    if value in (None, ""):
        return "N/A"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    sign = "+" if number > 0 else ""
    return f"{sign}{number:.2f}%"


def _format_agent_performance_summary(payload: Dict[str, Any]) -> str:
    """Return a user-friendly breakdown for the agent performance command."""
    agent = payload.get("agent_info") or {}
    date_range = payload.get("date_range") or {}
    metrics = payload.get("performance_comparison") or {}

    sections: List[str] = []

    # Agent details
    detail_rows: List[Tuple[str, str]] = []
    name = agent.get("name") or agent.get("agent_name") or "Unknown"
    detail_rows.append(("Name", name))

    if agent.get("id"):
        detail_rows.append(("ID", agent["id"]))
    if agent.get("status"):
        detail_rows.append(("Status", agent["status"]))
    model = agent.get("model_name") or agent.get("model")
    if model:
        detail_rows.append(("Model", model))
    if agent.get("total_conversations") is not None:
        detail_rows.append(("Total conversations", _format_number(agent.get("total_conversations"))))
    if agent.get("total_messages") is not None:
        detail_rows.append(("Total messages", _format_number(agent.get("total_messages"))))
    if agent.get("average_response_time") is not None:
        detail_rows.append(("Avg response time (s)", _format_number(agent.get("average_response_time"))))
    if agent.get("created_at"):
        detail_rows.append(("Created", _format_date_value(agent.get("created_at"))))

    if detail_rows:
        sections.append("Agent Details")
        sections.append("-------------")
        sections.extend(f"{label}: {value}" for label, value in detail_rows)
        sections.append("")

    # Date range
    start_raw = date_range.get("start_date") or date_range.get("start")
    end_raw = date_range.get("end_date") or date_range.get("end")
    if start_raw or end_raw:
        sections.append("Date Range")
        sections.append("----------")
        if start_raw:
            sections.append(f"Start: {_format_date_value(start_raw)}")
        if end_raw:
            sections.append(f"End:   {_format_date_value(end_raw)}")
        duration = _format_range_duration(start_raw, end_raw)
        if duration:
            sections.append(f"Duration: {duration}")
        sections.append("")

    # Metrics
    metric_rows: List[Dict[str, str]] = []
    if isinstance(metrics, dict):
        for key, metric in metrics.items():
            if not isinstance(metric, dict):
                continue
            metric_rows.append({
                "Metric": _format_metric_label(key),
                "Agent": _format_metric_value(metric.get("agent_value")),
                "Company Avg": _format_metric_value(metric.get("company_average")),
                "Vs Avg": _format_relative_percent(metric.get("performance_vs_average_percent")),
            })

    sections.append("Performance Metrics")
    sections.append("-------------------")
    if metric_rows:
        sections.append(format_output(metric_rows, "table").rstrip())
    else:
        sections.append("No performance metrics available.")

    return "\n".join(sections).rstrip()



def _build_dashboard_sections(payload: Dict[str, Any]) -> List[Tuple[str, List[Dict[str, Any]]]]:
    """Transform the dashboard payload into titled table sections."""
    sections: List[Tuple[str, List[Dict[str, Any]]]] = []

    core = payload.get("core_metrics")
    if isinstance(core, dict):
        _append_section(sections, "Core Metrics", [
            {"Metric": "Scope", "Value": core.get("scope", "")},
            {"Metric": "Conversations", "Value": core.get("conversation_count", 0)},
            {"Metric": "Documents", "Value": core.get("document_count", 0)},
            {"Metric": "Leads", "Value": core.get("lead_count", 0)},
            {"Metric": "Users", "Value": core.get("total_users", 0)},
            {"Metric": "DB Connections", "Value": core.get("connection_count", 0)},
        ])

    conv = payload.get("conversation_analytics")
    if isinstance(conv, dict):
        _append_section(
            sections,
            "Conversation Status",
            _dict_to_rows(conv.get("conversation_status"), key_label="Status", value_label="Count"),
        )

        lead_eng = conv.get("lead_engagement")
        if isinstance(lead_eng, dict):
            _append_section(sections, "Lead Engagement", [
                {"Metric": "Engaged Leads", "Value": lead_eng.get("engaged_leads", 0)},
                {"Metric": "Average Satisfaction", "Value": _format_number(lead_eng.get("average_satisfaction"))},
                {"Metric": "Total Conversions", "Value": lead_eng.get("total_conversions", 0)},
            ])

        message = conv.get("message_analytics")
        if isinstance(message, dict):
            _append_section(sections, "Message Analytics", [
                {"Metric": "Total Messages", "Value": message.get("total_messages", 0)},
                {"Metric": "Average Processing Time (s)", "Value": _format_number(message.get("average_processing_time"))},
                {"Metric": "Average Confidence", "Value": _format_number(message.get("average_confidence_score"))},
                {"Metric": "Average Rating", "Value": _format_number(message.get("average_rating"))},
                {"Metric": "Rated Messages", "Value": message.get("rated_messages", 0)},
                {"Metric": "Average Tokens / Message", "Value": _format_number(message.get("average_tokens_per_message"))},
                {"Metric": "Total Tokens", "Value": message.get("total_tokens", 0)},
            ])

        _append_section(
            sections,
            "Message Roles",
            _dict_to_rows(conv.get("message_roles"), key_label="Role", value_label="Count"),
        )

        timeline = conv.get("activity_timeline")
        if isinstance(timeline, list) and timeline:
            _append_section(sections, "Conversation Activity Timeline", [
                {
                    "Date": item.get("date", ""),
                    "Conversations": item.get("conversations", 0),
                    "Messages": item.get("messages", 0),
                }
                for item in timeline
            ])

        top_conv = conv.get("top_conversations")
        if isinstance(top_conv, list) and top_conv:
            _append_section(sections, "Top Conversations", [
                {
                    "Lead": item.get("lead_name", "Unknown"),
                    "Email": item.get("lead_email", ""),
                    "Messages": item.get("message_count", 0),
                    "Last Activity": item.get("last_activity", ""),
                    "Title": item.get("title", ""),
                }
                for item in top_conv
            ])

    agent = payload.get("agent_analytics")
    if isinstance(agent, dict):
        _append_section(
            sections,
            "Agent Status Distribution",
            _dict_to_rows(agent.get("agent_status_distribution"), key_label="Status", value_label="Count"),
        )
        top_agents = agent.get("top_performing_agents")
        if isinstance(top_agents, list) and top_agents:
            _append_section(sections, "Top Performing Agents", [
                {
                    "Agent": item.get("name", "Unknown"),
                    "Status": item.get("status", "unknown"),
                    "Conversations": item.get("total_conversations", 0),
                    "Messages": item.get("total_messages", 0),
                    "Average Rating": _format_number(item.get("average_rating")),
                }
                for item in top_agents
            ])

    lead = payload.get("lead_analytics")
    if isinstance(lead, dict):
        consent = lead.get("consent_analytics")
        if isinstance(consent, dict):
            _append_section(sections, "Lead Consent Analytics", [
                {"Metric": "Total Leads", "Value": consent.get("total_leads", 0)},
                {"Metric": "Data Consent Rate", "Value": _format_percent(consent.get("data_consent_rate"))},
                {"Metric": "Marketing Consent Rate", "Value": _format_percent(consent.get("marketing_consent_rate"))},
            ])
        _append_section(
            sections,
            "Lead Status Distribution",
            _dict_to_rows(lead.get("lead_status_distribution"), key_label="Status", value_label="Lead Count"),
        )
        _append_section(
            sections,
            "Lead Sources",
            _dict_to_rows(lead.get("lead_sources"), key_label="Source", value_label="Lead Count"),
        )
        daily_leads = lead.get("daily_new_leads")
        if isinstance(daily_leads, list) and daily_leads:
            _append_section(sections, "Daily New Leads", [
                {"Date": item.get("date", ""), "Lead Count": item.get("count", 0)}
                for item in daily_leads
            ])

    doc = payload.get("document_analytics")
    if isinstance(doc, dict):
        storage = doc.get("storage_analytics")
        if isinstance(storage, dict):
            _append_section(sections, "Document Storage", [
                {"Metric": "Total Size (MB)", "Value": storage.get("total_size_mb", "0")},
                {"Metric": "Average Size (MB)", "Value": storage.get("average_size_mb", "0")},
                {"Metric": "Total Words", "Value": storage.get("total_words", 0)},
                {"Metric": "Average Words", "Value": storage.get("average_words", "0")},
                {"Metric": "Largest File (MB)", "Value": storage.get("largest_file_mb", 0)},
            ])
        processing = doc.get("processing_status")
        _append_section(
            sections,
            "Document Processing Status",
            _dict_to_rows(processing, key_label="Status", value_label="Count"),
        )
        doc_types = doc.get("document_types")
        _append_section(
            sections,
            "Document Types",
            _dict_to_rows(doc_types, key_label="Type", value_label="Count"),
        )
        uploads = doc.get("daily_uploads")
        if isinstance(uploads, list) and uploads:
            _append_section(sections, "Daily Document Uploads", [
                {"Date": item.get("date", ""), "Documents": item.get("count", 0)}
                for item in uploads
            ])
        top_users = doc.get("top_users_by_documents")
        if isinstance(top_users, list) and top_users:
            _append_section(sections, "Top Users By Documents", [
                {
                    "User": item.get("full_name", item.get("username", "Unknown")),
                    "Username": item.get("username", ""),
                    "Documents": item.get("document_count", 0),
                }
                for item in top_users
            ])

    activity = payload.get("activity_analytics")
    if isinstance(activity, dict):
        sessions = activity.get("session_analytics")
        if isinstance(sessions, dict):
            _append_section(sections, "User Sessions", [
                {"Metric": "Total Sessions", "Value": sessions.get("total_sessions", 0)},
                {"Metric": "Unique IPs", "Value": sessions.get("unique_ip_addresses", 0)},
                {"Metric": "Avg Session Duration (min)", "Value": _format_number(sessions.get("average_session_duration_minutes"))},
            ])
        logins = activity.get("login_timeline")
        if isinstance(logins, list) and logins:
            _append_section(sections, "Login Timeline", [
                {"Date": item.get("date", ""), "Unique Logins": item.get("unique_logins", 0)}
                for item in logins
            ])

    company = payload.get("company_analytics")
    if isinstance(company, dict):
        info = company.get("company_info")
        if isinstance(info, dict):
            _append_section(sections, "Company Info", [
                {"Field": _humanize_key(key), "Value": _format_bool(value)}
                for key, value in info.items()
                if not isinstance(value, (dict, list))
            ])
        growth = company.get("user_growth_90days")
        if isinstance(growth, list) and growth:
            _append_section(sections, "User Growth (90 days)", [
                {"Date": item.get("date", ""), "New Users": item.get("new_users", 0)}
                for item in growth
            ])

    perf = payload.get("performance_analytics")
    if isinstance(perf, dict):
        doc_perf = perf.get("document_processing")
        if isinstance(doc_perf, dict):
            _append_section(sections, "Document Processing Performance", [
                {"Metric": "Avg Processing Time (s)", "Value": doc_perf.get("average_processing_time_seconds", "0")},
                {"Metric": "Success Rate", "Value": _format_percent(doc_perf.get("success_rate"))},
                {"Metric": "Failed Documents", "Value": doc_perf.get("failed_documents", 0)},
            ])
        model_perf = perf.get("model_performance")
        if isinstance(model_perf, list) and model_perf:
            _append_section(sections, "Model Performance", [
                {
                    "Model": item.get("model", "unknown"),
                    "Messages": item.get("message_count", 0),
                    "Avg Processing Time (s)": _format_number(item.get("average_processing_time")),
                    "Avg Confidence": _format_number(item.get("average_confidence")),
                }
                for item in model_perf
            ])

    database = payload.get("database_analytics")
    if isinstance(database, dict):
        _append_section(
            sections,
            "Database Connection Status",
            _dict_to_rows(database.get("connection_status"), key_label="Status", value_label="Count"),
        )
        _append_section(
            sections,
            "Database Connection Types",
            _dict_to_rows(database.get("connection_types"), key_label="Type", value_label="Count"),
        )
        table_stats = database.get("table_analytics")
        if isinstance(table_stats, dict):
            _append_section(sections, "Database Table Analytics", [
                {"Metric": "Total Tables", "Value": table_stats.get("total_tables", 0)},
                {"Metric": "Total Rows", "Value": table_stats.get("total_rows", 0)},
                {"Metric": "Total Size (bytes)", "Value": table_stats.get("total_size_bytes", 0)},
            ])
        recent_tests = database.get("recent_tests")
        if isinstance(recent_tests, list) and recent_tests:
            _append_section(sections, "Recent Database Tests", [
                {
                    "Connection": item.get("connection_name", "Unknown"),
                    "Status": item.get("status", ""),
                    "Tested At": item.get("tested_at", ""),
                }
                for item in recent_tests
            ])

    website = payload.get("website_analytics")
    if isinstance(website, dict):
        _append_section(
            sections,
            "Website Sources",
            _dict_to_rows(website.get("sources"), key_label="Status", value_label="Count"),
        )
        _append_section(
            sections,
            "Website Pages",
            _dict_to_rows(website.get("pages"), key_label="Status", value_label="Count"),
        )

    security = payload.get("security_analytics")
    if isinstance(security, dict):
        _append_section(
            sections,
            "Security Risk Distribution (7d)",
            _dict_to_rows(security.get("risk_distribution_7days"), key_label="Risk Level", value_label="Count"),
        )
        _append_section(
            sections,
            "User Security Status",
            _dict_to_rows(security.get("user_security_status"), key_label="Metric", value_label="Value"),
        )
        events = security.get("recent_audit_events")
        if isinstance(events, list) and events:
            _append_section(sections, "Recent Audit Events", [
                {
                    "Timestamp": item.get("timestamp", ""),
                    "Event": item.get("event", ""),
                    "Actor": item.get("actor", ""),
                }
                for item in events
            ])

    user_mgmt = payload.get("user_management")
    if isinstance(user_mgmt, dict):
        _append_section(sections, "User Management", [
            {"Metric": "Active Users (24h)", "Value": user_mgmt.get("active_users_24h", 0)},
        ])
        _append_section(
            sections,
            "Role Distribution",
            _dict_to_rows(user_mgmt.get("role_distribution"), key_label="Role", value_label="Count"),
        )
        _append_section(
            sections,
            "User Status Distribution",
            _dict_to_rows(user_mgmt.get("user_status_distribution"), key_label="Status", value_label="Count"),
        )

    user_context = payload.get("user_context")
    if isinstance(user_context, dict):
        _append_section(sections, "User Context", [
            {"Field": _humanize_key(key), "Value": _format_bool(value)}
            for key, value in user_context.items()
            if not isinstance(value, (dict, list))
        ])

    system_metrics = payload.get("system_metrics")
    if isinstance(system_metrics, dict):
        health = system_metrics.get("system_health")
        if isinstance(health, list) and health:
            rows = []
            for item in health:
                if isinstance(item, dict):
                    rows.append({
                        "Component": item.get("component", "Unknown"),
                        "Status": item.get("status", ""),
                        "Details": item.get("details", ""),
                        "Checked At": item.get("checked_at", ""),
                    })
            _append_section(sections, "System Health", rows)

    generated_at = payload.get("generated_at")
    if generated_at:
        _append_section(sections, "Report Info", [
            {"Metric": "Generated At", "Value": generated_at},
        ])

    return sections


def _build_usage_sections(payload: Dict[str, Any]) -> List[Tuple[str, List[Dict[str, Any]]]]:
    """Transform usage analytics payload into titled table sections."""
    sections: List[Tuple[str, List[Dict[str, Any]]]] = []

    # Agent Usage
    agent = payload.get("agent_usage")
    if isinstance(agent, dict):
        rows = [
            {"Metric": "Active Agents", "Value": agent.get("active_agents", 0)},
            {"Metric": "Total Agents", "Value": agent.get("total_agents", 0)},
            {"Metric": "Total Conversations", "Value": agent.get("total_conversations", 0)},
            {"Metric": "Total Messages", "Value": agent.get("total_messages", 0)},
            {"Metric": "Avg Agent Rating", "Value": _format_number(agent.get("avg_agent_rating"))},
        ]
        _append_section(sections, "Agent Usage", rows)

    # API Usage
    api = payload.get("api_usage")
    if isinstance(api, dict):
        _append_section(sections, "API Usage", [
            {"Metric": "Total API Calls", "Value": api.get("total_api_calls", 0)},
            {"Metric": "Success Count", "Value": api.get("success_count", 0)},
            {"Metric": "Error Count", "Value": api.get("error_count", 0)},
            {"Metric": "Error Rate", "Value": _format_percent(api.get("error_rate_percent"))},
            {"Metric": "Active API Keys", "Value": api.get("active_api_keys", 0)},
            {"Metric": "Avg Response Time (ms)", "Value": _format_number(api.get("avg_response_time_ms"))},
        ])

    # Storage Usage
    storage = payload.get("storage_usage")
    if isinstance(storage, dict):
        _append_section(sections, "Storage Usage", [
            {"Metric": "Total Conversations", "Value": storage.get("total_conversations", 0)},
            {"Metric": "Total Messages", "Value": storage.get("total_messages", 0)},
            {"Metric": "Total Content Size (Bytes)", "Value": storage.get("total_content_size_bytes", 0)},
        ])

    # Token Usage
    token = payload.get("token_usage")
    if isinstance(token, dict):
        _append_section(sections, "Token Usage", [
            {"Metric": "Total Tokens", "Value": token.get("total_tokens", 0)},
            {"Metric": "Total Messages Processed", "Value": token.get("total_messages_processed", 0)},
            {"Metric": "Avg Tokens / Message", "Value": _format_number(token.get("avg_tokens_per_message"))},
        ])

    # Endpoint Usage
    endpoints = payload.get("endpoint_usage")
    if isinstance(endpoints, list) and endpoints:
        _append_section(sections, "Endpoint Usage", [
            {
                "Method": item.get("method", ""),
                "Endpoint": item.get("endpoint", ""),
                "Calls": item.get("call_count", 0),
                "Avg Time (ms)": _format_number(item.get("avg_response_time_ms")),
            }
            for item in endpoints
        ])

    # Top Client IPs
    ips = payload.get("top_client_ips")
    if isinstance(ips, list) and ips:
        _append_section(sections, "Top Client IPs", [
            {
                "IP Address": item.get("ip_address", ""),
                "Requests": item.get("request_count", 0),
            }
            for item in ips
        ])

    # Daily Usage Trend
    trend = payload.get("daily_usage_trend")
    if isinstance(trend, list) and trend:
        _append_section(sections, "Daily Usage Trend", [
            {
                "Date": item.get("date", ""),
                "API Calls": item.get("api_calls", 0),
                "Errors": item.get("errors", 0),
                "Success Rate": _format_percent(item.get("success_rate_percent")),
            }
            for item in trend
        ])

    # Date Range
    date_range = payload.get("date_range")
    if isinstance(date_range, dict):
        _append_section(sections, "Date Range", [
            {"Metric": "Start Date", "Value": _format_date_value(date_range.get("start_date"))},
            {"Metric": "End Date", "Value": _format_date_value(date_range.get("end_date"))},
        ])

    return sections

@click.group(name="analytics")
def cmd() -> None:
    """Access analytics dashboards and exports."""


@cmd.command("dashboard")
@auth_option()
@format_option(default="json")
@click.option("--company-id", help="Optional company ID (super admin).")
def dashboard(auth: str, format: str, company_id: Optional[str]) -> None:
    """Retrieve the main analytics dashboard."""
    client = make_client()
    params = {}
    if company_id:
        params["company_id"] = company_id
    response = client.get("/api/v1/analytic/dashboard", params=params, **auth_kwargs(auth))

    if format == "table":
        sections = _build_dashboard_sections(response)
        if not sections:
            click.echo("No analytics data to display")
            return

        for index, (title, rows) in enumerate(sections):
            if index > 0:
                click.echo()
            click.echo(title)
            click.echo(format_output(rows, "table").rstrip())
        return

    click.echo(format_output(response, format))


@cmd.command("agent")
@auth_option()
@format_option()
@click.argument("agent_id", required=False)
@click.option("--start-date", help="ISO start date.")
@click.option("--end-date", help="ISO end date.")
def agent_analytics(auth: str, format: str, agent_id: Optional[str], start_date: Optional[str], end_date: Optional[str]) -> None:
    """Retrieve analytics for a single agent. Prompts for selection when no agent ID is provided."""
    client = make_client()
    
    if agent_id is None:
        from ..interactive import select_agent
        click.echo("\n📊 Select an agent to view analytics:")
        agent_id, _ = select_agent(client, message="Select agent")
    
    params = {}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    response = client.get(
        f"/api/v1/analytic/agent/{agent_id}",
        params=params,
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("agent-performance")
@auth_option()
@format_option()
@click.argument("agent_id", required=False)
@click.option("--start-date")
@click.option("--end-date")
def agent_performance(auth: str, format: str, agent_id: Optional[str], start_date: Optional[str], end_date: Optional[str]) -> None:
    """Compare agent performance to company averages.

    If no agent ID is provided, an interactive selection menu will be shown.
    """
    client = make_client()

    if agent_id is None:
        from ..interactive import select_agent

        click.echo("\n[?] Select an agent to analyze:")
        agent_id, _ = select_agent(client, message="Select agent")

    params = {}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    response = client.get(
        f"/api/v1/analytic/agent/{agent_id}/performance-comparison",
        params=params,
        **auth_kwargs(auth),
    )
    if format == "table" and isinstance(response, dict):
        click.echo(_format_agent_performance_summary(response))
        return
    click.echo(format_output(response, format))


@cmd.command("conversation")
@auth_option()
@format_option()
@click.argument("conversation_id", required=False)
def conversation_analytics(auth: str, format: str, conversation_id: Optional[str]) -> None:
    """Retrieve analytics for a conversation."""
    client = make_client()
    
    if conversation_id is None:
        from ..interactive import select_conversation
        click.echo("\n💬 Select a conversation to analyze:")
        conversation_id, _ = select_conversation(client, message="Select a conversation")
    
    response = client.get(
        f"/api/v1/analytic/conversation/{conversation_id}",
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("leads")
@auth_option()
@format_option(default="json")
@click.option("--start-date")
@click.option("--end-date")
@click.option("--days", type=int, help="Number of days to look back (alternative to start-date)")
@click.option("--company-id", help="Super admin override company ID.")
def leads_analytics(auth: str, format: str, start_date: Optional[str], end_date: Optional[str], days: Optional[int], company_id: Optional[str]) -> None:
    """Retrieve lead analytics."""
    client = make_client()
    params = {}
    
    if days:
        end = datetime.now()
        start = end - timedelta(days=days)
        params["start_date"] = start.isoformat()
        params["end_date"] = end.isoformat()
    else:
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
    
    if company_id:
        params["company_id"] = company_id
    response = client.get("/api/v1/analytic/leads", params=params, **auth_kwargs(auth))

    if format == "table":
        sections = _build_lead_analytics_sections(response)
        if not sections:
            click.echo("No analytics data to display")
            return

        for index, (title, rows) in enumerate(sections):
            if index > 0:
                click.echo()
            click.echo(title)
            click.echo(format_output(rows, "table").rstrip())
        return

    click.echo(format_output(response, format))


@cmd.command("usage")
@auth_option()
@format_option(default="json")
@click.option("--start-date")
@click.option("--end-date")
def usage(auth: str, format: str, start_date: Optional[str], end_date: Optional[str]) -> None:
    """Retrieve platform usage analytics."""
    client = make_client()
    params = {}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    response = client.get("/api/v1/analytic/usage", params=params, **auth_kwargs(auth))

    if format == "table":
        sections = _build_usage_sections(response)
        if not sections:
            click.echo("No usage data to display")
            return

        for index, (title, rows) in enumerate(sections):
            if index > 0:
                click.echo()
            click.echo(title)
            click.echo(format_output(rows, "table").rstrip())
        return

    click.echo(format_output(response, format))


@cmd.command("export")
@auth_option()
@click.option("--payload", help="JSON payload describing the export request.")
@click.option("--type", "export_type", type=click.Choice(["conversations", "leads", "agents", "usage"]), help="Type of data to export")
@click.option("--format", "output_format", type=click.Choice(["csv", "json"]), default="csv", help="Export format")
@click.option("--start-date", help="Start date for export")
@click.option("--end-date", help="End date for export")
def export(
    auth: str,
    payload: Optional[str],
    export_type: Optional[str],
    output_format: str,
    start_date: Optional[str],
    end_date: Optional[str]
) -> None:
    """Export analytics data.
    
    Examples:
        # Export conversations as CSV
        knowrithm analytics export --type conversations --format csv
        
        # Export leads with date range
        knowrithm analytics export --type leads --format json --start-date 2024-01-01
        
        # Custom export with payload
        knowrithm analytics export --payload '{"type": "agents", "format": "csv"}'
    """
    client = make_client()
    
    if payload:
        body = load_json_payload(payload)
    else:
        if not export_type:
            raise click.ClickException("Either --payload or --type is required")
        
        body = {
            "type": export_type,
            "format": output_format
        }
        
        if start_date:
            body["start_date"] = start_date
        if end_date:
            body["end_date"] = end_date
    
    response = client.post("/api/v1/analytic/export", json=body, **auth_kwargs(auth))
    
    # If response is CSV (wrapped in raw dict by client), print directly
    if isinstance(response, dict) and "raw" in response and len(response) == 1:
        click.echo(response["raw"])
    elif isinstance(response, str):
        click.echo(response)
    else:
        click.echo(format_output(response, output_format))
