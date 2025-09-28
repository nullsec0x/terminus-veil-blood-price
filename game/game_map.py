"""Game map system for Terminus Veil: Blood Price."""

import random
from typing import List, Tuple, Optional
from .dungeon_generator import DungeonGenerator
from .fov import FOVCalculator, VisibilityTracker
from .ascii_art import WallRenderer, ASCIIChars, ColorScheme, get_colored_char, get_corrupted_floor_char
from .sacrifice import Altar


class GameMap:
    """Represents the game map and handles map-related operations."""

    def __init__(self, width: int = 80, height: int = 40, use_procedural: bool = True):
        """Initialize a game map.

        Args:
            width: Width of the map
            height: Height of the map
            use_procedural: Whether to use procedural generation
        """
        self.width = width
        self.height = height
        self.use_procedural = use_procedural

        if use_procedural:
            self.tiles = self._generate_procedural_map()
        else:
            self.tiles = self._create_simple_map()

        self.fov_calculator = FOVCalculator(self.tiles)
        self.visibility_tracker = VisibilityTracker()

        self.wall_renderer = WallRenderer(self.tiles)

        self.player_start, self.exit_pos = self._find_special_positions()
        self.altars: List[Altar] = []

    def _generate_procedural_map(self) -> List[List[str]]:
        """Generate a procedural map.

        Returns:
            2D list representing the map
        """
        generator = DungeonGenerator(self.width, self.height)
        return generator.generate_bsp_dungeon()

    def _create_simple_map(self) -> List[List[str]]:
        """Create a simple hardcoded map for testing.

        Returns:
            2D list representing the map
        """
        map_data = []

        for y in range(self.height):
            row = []
            for x in range(self.width):
                if (x == 0 or x == self.width - 1 or
                    y == 0 or y == self.height - 1):
                    row.append('#')
                else:
                    row.append('.')
            map_data.append(row)

        for y in range(5, 15):
            if y < len(map_data) and 10 < len(map_data[y]):
                map_data[y][10] = '#'

        for x in range(15, 25):
            if 10 < len(map_data) and x < len(map_data[10]):
                map_data[10][x] = '#'

        return map_data

    def _find_special_positions(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """Find positions for player start and exit.

        Returns:
            Tuple of (player_start, exit_position)
        """
        generator = DungeonGenerator(self.width, self.height)
        positions = generator.find_room_center_positions(self.tiles, 2)

        if len(positions) >= 2:
            return positions[0], positions[1]
        elif len(positions) == 1:
            return positions[0], positions[0]
        else:
            return (self.width // 2, self.height // 2), (self.width // 2 + 1, self.height // 2)

    def place_exit(self):
        """Place the exit on the map."""
        if self.exit_pos:
            x, y = self.exit_pos
            if 0 <= x < self.width and 0 <= y < self.height:
                self.tiles[y][x] = '>'

    def place_altars(self, sacrifice_system, count: int = 1, level: int = 1):
        """Place altars on the map.

        Args:
            sacrifice_system: Sacrifice system to manage altars
            count: Number of altars to place
            level: Current dungeon level for altar difficulty
        """
        generator = DungeonGenerator(self.width, self.height)
        positions = generator.find_room_center_positions(self.tiles, count)

        for x, y in positions:
            altar = Altar(x, y, level)
            self.altars.append(altar)
            sacrifice_system.altars.append(altar)

    def get_tile(self, x: int, y: int) -> str:
        """Get the tile at given coordinates.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Character representing the tile
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return '#'

    def is_walkable(self, x: int, y: int) -> bool:
        """Check if a tile is walkable.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            True if the tile can be walked on
        """
        tile = self.get_tile(x, y)
        return tile in ['.', '>']

    def update_fov(self, player_x: int, player_y: int):
        """Update the field of view from player position.

        Args:
            player_x: Player's X coordinate
            player_y: Player's Y coordinate
        """
        base_radius = 8
        if hasattr(self, 'player') and hasattr(self.player, 'sight_radius_reduction'):
            base_radius = max(3, base_radius - self.player.sight_radius_reduction)

        visible_tiles = self.fov_calculator.calculate_simple_fov(player_x, player_y, base_radius)
        self.visibility_tracker.update_visibility(visible_tiles)

    def render_with_entities(self, player_x: int, player_y: int,
                           monster_manager=None, item_manager=None, player=None) -> str:
        """Render the map with the player position, FOV, monsters, and items.

        Args:
            player_x: Player's X coordinate
            player_y: Player's Y coordinate
            monster_manager: Monster manager for rendering monsters
            item_manager: Item manager for rendering items
            player: Player object for sacrifice effects

        Returns:
            String representation of the map
        """
        lines = []
        for y in range(self.height):
            line = ""
            for x in range(self.width):
                altar_here = any(altar.x == x and altar.y == y and not altar.used for altar in self.altars)

                if x == player_x and y == player_y:
                    line += get_colored_char('☺', ColorScheme.PLAYER)
                elif altar_here and self.visibility_tracker.is_visible(x, y):
                    line += get_colored_char('Ω', ColorScheme.ALTAR)
                elif (monster_manager and
                      self.visibility_tracker.is_visible(x, y)):
                    monster = monster_manager.get_monster_at(x, y)
                    if monster:
                        if monster.is_alive:
                            if monster.monster_type.name == 'GOBLIN':
                                line += get_colored_char(monster.symbol, ColorScheme.GOBLIN)
                            elif monster.monster_type.name == 'ORC':
                                line += get_colored_char(monster.symbol, ColorScheme.ORC)
                            elif monster.monster_type.name == 'DRAGON':
                                line += get_colored_char(monster.symbol, ColorScheme.DRAGON)
                            else:
                                line += monster.symbol
                        else:
                            line += get_colored_char(monster.symbol, ColorScheme.CORPSE)
                    elif (item_manager):
                        item = item_manager.get_item_at(x, y)
                        if item:
                            if item.item_type.name == 'HEALTH_POTION':
                                line += get_colored_char(item.symbol, ColorScheme.HEALTH_POTION)
                            elif item.item_type.name == 'GOLD':
                                line += get_colored_char(item.symbol, ColorScheme.GOLD)
                            elif item.item_type.name == 'MAGIC_SCROLL':
                                line += get_colored_char(item.symbol, ColorScheme.MAGIC_SCROLL)
                            elif item.item_type.name == 'WEAPON':
                                line += get_colored_char(item.symbol, ColorScheme.WEAPON)
                            else:
                                line += item.symbol
                        else:
                            if self.tiles[y][x] == '>':
                                line += get_colored_char('▼', ColorScheme.EXIT)
                            else:
                                if player:
                                    line += get_corrupted_floor_char(x, y, player)
                                else:
                                    line += get_colored_char('·', ColorScheme.FLOOR)
                    else:
                        if self.tiles[y][x] == '>':
                            line += get_colored_char('▼', ColorScheme.EXIT)
                        else:
                            if player:
                                line += get_corrupted_floor_char(x, y, player)
                            else:
                                line += get_colored_char('·', ColorScheme.FLOOR)
                elif self.visibility_tracker.is_visible(x, y):
                    if item_manager:
                        item = item_manager.get_item_at(x, y)
                        if item:
                            if item.item_type.name == 'HEALTH_POTION':
                                line += get_colored_char(item.symbol, ColorScheme.HEALTH_POTION)
                            elif item.item_type.name == 'GOLD':
                                line += get_colored_char(item.symbol, ColorScheme.GOLD)
                            elif item.item_type.name == 'MAGIC_SCROLL':
                                line += get_colored_char(item.symbol, ColorScheme.MAGIC_SCROLL)
                            elif item.item_type.name == 'WEAPON':
                                line += get_colored_char(item.symbol, ColorScheme.WEAPON)
                            else:
                                line += item.symbol
                        else:
                            if self.tiles[y][x] == '>':
                                line += get_colored_char('▼', ColorScheme.EXIT)
                            else:
                                if player:
                                    line += get_corrupted_floor_char(x, y, player)
                                else:
                                    line += get_colored_char('·', ColorScheme.FLOOR)
                    else:
                        if self.tiles[y][x] == '>':
                            line += get_colored_char('▼', ColorScheme.EXIT)
                        else:
                            if player:
                                line += get_corrupted_floor_char(x, y, player)
                            else:
                                line += get_colored_char('·', ColorScheme.FLOOR)
                elif self.visibility_tracker.is_explored(x, y) or self.tiles[y][x] == '#':
                    tile = self.tiles[y][x]
                    if tile == '#':
                        wall_char = self.wall_renderer.get_wall_char(x, y)
                        if self.visibility_tracker.is_explored(x, y):
                            line += get_colored_char(wall_char, ColorScheme.WALL)
                        else:
                            line += get_colored_char(wall_char, ColorScheme.WALL_EXPLORED)
                    else:
                        if (hasattr(player, 'memory_loss_count') and
                            player.memory_loss_count > 0 and
                            random.random() < player.memory_loss_count * 0.1):
                            line += get_colored_char(' ', ColorScheme.MEMORY_EFFECT)
                        else:
                            line += get_colored_char('░', ColorScheme.FLOOR_EXPLORED)
                else:
                    line += ' '
            lines.append(line)
        return '\n'.join(lines)
