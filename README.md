# Terminus Veil: Blood Price - A Python Roguelike by Nullsec0x

![banner](./assets/banner.png)

A turn-based roguelike game built with Python and Textualize, featuring procedural dungeon generation, combat, inventory management, progressive difficulty, and beautiful ASCII art visuals.  
This enhanced version introduces **character classes, magic systems, expanded content, quests, and deeper gameplay mechanics with a unique Blood Price system that demands strategic sacrifices.**

---

## Features 

### Core Gameplay
- **Turn-based movement and combat** - Move with WASD or arrow keys
- **Procedural dungeon generation** - Every level is unique using BSP algorithm, crafted by Nullsec0x
- **Field of View (FOV)** - Realistic line-of-sight with exploration memory, implemented by Nullsec0x
- **Progressive difficulty** - Each level becomes more challenging, designed by Nullsec0x
- **Character Classes** - Choose from Warrior, Rogue, or Mage with unique abilities
- **Magic System** - Cast spells with mana management and spell cooldowns
- **Quest System** - Complete objectives for special rewards
- **Save/Load Functionality** - Continue your adventure across sessions
- **Blood Price System** - Strategic sacrifices for powerful benefits

### Visual Design 
- **Beautiful ASCII art** - Enhanced character designs with Unicode symbols
- **Smart wall rendering** - Walls use proper line-drawing characters (╔╗╚╝║═╬)
- **Color-coded entities** - Different colors for monsters, items, and terrain
- **Expressive characters** - Player (☺), Goblins (♠), Orcs (♣), Dragons (♦), Liches (♛), Elementals (◘)
- **Enhanced UI** - Improved status panels and interactive menus
- **Sacrifice Altars** - Special interactive locations for blood rituals

### Combat System 
- **Multiple monster types**: Goblins (♠), Orcs (♣), Dragons (♦), Liches (♛), Elementals (◘)
- **Strategic combat** - Attack by moving into enemies or using ranged spells
- **Advanced Monster AI** - Enemies use tactics, flee when wounded, and work together
- **Health, mana, and damage system** with visual feedback
- **Death animations** - Monsters become skulls (☠) when defeated
- **Critical hits and status effects** - Poison, burning, freezing conditions
- **Sacrificial combat** - Offer defeated enemies to gain temporary powers

### Inventory & Items 
- **Expanded collectible items**: Health Potions (♥), Mana Potions (♠), Gold (¤), Magic Scrolls (♪), Weapons (†), Armor (◘), Rings (○), Amulets (☼)
- **Enhanced inventory management** - Categorized inventory with sorting options
- **Item usage** - Press 1 for health potions, 2 for mana potions, 3 for scrolls, i for inventory
- **Equipment system** - Multiple equipment slots with stat bonuses
- **Item identification** - Unknown items reveal properties when used
- **Sacrificial components** - Collect body parts and essences for rituals

### Progression by Nullsec0x
- **Multi-level dungeons** - Descend deeper by finding the exit (▼)
- **Scaling difficulty** - More monsters, items, and environmental hazards
- **Experience and Leveling** - Gain XP to increase stats and learn new abilities
- **Score system** - Earn points for progression, combat, and quest completion
- **Persistent progression** - Keep items, stats, and quest progress between levels
- **Sacrifice progression** - Unlock permanent bonuses through blood offerings

---

## The Blood Price System

### Sacrifice Mechanics
- **Altars of Power (♈)** scattered throughout dungeons accept offerings
- Sacrifice enemies to gain temporary buffs and permanent upgrades
- **Blood Essence** currency earned from sacrifices unlocks powerful abilities
- **Strategic choices** - sacrifice health, items, or enemies for different benefits

### Types of Sacrifices
| Symbol | Sacrifice Type | Effect |
|--------|----------------|--------|
| ♈ | Health Sacrifice | Gain massive temporary power at cost of HP |
| ⚷ | Enemy Sacrifice | Offer defeated monsters for permanent stat boosts |
| ☣ | Item Sacrifice | Destroy powerful items for unique abilities |
| ⚔ | Combat Sacrifice | Enter berserk state with enhanced abilities |

### Blood Magic Abilities
- **Hemomancy** - Cast spells using HP instead of mana
- **Blood Rites** - Rituals that provide long-lasting buffs
- **Sacrificial Protection** - Temporary invulnerability at great cost
- **Essence Harvest** - Extract power from defeated enemies

---

## Visual Elements 

### Characters
| Symbol | Entity | Color |
|--------|--------|-------|
| ☺ | Player | Bright Yellow |
| ♠ | Goblin | Green |
| ♣ | Orc | Red |
| ♦ | Dragon | Bright Red |
| ♛ | Lich | Purple |
| ◘ | Elemental | Cyan |
| ☠ | Corpse | Gray |
| ♥ | Health Potion | Bright Red |
| ♠ | Mana Potion | Bright Blue |
| ¤ | Gold | Yellow |
| ♪ | Magic Scroll | Bright Magenta |
| † | Weapon | Bright White |
| ◘ | Armor | Gray |
| ○ | Ring | Bright Yellow |
| ☼ | Amulet | Bright Cyan |
| ▼ | Exit/Stairs | Bright Green |
| ? | Quest Item | Bright Yellow |
| ♈ | Sacrifice Altar | Blood Red |
| ⚷ | Blood Essence | Crimson |

### Map Elements
- **Walls**: Smart line-drawing characters (╔╗╚╝║═╬╦╩╠╣)
- **Floors**: Small dots (·) for visible areas, shaded (░) for explored
- **Visibility**: Full color for visible, dimmed for explored, hidden for unseen
- **Hazards**: Traps and environmental dangers with special markers
- **Ritual Circles**: Special areas for powerful sacrifices

---

## Controls 

| Key | Action |
|-----|--------|
| WASD / Arrow Keys | Move / Attack |
| 1 | Use Health Potion (♥) |
| 2 | Use Mana Potion (♠) |
| 3 | Use Magic Scroll (♪) |
| i | Open Inventory |
| c | View Character Sheet |
| q | View Quest Log |
| m | Cast Spell / Use Magic |
| x | Perform Sacrifice (at altars) |
| r | Restart Game |
| s | Save Game |
| l | Load Game |
| Esc | Close Menu / Cancel |
| q | Quit |

---

## Installation & Running 

### Requirements
- Python 3.11+
- Textualize library

### Setup
```bash
# Clone the repository
git clone https://github.com/nullsec0x/terminus-veil-blood-price
cd terminus-veil-blood-price

# Install dependencies
pip install textual

# Run the game
python3 main.py
```

### Building Executable 
To create a standalone executable:
```bash
pip install pyinstaller
pyinstaller --onefile main.py
```

---

## Game Mechanics 

### Combat
- Move into an enemy to attack or use ranged spells
- Damage is calculated with stats, equipment, and randomness
- Monsters attack back when adjacent and use special abilities
- Dead monsters leave skulls (☠) and drop loot
- Critical hits and status effects add tactical depth
- **Sacrificial Finishers** - Special moves that cost HP but guarantee kills

### Character System
- **Warrior**: High health and strength, combat-focused abilities, excels at physical sacrifices
- **Rogue**: High dexterity, stealth, and critical strikes, can sacrifice stealth for power
- **Mage**: Powerful spells but lower defense, mana management, blood magic specialization

### Blood Price System
- **Health for Power**: Sacrifice HP for temporary combat enhancements
- **Enemy Essence**: Offer monster remains at altars for permanent upgrades
- **Item Destruction**: Sacrifice powerful items for unique blood abilities
- **Ritual Consequences**: Every sacrifice has permanent story implications

### Magic System
- **Spell Schools**: Destruction, Restoration, Alteration, Blood Magic
- **Mana Pool**: Regenerates over time and through potions
- **Spell Effects**: Direct damage, healing, buffs, debuffs, and utility
- **Spell Learning**: Unlock new spells as you level up
- **Blood Casting**: Use HP instead of mana for more powerful effects

### Items
- **Health Potions (♥)**: Restore 25–40 HP based on quality
- **Mana Potions (♠)**: Restore 15–30 MP based on quality
- **Gold (¤)**: Currency for merchants (future feature)
- **Magic Scrolls (♪)**: One-time spell effects
- **Weapons (†)**: Increase attack power with special properties
- **Armor (◘)**: Provide defense and resistance to elements
- **Rings (○) and Amulets (☼)**: Grant special bonuses and abilities
- **Ritual Components**: Body parts, essences, and artifacts for sacrifices

### Progression
- Find the stairs (▼) to advance to the next level
- Gain experience from combat and quest completion
- Level up to increase stats and learn new abilities
- Each level introduces new monsters, hazards, and loot
- Complete quests for unique rewards and story progression
- **Sacrifice milestones** - Permanent upgrades through blood offerings

---

## Architecture 

The game is built with a modular architecture by Nullsec0x:

- `main.py` - Main application and UI using Textualize
- `game/player.py` - Player character, classes, and inventory
- `game/game_map.py` - Map rendering and FOV system
- `game/dungeon_generator.py` - Procedural generation algorithms
- `game/monster.py` - Monster AI and management
- `game/combat.py` - Combat system and game state
- `game/items.py` - Item system and inventory management
- `game/fov.py` - Field of view calculations
- `game/ascii_art.py` - Visual enhancements and ASCII art
- `game/magic.py` - Spell system and magic effects
- `game/quests.py` - Quest tracking and objectives
- `game/save_system.py` - Save and load functionality
- `game/sacrifice.py` - Blood Price system and ritual mechanics
- `game/blood_magic.py` - Hemomancy and sacrifice-based spells

---

## Development 

### Project Structure
```
Terminus-Veil-Blood-Price/
├── main.py              # Main application entry point
├── game/                # Game logic modules
│   ├── __init__.py
│   ├── player.py        # Player character and classes
│   ├── game_map.py      # Map and rendering
│   ├── dungeon_generator.py  # Procedural generation
│   ├── monster.py       # Monster system
│   ├── combat.py        # Combat and game state
│   ├── items.py         # Items and inventory
│   ├── fov.py           # Field of view
│   ├── ascii_art.py     # Visual enhancements
│   ├── magic.py         # Spell system
│   ├── quests.py        # Quest system
│   ├── save_system.py   # Save/load functionality
│   ├── sacrifice.py     # Blood Price mechanics
│   └── blood_magic.py   # Sacrifice-based magic
└── README.md            # This file
```

### Key Algorithms 
- **BSP Dungeon Generation**: Creates rooms and corridors with varied terrain
- **Shadowcasting FOV**: Realistic line-of-sight calculation
- **Smart Wall Rendering**: Automatic line-drawing character selection
- **Turn-based System**: Ensures fair gameplay with initiative tracking
- **Pathfinding AI**: Monsters use efficient pathfinding to chase players
- **Sacrifice Calculation**: Balanced risk/reward system for blood offerings

### Visual Enhancements 
- **Unicode Characters**: Rich symbol set for better visual appeal
- **Color Coding**: Textualize rich markup for entity differentiation
- **Smart Walls**: Context-aware wall character selection
- **Memory System**: Different visual states for visible/explored/hidden areas
- **Animated Effects**: Spell animations and combat feedback
- **Blood Effects**: Visual indicators for sacrifice mechanics

---

## Contributing

This project was built by Nullsec0x with contributions from **@fraisazwina** and **@froggy_inluv**.  
Feel free to fork and extend with additional features like:
- Additional character classes and specializations
- More monster types and boss encounters
- Expanded magic schools and spells
- Merchant and economy system
- Multi-level dungeon themes (forest, caves, castle)
- Sound effects and music integration
- Graphical tile sets alongside ASCII
- More intricate sacrifice rituals and consequences
- Bloodline system tracking sacrifice choices across generations

---

## License

Open source - feel free to use and modify. Created by Nullsec0x.

---

## Credits

Built by Nullsec0x with:
- [Textualize](https://textual.textualize.io/) - Modern TUI framework
- Python 3.11 - Programming language
- Unicode characters for enhanced ASCII art
- Various algorithms from roguelike development community
- Inspiration from classic roguelikes like NetHack, ADOM, and Brogue
- Themes of sacrifice and consequence from dark fantasy literature
