"""
Unit tests for Google Gemini LLM Client, prompt extraction, and fallback mechanisms.
Grounding: Phase 2 Step 5 (LLM Reasoning Engine) and Step 8 (LLM-as-a-Judge).
"""

import pytest
import os
import json
from code.agent.llm_client import GeminiClient
from code.agent.ticket_validator import TicketValidator
from code.experiments.runner import LLMJudge
from code.data.mock_network_env import MockNetworkEnv


def test_gemini_client_initialization():
    client = GeminiClient(api_key="test_key_gemini", model_name="gemini-1.5-flash")
    assert client.model_name == "gemini-1.5-flash"
    assert client.api_key == "test_key_gemini"


def test_gemini_client_simulated_fallback():
    client = GeminiClient(api_key=None, model_name="gemini-1.5-flash")
    res = client.generate_text("Validate ticket: link is down")
    assert "text" in res
    assert res["model"] == "gemini-1.5-flash"
    assert res["input_tokens"] > 0
    assert res["output_tokens"] > 0


def test_gemini_client_json_extraction():
    client = GeminiClient(api_key=None, model_name="gemini-1.5-flash")
    res = client.generate_json("Evaluate ticket_valid for healthy network")
    assert "parsed_json" in res
    assert isinstance(res["parsed_json"], dict)


def test_ticket_validator_with_gemini_client():
    client = GeminiClient(api_key="mock_key", model_name="gemini-1.5-flash")
    validator = TicketValidator(llm_client=client, use_llm=True)
    env = MockNetworkEnv(scenario="datacenter_clos", topology_size="small", fault_injected=False)

    ticket = "Users report high latency to server A, but ping shows 0% loss and link is UP."
    res = validator.validate(ticket, env, "Small CLOS topology")
    assert "ticket_valid" in res
    assert res["ticket_valid"] is False


def test_llm_judge_with_gemini_client():
    client = GeminiClient(api_key="mock_key", model_name="gemini-1.5-flash")
    judge = LLMJudge(llm_client=client, use_llm=True)

    incident = {
        "scenario": "datacenter_clos",
        "ground_truth_has_fault": True,
        "ground_truth_fault_family": "link_failure",
        "ground_truth_device": "leaf_sw1",
        "ground_truth_fix": "no shut eth1"
    }
    agent_out = {
        "ticket_valid": True,
        "detected": True,
        "localized_device": "leaf_sw1",
        "root_cause": "link_failure",
        "confidence": 0.95,
        "remediation": {"remediation_proposed": True, "requires_human_approval": True, "pre_flight_check": "ping target"},
        "trace_logs": [{"turn": 1, "action": "ticket_validation"}]
    }

    scores = judge.evaluate(incident, agent_out)
    assert "overall_judge_score" in scores
    assert 1.0 <= scores["overall_judge_score"] <= 5.0
    assert scores["outcome_score"] == 5.0
