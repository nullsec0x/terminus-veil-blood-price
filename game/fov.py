"""Field of View (FOV) system for the roguelike."""

import math
from typing import Set, Tuple, List


class FOVCalculator:
    """Calculates field of view using shadowcasting algorithm."""
    
    def __init__(self, game_map: List[List[str]]):
        """Initialize the FOV calculator.
        
        Args:
            game_map: The game map to calculate FOV on
        """
        self.game_map = game_map
        self.width = len(game_map[0]) if game_map else 0
        self.height = len(game_map)
    
    def calculate_fov(self, player_x: int, player_y: int, 
                      radius: int = 8) -> Set[Tuple[int, int]]:
        """Calculate field of view from player position.
        
        Args:
            player_x: Player's X coordinate
            player_y: Player's Y coordinate
            radius: Maximum sight radius
            
        Returns:
            Set of (x, y) tuples that are visible
        """
        visible = set()
        visible.add((player_x, player_y))  
        
        for direction in range(8):
            self._cast_ray(player_x, player_y, direction, radius, visible)
        
        return visible
    
    def _cast_ray(self, start_x: int, start_y: int, direction: int, 
                  radius: int, visible: Set[Tuple[int, int]]):
        """Cast a ray in a specific direction.
        
        Args:
            start_x, start_y: Starting position
            direction: Direction to cast (0-7)
            radius: Maximum distance
            visible: Set to add visible tiles to
        """
        directions = [
            (0, -1),   
            (1, -1),   
            (1, 0),   
            (1, 1),    
            (0, 1),   
            (-1, 1),   
            (-1, 0),  
            (-1, -1)   
        ]
        
        dx, dy = directions[direction]
        
        for distance in range(1, radius + 1):
            x = start_x + dx * distance
            y = start_y + dy * distance
            
            if not (0 <= x < self.width and 0 <= y < self.height):
                break
            
            visible.add((x, y))
            
            if self.game_map[y][x] == '#':
                break
    
    def calculate_simple_fov(self, player_x: int, player_y: int, 
                           radius: int = 8) -> Set[Tuple[int, int]]:
        """Calculate a simple circular field of view.
        
        Args:
            player_x: Player's X coordinate
            player_y: Player's Y coordinate
            radius: Maximum sight radius
            
        Returns:
            Set of (x, y) tuples that are visible
        """
        visible = set()
        
        for y in range(max(0, player_y - radius), 
                      min(self.height, player_y + radius + 1)):
            for x in range(max(0, player_x - radius), 
                          min(self.width, player_x + radius + 1)):
                distance = math.sqrt((x - player_x) ** 2 + (y - player_y) ** 2)
                
                if distance <= radius:
                    if self._has_line_of_sight(player_x, player_y, x, y):
                        visible.add((x, y))
        
        return visible
    
    def _has_line_of_sight(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        """Check if there's a clear line of sight between two points.
        
        Args:
            x1, y1: Start point
            x2, y2: End point
            
        Returns:
            True if line of sight is clear
        """
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        
        x, y = x1, y1
        
        x_inc = 1 if x1 < x2 else -1
        y_inc = 1 if y1 < y2 else -1
        
        error = dx - dy
        
        while True:
            if (x, y) != (x1, y1) and self.game_map[y][x] == '#':
                return False
            
            if x == x2 and y == y2:
                break
            
            error2 = 2 * error
            
            if error2 > -dy:
                error -= dy
                x += x_inc
            
            if error2 < dx:
                error += dx
                y += y_inc
        
        return True


class VisibilityTracker:
    """Tracks what the player has seen (explored vs currently visible)."""
    
    def __init__(self):
        """Initialize the visibility tracker."""
        self.explored: Set[Tuple[int, int]] = set()
        self.visible: Set[Tuple[int, int]] = set()
    
    def update_visibility(self, new_visible: Set[Tuple[int, int]]):
        """Update the current visibility and explored areas.
        
        Args:
            new_visible: Set of currently visible tiles
        """
        self.visible = new_visible
        self.explored.update(new_visible)
    
    def is_visible(self, x: int, y: int) -> bool:
        """Check if a tile is currently visible.
        
        Args:
            x, y: Tile coordinates
            
        Returns:
            True if tile is currently visible
        """
        return (x, y) in self.visible
    
    def is_explored(self, x: int, y: int) -> bool:
        """Check if a tile has been explored.
        
        Args:
            x, y: Tile coordinates
            
        Returns:
            True if tile has been seen before
        """
        return (x, y) in self.explored

