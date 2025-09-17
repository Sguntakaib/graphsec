"""
Layout Optimization Module
Provides performance optimization, visual enhancements, and animation support
for the advanced layout engine.
"""

import math
import time
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import asyncio


@dataclass
class LayoutMetrics:
    """Metrics for layout quality assessment"""
    total_nodes: int
    vulnerability_nodes: int
    main_nodes: int
    overlapping_nodes: int
    average_spacing: float
    canvas_utilization: float
    edge_crossings: int
    layout_time: float
    algorithm_used: str


@dataclass
class AnimationFrame:
    """Single frame in layout animation"""
    node_positions: Dict[str, Dict[str, float]]
    timestamp: float
    frame_number: int


class LayoutOptimizer:
    """Optimization utilities for layout algorithms"""
    
    def __init__(self):
        self.cache: Dict[str, Dict] = {}
        self.performance_metrics: List[LayoutMetrics] = []
    
    def optimize_large_layout(self, nodes: List[Dict], edges: List[Dict], 
                            target_algorithm: str) -> Dict[str, Any]:
        """Optimize layout calculation for large diagrams (100+ nodes)"""
        
        node_count = len(nodes)
        
        # Use progressive rendering for very large layouts
        if node_count > 200:
            return self._progressive_layout_calculation(nodes, edges, target_algorithm)
        
        # Use chunked processing for moderately large layouts
        elif node_count > 100:
            return self._chunked_layout_calculation(nodes, edges, target_algorithm)
        
        # Standard processing for smaller layouts
        else:
            return {"status": "standard_processing", "optimization": None}
    
    def _progressive_layout_calculation(self, nodes: List[Dict], edges: List[Dict], 
                                      algorithm: str) -> Dict[str, Any]:
        """Calculate layout progressively in chunks"""
        
        # Separate nodes by importance
        critical_nodes = [n for n in nodes if n.get("type") in ["Asset", "Control"]]
        secondary_nodes = [n for n in nodes if n.get("type") in ["Surface", "Actor"]]
        vulnerability_nodes = [n for n in nodes if n.get("type") == "vulnerability"]
        
        chunks = [
            ("critical", critical_nodes),
            ("secondary", secondary_nodes), 
            ("vulnerabilities", vulnerability_nodes)
        ]
        
        return {
            "status": "progressive_processing",
            "chunks": len(chunks),
            "total_nodes": len(nodes),
            "optimization": "progressive_rendering"
        }
    
    def _chunked_layout_calculation(self, nodes: List[Dict], edges: List[Dict], 
                                  algorithm: str) -> Dict[str, Any]:
        """Process layout in parallel chunks"""
        
        chunk_size = 50
        chunks = [nodes[i:i + chunk_size] for i in range(0, len(nodes), chunk_size)]
        
        return {
            "status": "chunked_processing",
            "chunks": len(chunks),
            "chunk_size": chunk_size,
            "optimization": "parallel_chunks"
        }
    
    def calculate_layout_metrics(self, layout_positions: Dict[str, Dict[str, float]], 
                               nodes: List[Dict], edges: List[Dict],
                               algorithm: str, calculation_time: float) -> LayoutMetrics:
        """Calculate comprehensive layout quality metrics"""
        
        total_nodes = len(nodes)
        vulnerability_nodes = len([n for n in nodes if n.get("type") == "vulnerability"])
        main_nodes = total_nodes - vulnerability_nodes
        
        # Calculate overlapping nodes
        overlapping_nodes = self._count_overlapping_nodes(layout_positions)
        
        # Calculate average spacing
        average_spacing = self._calculate_average_spacing(layout_positions)
        
        # Calculate canvas utilization
        canvas_utilization = self._calculate_canvas_utilization(layout_positions)
        
        # Estimate edge crossings (simplified)
        edge_crossings = self._estimate_edge_crossings(layout_positions, edges)
        
        return LayoutMetrics(
            total_nodes=total_nodes,
            vulnerability_nodes=vulnerability_nodes,
            main_nodes=main_nodes,
            overlapping_nodes=overlapping_nodes,
            average_spacing=average_spacing,
            canvas_utilization=canvas_utilization,
            edge_crossings=edge_crossings,
            layout_time=calculation_time,
            algorithm_used=algorithm
        )
    
    def _count_overlapping_nodes(self, layout_positions: Dict[str, Dict[str, float]]) -> int:
        """Count nodes that overlap with others"""
        overlaps = 0
        positions = list(layout_positions.items())
        
        for i, (node1_id, pos1) in enumerate(positions):
            for j, (node2_id, pos2) in enumerate(positions[i+1:], i+1):
                distance = math.sqrt((pos1["x"] - pos2["x"])**2 + (pos1["y"] - pos2["y"])**2)
                if distance < 80:  # Minimum safe distance
                    overlaps += 1
        
        return overlaps
    
    def _calculate_average_spacing(self, layout_positions: Dict[str, Dict[str, float]]) -> float:
        """Calculate average distance between nodes"""
        if len(layout_positions) < 2:
            return 0.0
        
        distances = []
        positions = list(layout_positions.values())
        
        for i, pos1 in enumerate(positions):
            for pos2 in positions[i+1:]:
                distance = math.sqrt((pos1["x"] - pos2["x"])**2 + (pos1["y"] - pos2["y"])**2)
                distances.append(distance)
        
        return sum(distances) / len(distances) if distances else 0.0
    
    def _calculate_canvas_utilization(self, layout_positions: Dict[str, Dict[str, float]]) -> float:
        """Calculate how well the layout utilizes available canvas space"""
        if not layout_positions:
            return 0.0
        
        positions = list(layout_positions.values())
        
        min_x = min(pos["x"] for pos in positions)
        max_x = max(pos["x"] for pos in positions)
        min_y = min(pos["y"] for pos in positions)
        max_y = max(pos["y"] for pos in positions)
        
        used_width = max_x - min_x
        used_height = max_y - min_y
        used_area = used_width * used_height
        
        # Assume standard canvas size for calculation
        canvas_area = 1920 * 1080
        
        return min(1.0, used_area / canvas_area) if canvas_area > 0 else 0.0
    
    def _estimate_edge_crossings(self, layout_positions: Dict[str, Dict[str, float]], 
                               edges: List[Dict]) -> int:
        """Estimate number of edge crossings (simplified calculation)"""
        crossings = 0
        
        for i, edge1 in enumerate(edges):
            pos1_start = layout_positions.get(edge1.get("source", ""))
            pos1_end = layout_positions.get(edge1.get("target", ""))
            
            if not pos1_start or not pos1_end:
                continue
            
            for edge2 in edges[i+1:]:
                pos2_start = layout_positions.get(edge2.get("source", ""))
                pos2_end = layout_positions.get(edge2.get("target", ""))
                
                if not pos2_start or not pos2_end:
                    continue
                
                # Simple line intersection check
                if self._lines_intersect(pos1_start, pos1_end, pos2_start, pos2_end):
                    crossings += 1
        
        return crossings
    
    def _lines_intersect(self, p1: Dict, p2: Dict, p3: Dict, p4: Dict) -> bool:
        """Check if two line segments intersect"""
        def ccw(A, B, C):
            return (C["y"] - A["y"]) * (B["x"] - A["x"]) > (B["y"] - A["y"]) * (C["x"] - A["x"])
        
        return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)
    
    def generate_layout_animation(self, start_positions: Dict[str, Dict[str, float]], 
                                end_positions: Dict[str, Dict[str, float]], 
                                duration: float = 1.0, fps: int = 30) -> List[AnimationFrame]:
        """Generate smooth animation frames between two layouts"""
        
        frames = []
        total_frames = int(duration * fps)
        
        for frame_num in range(total_frames + 1):
            progress = frame_num / total_frames
            # Use easing function for smooth animation
            eased_progress = self._ease_in_out_cubic(progress)
            
            frame_positions = {}
            for node_id in end_positions:
                start_pos = start_positions.get(node_id, {"x": 0, "y": 0})
                end_pos = end_positions[node_id]
                
                # Interpolate position
                frame_positions[node_id] = {
                    "x": start_pos["x"] + (end_pos["x"] - start_pos["x"]) * eased_progress,
                    "y": start_pos["y"] + (end_pos["y"] - start_pos["y"]) * eased_progress
                }
            
            frames.append(AnimationFrame(
                node_positions=frame_positions,
                timestamp=time.time() + (frame_num / fps),
                frame_number=frame_num
            ))
        
        return frames
    
    def _ease_in_out_cubic(self, t: float) -> float:
        """Cubic easing function for smooth animation"""
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - pow(-2 * t + 2, 3) / 2
    
    def optimize_edge_routing(self, layout_positions: Dict[str, Dict[str, float]], 
                            edges: List[Dict]) -> Dict[str, List[Dict[str, float]]]:
        """Calculate optimal edge paths to minimize visual clutter"""
        
        edge_paths = {}
        
        for edge in edges:
            source_id = edge.get("source")
            target_id = edge.get("target")
            
            if not source_id or not target_id:
                continue
            
            source_pos = layout_positions.get(source_id)
            target_pos = layout_positions.get(target_id)
            
            if not source_pos or not target_pos:
                continue
            
            # Calculate optimal bezier curve path
            path_points = self._calculate_bezier_path(source_pos, target_pos, layout_positions)
            edge_paths[f"{source_id}-{target_id}"] = path_points
        
        return edge_paths
    
    def _calculate_bezier_path(self, start_pos: Dict[str, float], end_pos: Dict[str, float], 
                             all_positions: Dict[str, Dict[str, float]]) -> List[Dict[str, float]]:
        """Calculate bezier curve path between two points"""
        
        # Calculate control points to avoid other nodes
        mid_x = (start_pos["x"] + end_pos["x"]) / 2
        mid_y = (start_pos["y"] + end_pos["y"]) / 2
        
        # Offset control points perpendicular to the line
        dx = end_pos["x"] - start_pos["x"]
        dy = end_pos["y"] - start_pos["y"]
        length = math.sqrt(dx**2 + dy**2)
        
        if length > 0:
            # Perpendicular offset
            offset_x = -dy / length * 50  # 50px offset
            offset_y = dx / length * 50
            
            control1 = {
                "x": start_pos["x"] + dx * 0.25 + offset_x,
                "y": start_pos["y"] + dy * 0.25 + offset_y
            }
            control2 = {
                "x": start_pos["x"] + dx * 0.75 + offset_x,
                "y": start_pos["y"] + dy * 0.75 + offset_y
            }
        else:
            control1 = start_pos.copy()
            control2 = end_pos.copy()
        
        # Generate bezier curve points
        path_points = []
        for t in range(0, 11):  # 11 points along the curve
            t = t / 10.0
            
            x = (1-t)**3 * start_pos["x"] + 3*(1-t)**2*t * control1["x"] + 3*(1-t)*t**2 * control2["x"] + t**3 * end_pos["x"]
            y = (1-t)**3 * start_pos["y"] + 3*(1-t)**2*t * control1["y"] + 3*(1-t)*t**2 * control2["y"] + t**3 * end_pos["y"]
            
            path_points.append({"x": x, "y": y})
        
        return path_points
    
    def create_visual_groups(self, nodes: List[Dict], layout_positions: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Create visual grouping information for related nodes"""
        
        # Group by node type
        type_groups = {}
        for node in nodes:
            node_type = node.get("type", "Unknown")
            if node_type not in type_groups:
                type_groups[node_type] = []
            type_groups[node_type].append(node["id"])
        
        # Calculate group boundaries
        group_boundaries = {}
        for group_type, node_ids in type_groups.items():
            if len(node_ids) < 2:
                continue
            
            positions = [layout_positions[node_id] for node_id in node_ids if node_id in layout_positions]
            if not positions:
                continue
            
            min_x = min(pos["x"] for pos in positions) - 30
            max_x = max(pos["x"] for pos in positions) + 30
            min_y = min(pos["y"] for pos in positions) - 30
            max_y = max(pos["y"] for pos in positions) + 30
            
            group_boundaries[group_type] = {
                "x": min_x,
                "y": min_y,
                "width": max_x - min_x,
                "height": max_y - min_y,
                "nodes": node_ids
            }
        
        return {
            "type_groups": type_groups,
            "group_boundaries": group_boundaries
        }
    
    def suggest_layout_improvements(self, metrics: LayoutMetrics) -> List[str]:
        """Suggest improvements based on layout metrics"""
        suggestions = []
        
        if metrics.overlapping_nodes > 0:
            suggestions.append(f"Reduce {metrics.overlapping_nodes} overlapping nodes by increasing spacing")
        
        if metrics.canvas_utilization < 0.3:
            suggestions.append("Increase node spacing to better utilize canvas space")
        elif metrics.canvas_utilization > 0.9:
            suggestions.append("Consider using a larger canvas or reducing node sizes")
        
        if metrics.edge_crossings > metrics.total_nodes:
            suggestions.append("High edge crossings detected - consider hierarchical layout")
        
        if metrics.layout_time > 2.0:
            suggestions.append("Layout calculation is slow - consider optimization for large diagrams")
        
        if metrics.average_spacing < 100:
            suggestions.append("Nodes are too close together - increase minimum spacing")
        
        return suggestions
    
    def cache_layout_result(self, cache_key: str, layout_result: Dict):
        """Cache layout result for similar configurations"""
        self.cache[cache_key] = {
            "result": layout_result,
            "timestamp": time.time()
        }
        
        # Limit cache size
        if len(self.cache) > 100:
            # Remove oldest entries
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]["timestamp"])
            del self.cache[oldest_key]
    
    def get_cached_layout(self, cache_key: str, max_age: float = 300) -> Optional[Dict]:
        """Get cached layout result if available and not expired"""
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if time.time() - cached["timestamp"] < max_age:
                return cached["result"]
            else:
                # Remove expired cache
                del self.cache[cache_key]
        return None


# Global optimizer instance
layout_optimizer = LayoutOptimizer()