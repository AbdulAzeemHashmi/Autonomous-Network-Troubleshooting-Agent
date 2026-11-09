"""
Unit tests for all 5 baseline architectures.
"""

import pytest
from code.data.mock_network_env import MockNetworkEnv
from code.baselines.zero_shot import ZeroShotAgent
from code.baselines.react_agent import ReActAgent
from code.baselines.coding_agent import CodingAgent
from code.baselines.sade_style import SADEAgent
from code.baselines.scripted_rules import ScriptedRuleAgent


def test_zero_shot_baseline():
    agent = ZeroShotAgent()
    inc = {"ticket_text": "Severe link down on eth1 on leaf1", "is_healthy_control": False}
    env = MockNetworkEnv("datacenter_clos", "small")
    res = agent.troubleshoot(inc, env)
    assert res["detected"] is True
    assert res["root_cause"] == "link_failure"
    assert res["turns_used"] == 1


def test_react_baseline():
    agent = ReActAgent()
    inc = {"ticket_text": "Investigate leaf1", "is_healthy_control": False}
    env = MockNetworkEnv("datacenter_clos", "small", fault_injected=True, fault_family="link_failure", faulty_device="leaf1")
    res = agent.troubleshoot(inc, env)
    assert res["detected"] is True
    assert res["turns_used"] > 0
    assert res["cost_usd"] > 0


def test_coding_agent_baseline():
    agent = CodingAgent()
    inc = {"ticket_text": "Service check on leaf1", "is_healthy_control": False}
    env = MockNetworkEnv("datacenter_clos", "small", fault_injected=True, fault_family="service_failure", faulty_device="leaf1")
    res = agent.troubleshoot(inc, env)
    assert res["detected"] is True
    assert res["input_tokens"] > 500


def test_sade_style_baseline():
    agent = SADEAgent()
    # On healthy control, SADE over-diagnoses (as shown in FaulT-Bench paper)
    inc_healthy = {"ticket_text": "Check leaf1 please", "is_healthy_control": True}
    env_healthy = MockNetworkEnv("datacenter_clos", "small", fault_injected=False)
    res_healthy = agent.troubleshoot(inc_healthy, env_healthy)
    assert res_healthy["detected"] is True
    assert res_healthy["abstain_invoked"] is False


def test_scripted_rules_baseline():
    agent = ScriptedRuleAgent()
    inc_fault = {"ticket_text": "Check leaf1", "is_healthy_control": False}
    env_fault = MockNetworkEnv("datacenter_clos", "small", fault_injected=True, fault_family="link_failure", faulty_device="leaf1")
    res_fault = agent.troubleshoot(inc_fault, env_fault)
    assert res_fault["detected"] is True
    assert res_fault["root_cause"] == "link_failure"
    assert res_fault["cost_usd"] == 0.0

    # Healthy check
    env_healthy = MockNetworkEnv("datacenter_clos", "small", fault_injected=False)
    res_healthy = agent.troubleshoot(inc_fault, env_healthy)
    assert res_healthy["detected"] is False
