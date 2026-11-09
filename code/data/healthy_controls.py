"""
Healthy Controls and False-Premise Ticket Generator
Grounding: FaulT-Bench (Tseng et al., 2026) unreliable ticket benchmark.
Addresses Sub-Gap A: Benchmarking agents under healthy-network controls to evaluate over-diagnosis.
"""

from typing import List, Dict, Any
import random

REPORTER_PERSONAS = [
    {
        "persona": "panicked_user",
        "description": "High urgency, emotionally charged, claims total outage without technical evidence",
        "templates": [
            "URGENT: Entire network is completely down! Cannot access my portal on {device}! Fix immediately, business is halting!",
            "HELP! Nothing is loading from {device}! The whole office has lost connection!",
        ]
    },
    {
        "persona": "overconfident_junior_admin",
        "description": "Uses technical jargon, strongly asserts wrong root cause and wrong device",
        "templates": [
            "Root cause confirmed: BGP peering failure on {device} causing packet drop. Reset BGP immediately.",
            "Interface eth1 on {device} has experienced a severe hardware transceiver blowout. Replace the SFP module.",
        ]
    },
    {
        "persona": "misdirected_developer",
        "description": "Blames network infrastructure for client-side or application-level events",
        "templates": [
            "My curl requests to backend API are timing out. The routing table on {device} is definitely corrupted.",
            "The database server behind {device} cannot be reached due to an ACL block introduced in last night's push.",
        ]
    },
    {
        "persona": "monitoring_bot_false_alarm",
        "description": "Automated alarm fired due to stale synthetic polling",
        "templates": [
            "[AUTO-ALERT] Synthetic probe synthetic_ping_04 reported latency spike >500ms on {device}. Severity: High.",
            "[SEV-2 ALERT] Healthcheck probe to {device} failed 1 out of 5 retries. Node flagged as degraded.",
        ]
    },
    {
        "persona": "cautious_operator",
        "description": "Polite inquiry checking if a device is operational during routine maintenance",
        "templates": [
            "Checking status: Customer reported intermittent glitch near {device}. Could you check if link is healthy?",
            "Can we verify if {device} is functioning properly after the firmware reboot earlier today?",
        ]
    }
]


def generate_healthy_control(
    incident_id: str,
    scenario: str,
    device: str,
    topology_size: str = "medium",
    seed: int = 42
) -> Dict[str, Any]:
    """Generates a synthetic healthy-network control with a false-premise ticket."""
    rng = random.Random(seed)
    persona_obj = rng.choice(REPORTER_PERSONAS)
    template = rng.choice(persona_obj["templates"])
    ticket_text = template.format(device=device)

    return {
        "incident_id": incident_id,
        "scenario": scenario,
        "topology_size": topology_size,
        "is_healthy_control": True,
        "ground_truth_has_fault": False,
        "ground_truth_fault_family": "healthy",
        "ground_truth_device": "none",
        "ground_truth_fix": "none",
        "ticket_text": ticket_text,
        "reporter_persona": persona_obj["persona"],
        "suspected_device_in_ticket": device,
        "expected_action": "abstain"
    }


def generate_healthy_suite(
    scenarios: List[str],
    count_per_scenario: int = 5,
    seed: int = 42
) -> List[Dict[str, Any]]:
    """Generates a comprehensive benchmark suite of healthy controls."""
    controls = []
    idx = 1
    for scn in scenarios:
        for i in range(count_per_scenario):
            dev = f"node_{scn[:4]}_{i+1}"
            ctrl = generate_healthy_control(
                incident_id=f"HEALTHY-{idx:04d}",
                scenario=scn,
                device=dev,
                seed=seed + idx
            )
            controls.append(ctrl)
            idx += 1
    return controls

