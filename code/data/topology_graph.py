"""
Topology Graph Builder and Dependency Reasoner
Grounding: RCLAgent (Zhang et al., 2026) evidence graph and NIKA network topologies.
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
        """Constructs canonical topologies corresponding to NIKA and FaulT-Bench scenarios."""
        # Determine node count scale
        if self.topology_size == "small":
            node_mult = 1
        elif self.topology_size == "large":
            node_mult = 8
        else:
            node_mult = 3

        if "clos" in self.scenario_name or "datacenter" in self.scenario_name:
            # 2-tier or 3-tier CLOS spine-leaf
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

        elif "isp" in self.scenario_name or "transit" in self.scenario_name:
            # Ring and mesh backbone
            num_routers = max(6, 6 * node_mult // 2)
            routers = [f"cr{i+1}" for i in range(num_routers)]
            for r in routers:
                self.graph.add_node(r, role="core_router", layer="wan", status="up")
            for i in range(num_routers):
                # Ring + cross chords
                self.graph.add_edge(routers[i], routers[(i + 1) % num_routers], bandwidth="400Gbps", loss=0.0, delay=5.0)
                if num_routers > 4:
                    self.graph.add_edge(routers[i], routers[(i + 2) % num_routers], bandwidth="100Gbps", loss=0.0, delay=8.0)

        elif "sdn" in self.scenario_name or "cloud" in self.scenario_name:
            # SDN Controller and OpenFlow forwarders
            ctrl = "sdn_ctrl_1"
            self.graph.add_node(ctrl, role="controller", layer="control", status="up")
            num_switches = max(4, 4 * node_mult // 2)
            switches = [f"sw{i+1}" for i in range(num_switches)]
            for sw in switches:
                self.graph.add_node(sw, role="openflow_switch", layer="forwarding", status="up")
                self.graph.add_edge(ctrl, sw, bandwidth="10Gbps", loss=0.0, delay=2.0)
            for i in range(len(switches) - 1):
                self.graph.add_edge(switches[i], switches[i+1], bandwidth="40Gbps", loss=0.0, delay=1.5)

        else:
            # Default enterprise / campus campus_core_access
            core1, core2 = "core_sw1", "core_sw2"
            dist1, dist2 = "dist_sw1", "dist_sw2"
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
