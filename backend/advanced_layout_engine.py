"""
Advanced Auto-Layout Engine for Security Modeling Platform
Implements comprehensive multi-tier layout system with collision detection,
dynamic spacing, multi-ring orbital system, and advanced algorithms.
"""

import math
import networkx as nx
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum
import random
from collections import defaultdict


class LayoutAlgorithm(Enum):
    ENHANCED_SMART_HIERARCHICAL = "enhanced_smart_hierarchical"
    ORGANIC_FLOW = "organic_flow"
    SECURITY_PERIMETER = "security_perimeter"
    FORCE_DIRECTED_ADVANCED = "force_directed_advanced"
    NETWORK_TOPOLOGY_ADVANCED = "network_topology_advanced"


@dataclass
class NodePosition:
    x: float
    y: float
    radius: float = 50.0
    
    def distance_to(self, other: 'NodePosition') -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)


@dataclass
class CanvasDimensions:
    width: int
    height: int
    margin: int = 100


class SpatialGrid:
    """Efficient collision detection using spatial partitioning"""
    
    def __init__(self, width: int, height: int, cell_size: int = 100):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.cols = (width // cell_size) + 1
        self.rows = (height // cell_size) + 1
        self.grid: Dict[Tuple[int, int], List[Tuple[str, NodePosition]]] = defaultdict(list)
        self.node_positions: Dict[str, NodePosition] = {}
    
    def _get_cell_coords(self, x: float, y: float) -> Tuple[int, int]:
        col = max(0, min(self.cols - 1, int(x // self.cell_size)))
        row = max(0, min(self.rows - 1, int(y // self.cell_size)))
        return (col, row)
    
    def add_node(self, node_id: str, position: NodePosition):
        """Add node to spatial grid for collision detection"""
        cell = self._get_cell_coords(position.x, position.y)
        self.grid[cell].append((node_id, position))
        self.node_positions[node_id] = position
    
    def check_collision(self, position: NodePosition, exclude_node: Optional[str] = None) -> bool:
        """Check if position would collide with existing nodes"""
        # Check all surrounding cells
        cell_x, cell_y = self._get_cell_coords(position.x, position.y)
        
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                check_cell = (cell_x + dx, cell_y + dy)
                if check_cell in self.grid:
                    for node_id, node_pos in self.grid[check_cell]:
                        if node_id != exclude_node:
                            distance = position.distance_to(node_pos)
                            min_distance = position.radius + node_pos.radius + 20  # 20px buffer
                            if distance < min_distance:
                                return True
        return False
    
    def find_nearest_free_position(self, preferred_position: NodePosition, 
                                 exclude_node: Optional[str] = None,
                                 max_attempts: int = 100) -> NodePosition:
        """Find nearest position that doesn't collide"""
        if not self.check_collision(preferred_position, exclude_node):
            return preferred_position
        
        # Spiral search pattern
        for radius in range(20, 500, 20):
            for angle in range(0, 360, 15):
                angle_rad = math.radians(angle)
                test_position = NodePosition(
                    x=preferred_position.x + radius * math.cos(angle_rad),
                    y=preferred_position.y + radius * math.sin(angle_rad),
                    radius=preferred_position.radius
                )
                
                if not self.check_collision(test_position, exclude_node):
                    return test_position
        
        # Fallback to original position if no free space found
        return preferred_position


class AdvancedLayoutEngine:
    """Advanced layout engine with comprehensive algorithms and optimization"""
    
    def __init__(self):
        self.spatial_grid: Optional[SpatialGrid] = None
        self.canvas: CanvasDimensions = CanvasDimensions(1920, 1080)
    
    def calculate_optimal_canvas_size(self, node_count: int, vulnerability_count: int) -> CanvasDimensions:
        """Calculate optimal canvas dimensions based on content"""
        base_width = 1920
        base_height = 1080
        
        # Scale based on total node count
        scale_factor = max(1.0, math.sqrt(node_count / 20))
        
        # Additional scaling for high vulnerability density
        vuln_scale = 1 + (vulnerability_count / 100)
        
        # Ensure minimum usable size
        width = max(1920, int(base_width * scale_factor * vuln_scale))
        height = max(1080, int(base_height * scale_factor * vuln_scale))
        
        return CanvasDimensions(width, height, 100)
    
    def select_optimal_layout_algorithm(self, nodes: List[Dict], edges: List[Dict]) -> LayoutAlgorithm:
        """Automatically select best layout algorithm based on content"""
        node_count = len(nodes)
        vulnerability_count = len([n for n in nodes if n.get("type") == "vulnerability"])
        edge_density = len(edges) / (node_count * (node_count - 1)) if node_count > 1 else 0
        
        # High vulnerability density scenarios
        if vulnerability_count > 30:
            return LayoutAlgorithm.ENHANCED_SMART_HIERARCHICAL
        
        # High connectivity scenarios
        elif edge_density > 0.3:
            return LayoutAlgorithm.ORGANIC_FLOW
        
        # Security-focused models with clear zones
        elif self._has_clear_security_zones(nodes):
            return LayoutAlgorithm.SECURITY_PERIMETER
        
        # Default to enhanced hierarchical
        else:
            return LayoutAlgorithm.ENHANCED_SMART_HIERARCHICAL
    
    def _has_clear_security_zones(self, nodes: List[Dict]) -> bool:
        """Check if nodes represent clear security zones"""
        zone_types = ["Actor", "Surface", "Asset", "Control"]
        found_types = set(node.get("type", "") for node in nodes)
        return len(found_types.intersection(zone_types)) >= 3
    
    def generate_layout(self, G: nx.DiGraph, nodes: List[Dict], edges: List[Dict], 
                       algorithm: Optional[LayoutAlgorithm] = None) -> Dict[str, Dict[str, float]]:
        """Generate layout using specified or auto-selected algorithm"""
        
        if algorithm is None:
            algorithm = self.select_optimal_layout_algorithm(nodes, edges)
        
        # Calculate optimal canvas size
        vulnerability_count = len([n for n in nodes if n.get("type") == "vulnerability"])
        self.canvas = self.calculate_optimal_canvas_size(len(nodes), vulnerability_count)
        
        # Initialize spatial grid for collision detection
        self.spatial_grid = SpatialGrid(self.canvas.width, self.canvas.height)
        
        # Execute layout algorithm
        if algorithm == LayoutAlgorithm.ENHANCED_SMART_HIERARCHICAL:
            return self._enhanced_smart_hierarchical_layout(G, nodes)
        elif algorithm == LayoutAlgorithm.ORGANIC_FLOW:
            return self._organic_flow_layout(G, nodes, edges)
        elif algorithm == LayoutAlgorithm.SECURITY_PERIMETER:
            return self._security_perimeter_layout(G, nodes, edges)
        elif algorithm == LayoutAlgorithm.FORCE_DIRECTED_ADVANCED:
            return self._force_directed_advanced_layout(G, nodes, edges)
        elif algorithm == LayoutAlgorithm.NETWORK_TOPOLOGY_ADVANCED:
            return self._network_topology_advanced_layout(G, nodes, edges)
        else:
            return self._enhanced_smart_hierarchical_layout(G, nodes)
    
    def _enhanced_smart_hierarchical_layout(self, G: nx.DiGraph, nodes: List[Dict]) -> Dict[str, Dict[str, float]]:
        """Enhanced hierarchical layout with collision detection and adaptive spacing"""
        
        # Separate node types
        vulnerability_nodes = [n for n in nodes if n.get("type") == "vulnerability"]
        main_nodes = [n for n in nodes if n.get("type") != "vulnerability"]
        
        layout_positions = {}
        
        # Calculate optimal canvas utilization
        total_nodes = len(nodes)
        canvas_utilization = min(0.8, max(0.5, total_nodes / 100))  # 50-80% canvas usage
        
        # Dynamic layer spacing based on node density
        layer_count = len(set(self._get_node_layer(node) for node in main_nodes))
        base_layer_height = max(200, self.canvas.height * 0.15)  # 15% of canvas height per layer
        layer_height = base_layer_height * (1 + (total_nodes / 50))  # Scale with node count
        
        # Position main nodes with enhanced spacing
        layout_positions = self._position_main_nodes_enhanced(main_nodes)
        
        # Position vulnerability nodes with multi-ring orbital system
        self._position_vulnerability_nodes_multi_ring(layout_positions, vulnerability_nodes, main_nodes)
        
        return layout_positions
    
    def _get_node_layer(self, node: Dict) -> int:
        """Get hierarchical layer for a node based on security semantics"""
        layer_order = {
            "Zone": 0,      # Network zones at the top
            "Actor": 1,     # Threat actors 
            "Surface": 2,   # Attack surfaces
            "Asset": 3,     # Protected assets
            "Control": 4,   # Security controls
            "Signal": 5     # Detection signals
        }
        return layer_order.get(node.get("type", "Unknown"), 3)
    
    def _position_main_nodes_enhanced(self, main_nodes: List[Dict]) -> Dict[str, Dict[str, float]]:
        """Position main nodes with enhanced collision detection and spacing"""
        layout_positions = {}
        
        # Group nodes by security layer
        layers = defaultdict(list)
        for node in main_nodes:
            layer = self._get_node_layer(node)
            layers[layer].append(node)
        
        # Calculate dynamic spacing
        max_nodes_per_layer = max(len(nodes) for nodes in layers.values()) if layers else 1
        layer_width = self.canvas.width * 0.8  # Use 80% of canvas width
        base_node_spacing = max(150, layer_width / max_nodes_per_layer)
        
        # Position nodes layer by layer
        for layer_idx, layer_nodes in sorted(layers.items()):
            y_pos = self.canvas.margin + (layer_idx * (self.canvas.height * 0.15))
            
            # Calculate x positions with collision avoidance
            total_width = len(layer_nodes) * base_node_spacing
            start_x = (self.canvas.width - total_width) / 2
            
            # Group by subtype for better organization
            subtype_groups = defaultdict(list)
            for node in layer_nodes:
                subtype = node.get("subtype", "default")
                subtype_groups[subtype].append(node)
            
            current_x = start_x
            for subtype, subtype_nodes in subtype_groups.items():
                for node in subtype_nodes:
                    # Find collision-free position
                    preferred_pos = NodePosition(current_x, y_pos, 50)
                    final_pos = self.spatial_grid.find_nearest_free_position(preferred_pos)
                    
                    layout_positions[node["id"]] = {
                        "x": final_pos.x,
                        "y": final_pos.y
                    }
                    
                    # Add to spatial grid
                    self.spatial_grid.add_node(node["id"], final_pos)
                    current_x += base_node_spacing
                
                current_x += base_node_spacing * 0.5  # Gap between subtypes
        
        return layout_positions
    
    def calculate_optimal_rings(self, vulnerability_count: int) -> List[Tuple[int, float]]:
        """Calculate optimal number of rings and nodes per ring"""
        if vulnerability_count <= 6:
            return [(vulnerability_count, 120)]  # Single ring
        elif vulnerability_count <= 18:
            inner_count = min(8, vulnerability_count // 2)
            outer_count = vulnerability_count - inner_count
            return [(inner_count, 120), (outer_count, 200)]  # Two rings
        else:
            # Three rings for high density
            inner = min(8, vulnerability_count // 3)
            middle = min(12, (vulnerability_count - inner) // 2)
            outer = vulnerability_count - inner - middle
            return [(inner, 120), (middle, 200), (outer, 280)]
    
    def _position_vulnerability_nodes_multi_ring(self, layout_positions: Dict, 
                                               vulnerability_nodes: List[Dict], 
                                               main_nodes: List[Dict]):
        """Position vulnerability nodes using multi-ring orbital system"""
        
        # Group vulnerabilities by parent
        vuln_by_parent = defaultdict(list)
        for vuln in vulnerability_nodes:
            parent_id = vuln.get("parent_node_id")
            if parent_id:
                vuln_by_parent[parent_id].append(vuln)
        
        # Position vulnerabilities around each parent
        for parent_id, vulns in vuln_by_parent.items():
            parent_pos = layout_positions.get(parent_id)
            if not parent_pos:
                continue
            
            # Sort vulnerabilities by severity (Critical first)
            severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
            vulns.sort(key=lambda v: severity_order.get(v.get("severity", "Low"), 3))
            
            # Calculate optimal ring distribution
            ring_distribution = self.calculate_optimal_rings(len(vulns))
            
            vuln_index = 0
            for ring_nodes, ring_radius in ring_distribution:
                if vuln_index >= len(vulns):
                    break
                
                # Position nodes in this ring
                for i in range(ring_nodes):
                    if vuln_index >= len(vulns):
                        break
                    
                    vuln = vulns[vuln_index]
                    angle = (2 * math.pi * i) / ring_nodes
                    
                    # Calculate base position
                    base_x = parent_pos["x"] + ring_radius * math.cos(angle)
                    base_y = parent_pos["y"] + ring_radius * math.sin(angle)
                    
                    # Ensure no collision with other nodes
                    preferred_pos = NodePosition(base_x, base_y, 25)  # Smaller radius for vulnerabilities
                    final_pos = self.spatial_grid.find_nearest_free_position(preferred_pos)
                    
                    layout_positions[vuln["id"]] = {
                        "x": final_pos.x,
                        "y": final_pos.y
                    }
                    
                    # Add to spatial grid
                    self.spatial_grid.add_node(vuln["id"], final_pos)
                    vuln_index += 1
    
    def _organic_flow_layout(self, G: nx.DiGraph, nodes: List[Dict], edges: List[Dict]) -> Dict[str, Dict[str, float]]:
        """Create natural, flowing layouts that mimic real network topologies"""
        
        # Use modified spring-force algorithm for main nodes
        vulnerability_nodes = [n for n in nodes if n.get("type") == "vulnerability"]
        main_nodes = [n for n in nodes if n.get("type") != "vulnerability"]
        
        # Create subgraph with only main nodes
        main_graph = nx.DiGraph()
        for node in main_nodes:
            main_graph.add_node(node["id"], **node)
        
        for edge in edges:
            if main_graph.has_node(edge["source"]) and main_graph.has_node(edge["target"]):
                main_graph.add_edge(edge["source"], edge["target"])
        
        # Apply force-directed layout with custom parameters
        if len(main_nodes) > 1:
            # Use spring layout with organic parameters
            pos = nx.spring_layout(
                main_graph, 
                k=3,  # Optimal distance between nodes
                iterations=100,  # More iterations for better convergence
                weight='weight',
                scale=self.canvas.width * 0.4,
                center=(self.canvas.width/2, self.canvas.height/2)
            )
            
            layout_positions = {}
            for node_id, (x, y) in pos.items():
                layout_positions[node_id] = {"x": x, "y": y}
                self.spatial_grid.add_node(node_id, NodePosition(x, y, 50))
        else:
            layout_positions = {main_nodes[0]["id"]: {"x": self.canvas.width/2, "y": self.canvas.height/2}}
        
        # Add vulnerability nodes with orbital positioning
        self._position_vulnerability_nodes_multi_ring(layout_positions, vulnerability_nodes, main_nodes)
        
        return layout_positions
    
    def _security_perimeter_layout(self, G: nx.DiGraph, nodes: List[Dict], edges: List[Dict]) -> Dict[str, Dict[str, float]]:
        """Layout based on security zones and perimeters"""
        
        # Define concentric security zones
        security_zones = {
            "Actor": {"layer": 0, "radius": self.canvas.width * 0.4},    # Outer perimeter - attackers
            "Surface": {"layer": 1, "radius": self.canvas.width * 0.3},  # Attack surfaces
            "Asset": {"layer": 2, "radius": self.canvas.width * 0.2},    # Protected assets - center
            "Control": {"layer": 1.5, "radius": self.canvas.width * 0.25}, # Controls between surfaces and assets
            "Zone": {"layer": 0.5, "radius": self.canvas.width * 0.35}   # Network zones
        }
        
        layout_positions = {}
        center_x, center_y = self.canvas.width / 2, self.canvas.height / 2
        
        # Group nodes by security zone
        zone_nodes = defaultdict(list)
        vulnerability_nodes = []
        
        for node in nodes:
            if node.get("type") == "vulnerability":
                vulnerability_nodes.append(node)
            else:
                node_type = node.get("type", "Asset")  # Default to asset
                zone_nodes[node_type].append(node)
        
        # Position nodes in concentric circles
        for zone_type, zone_nodes_list in zone_nodes.items():
            zone_config = security_zones.get(zone_type, {"layer": 2, "radius": self.canvas.width * 0.2})
            radius = zone_config["radius"]
            
            if len(zone_nodes_list) == 1:
                # Single node at center of zone
                angle = 0
            else:
                # Distribute evenly around the circle
                angle_step = 2 * math.pi / len(zone_nodes_list)
                angle = 0
            
            for node in zone_nodes_list:
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                
                # Ensure collision-free positioning
                preferred_pos = NodePosition(x, y, 50)
                final_pos = self.spatial_grid.find_nearest_free_position(preferred_pos)
                
                layout_positions[node["id"]] = {
                    "x": final_pos.x,
                    "y": final_pos.y
                }
                
                self.spatial_grid.add_node(node["id"], final_pos)
                angle += angle_step if len(zone_nodes_list) > 1 else 0
        
        # Position vulnerability nodes
        main_nodes = [n for n in nodes if n.get("type") != "vulnerability"]
        self._position_vulnerability_nodes_multi_ring(layout_positions, vulnerability_nodes, main_nodes)
        
        return layout_positions
    
    def _force_directed_advanced_layout(self, G: nx.DiGraph, nodes: List[Dict], edges: List[Dict]) -> Dict[str, Dict[str, float]]:
        """Advanced force-directed layout with custom forces"""
        
        # Separate node types
        vulnerability_nodes = [n for n in nodes if n.get("type") == "vulnerability"]
        main_nodes = [n for n in nodes if n.get("type") != "vulnerability"]
        
        # Create weighted graph for better force calculation
        weighted_graph = nx.DiGraph()
        for node in main_nodes:
            weighted_graph.add_node(node["id"], 
                                  type=node.get("type"), 
                                  weight=self._calculate_node_weight(node))
        
        for edge in edges:
            if weighted_graph.has_node(edge["source"]) and weighted_graph.has_node(edge["target"]):
                weighted_graph.add_edge(edge["source"], edge["target"], weight=1.0)
        
        # Apply advanced spring layout
        if len(main_nodes) > 1:
            # Custom spring layout with node weights
            pos = nx.spring_layout(
                weighted_graph,
                k=4.0,  # Increase repulsion
                iterations=200,  # More iterations
                threshold=1e-6,  # Better convergence
                weight='weight',
                scale=min(self.canvas.width, self.canvas.height) * 0.4,
                center=(self.canvas.width/2, self.canvas.height/2)
            )
            
            layout_positions = {}
            for node_id, (x, y) in pos.items():
                layout_positions[node_id] = {"x": x, "y": y}
                self.spatial_grid.add_node(node_id, NodePosition(x, y, 50))
        else:
            layout_positions = {main_nodes[0]["id"]: {"x": self.canvas.width/2, "y": self.canvas.height/2}}
        
        # Position vulnerability nodes
        self._position_vulnerability_nodes_multi_ring(layout_positions, vulnerability_nodes, main_nodes)
        
        return layout_positions
    
    def _calculate_node_weight(self, node: Dict) -> float:
        """Calculate node weight for force-directed algorithms"""
        # Weight based on node type importance
        type_weights = {
            "Asset": 2.0,     # Assets are heavier (attract more)
            "Control": 1.5,   # Controls are moderately heavy
            "Surface": 1.0,   # Surfaces have normal weight
            "Actor": 0.8,     # Actors are lighter (repel more)
            "Zone": 1.2       # Zones are moderately heavy
        }
        return type_weights.get(node.get("type", "Asset"), 1.0)
    
    def _network_topology_advanced_layout(self, G: nx.DiGraph, nodes: List[Dict], edges: List[Dict]) -> Dict[str, Dict[str, float]]:
        """Advanced network topology-aware layout using graph analysis"""
        
        vulnerability_nodes = [n for n in nodes if n.get("type") == "vulnerability"]
        main_nodes = [n for n in nodes if n.get("type") != "vulnerability"]
        
        if len(main_nodes) <= 1:
            center_pos = {"x": self.canvas.width/2, "y": self.canvas.height/2}
            layout_positions = {main_nodes[0]["id"]: center_pos} if main_nodes else {}
            self._position_vulnerability_nodes_multi_ring(layout_positions, vulnerability_nodes, main_nodes)
            return layout_positions
        
        # Create main node graph
        main_graph = nx.DiGraph()
        for node in main_nodes:
            main_graph.add_node(node["id"], **node)
        
        for edge in edges:
            if main_graph.has_node(edge["source"]) and main_graph.has_node(edge["target"]):
                main_graph.add_edge(edge["source"], edge["target"])
        
        # Use hierarchical layout for directed graphs
        try:
            # Try to use planar layout if possible
            if nx.is_planar(main_graph.to_undirected()):
                pos = nx.planar_layout(main_graph, scale=min(self.canvas.width, self.canvas.height) * 0.4)
                pos = {node_id: (x + self.canvas.width/2, y + self.canvas.height/2) for node_id, (x, y) in pos.items()}
            else:
                # Use shell layout for complex topologies
                # Group nodes by type for shell assignment
                shells = []
                type_groups = defaultdict(list)
                for node in main_nodes:
                    node_type = node.get("type", "Asset")
                    type_groups[node_type].append(node["id"])
                
                # Create concentric shells
                for node_type, node_ids in type_groups.items():
                    shells.append(node_ids)
                
                pos = nx.shell_layout(main_graph, nlist=shells, scale=min(self.canvas.width, self.canvas.height) * 0.4)
                pos = {node_id: (x + self.canvas.width/2, y + self.canvas.height/2) for node_id, (x, y) in pos.items()}
            
            layout_positions = {}
            for node_id, (x, y) in pos.items():
                layout_positions[node_id] = {"x": x, "y": y}
                self.spatial_grid.add_node(node_id, NodePosition(x, y, 50))
                
        except:
            # Fallback to spring layout
            pos = nx.spring_layout(main_graph, k=3, iterations=100, 
                                 scale=min(self.canvas.width, self.canvas.height) * 0.4,
                                 center=(self.canvas.width/2, self.canvas.height/2))
            layout_positions = {}
            for node_id, (x, y) in pos.items():
                layout_positions[node_id] = {"x": x, "y": y}
                self.spatial_grid.add_node(node_id, NodePosition(x, y, 50))
        
        # Position vulnerability nodes
        self._position_vulnerability_nodes_multi_ring(layout_positions, vulnerability_nodes, main_nodes)
        
        return layout_positions


# Global layout engine instance
layout_engine = AdvancedLayoutEngine()