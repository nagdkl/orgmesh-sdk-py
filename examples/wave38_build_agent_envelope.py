"""Build a Wave 38 Synergy agent envelope locally."""

from __future__ import annotations

import json

from orgmesh_sdk_py.agent_envelope import build_wave38_research_simulator_envelope


if __name__ == "__main__":
    print(json.dumps(build_wave38_research_simulator_envelope(), ensure_ascii=False, indent=2))
