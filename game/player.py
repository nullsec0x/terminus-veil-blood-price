
from .items import Inventory


class Player:

    def __init__(self, x: int, y: int):
        """Initialize the player at given coordinates.

        Args:
            x: X coordinate on the map
            y: Y coordinate on the map
        """
        self.x = x
        self.y = y
        self.symbol = '☺'
        self.hp = 100
        self.max_hp = 100
        self.attack_power = 10
        self.inventory = Inventory()

        self._reset_sacrifice_attributes()

    def _reset_sacrifice_attributes(self):
        """Reset all sacrifice-related attributes to default values."""
        self.crit_chance = 0.0
        self.memory_loss_count = 0
        self.sight_radius_reduction = 0
        self.disabled_movements = set()
        self.temp_attack_buff = 0
        self.temp_buff_turns = 0
        self.movement_penalty = 0
        self.hp_regeneration = 0
        self.surprise_damage = 1.0
        self.vampire_touch = False
        self.can_use_potions = True

    def move(self, dx: int, dy: int, game_map) -> bool:
        """Attempt to move the player by dx, dy.

        Args:
            dx: Change in x coordinate
            dy: Change in y coordinate
            game_map: The game map to check for collisions

        Returns:
            True if move was successful, False if blocked
        """
        if dx > 0 and 'right' in self.disabled_movements:
            return False
        if dx < 0 and 'left' in self.disabled_movements:
            return False
        if dy > 0 and 'down' in self.disabled_movements:
            return False
        if dy < 0 and 'up' in self.disabled_movements:
            return False

        if self.movement_penalty > 0 and random.random() < self.movement_penalty * 0.1:
            return False

        new_x = self.x + dx
        new_y = self.y + dy

        if (0 <= new_x < len(game_map[0]) and
            0 <= new_y < len(game_map) and
            game_map[new_y][new_x] != '#'):
            self.x = new_x
            self.y = new_y
            return True
        return False

    def take_damage(self, damage: int):
        """Apply damage to the player.

        Args:
            damage: Amount of damage to take
        """
        self.hp = max(0, self.hp - damage)

    def heal(self, amount: int):
        """Heal the player.

        Args:
            amount: Amount of HP to restore
        """
        self.hp = min(self.max_hp, self.hp + amount)

    def is_alive(self) -> bool:
        """Check if the player is still alive.

        Returns:
            True if player has HP > 0
        """
        return self.hp > 0

    def get_effective_attack(self) -> int:
        """Get attack power including temporary buffs.

        Returns:
            Effective attack power
        """
        return self.attack_power + self.temp_attack_buff

    def update_temporary_buffs(self):
        """Update temporary buff durations and regeneration."""
        if self.temp_attack_buff > 0 and self.temp_buff_turns > 0:
            self.temp_buff_turns -= 1
            if self.temp_buff_turns <= 0:
                self.temp_attack_buff = 0

        if self.hp_regeneration > 0 and self.hp < self.max_hp:
            self.hp = min(self.max_hp, self.hp + self.hp_regeneration)

    def can_crit(self) -> bool:
        """Check if attack should be critical.

        Returns:
            True if critical hit occurs
        """
        import random
        return random.random() < self.crit_chance

    def reset(self, x: int, y: int):
        """Reset player to initial state at new position.

        Args:
            x: New X coordinate
            y: New Y coordinate
        """
        self.x = x
        self.y = y
        self.hp = 100
        self.max_hp = 100
        self.attack_power = 10
        self.inventory = Inventory()

        # Reset all sacrifice effects
        self._reset_sacrifice_attributes()
