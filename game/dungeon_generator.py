"""Procedural dungeon generation for Terminus Veil: Blood Price."""

import random
from typing import Tuple, List, Set


class DungeonGenerator:
    """Generates procedural dungeons using various algorithms."""

    def __init__(self, width: int, height: int):
        """Initialize the dungeon generator.

        Args:
            width: Width of the dungeon
            height: Height of the dungeon
        """
        self.width = width
        self.height = height

    def generate_random_walk(self, steps: int = 1000) -> List[List[str]]:
        """Generate a dungeon using random walk algorithm.

        Args:
            steps: Number of steps to take in the random walk

        Returns:
            2D list representing the generated dungeon
        """
        dungeon = [['#' for _ in range(self.width)] for _ in range(self.height)]

        x, y = self.width // 2, self.height // 2

        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

        for _ in range(steps):
            if 1 <= x < self.width - 1 and 1 <= y < self.height - 1:
                dungeon[y][x] = '.'

            dx, dy = random.choice(directions)
            new_x, new_y = x + dx, y + dy

            if 1 <= new_x < self.width - 1 and 1 <= new_y < self.height - 1:
                x, y = new_x, new_y

        return dungeon

    def generate_bsp_dungeon(self, min_room_size: int = 6) -> List[List[str]]:
        """Generate a dungeon using Binary Space Partitioning.

        Args:
            min_room_size: Minimum size for rooms

        Returns:
            2D list representing the generated dungeon
        """
        dungeon = [['#' for _ in range(self.width)] for _ in range(self.height)]

        rooms = self._split_space(1, 1, self.width - 2, self.height - 2, min_room_size)

        for room in rooms:
            x, y, w, h = room
            for ry in range(y, y + h):
                for rx in range(x, x + w):
                    if 0 <= rx < self.width and 0 <= ry < self.height:
                        dungeon[ry][rx] = '.'

        self._connect_rooms(dungeon, rooms)

        return dungeon

    def _split_space(self, x: int, y: int, width: int, height: int,
                     min_size: int) -> List[Tuple[int, int, int, int]]:
        """Recursively split space into rooms.

        Args:
            x, y: Top-left corner of the space
            width, height: Dimensions of the space
            min_size: Minimum room size

        Returns:
            List of room tuples (x, y, width, height)
        """
        rooms = []

        if width < min_size * 2 or height < min_size * 2:
            room_width = max(3, width - 2)
            room_height = max(3, height - 2)
            room_x = x + random.randint(0, max(0, width - room_width))
            room_y = y + random.randint(0, max(0, height - room_height))
            rooms.append((room_x, room_y, room_width, room_height))
            return rooms

        split_horizontal = random.choice([True, False])

        if split_horizontal:
            split_point = random.randint(min_size, height - min_size)
            rooms.extend(self._split_space(x, y, width, split_point, min_size))
            rooms.extend(self._split_space(x, y + split_point, width,
                                         height - split_point, min_size))
        else:
            split_point = random.randint(min_size, width - min_size)
            rooms.extend(self._split_space(x, y, split_point, height, min_size))
            rooms.extend(self._split_space(x + split_point, y,
                                         width - split_point, height, min_size))

        return rooms

    def _connect_rooms(self, dungeon: List[List[str]],
                       rooms: List[Tuple[int, int, int, int]]):
        """Connect rooms with corridors.

        Args:
            dungeon: The dungeon map to modify
            rooms: List of room tuples
        """
        for i in range(len(rooms) - 1):
            room1 = rooms[i]
            room2 = rooms[i + 1]

            x1 = room1[0] + room1[2] // 2
            y1 = room1[1] + room1[3] // 2
            x2 = room2[0] + room2[2] // 2
            y2 = room2[1] + room2[3] // 2

            self._carve_corridor(dungeon, x1, y1, x2, y1)
            self._carve_corridor(dungeon, x2, y1, x2, y2)

    def _carve_corridor(self, dungeon: List[List[str]], x1: int, y1: int,
                        x2: int, y2: int):
        """Carve a corridor between two points.

        Args:
            dungeon: The dungeon map to modify
            x1, y1: Start point
            x2, y2: End point
        """
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1

        for x in range(x1, x2 + 1):
            if 0 <= x < self.width and 0 <= y1 < self.height:
                dungeon[y1][x] = '.'

        for y in range(y1, y2 + 1):
            if 0 <= x2 < self.width and 0 <= y < self.height:
                dungeon[y][x2] = '.'

    def find_valid_positions(self, dungeon: List[List[str]],
                           count: int = 2) -> List[Tuple[int, int]]:
        """Find valid floor positions in the dungeon.

        Args:
            dungeon: The dungeon map
            count: Number of positions to find

        Returns:
            List of (x, y) tuples for valid positions
        """
        floor_tiles = []
        for y in range(len(dungeon)):
            for x in range(len(dungeon[0])):
                if dungeon[y][x] == '.':
                    floor_tiles.append((x, y))

        if len(floor_tiles) < count:
            return floor_tiles

        return random.sample(floor_tiles, count)

    def find_room_center_positions(self, dungeon: List[List[str]],
                                  count: int = 2) -> List[Tuple[int, int]]:
        """Find positions in room centers for special placement.

        Args:
            dungeon: The dungeon map
            count: Number of positions to find

        Returns:
            List of (x, y) tuples for room centers
        """
        visited = set()
        rooms = []

        for y in range(1, len(dungeon) - 1):
            for x in range(1, len(dungeon[0]) - 1):
                if dungeon[y][x] == '.' and (x, y) not in visited:
                    room_tiles = []
                    stack = [(x, y)]

                    while stack:
                        cx, cy = stack.pop()
                        if (cx, cy) in visited:
                            continue
                        visited.add((cx, cy))
                        room_tiles.append((cx, cy))

                        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                            nx, ny = cx + dx, cy + dy
                            if (0 <= nx < len(dungeon[0]) and
                                0 <= ny < len(dungeon) and
                                dungeon[ny][nx] == '.' and
                                (nx, ny) not in visited):
                                stack.append((nx, ny))

                    if len(room_tiles) > 10:
                        rooms.append(room_tiles)

        centers = []
        for room in rooms:
            if room:
                xs = [t[0] for t in room]
                ys = [t[1] for t in room]
                center_x = sum(xs) // len(xs)
                center_y = sum(ys) // len(ys)
                centers.append((center_x, center_y))

        if len(centers) < count:
            return self.find_valid_positions(dungeon, count)

        return random.sample(centers, min(count, len(centers)))
