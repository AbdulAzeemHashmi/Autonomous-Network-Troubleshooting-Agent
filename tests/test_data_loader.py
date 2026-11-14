"""
Unit tests for data loaders, preprocessing, healthy controls, topology builder,
and Course Recommended Benchmarks (Abilene and NetManAIOps).
"""

import pytest
import os
from code.data.loader import IncidentDataset
from code.data.preprocessing import Preprocessor
from code.data.fault_family_index import lookup_symptom, FAULT_FAMILIES
from code.data.topology_graph import TopologyGraph
from code.data.mock_network_env import MockNetworkEnv


def test_topology_graph_construction():
    topo = TopologyGraph("datacenter_clos", "small")
    assert topo.graph.number_of_nodes() >= 8
    assert topo.graph.number_of_edges() >= 8
    nodes = topo.get_nodes()
    assert len(nodes) > 0


def test_course_benchmarks_topologies():
    # Test Abilene 11-node core backbone
    abilene = TopologyGraph("abilene_backbone", "small")
    assert abilene.graph.number_of_nodes() == 11
    assert "ATLA" in abilene.get_nodes()
    assert "SNVA" in abilene.get_nodes()
    assert abilene.graph.number_of_edges() >= 14

    # Test NetManAIOps enterprise multi-service topology
    netman = TopologyGraph("netman_aiops", "medium")
    assert netman.graph.number_of_nodes() >= 12
    assert "core_gw1" in netman.get_nodes()
    assert "db_cluster_primary" in netman.get_nodes()


def test_fault_family_index():
    assert "link_failure" in FAULT_FAMILIES
    matches = lookup_symptom("Interface eth1 line protocol is DOWN, carrier lost")
    assert len(matches) > 0
    assert matches[0]["family"] == "link_failure"


def test_dataset_generation_and_audit(tmp_path):
    dataset_mgr = IncidentDataset()
    incidents = dataset_mgr.generate_benchmark_dataset(total_target=20, healthy_ratio=0.25)
    assert len(incidents) == 20

    healthy_count = sum(1 for inc in incidents if inc["is_healthy_control"])
    assert healthy_count == 5

    preprocessor = Preprocessor(max_tokens=500)
    audit_csv = str(tmp_path / "test_audit.csv")
    valid_incidents, audit_df = preprocessor.audit_fault_injections(incidents, audit_csv)

    assert len(valid_incidents) == 20
    assert os.path.exists(audit_csv)
    assert len(audit_df) == 20


def test_mock_network_env_execution():
    env = MockNetworkEnv("campus_network", "small", fault_injected=True, fault_family="link_failure", faulty_device="dist_sw1")
    out = env.execute_command("dist_sw1", "show interface eth1")
    assert "DOWN" in out or "NO-CARRIER" in out

    out_ping = env.execute_command("dist_sw1", "ping target")
    assert "Destination Host Unreachable" in out_ping
