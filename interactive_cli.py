#!/usr/bin/env python3
"""
Interactive CLI Demonstrator for Autonomous Network Troubleshooting Agent
Course: Computer Networks | FAST-NUCES
Authors: Abdul Azeem (24I-2013), Taha Amjad (24K-0007)

Allows interactive troubleshooting on any of the 15 supported topologies
with verbose step-by-step display of each of the seven agent phases.
"""

import sys
import os
import argparse
from typing import Dict, Any

from code.data.loader import (
    NIKA_SCENARIOS,
    FAULT_BENCH_TOPOLOGIES,
    COURSE_RECOMMENDED_SCENARIOS,
    IncidentDataset
)
from code.data.mock_network_env import MockNetworkEnv
from code.agent.orchestrator import TroubleshootingAgent
from code.agent.llm_client import GeminiClient


def parse_args():
    parser = argparse.ArgumentParser(
        description="Interactive Network Troubleshooting Demonstrator"
    )
    parser.add_argument(
        "--scenario",
        type=str,
        default="abilene_backbone",
        help="Target topology scenario (e.g., abilene_backbone, netman_aiops, datacenter_clos, etc.)"
    )
    parser.add_argument(
        "--healthy",
        action="store_true",
        help="Simulate a healthy network control with a false-alarm ticket"
    )
    parser.add_argument(
        "--use_live_llm",
        action="store_true",
        help="Invoke live Google Gemini API"
    )
    parser.add_argument(
        "--gemini_api_key",
        type=str,
        default="AQ.Ab8RN6Jm756xpaJsA3EJUqblruoGPIx_QochLYy4HS2yW0LhXQ",
        help="Google Gemini API key"
    )
    parser.add_argument(
        "--gemini_model",
        type=str,
        default="gemini-1.5-flash",
        help="Gemini model name (gemini-1.5-flash, gemini-2.0-flash)"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print("=" * 80)
    print("AUTONOMOUS NETWORK TROUBLESHOOTING AGENT - INTERACTIVE DEMO")
    print("Course: Computer Networks (CS-3001) | FAST-NUCES")
    print("Authors: Abdul Azeem (24I-2013), Taha Amjad (24K-0007)")
    print("=" * 80)

    dataset_mgr = IncidentDataset()
    incidents = dataset_mgr.generate_benchmark_dataset(total_target=60, healthy_ratio=0.25)

    # Find a matching incident
    matching = [
        inc for inc in incidents
        if inc["scenario"] == args.scenario and inc["ground_truth_has_fault"] == (not args.healthy)
    ]
    if not matching:
        matching = [inc for inc in incidents if inc["ground_truth_has_fault"] == (not args.healthy)]

    target_incident = matching[0] if matching else incidents[0]

    print(f"\n[+] Loaded Scenario: {target_incident['scenario']}")
    print(f"[+] Topology Size:   {target_incident['topology_size']}")
    print(f"[+] Ground Truth:    {'Fault Injected: ' + target_incident['ground_truth_fault_family'] if target_incident['ground_truth_has_fault'] else 'Healthy Control (No Fault)'}")
    print(f"[+] Reported Ticket: \"{target_incident['ticket_text']}\"")

    env = MockNetworkEnv(
        scenario=target_incident["scenario"],
        topology_size=target_incident["topology_size"],
        fault_injected=target_incident["ground_truth_has_fault"],
        fault_family=target_incident["ground_truth_fault_family"],
        faulty_device=target_incident["ground_truth_device"]
    )

    llm_client = GeminiClient(api_key=args.gemini_api_key, model_name=args.gemini_model)

    agent = TroubleshootingAgent(
        turn_budget=20,
        llm_client=llm_client,
        use_llm=args.use_live_llm
    )

    print("\n" + "-" * 80)
    print(">>> Executing 7-Phase Diagnostic Escalation...")
    print("-" * 80)

    res = agent.troubleshoot(target_incident, env)

    print("\n--- PHASE-BY-PHASE EXECUTION TRACE ---")
    for log in res.get("trace_logs", []):
        phase_num = log.get("phase", "?")
        action = log.get("action", "")
        print(f"  [Turn {log.get('turn', 0)}] Phase {phase_num}: {action}")

    print("\n" + "=" * 80)
    print("FINAL DIAGNOSTIC REPORT")
    print("=" * 80)
    print(f"Fault Detected:       {res['detected']}")
    print(f"Localized Device:     {res['localized_device']}")
    print(f"Predicted Root Cause: {res['root_cause']}")
    print(f"Calibrated Confidence:{res['confidence']}")
    print(f"Abstain Invoked:      {res['abstain_invoked']}")
    print(f"Investigation Turns:  {res['turns_used']} / 20")
    print(f"Elapsed Time:         {res['time_seconds']}s")
    print(f"Token Consumption:    {res['input_tokens']} in / {res['output_tokens']} out")
    print(f"Estimated Dollar Cost: ${res['cost_usd']}")

    rem = res.get("remediation", {})
    print("\nREMEDIATION PROPOSAL:")
    if rem.get("remediation_proposed", False):
        print(f"  Action:           {rem.get('action_type')}")
        print(f"  Command:          {rem.get('proposed_command')}")
        print(f"  Pre-check:        {rem.get('pre_flight_check')}")
        print(f"  Post-check:       {rem.get('post_flight_check')}")
        print(f"  Rollback:         {rem.get('rollback_procedure')}")
        print(f"  Human Gate Flag:  {rem.get('requires_human_approval')} (MANDATORY APPROVAL)")
    else:
        print(f"  Status: No automated action proposed ({rem.get('reason', 'N/A')})")

    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
