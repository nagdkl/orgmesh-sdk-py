"""Small Wave 38 helpers for Synergy agent message envelopes.

This module is intentionally dependency-light and side-effect free:
- no network calls
- no GitHub writes
- no secret access
- no branch or PR operations
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

ALLOWED_AUTONOMY_PHASES = {
    "phase_0_docs_only",
    "phase_1_report_only",
    "phase_2_draft_pr_only",
    "phase_3_human_approved_apply",
    "phase_4_limited_autonomous_runtime",
}

ALLOWED_RISK_LEVELS = {"low", "medium", "high", "critical"}


def utc_now() -> str:
    """Return an RFC3339-like UTC timestamp without microseconds."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class AgentEnvelope:
    """Typed builder for `synergy.agent-message-envelope/v1` payloads."""

    message_id: str
    mission_id: str
    correlation_id: str
    source_repo: str
    target_repo: str
    subject: str
    payload_kind: str
    autonomy_phase: str = "phase_1_report_only"
    created_at: str = field(default_factory=utc_now)
    payload_ref: str | None = None
    payload: dict[str, Any] | None = None
    private_payload_inline: bool = False
    risk_level: str = "low"
    requires_human_approval: bool = True
    evidence_ref: str | None = None
    stop_conditions: list[str] = field(default_factory=list)
    labels: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        envelope = {
            "schema": "synergy.agent-message-envelope/v1",
            "message_id": self.message_id,
            "mission_id": self.mission_id,
            "correlation_id": self.correlation_id,
            "created_at": self.created_at,
            "source_repo": self.source_repo,
            "target_repo": self.target_repo,
            "autonomy_phase": self.autonomy_phase,
            "subject": self.subject,
            "payload_kind": self.payload_kind,
            "payload_ref": self.payload_ref,
            "payload": self.payload,
            "private_payload_inline": self.private_payload_inline,
            "risk_level": self.risk_level,
            "requires_human_approval": self.requires_human_approval,
            "evidence_ref": self.evidence_ref,
            "stop_conditions": self.stop_conditions,
            "labels": self.labels,
        }
        validate_agent_envelope_basics(envelope)
        return envelope


def validate_agent_envelope_basics(envelope: dict[str, Any]) -> None:
    """Validate basic local invariants before JSON Schema validation.

    Full compatibility validation belongs to `nagdkl/orgmesh-contracts` schemas.
    """
    errors: list[str] = []

    if envelope.get("schema") != "synergy.agent-message-envelope/v1":
        errors.append("schema must be synergy.agent-message-envelope/v1")
    if envelope.get("autonomy_phase") not in ALLOWED_AUTONOMY_PHASES:
        errors.append("unknown autonomy_phase")
    if envelope.get("risk_level") not in ALLOWED_RISK_LEVELS:
        errors.append("unknown risk_level")
    if envelope.get("private_payload_inline") is not False:
        errors.append("private_payload_inline must be false by default")
    if envelope.get("requires_human_approval") is not True:
        errors.append("requires_human_approval must remain true by default")
    subject = str(envelope.get("subject", ""))
    if not subject.startswith("synergy.") or ".v" not in subject:
        errors.append("subject must use a versioned synergy.*.vN namespace")

    if errors:
        raise ValueError("Invalid Synergy agent envelope: " + "; ".join(errors))


def build_wave38_research_simulator_envelope() -> dict[str, Any]:
    """Build the default Wave 38 local research simulator envelope."""
    return AgentEnvelope(
        message_id="msg-wave38-sdk-0001",
        mission_id="wave_38_local_agent_bus",
        correlation_id="corr-wave38-sdk-0001",
        source_repo="nagdkl/synergy-run",
        target_repo="nagdkl/synergy-lab",
        subject="synergy.tasks.research.v1",
        payload_kind="simulator_task",
        payload={
            "goal": "Build a local-only research simulator task envelope.",
            "constraints": [
                "no_github_writes",
                "no_external_llm_calls",
                "no_secrets",
                "explicit_output_dir_only",
            ],
        },
        stop_conditions=[
            "secret_detected",
            "external_llm_private_payload_attempt",
            "git_write_attempt",
            "production_deploy_attempt",
        ],
        labels=["wave-38", "local-simulator", "report-only"],
    ).to_dict()
