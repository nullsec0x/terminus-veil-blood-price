"""Item and inventory system for the roguelike game."""

import random
from typing import List, Dict, Optional, Tuple
from enum import Enum


class ItemType(Enum):
    """Different types of items."""
    HEALTH_POTION = ("♥", "Health Potion", "Restores 25 HP")
    GOLD = ("¤", "Gold", "Valuable currency")
    MAGIC_SCROLL = ("♪", "Magic Scroll", "Mysterious scroll with unknown power")
    WEAPON = ("†", "Sword", "A sharp blade that increases attack power")


class Item:
    """Represents an item in the game."""
    
    def __init__(self, x: int, y: int, item_type: ItemType, value: int = 1):
        """Initialize an item.
        
        Args:
            x: X coordinate
            y: Y coordinate
            item_type: Type of item
            value: Value/quantity of the item
        """
        self.x = x
        self.y = y
        self.item_type = item_type
        self.symbol = item_type.value[0]
        self.name = item_type.value[1]
        self.description = item_type.value[2]
        self.value = value
        self.is_collected = False
    
    def use(self, player) -> str:
        """Use the item on the player.
        
        Args:
            player: Player object
            
        Returns:
            Message describing the effect
        """
        if self.item_type == ItemType.HEALTH_POTION:
            heal_amount = min(25, player.max_hp - player.hp)
            player.hp += heal_amount
            return f"You drink the health potion and recover {heal_amount} HP!"
        
        elif self.item_type == ItemType.MAGIC_SCROLL:
            effect = random.choice([
                "heal", "damage_boost", "nothing"
            ])
            
            if effect == "heal":
                heal_amount = random.randint(10, 30)
                player.hp = min(player.max_hp, player.hp + heal_amount)
                return f"The scroll glows and heals you for {heal_amount} HP!"
            elif effect == "damage_boost":
                player.attack_power += 2
                return "The scroll enhances your combat abilities! Attack +2!"
            else:
                return "The scroll crumbles to dust. Nothing happens."
        
        elif self.item_type == ItemType.WEAPON:
            player.attack_power += 5
            return "You equip the sword! Attack power increased by 5!"
        
        elif self.item_type == ItemType.GOLD:
            return f"You collect {self.value} gold pieces!"
        
        return f"You can't use the {self.name}."


class Inventory:
    """Manages the player's inventory."""
    
    def __init__(self):
        """Initialize an empty inventory."""
        self.items: Dict[ItemType, int] = {}
        self.gold = 0
    
    def add_item(self, item: Item) -> str:
        """Add an item to the inventory.
        
        Args:
            item: Item to add
            
        Returns:
            Message describing what was added
        """
        if item.item_type == ItemType.GOLD:
            self.gold += item.value
            return f"Picked up {item.value} gold!"
        else:
            if item.item_type in self.items:
                self.items[item.item_type] += item.value
            else:
                self.items[item.item_type] = item.value
            return f"Picked up {item.name}!"
    
    def use_item(self, item_type: ItemType, player) -> Optional[str]:
        """Use an item from the inventory.
        
        Args:
            item_type: Type of item to use
            player: Player object
            
        Returns:
            Message describing the effect, or None if item not available
        """
        if item_type not in self.items or self.items[item_type] <= 0:
            return None
        
        temp_item = Item(0, 0, item_type)
        effect_message = temp_item.use(player)
        
        self.items[item_type] -= 1
        if self.items[item_type] <= 0:
            del self.items[item_type]
        
        return effect_message
    
    def get_item_count(self, item_type: ItemType) -> int:
        """Get the count of a specific item type.
        
        Args:
            item_type: Type of item
            
        Returns:
            Number of items of that type
        """
        return self.items.get(item_type, 0)
    
    def get_inventory_display(self) -> str:
        """Get a string representation of the inventory.
        
        Returns:
            Formatted inventory string
        """
        lines = [f"Gold: {self.gold}"]
        
        for item_type, count in self.items.items():
            lines.append(f"{item_type.value[1]}: {count}")
        
        return "\n".join(lines) if lines else "Empty"


class ItemManager:
    """Manages all items in the game world."""
    
    def __init__(self):
        """Initialize the item manager."""
        self.items: List[Item] = []
    
    def spawn_items(self, game_map, count: int = 8):
        """Spawn items randomly on the map.
        
        Args:
            game_map: Game map to spawn items on
            count: Number of items to spawn
        """
        from .dungeon_generator import DungeonGenerator
        
        generator = DungeonGenerator(len(game_map[0]), len(game_map))
        positions = generator.find_valid_positions(game_map, count)
        
        for i, (x, y) in enumerate(positions):
            # Choose item type with weighted probability
            rand = random.random()
            
            if rand < 0.4:  # 40% chance
                item_type = ItemType.GOLD
                value = random.randint(5, 20)
            elif rand < 0.7:  # 30% chance
                item_type = ItemType.HEALTH_POTION
                value = 1
            elif rand < 0.9:  # 20% chance
                item_type = ItemType.MAGIC_SCROLL
                value = 1
            else:  # 10% chance
                item_type = ItemType.WEAPON
                value = 1
            
            item = Item(x, y, item_type, value)
            self.items.append(item)
    
    def get_item_at(self, x: int, y: int) -> Optional[Item]:
        """Get item at specific position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Item at position or None
        """
        for item in self.items:
            if item.x == x and item.y == y and not item.is_collected:
                return item
        return None
    
    def collect_item(self, x: int, y: int) -> Optional[Item]:
        """Collect an item at the specified position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Collected item or None
        """
        item = self.get_item_at(x, y)
        if item:
            item.is_collected = True
            return item
        return None
    
    def get_visible_items(self, visibility_tracker) -> List[Item]:
        """Get all items that are currently visible.
        
        Args:
            visibility_tracker: FOV tracker
            
        Returns:
            List of visible items
        """
        visible_items = []
        for item in self.items:
            if (not item.is_collected and 
                visibility_tracker.is_visible(item.x, item.y)):
                visible_items.append(item)
        return visible_items

