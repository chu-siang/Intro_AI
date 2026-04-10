"""Backward-compatible map renderer entry point."""

from osm_routing_system.map_renderer import load_path_graph, save_route_map_png

__all__ = ["load_path_graph", "save_route_map_png"]
