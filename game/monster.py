"""Monster system for Terminus Veil: Blood Price."""

import random
from typing import List, Tuple, Optional
from enum import Enum


class MonsterType(Enum):
    """Different types of monsters."""
    GOBLIN = ("♠", 20, 5, "Goblin")
    ORC = ("♣", 35, 8, "Orc")
    DRAGON = ("♦", 100, 15, "Dragon")


class Monster:
    """Represents a monster in the game."""

    def __init__(self, x: int, y: int, monster_type: MonsterType):
        """Initialize a monster.

        Args:
            x: X coordinate
            y: Y coordinate
            monster_type: Type of monster
        """
        self.x = x
        self.y = y
        self.monster_type = monster_type
        self.symbol = monster_type.value[0]
        self.max_hp = monster_type.value[1]
        self.hp = self.max_hp
        self.attack_power = monster_type.value[2]
        self.name = monster_type.value[3]
        self.is_alive = True
        self.turns_since_last_move = 0

    def take_damage(self, damage: int) -> bool:
        """Apply damage to the monster.

        Args:
            damage: Amount of damage to take

        Returns:
            True if monster died from this damage
        """
        self.hp = max(0, self.hp - damage)
        if self.hp <= 0:
            self.is_alive = False
            self.symbol = '☠'
            return True
        return False

    def attack(self, target) -> int:
        """Attack a target.

        Args:
            target: Target to attack (usually player)

        Returns:
            Damage dealt
        """
        if not self.is_alive:
            return 0

        damage = random.randint(max(1, self.attack_power - 2), self.attack_power + 2)
        return damage

    def move_towards(self, target_x: int, target_y: int, game_map, speed_buff: int = 0) -> bool:
        """Move one step towards target position.

        Args:
            target_x: Target X coordinate
            target_y: Target Y coordinate
            game_map: Game map for collision detection
            speed_buff: How much faster monsters move (0 = normal, 1 = 50% faster, etc.)

        Returns:
            True if moved successfully
        """
        if not self.is_alive:
            return False

        # Apply speed buff from sacrifices
        self.turns_since_last_move += 1
        move_threshold = max(1, 2 - speed_buff)  # Faster monsters move more often

        if self.turns_since_last_move < move_threshold:
            return False

        self.turns_since_last_move = 0

        dx = 0
        dy = 0

        if target_x > self.x:
            dx = 1
        elif target_x < self.x:
            dx = -1

        if target_y > self.y:
            dy = 1
        elif target_y < self.y:
            dy = -1

        # Sometimes move diagonally for more intelligent pursuit
        if dx != 0 and dy != 0 and random.random() < 0.3:
            if random.random() < 0.5:
                dy = 0
            else:
                dx = 0

        new_x = self.x + dx
        new_y = self.y + dy

        if (0 <= new_x < len(game_map[0]) and
            0 <= new_y < len(game_map) and
            game_map[new_y][new_x] != '#'):
            self.x = new_x
            self.y = new_y
            return True

        return False

    def distance_to(self, x: int, y: int) -> float:
        """Calculate distance to a point.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Distance to the point
        """
        return ((self.x - x) ** 2 + (self.y - y) ** 2) ** 0.5

    def is_adjacent_to(self, x: int, y: int) -> bool:
        """Check if monster is adjacent to a position.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            True if adjacent
        """
        return abs(self.x - x) <= 1 and abs(self.y - y) <= 1 and (self.x != x or self.y != y)


class MonsterManager:
    """Manages all monsters in the game."""

    def __init__(self):
        """Initialize the monster manager."""
        self.monsters: List[Monster] = []

    def spawn_monsters(self, game_map, count: int = 5, level: int = 1):
        """Spawn monsters on the map.

        Args:
            game_map: Game map to spawn monsters on
            count: Number of monsters to spawn
            level: Current dungeon level for difficulty scaling
        """
        from .dungeon_generator import DungeonGenerator

        generator = DungeonGenerator(len(game_map[0]), len(game_map))
        positions = generator.find_valid_positions(game_map, count)

        for i, (x, y) in enumerate(positions):
            rand = random.random()

            # Scale monster difficulty with level and sacrifices
            if level == 1:
                if rand < 0.8:
                    monster_type = MonsterType.GOBLIN
                else:
                    monster_type = MonsterType.ORC
            elif level <= 3:
                if rand < 0.4:
                    monster_type = MonsterType.GOBLIN
                elif rand < 0.8:
                    monster_type = MonsterType.ORC
                else:
                    monster_type = MonsterType.DRAGON
            else:
                if rand < 0.2:
                    monster_type = MonsterType.GOBLIN
                elif rand < 0.5:
                    monster_type = MonsterType.ORC
                else:
                    monster_type = MonsterType.DRAGON

            monster = Monster(x, y, monster_type)

            # Scale monster stats with level
            bonus_hp = (level - 1) * 8
            bonus_attack = (level - 1) * 3
            monster.max_hp += bonus_hp
            monster.hp += bonus_hp
            monster.attack_power += bonus_attack

            self.monsters.append(monster)

    def get_monster_at(self, x: int, y: int) -> Optional[Monster]:
        """Get monster at specific position.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Monster at position or None
        """
        for monster in self.monsters:
            if monster.x == x and monster.y == y and monster.is_alive:
                return monster
        return None

    def remove_dead_monsters(self):
        """Remove dead monsters from the list."""
        self.monsters = [m for m in self.monsters if m.is_alive]

    def update_monsters(self, player_x: int, player_y: int, game_map,
                       visibility_tracker, speed_buff: int = 0) -> List[str]:
        """Update all monsters (AI and movement).

        Args:
            player_x: Player's X coordinate
            player_y: Player's Y coordinate
            game_map: Game map
            visibility_tracker: FOV tracker
            speed_buff: Monster speed multiplier from sacrifices

        Returns:
            List of action messages
        """
        messages = []

        for monster in self.monsters[:]:
            if not monster.is_alive:
                continue

            if not visibility_tracker.is_visible(monster.x, monster.y):
                continue

            if monster.is_adjacent_to(player_x, player_y):
                messages.append(f"The {monster.name} growls menacingly!")
            else:
                distance = monster.distance_to(player_x, player_y)
                if distance <= 8:
                    if self._can_see_player(monster, player_x, player_y, game_map):
                        old_x, old_y = monster.x, monster.y
                        if monster.move_towards(player_x, player_y, game_map, speed_buff):
                            conflicting_monster = self.get_monster_at(monster.x, monster.y)
                            if conflicting_monster and conflicting_monster != monster:
                                monster.x, monster.y = old_x, old_y
                            else:
                                messages.append(f"The {monster.name} moves closer!")

        return messages

    def _can_see_player(self, monster: Monster, player_x: int, player_y: int,
                       game_map) -> bool:
        """Check if monster can see the player.

        Args:
            monster: The monster
            player_x: Player's X coordinate
            player_y: Player's Y coordinate
            game_map: Game map

        Returns:
            True if monster can see player
        """
        dx = abs(player_x - monster.x)
        dy = abs(player_y - monster.y)

        if dx == 0 and dy == 0:
            return True

        x1, y1 = monster.x, monster.y
        x2, y2 = player_x, player_y

        x_step = 1 if x1 < x2 else -1
        y_step = 1 if y1 < y2 else -1

        if dx > dy:
            error = dx / 2
            y = y1
            for x in range(x1, x2, x_step):
                if game_map[y][x] == '#':
                    return False
                error -= dy
                if error < 0:
                    y += y_step
                    error += dx
        else:
            error = dy / 2
            x = x1
            for y in range(y1, y2, y_step):
                if game_map[y][x] == '#':
                    return False
                error -= dx
                if error < 0:
                    x += x_step
                    error += dy

        return True
