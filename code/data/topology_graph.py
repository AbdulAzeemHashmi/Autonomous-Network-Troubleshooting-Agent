"""
Topology Graph Builder and Dependency Reasoner
Grounding: RCLAgent (Zhang et al., 2026) evidence graph, NIKA network topologies,
and Course Recommended Datasets (Abilene Internet2 Backbone and NetManAIOps).
"""

from typing import Dict, List, Any, Optional
import networkx as nx


class TopologyGraph:
    """Manages network topology graphs, path computations, and upstream/downstream dependency tracking."""

    def __init__(self, scenario_name: str, topology_size: str = "medium"):
        self.scenario_name = scenario_name
        self.topology_size = topology_size
        self.graph = nx.Graph()
        self._build_topology()

    def _build_topology(self):
        """Constructs canonical topologies corresponding to NIKA, FaulT-Bench, Abilene, and NetManAIOps."""
        # Determine node count scale
        if self.topology_size == "small":
            node_mult = 1
        elif self.topology_size == "large":
            node_mult = 8
        else:
            node_mult = 3

        # -------------------------------------------------------------
        # 1. Course Recommended Benchmark: Abilene Network (Internet2 11-node backbone)
        # -------------------------------------------------------------
        if "abilene" in self.scenario_name:
            nodes_abilene = [
                "ATLA", "CHIN", "DNVR", "HSTN", "IPLS",
                "KSCY", "LOSA", "NYCM", "SNVA", "STTL", "WASH"
            ]
            for n in nodes_abilene:
                self.graph.add_node(n, role="core_router", layer="backbone", status="up")

            abilene_links = [
                ("STTL", "SNVA", 10.0), ("STTL", "DNVR", 15.0),
                ("SNVA", "LOSA", 5.0),  ("SNVA", "DNVR", 12.0),
                ("LOSA", "HSTN", 18.0), ("DNVR", "KSCY", 8.0),
                ("KSCY", "IPLS", 6.0),  ("KSCY", "HSTN", 10.0),
                ("IPLS", "CHIN", 4.0),  ("IPLS", "ATLA", 8.0),
                ("CHIN", "NYCM", 11.0), ("HSTN", "ATLA", 9.0),
                ("ATLA", "WASH", 7.0),  ("WASH", "NYCM", 3.0)
            ]
            for u, v, d in abilene_links:
                self.graph.add_edge(u, v, bandwidth="100Gbps", loss=0.0, delay=d)

            # In medium and large variants, attach regional ingress/egress edge switches
            if self.topology_size in ["medium", "large"]:
                num_edge_per_core = 2 if self.topology_size == "medium" else 6
                for core in nodes_abilene:
                    for e_idx in range(num_edge_per_core):
                        edge_name = f"{core.lower()}_edge_{e_idx+1}"
                        self.graph.add_node(edge_name, role="edge_router", layer="access", status="up")
                        self.graph.add_edge(core, edge_name, bandwidth="10Gbps", loss=0.0, delay=1.0)

        # -------------------------------------------------------------
        # 2. Course Recommended Benchmark: NetManAIOps Multi-tier Enterprise Network
        # -------------------------------------------------------------
        elif "netman" in self.scenario_name or "aiops" in self.scenario_name:
            core_gateways = ["core_gw1", "core_gw2"]
            agg_switches = ["agg_sw1", "agg_sw2", "agg_sw3"]
            acc_switches = [f"acc_sw{i+1}" for i in range(max(4, 4 * node_mult // 2))]
            service_nodes = ["auth_srv", "db_cluster_primary", "api_gateway", "cache_node"]

            for cg in core_gateways:
                self.graph.add_node(cg, role="core_gateway", layer="core", status="up")
            self.graph.add_edge("core_gw1", "core_gw2", bandwidth="100Gbps", loss=0.0, delay=0.5)

            for agg in agg_switches:
                self.graph.add_node(agg, role="aggregation", layer="distribution", status="up")
                for cg in core_gateways:
                    self.graph.add_edge(cg, agg, bandwidth="40Gbps", loss=0.0, delay=1.0)

            for i, acc in enumerate(acc_switches):
                self.graph.add_node(acc, role="access", layer="edge", status="up")
                self.graph.add_edge(agg_switches[i % len(agg_switches)], acc, bandwidth="10Gbps", loss=0.0, delay=1.5)

            for i, srv in enumerate(service_nodes):
                self.graph.add_node(srv, role="service_host", layer="application", status="up")
                self.graph.add_edge(acc_switches[i % len(acc_switches)], srv, bandwidth="10Gbps", loss=0.0, delay=0.5)

        # -------------------------------------------------------------
        # 3. CLOS Leaf-Spine Architecture (NIKA & FaulT-Bench)
        # -------------------------------------------------------------
        elif "clos" in self.scenario_name or "datacenter" in self.scenario_name:
            num_spines = max(2, 2 * node_mult // 2)
            num_leafs = max(4, 4 * node_mult // 2)
            num_servers = max(4, 4 * node_mult // 2)

            spines = [f"spine{i+1}" for i in range(num_spines)]
            leafs = [f"leaf{i+1}" for i in range(num_leafs)]
            servers = [f"srv{i+1}" for i in range(num_servers)]

            for s in spines:
                self.graph.add_node(s, role="spine", layer="core", status="up")
            for l in leafs:
                self.graph.add_node(l, role="leaf", layer="aggregation", status="up")
                for s in spines:
                    self.graph.add_edge(s, l, bandwidth="100Gbps", loss=0.0, delay=1.0)
            for i, srv in enumerate(servers):
                target_leaf = leafs[i % len(leafs)]
                self.graph.add_node(srv, role="host", layer="access", status="up")
                self.graph.add_edge(target_leaf, srv, bandwidth="25Gbps", loss=0.0, delay=0.5)

        # -------------------------------------------------------------
        # 4. ISP and Transit WAN Backbones
        # -------------------------------------------------------------
        elif "isp" in self.scenario_name or "transit" in self.scenario_name:
            num_routers = max(6, 6 * node_mult // 2)
            routers = [f"cr{i+1}" for i in range(num_routers)]
            for r in routers:
                self.graph.add_node(r, role="core_router", layer="wan", status="up")
            for i in range(num_routers):
                self.graph.add_edge(routers[i], routers[(i + 1) % num_routers], bandwidth="400Gbps", loss=0.0, delay=5.0)
                if num_routers > 4:
                    self.graph.add_edge(routers[i], routers[(i + 2) % num_routers], bandwidth="100Gbps", loss=0.0, delay=8.0)

        # -------------------------------------------------------------
        # 5. SDN Cloud Fabric
        # -------------------------------------------------------------
        elif "sdn" in self.scenario_name or "cloud" in self.scenario_name:
            ctrl = "sdn_ctrl_1"
            self.graph.add_node(ctrl, role="controller", layer="control", status="up")
            num_switches = max(4, 4 * node_mult // 2)
            switches = [f"sw{i+1}" for i in range(num_switches)]
            for sw in switches:
                self.graph.add_node(sw, role="openflow_switch", layer="forwarding", status="up")
                self.graph.add_edge(ctrl, sw, bandwidth="10Gbps", loss=0.0, delay=2.0)
            for i in range(len(switches) - 1):
                self.graph.add_edge(switches[i], switches[i+1], bandwidth="40Gbps", loss=0.0, delay=1.5)

        # -------------------------------------------------------------
        # 6. Default Enterprise / Campus Topology
        # -------------------------------------------------------------
        else:
            core1, core2 = "core_sw1", "core_sw2"
            self.graph.add_node(core1, role="core", layer="core", status="up")
            self.graph.add_node(core2, role="core", layer="core", status="up")
            self.graph.add_edge(core1, core2, bandwidth="40Gbps", loss=0.0, delay=0.5)

            num_access = max(4, 4 * node_mult // 2)
            access_sws = [f"access_sw{i+1}" for i in range(num_access)]
            for acc in access_sws:
                self.graph.add_node(acc, role="access", layer="edge", status="up")
                self.graph.add_edge(core1, acc, bandwidth="10Gbps", loss=0.0, delay=1.0)
                self.graph.add_edge(core2, acc, bandwidth="10Gbps", loss=0.0, delay=1.0)

    def get_nodes(self) -> List[str]:
        return list(self.graph.nodes())

    def get_neighbors(self, node: str) -> List[str]:
        if node in self.graph:
            return list(self.graph.neighbors(node))
        return []

    def get_shortest_path(self, src: str, dst: str) -> Optional[List[str]]:
        if src in self.graph and dst in self.graph:
            try:
                return nx.shortest_path(self.graph, src, dst)
            except nx.NetworkXNoPath:
                return None
        return None

    def summarize(self) -> str:
        return (f"Topology: {self.scenario_name} ({self.topology_size}) - "
                f"Nodes: {self.graph.number_of_nodes()}, Edges: {self.graph.number_of_edges()}")
