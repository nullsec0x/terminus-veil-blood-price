
import random
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Header, Footer
from textual.binding import Binding

from game.player import Player
from game.game_map import GameMap
from game.monster import MonsterManager
from game.combat import CombatSystem, GameState
from game.items import ItemManager, ItemType
from game.fov import FOVCalculator, VisibilityTracker
from game.sacrifice import SacrificeSystem, SacrificeType


class GameDisplay(Static):

    def __init__(self, game_map: GameMap, player: Player, monster_manager: MonsterManager,
                 item_manager: ItemManager, game_state: GameState, sacrifice_system: SacrificeSystem):
        super().__init__()
        self.game_map = game_map
        self.player = player
        self.monster_manager = monster_manager
        self.item_manager = item_manager
        self.game_state = game_state
        self.sacrifice_system = sacrifice_system
        self.update_display()

    def update_display(self):
        if self.game_state and self.game_state.game_over:
            game_over_text = """
[bold red on black]
╔══════════════════════════════════════╗
║                                      ║
║           BLOOD PRICE PAID           ║
║              GAME OVER               ║
║                                      ║
║        Press 'r' to start anew       ║
║         Press 'q' to embrace         ║
║              the void                ║
║                                      ║
╚══════════════════════════════════════╝
[/]
"""
            self.update(game_over_text)
        else:
            map_str = self.game_map.render_with_entities(
                self.player.x, self.player.y, self.monster_manager, self.item_manager, self.player
            )

            sacrifices_needed = self.sacrifice_system.get_sacrifices_remaining()
            if sacrifices_needed > 0:
                map_str += f"\n[red]Sacrifices needed for exit: {sacrifices_needed}[/]"
            else:
                map_str += f"\n[green]The exit awaits! ({self.sacrifice_system.get_total_sacrifices()} sacrifices made)[/]"

            self.update(f"[white on black]{map_str}[/]")


class StatusDisplay(Static):

    def __init__(self, player: Player, game_state: GameState, sacrifice_system: SacrificeSystem):
        super().__init__()
        self.player = player
        self.game_state = game_state
        self.sacrifice_system = sacrifice_system
        self.update_status()

    def update_status(self):
        inventory_str = self.player.inventory.get_inventory_display()

        sacrifice_info = f"\n[bold red]Total Sacrifices: {self.sacrifice_system.get_total_sacrifices()}[/]"
        sacrifice_info += f"\n[red]Needed for exit: {self.sacrifice_system.get_sacrifices_remaining()}[/]"

        effects = []
        if hasattr(self.player, 'crit_chance') and self.player.crit_chance > 0:
            effects.append(f"Crit: {self.player.crit_chance*100:.1f}%")
        if hasattr(self.player, 'sight_radius_reduction') and self.player.sight_radius_reduction > 0:
            effects.append(f"FOV -{self.player.sight_radius_reduction}")
        if hasattr(self.player, 'hp_regeneration') and self.player.hp_regeneration > 0:
            effects.append(f"Regen: +{self.player.hp_regeneration} HP/turn")
        if hasattr(self.player, 'vampire_touch') and self.player.vampire_touch:
            effects.append("Vampiric")
        if hasattr(self.player, 'surprise_damage') and self.player.surprise_damage > 1.0:
            effects.append("Ambush x2")
        if not getattr(self.player, 'can_use_potions', True):
            effects.append("No Potions")

        if effects:
            sacrifice_info += f"\n[yellow]Effects: {', '.join(effects)}[/]"
        else:
            sacrifice_info += f"\n[dim]No active effects[/]"

        status_text = f"""
[bold]Terminus Veil: Blood Price[/bold]
Level: {self.game_state.current_level}
Score: {self.game_state.score}

[bold]Player Status[/bold]
HP: {self.player.hp}/{self.player.max_hp}
Position: ({self.player.x}, {self.player.y})
Attack: {self.player.get_effective_attack()}
{sacrifice_info}

[bold]Inventory[/bold]
{inventory_str}

[dim]Altars: Ω | Exit: ▼ | Press E at altars[/dim]
        """
        self.update(status_text.strip())


class MessageDisplay(Static):

    def __init__(self, combat_system: CombatSystem, sacrifice_system: SacrificeSystem, parent_app):
        super().__init__()
        self.combat_system = combat_system
        self.sacrifice_system = sacrifice_system
        self.parent_app = parent_app
        self.update_messages()

    def update_messages(self):
        if self.parent_app.in_altar_menu and self.parent_app.current_altar:
            if self.parent_app.waiting_for_confirmation:
                # Show confirmation prompt
                sacrifice_type = self.parent_app.current_altar.sacrifice_options[self.parent_app.selected_sacrifice_index]
                name, cost, benefit = sacrifice_type.value
                message_text = f"""[bold red]THE ALTAR DEMANDS {name.upper()}[/]

[red]Cost: {cost}[/]
[green]Benefit: {benefit}[/]

[bold]Will you pay the price?[/]
[green]Press Y to accept[/]  [red]Press N to refuse[/]"""
            else:
                message_text = self.parent_app.current_altar.get_sacrifice_menu()
        else:
            messages = self.combat_system.get_recent_messages(8)
            if messages:
                message_text = "\n".join(messages)
            else:
                message_text = "Welcome to Terminus Veil: Blood Price!\n\n[red]SACRIFICES MUST BE MADE TO PROGRESS[/]\n\nFind altars (Ω) and press 'E' to interact.\nEach altar offers 2 random sacrifices.\nChoose wisely - effects are permanent!"

        self.update(f"[bold]The Price Demands[/bold]\n{message_text}")


class RoguelikeApp(App):

    CSS = """
    Screen {
        layout: horizontal;
    }

    #game_area {
        width: 4fr;
        border: solid white;
        padding: 1;
        overflow: auto;
    }

    #info_area {
        width: 1fr;
        layout: vertical;
        margin-left: 1;
        min-width: 30;
    }

    #status_area {
        height: 1fr;
        border: solid white;
        padding: 1;
        margin-bottom: 1;
    }

    #message_area {
        height: 1fr;
        border: solid white;
        padding: 1;
        overflow: auto;
    }

    GameDisplay {
        text-style: bold;
        overflow: auto;
    }

    MessageDisplay {
        overflow-y: auto;
        max-height: 100%;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("up,w", "move_up", "Move Up"),
        Binding("down,s", "move_down", "Move Down"),
        Binding("left,a", "move_left", "Move Left"),
        Binding("right,d", "move_right", "Move Right"),
        Binding("r", "restart", "Restart"),
        Binding("i", "use_item", "Use Item"),
        Binding("e", "interact", "Interact"),
        Binding("y", "confirm_yes", "Yes"),
        Binding("n", "confirm_no", "No"),
        Binding("1", "select_1", "Select 1"),
        Binding("2", "select_2", "Select 2"),
    ]

    def __init__(self):
        super().__init__()
        self.in_altar_menu = False
        self.current_altar = None
        self.selected_sacrifice_index = 0
        self.waiting_for_confirmation = False
        self._initialize_game()

    def _initialize_game(self):
        self.game_map = GameMap()
        start_x, start_y = self.game_map.player_start
        self.player = Player(start_x, start_y)

        self.monster_manager = MonsterManager()
        self.combat_system = CombatSystem()
        self.game_state = GameState()
        self.item_manager = ItemManager()
        self.sacrifice_system = SacrificeSystem()

        self.game_map.place_exit()

        monster_count = self.game_state.get_monster_count_for_level()
        item_count = self.game_state.get_item_count_for_level()

        self.monster_manager.spawn_monsters(self.game_map.tiles, monster_count,
                                          self.game_state.current_level)
        self.item_manager.spawn_items(self.game_map.tiles, item_count)

        altar_count = min(2 + self.game_state.current_level // 2, 4)
        self.game_map.place_altars(self.sacrifice_system, altar_count, self.game_state.current_level)

        self.game_map.fov_calculator = FOVCalculator(self.game_map.tiles)
        self.game_map.visibility_tracker = VisibilityTracker()
        self.game_map.update_fov(self.player.x, self.player.y)

        self.game_map.player = self.player

        # Reset menu states
        self.in_altar_menu = False
        self.current_altar = None
        self.selected_sacrifice_index = 0
        self.waiting_for_confirmation = False

    def _advance_to_next_level(self):
        self.game_state.advance_level()

        self.game_map = GameMap()
        start_x, start_y = self.game_map.player_start
        self.player.x = start_x
        self.player.y = start_y

        self.monster_manager = MonsterManager()
        self.item_manager = ItemManager()

        self.game_map.place_exit()

        monster_count = self.game_state.get_monster_count_for_level()
        item_count = self.game_state.get_item_count_for_level()

        if hasattr(self.game_state, 'item_spawn_bonus'):
            item_count += self.game_state.item_spawn_bonus // 50

        self.monster_manager.spawn_monsters(self.game_map.tiles, monster_count,
                                          self.game_state.current_level)
        self.item_manager.spawn_items(self.game_map.tiles, item_count)

        altar_count = min(2 + self.game_state.current_level // 2, 4)
        self.game_map.place_altars(self.sacrifice_system, altar_count, self.game_state.current_level)

        self.game_map.fov_calculator = FOVCalculator(self.game_map.tiles)
        self.game_map.visibility_tracker = VisibilityTracker()
        self.game_map.update_fov(self.player.x, self.player.y)

        self.game_map.player = self.player

        game_display = self.query_one(GameDisplay)
        game_display.game_map = self.game_map
        game_display.player = self.player
        game_display.monster_manager = self.monster_manager
        game_display.item_manager = self.item_manager
        game_display.game_state = self.game_state
        game_display.sacrifice_system = self.sacrifice_system

        self.combat_system.combat_log.append(f"[bold]Descending to level {self.game_state.current_level}...[/]")
        sacrifices_needed = self.sacrifice_system.get_sacrifices_remaining()
        if sacrifices_needed > 0:
            self.combat_system.combat_log.append(f"[red]The exit demands {sacrifices_needed} more sacrifice(s)![/]")

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Container(id="game_area"):
                yield GameDisplay(self.game_map, self.player, self.monster_manager,
                                self.item_manager, self.game_state, self.sacrifice_system)
            with Container(id="info_area"):
                with Container(id="status_area"):
                    yield StatusDisplay(self.player, self.game_state, self.sacrifice_system)
                with Container(id="message_area"):
                    yield MessageDisplay(self.combat_system, self.sacrifice_system, self)
        yield Footer()

    def action_move_up(self) -> None:
        if not self.in_altar_menu:
            self._try_move(0, -1)

    def action_move_down(self) -> None:
        if not self.in_altar_menu:
            self._try_move(0, 1)

    def action_move_left(self) -> None:
        if not self.in_altar_menu:
            self._try_move(-1, 0)

    def action_move_right(self) -> None:
        if not self.in_altar_menu:
            self._try_move(1, 0)

    def action_interact(self) -> None:
        if self.in_altar_menu:
            self.in_altar_menu = False
            self.current_altar = None
            self.waiting_for_confirmation = False
            self.combat_system.combat_log.append("You step away from the altar.")
            self._update_displays()
            return

        altar = self.sacrifice_system.get_altar_at(self.player.x, self.player.y)
        if altar and not altar.used:
            self.current_altar = altar
            self.in_altar_menu = True
            self.selected_sacrifice_index = 0
            self.waiting_for_confirmation = False
            self.combat_system.combat_log.append("You approach the ancient altar...")
            self._update_displays()
        else:
            self.combat_system.combat_log.append("Nothing to interact with here.")
            self._update_displays()

    def action_confirm_yes(self) -> None:
        if self.waiting_for_confirmation and self.current_altar:
            sacrifice_type = self.current_altar.sacrifice_options[self.selected_sacrifice_index]
            result = self.sacrifice_system.apply_sacrifice_effect(
                sacrifice_type, self.player, self.game_state, self.game_map
            )
            self.current_altar.used = True
            self.combat_system.combat_log.append(result)

            if self.sacrifice_system.can_use_exit():
                self.combat_system.combat_log.append("[green]The exit groans open![/]")

            self.in_altar_menu = False
            self.current_altar = None
            self.waiting_for_confirmation = False
            self._update_displays()

    def action_confirm_no(self) -> None:
        if self.waiting_for_confirmation:
            self.waiting_for_confirmation = False
            self.combat_system.combat_log.append("You refuse the altar's demand.")
            self._update_displays()

    def _select_sacrifice_option(self, index: int):
        if not self.in_altar_menu or not self.current_altar:
            return

        if index < len(self.current_altar.sacrifice_options):
            self.selected_sacrifice_index = index
            self.waiting_for_confirmation = True
            self._update_displays()

    def action_select_1(self) -> None:
        if self.in_altar_menu and not self.waiting_for_confirmation:
            self._select_sacrifice_option(0)

    def action_select_2(self) -> None:
        if self.in_altar_menu and not self.waiting_for_confirmation:
            self._select_sacrifice_option(1)

    def action_restart(self) -> None:
        self.game_state = GameState()
        self.sacrifice_system = SacrificeSystem()

        self.game_map = GameMap()
        start_x, start_y = self.game_map.player_start
        self.player = Player(start_x, start_y)

        self.monster_manager = MonsterManager()
        self.combat_system = CombatSystem()
        self.item_manager = ItemManager()

        self.game_map.place_exit()

        monster_count = self.game_state.get_monster_count_for_level()
        item_count = self.game_state.get_item_count_for_level()

        self.monster_manager.spawn_monsters(self.game_map.tiles, monster_count,
                                          self.game_state.current_level)
        self.item_manager.spawn_items(self.game_map.tiles, item_count)

        altar_count = min(2 + self.game_state.current_level // 2, 4)
        self.game_map.place_altars(self.sacrifice_system, altar_count, self.game_state.current_level)

        self.game_map.fov_calculator = FOVCalculator(self.game_map.tiles)
        self.game_map.visibility_tracker = VisibilityTracker()
        self.game_map.update_fov(self.player.x, self.player.y)

        self.game_map.player = self.player

        self.in_altar_menu = False
        self.current_altar = None
        self.selected_sacrifice_index = 0
        self.waiting_for_confirmation = False

        game_display = self.query_one(GameDisplay)
        game_display.game_map = self.game_map
        game_display.player = self.player
        game_display.monster_manager = self.monster_manager
        game_display.item_manager = self.item_manager
        game_display.game_state = self.game_state
        game_display.sacrifice_system = self.sacrifice_system

        status_display = self.query_one(StatusDisplay)
        status_display.player = self.player
        status_display.game_state = self.game_state
        status_display.sacrifice_system = self.sacrifice_system

        message_display = self.query_one(MessageDisplay)
        message_display.combat_system = self.combat_system
        message_display.sacrifice_system = self.sacrifice_system
        message_display.parent_app = self

        self.combat_system.clear_log()
        self.combat_system.combat_log.append("[bold red]A new journey begins... All is forgotten![/]")

        self.refresh()
        self._update_displays()

    def action_use_item(self) -> None:
        if not self.in_altar_menu:
            if not getattr(self.player, 'can_use_potions', True):
                self.combat_system.combat_log.append("[red]You are forbidden from using potions![/]")
                return

            result = self.player.inventory.use_item(ItemType.HEALTH_POTION, self.player)
            if result:
                self.combat_system.combat_log.append(result)
            else:
                self.combat_system.combat_log.append("No health potions available!")
            self._update_displays()

    def _try_move(self, dx: int, dy: int):
        if self.game_state.game_over:
            return

        self.player.update_temporary_buffs()

        new_x = self.player.x + dx
        new_y = self.player.y + dy

        altar = self.sacrifice_system.get_altar_at(new_x, new_y)
        if altar and not altar.used:
            self.player.x = new_x
            self.player.y = new_y
            self.combat_system.combat_log.append("You stand before an ancient altar. Press 'E' to interact.")
            self._update_displays()
            return

        target_monster = self.monster_manager.get_monster_at(new_x, new_y)

        if target_monster and target_monster.is_alive:
            combat_messages = self.combat_system.player_attack_monster(self.player, target_monster)

            if self.player.can_crit():
                extra_damage = self.player.get_effective_attack() // 2
                target_monster.take_damage(extra_damage)
                combat_messages.append(f"[bold yellow]CRITICAL HIT![/] +{extra_damage} damage!")

            turn_messages = self.combat_system.process_turn(
                self.player, self.monster_manager, self.game_map.tiles,
                self.game_map.visibility_tracker, self.game_state
            )

        elif self.player.move(dx, dy, self.game_map.tiles):
            item = self.item_manager.collect_item(self.player.x, self.player.y)
            if item:
                pickup_message = self.player.inventory.add_item(item)
                self.combat_system.combat_log.append(pickup_message)

            if self.game_state.check_victory_condition(
                self.player.x, self.player.y, self.game_map.tiles, self.sacrifice_system, self.combat_system
            ):
                self._advance_to_next_level()
                self._update_displays()
                return

            turn_messages = self.combat_system.process_turn(
                self.player, self.monster_manager, self.game_map.tiles,
                self.game_map.visibility_tracker, self.game_state
            )

        self.game_state.check_defeat_condition(self.player)
        self._update_displays()

    def _update_displays(self) -> None:
        self.game_map.update_fov(self.player.x, self.player.y)

        game_display = self.query_one(GameDisplay)
        status_display = self.query_one(StatusDisplay)
        message_display = self.query_one(MessageDisplay)

        game_display.update_display()
        status_display.update_status()
        message_display.update_messages()


def main():
    app = RoguelikeApp()
    app.run()


if __name__ == "__main__":
    main()
