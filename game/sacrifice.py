"""Sacrifice system for Terminus Veil: Blood Price."""

import random
from typing import Dict, Tuple, List, Optional
from enum import Enum
from .items import ItemType


class SacrificeType(Enum):
    """Types of sacrifices available at altars."""
    BLOOD = ("Blood", "Permanently lose 15% Max HP", "Gain +5 permanent Attack power")
    SIGHT = ("Sight", "Shrink FOV radius by 2", "Gain 25% Critical Hit chance")
    MEMORY = ("Memory", "Lose all explored map memory", "Double item spawn rates")
    WEALTH = ("Wealth", "Lose 50% of your Gold", "Gain temporary +10 Attack for 15 turns")
    AGILITY = ("Agility", "Permanently lose 1 movement speed", "Gain +10 Max HP and healing")
    SOUL = ("Soul", "Lose a random inventory item", "Permanently gain +3 Attack and +10 Max HP")
    SANITY = ("Sanity", "Monsters become faster", "You deal double damage to surprised enemies")
    HOPE = ("Hope", "Exit requires 1 more sacrifice to unlock", "Gain permanent +2 HP regeneration per turn")
    FUTURE = ("Future", "Lose 25% of your score", "Reveal entire map for current level")
    FAMILY = ("Family", "Cannot use health potions anymore", "Gain permanent vampire touch (heal when attacking)")


class Altar:
    """Represents a sacrificial altar in the dungeon."""

    def __init__(self, x: int, y: int, level: int = 1):
        """Initialize an altar.

        Args:
            x: X coordinate
            y: Y coordinate
            level: Dungeon level for sacrifice options
        """
        self.x = x
        self.y = y
        self.symbol = "Ω"
        self.used = False
        self.level = level
        self.sacrifice_options = self._generate_sacrifice_options()

    def _generate_sacrifice_options(self) -> List[SacrificeType]:
        """Generate random sacrifice options for this altar.

        Returns:
            List of available sacrifice types (always 2)
        """
        all_options = list(SacrificeType)
        # Always return exactly 2 options
        return random.sample(all_options, 2)

    def get_sacrifice_prompt(self, option_index: int) -> str:
        """Get the sacrifice prompt for a specific option.

        Args:
            option_index: Index of the sacrifice option

        Returns:
            Formatted prompt string
        """
        if option_index >= len(self.sacrifice_options):
            return ""

        sacrifice_type = self.sacrifice_options[option_index]
        name, cost, benefit = sacrifice_type.value

        prompt = f"[bold red]THE ALTAR DEMANDS {name.upper()}[/]\n\n"
        prompt += f"[red]Cost: {cost}[/]\n"
        prompt += f"[green]Benefit: {benefit}[/]\n\n"
        prompt += "[dim]Press Y to accept, N to refuse[/]"

        return prompt

    def get_sacrifice_menu(self) -> str:
        """Get the menu of available sacrifices.

        Returns:
            Formatted menu string
        """
        menu = "[bold red]THE ALTAR HUNGERS... CHOOSE YOUR SACRIFICE[/]\n\n"

        for i, sacrifice_type in enumerate(self.sacrifice_options, 1):
            name, cost, benefit = sacrifice_type.value
            menu += f"[yellow]{i}. {name}[/]\n"
            menu += f"   [dim red]Cost: {cost}[/]\n"
            menu += f"   [dim green]Benefit: {benefit}[/]\n\n"

        menu += f"[dim]Choose 1-{len(self.sacrifice_options)} or press E to cancel[/]"
        return menu


class SacrificeSystem:
    """Handles sacrifice mechanics and effects."""

    def __init__(self):
        """Initialize the sacrifice system."""
        self.altars: List[Altar] = []
        self.player_sacrifices: Dict[SacrificeType, int] = {}
        self.sacrifices_required = 1  # Sacrifices needed to unlock exit
        self.total_sacrifices_made = 0

    def spawn_altars(self, game_map, count: int = 1, level: int = 1) -> List[Altar]:
        """Spawn altars randomly on the map.

        Args:
            game_map: Game map to spawn altars on
            count: Number of altars to spawn
            level: Current dungeon level

        Returns:
            List of spawned altars
        """
        from .dungeon_generator import DungeonGenerator

        generator = DungeonGenerator(len(game_map[0]), len(game_map))
        positions = generator.find_room_center_positions(game_map, count)

        new_altars = []
        for x, y in positions:
            altar = Altar(x, y, level)
            self.altars.append(altar)
            new_altars.append(altar)

        return new_altars

    def get_altar_at(self, x: int, y: int) -> Optional[Altar]:
        """Get altar at specific position.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Altar at position or None
        """
        for altar in self.altars:
            if altar.x == x and altar.y == y and not altar.used:
                return altar
        return None

    def apply_sacrifice_effect(self, sacrifice_type: SacrificeType, player, game_state, game_map) -> str:
        """Apply the effects of a sacrifice.

        Args:
            sacrifice_type: Type of sacrifice chosen
            player: Player object
            game_state: Game state object
            game_map: Game map object

        Returns:
            Message describing the sacrifice effect
        """
        self.player_sacrifices[sacrifice_type] = self.player_sacrifices.get(sacrifice_type, 0) + 1
        self.total_sacrifices_made += 1

        name, cost, benefit = sacrifice_type.value

        if sacrifice_type == SacrificeType.BLOOD:
            hp_loss = max(10, player.max_hp // 7)  # Lose ~15% max HP
            player.max_hp = max(30, player.max_hp - hp_loss)
            player.hp = min(player.hp, player.max_hp)
            player.attack_power += 5

            return f"[bright_red]You offer your blood![/] Max HP -{hp_loss}, Attack +5 permanently!"

        elif sacrifice_type == SacrificeType.SIGHT:
            player.sight_radius_reduction = getattr(player, 'sight_radius_reduction', 0) + 2
            player.crit_chance = getattr(player, 'crit_chance', 0) + 0.25

            return f"[yellow]You sacrifice your sight![/] FOV shrinks by 2, Critical chance +25%!"

        elif sacrifice_type == SacrificeType.MEMORY:
            # Clear all explored areas
            if hasattr(game_map, 'visibility_tracker'):
                game_map.visibility_tracker.explored.clear()

            game_state.item_spawn_bonus = getattr(game_state, 'item_spawn_bonus', 0) + 100  # Double items

            return f"[cyan]You sacrifice your memories![/] Map knowledge lost, items will abound!"

        elif sacrifice_type == SacrificeType.WEALTH:
            gold_loss = player.inventory.gold // 2  # Lose 50% gold
            player.inventory.gold -= gold_loss
            player.temp_attack_buff = getattr(player, 'temp_attack_buff', 0) + 10
            player.temp_buff_turns = 15

            return f"[gold]You sacrifice your wealth![/] Lost {gold_loss} gold, Attack +10 for 15 turns!"

        elif sacrifice_type == SacrificeType.AGILITY:
            player.movement_penalty = getattr(player, 'movement_penalty', 0) + 1
            player.max_hp += 10
            player.hp += 10

            return f"[magenta]You sacrifice your agility![/] Movement slowed, but gained +10 Max HP!"

        elif sacrifice_type == SacrificeType.SOUL:
            # Remove a random item
            if player.inventory.items:
                item_type = random.choice(list(player.inventory.items.keys()))
                count = player.inventory.items[item_type]
                if count > 0:
                    player.inventory.items[item_type] -= 1
                    if player.inventory.items[item_type] <= 0:
                        del player.inventory.items[item_type]

            player.attack_power += 3
            player.max_hp += 10
            player.hp = min(player.max_hp, player.hp + 10)

            return f"[bold white]You sacrifice a piece of your soul![/] Lost an item, but gained +3 Attack and +10 Max HP!"

        elif sacrifice_type == SacrificeType.SANITY:
            game_state.monster_speed_buff = getattr(game_state, 'monster_speed_buff', 0) + 1
            player.surprise_damage = 2.0  # Double damage to surprised enemies

            return f"[bold cyan]You sacrifice your sanity![/] Monsters move faster, but you ambush fiercely!"

        elif sacrifice_type == SacrificeType.HOPE:
            self.sacrifices_required += 1
            player.hp_regeneration = getattr(player, 'hp_regeneration', 0) + 2

            return f"[bold yellow]You sacrifice your hope![/] Deeper descent requires more sacrifice, but you regenerate 2 HP per turn!"

        elif sacrifice_type == SacrificeType.FUTURE:
            score_loss = game_state.score // 4  # Lose 25% score
            game_state.score = max(0, game_state.score - score_loss)

            # Reveal entire map
            if hasattr(game_map, 'visibility_tracker'):
                for y in range(len(game_map.tiles)):
                    for x in range(len(game_map.tiles[0])):
                        game_map.visibility_tracker.explored.add((x, y))

            return f"[bold green]You sacrifice your future![/] Lost {score_loss} score, but the map is revealed!"

        elif sacrifice_type == SacrificeType.FAMILY:
            player.can_use_potions = False
            player.vampire_touch = True  # Heal when attacking

            return f"[bold red]You sacrifice your family![/] Potions are forbidden, but you heal when dealing damage!"

        return f"[red]The altar accepts your {name.lower()} sacrifice![/]"

    def can_use_exit(self) -> bool:
        """Check if player can use the exit based on sacrifices made.

        Returns:
            True if player has made enough sacrifices
        """
        return self.total_sacrifices_made >= self.sacrifices_required

    def get_sacrifices_remaining(self) -> int:
        """Get how many more sacrifices are needed for the exit.

        Returns:
            Number of sacrifices needed
        """
        return max(0, self.sacrifices_required - self.total_sacrifices_made)

    def get_sacrifice_count(self, sacrifice_type: SacrificeType) -> int:
        """Get how many times a sacrifice type has been made.

        Args:
            sacrifice_type: Type of sacrifice

        Returns:
            Number of times sacrificed
        """
        return self.player_sacrifices.get(sacrifice_type, 0)

    def get_total_sacrifices(self) -> int:
        """Get total number of sacrifices made.

        Returns:
            Total sacrifice count
        """
        return self.total_sacrifices_made

    def reset(self):
        """Reset the sacrifice system for a new game."""
        self.altars.clear()
        self.player_sacrifices.clear()
        self.sacrifices_required = 1
        self.total_sacrifices_made = 0
