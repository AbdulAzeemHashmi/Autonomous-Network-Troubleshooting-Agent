"""
Unit tests for all 7 phases of the proposed troubleshooting agent.
"""

import pytest
from code.data.mock_network_env import MockNetworkEnv
from code.agent.ticket_validator import TicketValidator
from code.agent.evidence_scanner import EvidenceScanner
from code.agent.hypothesis_router import HypothesisRouter
from code.agent.falsification import FalsificationEngine
from code.agent.abstain import AbstainManager
from code.agent.root_cause import RootCauseSynthesizer
from code.agent.remediation import RemediationPlanner
from code.agent.orchestrator import TroubleshootingAgent


def test_phase1_ticket_validator():
    # Test on faulty network
    env_faulty = MockNetworkEnv("campus_network", "small", fault_injected=True, fault_family="link_failure", faulty_device="dist_sw1")
    validator = TicketValidator()
    res = validator.validate("Link down on dist_sw1", env_faulty, "test topo")
    assert res["ticket_valid"] is True
    assert res["suspected_device"] == "dist_sw1"

    # Test on healthy network
    env_healthy = MockNetworkEnv("campus_network", "small", fault_injected=False)
    res_healthy = validator.validate("URGENT: Entire network down on dist_sw1!", env_healthy, "test topo")
    assert res_healthy["ticket_valid"] is False


def test_phase2_layered_evidence_scan():
    env = MockNetworkEnv("datacenter_clos", "small", fault_injected=True, fault_family="link_failure", faulty_device="leaf1")
    scanner = EvidenceScanner()
    res = scanner.scan_layers("leaf1", env)
    assert res["anomalies_detected"] is True
    assert any(rec["layer"] == "L2" for rec in res["evidence_records"])


def test_phase3_hypothesis_router():
    router = HypothesisRouter()
    evidence = [{
        "layer": "L2",
        "symptom": "Interface line protocol down / carrier lost",
        "severity": "high",
        "raw_snippet": "Interface eth1 is DOWN"
    }]
    hyps = router.route_hypotheses("leaf1", evidence)
    assert len(hyps) > 0
    assert hyps[0]["fault_family"] == "link_failure"


def test_phase4_falsification():
    env = MockNetworkEnv("datacenter_clos", "small", fault_injected=True, fault_family="link_failure", faulty_device="leaf1")
    engine = FalsificationEngine()
    hyps = [
        {"fault_family": "link_failure", "device": "leaf1", "initial_confidence": 0.7, "proposed_falsification_probe": "show interface eth1"},
        {"fault_family": "congestion", "device": "leaf1", "initial_confidence": 0.5, "proposed_falsification_probe": "check_queue_drops"}
    ]
    surviving, falsified = engine.test_hypotheses(hyps, env)
    assert any(h["fault_family"] == "link_failure" for h in surviving)
    assert any(h["fault_family"] == "congestion" for h in falsified)


def test_phase5_abstain():
    abstain_mgr = AbstainManager()
    # Scenario: healthy network, no surviving hypotheses
    res = abstain_mgr.should_abstain({"ticket_valid": False}, [])
    assert res["abstain"] is True

    # Scenario: active fault with surviving hypothesis
    res2 = abstain_mgr.should_abstain({"ticket_valid": True}, [{"fault_family": "link_failure", "updated_confidence": 0.95}])
    assert res2["abstain"] is False


def test_phase6_root_cause_and_phase7_remediation():
    rca = RootCauseSynthesizer()
    hyps = [{"fault_family": "link_failure", "device": "leaf1", "updated_confidence": 0.95, "falsification_reason": "Carrier down"}]
    rca_res = rca.synthesize(hyps, {"abstain": False}, "leaf1")
    assert rca_res["detected"] is True
    assert rca_res["root_cause"] == "link_failure"

    remediation = RemediationPlanner(confidence_threshold=0.80)
    rem_res = remediation.plan_remediation(rca_res)
    assert rem_res["remediation_proposed"] is True
    assert rem_res["requires_human_approval"] is True
    assert "ip link set eth1 up" in rem_res["proposed_command"]


def test_agent_orchestrator_end_to_end():
    agent = TroubleshootingAgent()
    # Faulty incident
    inc_fault = {
        "incident_id": "INC-0001",
        "scenario": "datacenter_clos",
        "topology_size": "small",
        "ground_truth_has_fault": True,
        "ground_truth_fault_family": "link_failure",
        "ground_truth_device": "leaf1",
        "ticket_text": "Interface eth1 down on leaf1"
    }
    env_fault = MockNetworkEnv("datacenter_clos", "small", fault_injected=True, fault_family="link_failure", faulty_device="leaf1")
    out_fault = agent.troubleshoot(inc_fault, env_fault)
    assert out_fault["detected"] is True
    assert out_fault["root_cause"] == "link_failure"
    assert out_fault["turns_used"] <= 20

    # Healthy incident (Sub-Gap A test)
    inc_healthy = {
        "incident_id": "INC-0002",
        "scenario": "datacenter_clos",
        "topology_size": "small",
        "is_healthy_control": True,
        "ground_truth_has_fault": False,
        "ground_truth_fault_family": "healthy",
        "ground_truth_device": "none",
        "ticket_text": "URGENT: leaf1 has blown up!"
    }
    env_healthy = MockNetworkEnv("datacenter_clos", "small", fault_injected=False)
    out_healthy = agent.troubleshoot(inc_healthy, env_healthy)
    assert out_healthy["detected"] is False
    assert out_healthy["root_cause"] == "none"
    assert out_healthy["abstain_invoked"] is True

