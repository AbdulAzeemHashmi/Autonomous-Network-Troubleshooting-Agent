"""
Mock Network Environment & Telemetry Emulator
Grounding: NIKA (Wang et al., 2025) Kathara MCP interface and FaulT-Bench tool harness.
Simulates command executions across L2, L3, L4, and Service layers.
"""

from typing import Dict, Any, Optional, List
from code.data.topology_graph import TopologyGraph


class MockNetworkEnv:
    """Emulates live command-line execution and telemetry on network nodes."""

    def __init__(
        self,
        scenario: str,
        topology_size: str = "medium",
        fault_injected: bool = True,
        fault_family: str = "link_failure",
        faulty_device: Optional[str] = None,
        fault_parameters: Optional[Dict[str, Any]] = None
    ):
        self.scenario = scenario
        self.topology_size = topology_size
        self.fault_injected = fault_injected
        self.fault_family = fault_family
        self.fault_parameters = fault_parameters or {}
        self.topo = TopologyGraph(scenario, topology_size)
        nodes = self.topo.get_nodes()

        # If faulty device is not provided, pick an appropriate node
        if faulty_device and faulty_device in nodes:
            self.faulty_device = faulty_device
        else:
            self.faulty_device = nodes[1] if len(nodes) > 1 else nodes[0]

        self.execution_history: List[Dict[str, Any]] = []

    def execute_command(self, device: str, command: str) -> str:
        """Executes a diagnostic command on a target device and returns standard output."""
        self.execution_history.append({"device": device, "command": command})
        cmd = command.strip().lower()
        is_faulty = (self.fault_injected and device == self.faulty_device)

        # -------------------------------------------------------------
        # L2 Commands
        # -------------------------------------------------------------
        if "show interface" in cmd or "ip link" in cmd:
            if is_faulty and self.fault_family == "link_failure":
                return (
                    f"Interface eth1 is DOWN, line protocol is DOWN\n"
                    f"  Hardware is Ethernet, address is 52:54:00:12:34:56\n"
                    f"  Link state: NO-CARRIER, carrier lost 14 seconds ago\n"
                    f"  0 packets input, 0 bytes, 0 errors, 0 dropped\n"
                    f"  0 packets output, 0 bytes, 0 errors, 0 dropped"
                )
            elif is_faulty and self.fault_family == "hardware_transceiver":
                return (
                    f"Interface eth1 is UP, line protocol is UP\n"
                    f"  Hardware is 100GBASE-LR4, address is 52:54:00:12:34:56\n"
                    f"  1428591 packets input, 19482910 bytes\n"
                    f"  48291 CRC errors, 12044 frame errors, 891 runts, 0 giants\n"
                    f"  Rx optical power: -19.4 dBm (Threshold: -14.0 dBm ALARM LOW)"
                )
            else:
                return (
                    f"Interface eth0 is UP, line protocol is UP\n"
                    f"  Hardware is Ethernet, address is 52:54:00:aa:bb:cc\n"
                    f"  Link state: ACTIVE, full-duplex, 100Gbps\n"
                    f"  549102 packets input, 491029140 bytes, 0 CRC errors, 0 dropped\n"
                    f"  549011 packets output, 489912019 bytes, 0 collisions"
                )

        if "show mac" in cmd or "bridge fdb" in cmd:
            if is_faulty and self.fault_family == "link_failure":
                return "Mac Address Table: Empty on eth1 (port down)"
            return (
                "Mac Address Table\n"
                "Vlan    Mac Address       Type        Ports\n"
                "----    -----------       --------    -----\n"
                "10      52:54:00:aa:bb:cc DYNAMIC     eth0\n"
                "10      52:54:00:11:22:33 DYNAMIC     eth1\n"
                "Total Mac Addresses for this criterion: 2"
            )

        # -------------------------------------------------------------
        # L3 Commands
        # -------------------------------------------------------------
        if "ping" in cmd:
            if is_faulty and self.fault_family == "link_failure":
                return (
                    "PING target (10.0.1.5) 56(84) bytes of data.\n"
                    "From 10.0.1.1 icmp_seq=1 Destination Host Unreachable\n"
                    "From 10.0.1.1 icmp_seq=2 Destination Host Unreachable\n"
                    "--- target ping statistics ---\n"
                    "5 packets transmitted, 0 received, 100% packet loss"
                )
            elif is_faulty and self.fault_family == "congestion":
                return (
                    "PING target (10.0.1.5) 56(84) bytes of data.\n"
                    "64 bytes from 10.0.1.5: icmp_seq=1 ttl=62 time=312.4 ms\n"
                    "64 bytes from 10.0.1.5: icmp_seq=3 ttl=62 time=428.1 ms\n"
                    "--- target ping statistics ---\n"
                    "5 packets transmitted, 2 received, 60% packet loss, time 4010ms\n"
                    "rtt min/avg/max/mdev = 312.4/370.2/428.1/57.8 ms"
                )
            elif is_faulty and self.fault_family == "routing_misconfiguration":
                return (
                    "PING target (10.0.2.10) 56(84) bytes of data.\n"
                    "From 10.0.0.1 icmp_seq=1 Destination Net Unreachable\n"
                    "From 10.0.0.1 icmp_seq=2 Destination Net Unreachable\n"
                    "--- target ping statistics ---\n"
                    "5 packets transmitted, 0 received, 100% packet loss"
                )
            elif is_faulty and self.fault_family == "acl_firewall_block":
                return (
                    "PING target (10.0.1.50) 56(84) bytes of data.\n"
                    "From 10.0.1.254 icmp_seq=1 Packet filtered\n"
                    "From 10.0.1.254 icmp_seq=2 Destination Host Prohibited\n"
                    "--- target ping statistics ---\n"
                    "5 packets transmitted, 0 received, 100% packet loss"
                )
            else:
                return (
                    "PING target (10.0.0.2) 56(84) bytes of data.\n"
                    "64 bytes from 10.0.0.2: icmp_seq=1 ttl=64 time=0.82 ms\n"
                    "64 bytes from 10.0.0.2: icmp_seq=2 ttl=64 time=0.79 ms\n"
                    "--- target ping statistics ---\n"
                    "5 packets transmitted, 5 received, 0% packet loss, time 4001ms\n"
                    "rtt min/avg/max/mdev = 0.79/0.83/0.91/0.04 ms"
                )

        if "traceroute" in cmd:
            if is_faulty and self.fault_family == "routing_misconfiguration":
                return (
                    "traceroute to 10.0.2.10 (10.0.2.10), 30 hops max\n"
                    " 1  10.0.0.1 (10.0.0.1)  0.721 ms  0.680 ms\n"
                    " 2  * * * (Routing loop detected / blackhole)\n"
                    " 3  * * *"
                )
            return (
                "traceroute to 10.0.2.10 (10.0.2.10), 30 hops max\n"
                " 1  10.0.0.1 (10.0.0.1)  0.721 ms  0.680 ms\n"
                " 2  10.0.1.2 (10.0.1.2)  1.420 ms  1.398 ms\n"
                " 3  10.0.2.10 (10.0.2.10) 2.110 ms  2.091 ms"
            )

        if "show ip route" in cmd or "ip route" in cmd:
            if is_faulty and self.fault_family == "routing_misconfiguration":
                return (
                    "Codes: K - kernel, C - connected, S - static, R - RIP, B - BGP, O - OSPF\n"
                    "C>* 10.0.0.0/24 is directly connected, eth0\n"
                    "S   10.0.2.0/24 [1/0] via Null0 (blackhole misconfiguration)\n"
                    "Gateway of last resort is not set"
                )
            return (
                "Codes: K - kernel, C - connected, S - static, R - RIP, B - BGP, O - OSPF\n"
                "C>* 10.0.0.0/24 is directly connected, eth0\n"
                "O>* 10.0.1.0/24 [110/20] via 10.0.0.2, eth0\n"
                "O>* 10.0.2.0/24 [110/30] via 10.0.0.2, eth0\n"
                "O>* 0.0.0.0/0 [110/10] via 10.0.0.254, eth0"
            )

        # -------------------------------------------------------------
        # L4 & Sockets
        # -------------------------------------------------------------
        if "ss" in cmd or "netstat" in cmd:
            if is_faulty and self.fault_family == "service_failure":
                return (
                    "State      Recv-Q Send-Q Local Address:Port Peer Address:Port\n"
                    "LISTEN     0      128          *:22               *:*\n"
                    "Note: Process on port 80/443 (nginx) is dead/inactive"
                )
            return (
                "State      Recv-Q Send-Q Local Address:Port Peer Address:Port\n"
                "LISTEN     0      128          *:22               *:*\n"
                "LISTEN     0      511          *:80               *:*\n"
                "LISTEN     0      511          *:443              *:*\n"
                "ESTAB      0      0     10.0.0.2:80       10.0.1.15:49152"
            )

        # -------------------------------------------------------------
        # Services & Applications
        # -------------------------------------------------------------
        if "curl" in cmd or "http" in cmd:
            if is_faulty and self.fault_family == "service_failure":
                return "curl: (7) Failed to connect to port 80: Connection refused"
            elif is_faulty and self.fault_family == "acl_firewall_block":
                return "curl: (28) Failed to connect to 10.0.1.50: Connection timed out"
            return "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: 26\r\n\r\n{\"status\":\"healthy_ok\"}"

        if "dns" in cmd or "dig" in cmd or "nslookup" in cmd:
            if is_faulty and self.fault_family == "dns_failure":
                return ";; connection timed out; no servers could be reached\n;; Got SERVFAIL / NXDOMAIN"
            return (
                ";; ANSWER SECTION:\n"
                "api.internal.corp.   300   IN   A   10.0.2.50\n"
                ";; Query time: 1 msec\n;; SERVER: 10.0.0.53#53(10.0.0.53)"
            )

        if "check_queue_drops" in cmd or "tc -s qdisc" in cmd:
            if is_faulty and self.fault_family == "congestion":
                return (
                    "qdisc fq_codel 8001: dev eth0 root refcnt 2 limit 10240p flows 1024\n"
                    "  Sent 49819201 bytes 35819 pkt (dropped 8914, overlimits 12041 requeues 0)\n"
                    "  backlog 480100b 341p requeues 0\n"
                    "  queue utilization 98.4% (CONGESTION ALERT)"
                )
            return (
                "qdisc fq_codel 8001: dev eth0 root refcnt 2 limit 10240p flows 1024\n"
                "  Sent 10928120 bytes 8192 pkt (dropped 0, overlimits 0 requeues 0)\n"
                "  backlog 0b 0p requeues 0\n"
                "  queue utilization 2.1% (NORMAL)"
            )

        if "check_firewall_rules" in cmd or "iptables" in cmd:
            if is_faulty and self.fault_family == "acl_firewall_block":
                return (
                    "Chain FORWARD (policy ACCEPT 10 pkts, 640 bytes)\n"
                    "num   pkts bytes target     prot opt in     out     source      destination\n"
                    "1     4219  280K DROP       all  --  *      *       0.0.0.0/0   10.0.1.50   /* ACL-BLOCK-DENY */\n"
                    "2     198K  142M ACCEPT     all  --  *      *       0.0.0.0/0   0.0.0.0/0"
                )
            return (
                "Chain FORWARD (policy ACCEPT 48192 pkts, 32M bytes)\n"
                "num   pkts bytes target     prot opt in     out     source      destination\n"
                "1     48192  32M ACCEPT     all  --  *      *       0.0.0.0/0   0.0.0.0/0"
            )

        # Default fallback command response
        return f"Device {device} response to '{command}': command executed successfully with code 0."
