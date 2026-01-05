"""
MHA ROGUELIKE - FULLY INTEGRATED WEB VERSION
Complete game with all features from terminal version
Run with: python app_full.py
"""

from flask import Flask, render_template, request, jsonify, session, send_from_directory, send_file
from collections import Counter
import secrets
import sys
import os
import random
import time
from pathlib import Path

# Import complete game
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mha_roguelike_complete import *

def get_zone_description(zone_type, zone_number):
    """Get a random zone description for the given zone type"""
    descriptions = {
        'forest': [
            "Dense foliage surrounds you as ancient trees form a natural canopy overhead. The air is thick with the scent of moss and earth, and wildlife sounds echo through the undergrowth.",
            "A primeval woodland stretches in all directions, where twisted roots and hanging vines create natural obstacles. Shafts of green-filtered light pierce through the dense canopy above."
        ],
        'flashfire': [
            "Extreme heat radiates from every surface as flames dance along the walls in controlled patterns. The air shimmers with thermal distortion, and the temperature is almost unbearable.",
            "This zone simulates a catastrophic fire scenario where intense heat and periodic flame bursts test your ability to withstand extreme temperatures. Every breath feels like inhaling fire."
        ],
        'urban': [
            "The simulation recreates a dense city environment with abandoned streets, damaged buildings, and urban debris. The atmosphere of a disaster zone permeates every corner.",
            "Concrete and steel dominate this metropolitan landscape where everyday city elements have been transformed into tactical obstacles and hiding spots."
        ],
        'lake': [
            "Water is the dominant feature here - from shallow pools to deeper channels. The air is heavy with moisture, and the sound of dripping water echoes constantly.",
            "This aquatic environment challenges your ability to navigate partially flooded spaces where water levels vary and platforms shift beneath your feet."
        ],
        'mountain': [
            "Rough stone and jagged rock formations define this high-altitude simulation. The uneven terrain and rocky obstacles demand careful footing and strategic positioning.",
            "A harsh mountain environment where elevation changes, loose gravel, and stone outcroppings create a treacherous battlefield requiring both strength and agility."
        ],
        'blizzard': [
            "Frigid temperatures and ice-covered surfaces dominate this frozen zone. Your breath forms clouds in the air, and frost creeps across every surface with supernatural speed.",
            "An extreme cold environment where sub-zero temperatures, ice formations, and simulated wind chill test your endurance against the harshest winter conditions."
        ],
        'underground': [
            "Claustrophobic tunnels and cave systems wind through compressed earth and stone. The air is stale, support structures creak ominously, and darkness presses in from all sides.",
            "This subterranean zone simulates the dangers of underground rescue operations - from mine collapses to cave systems where every shadow could hide danger."
        ]
    }
    
    zone_descs = descriptions.get(zone_type, descriptions['forest'])
    # Randomly pick one of the two descriptions
    return random.choice(zone_descs)

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Store game sessions
games = {}

@app.route('/')
def homepage():
    """Serve the homepage"""
    return send_from_directory('.', 'homepage.html')

@app.route('/tip.jpeg')
def tip_image():
    """Serve the tip QR code image"""
    return send_from_directory('.', 'tip.jpeg')

@app.route('/player_guide')
@app.route('/player_guide/')
@app.route('/player_guide/player_guide.html')
def player_guide():
    """Serve the player guide"""
    return send_from_directory('player_guide', 'player_guide.html')

@app.route('/game')
def index():
    """Serve the main game page"""
    return render_template('game.html')

class FullWebGame:
    """Complete game session with all terminal features"""
    
    def __init__(self, session_id):
        self.session_id = session_id
        
        # Core game state
        self.characters = create_class_1a()
        self.global_tree = GlobalSkillTree()
        self.current_zone = 1
        self.current_floor = 1
        self.zone_bosses = {}
        
        # Character state
        self.selected_character = None
        self.current_theme = None
        
        # Zone navigation
        self.zone_map = None
        self.current_room = 1
        self.visited_rooms = set()
        self.cleared_rooms = set()  # Rooms where combat has been completed
        self.rested_in_rooms = set()
        
        # Combat state
        self.in_combat = False
        self.current_enemy = None
        self.combat_state = {}
        
        # PHASE 1: Shared inventory across all characters
        self.shared_inventory = []
        
        # Game flow
        self.game_state = 'intro'
        self.pending_input = None  # What type of input we're waiting for
        self.messages = []
        self.last_action = None
        
        # Options/choices
        self.current_options = []
        
        # Generate randomized zone themes
        self.zone_themes = self.generate_zone_sequence()
    
    def generate_zone_sequence(self):
        """Generate randomized zone sequence with no consecutive duplicates"""
        themes = ['forest', 'flashfire', 'urban', 'lake', 'mountain', 'blizzard', 'underground']
        sequence = []
        last_theme = None
        
        for i in range(20):
            available = [t for t in themes if t != last_theme]
            chosen = random.choice(available)
            sequence.append(chosen)
            last_theme = chosen
        
        return sequence
    
    def get_room_description(self, zone_theme, room_number):
        """Get unique room description based on zone theme and room number (1-5)"""
        descriptions = {
            'forest': [
                "You enter a dense grove where ancient trees tower overhead, their gnarled roots creating natural obstacles across the mossy floor. Shafts of dappled sunlight filter through the canopy above.",
                "The room opens into a clearing dominated by a massive fallen oak, its hollow trunk large enough to serve as cover. Thick underbrush lines the perimeter, rustling with unseen movement.",
                "Twisted vines hang from the ceiling like natural curtains, creating a maze-like environment. The air is thick with the scent of earth and decay, and mushrooms cluster on every surface.",
                "You step into a rocky outcropping within the forest, where a small waterfall cascades into a crystal-clear pool. Moss-covered boulders provide elevated positions around the space.",
                "The forest opens into a sun-drenched glade where wildflowers blanket the ground. A ring of ancient standing stones marks the center, their purpose long forgotten."
            ],
            'flashfire': [
                "You step into a burning city street where storefronts blaze on both sides. Flames pour from shattered windows, and the asphalt itself seems to melt under the intense heat.",
                "The room simulates a burning office building interior - desks and office equipment engulfed in flames, ceiling tiles raining down, emergency sprinklers long since failed.",
                "You enter what appears to be a shopping district consumed by fire. Store mannequins melt in display windows, and neon signs spark and flicker before dying in the inferno.",
                "The area resembles a city parking structure where vehicles have become explosive hazards. Flames leap from car to car, and concrete pillars glow red from the heat.",
                "You step into a burning apartment complex with flames visible through every window. Fire escapes have warped from the heat, and smoke billows through hallways."
            ],
            'urban': [
                "The room resembles a city street corner with storefronts, a bus stop bench, and a non-functional traffic light. Debris and abandoned vehicles provide cover throughout the space.",
                "You enter what appears to be a multi-story parking garage section, with concrete pillars supporting low ceilings. Abandoned cars sit at odd angles, some with doors hanging open.",
                "The area is set up like a small plaza with a dry fountain at its center. Cafe tables and chairs are scattered about, and shuttered shop windows line the walls.",
                "This room recreates a subway platform complete with tracks, a stationary train car, and tiled walls covered in faded advertisements and graffiti.",
                "You step into an urban rooftop environment with AC units, water towers, and ventilation systems creating a maze of obstacles. Gaps between sections simulate building edges."
            ],
            'lake': [
                "The room features a large pool of water in its center, with floating platforms and partially submerged ruins visible beneath the surface. The air is cool and damp.",
                "You enter a flooded chamber where water reaches knee-height throughout most of the space. A network of raised walkways and platforms provides dry paths across the room.",
                "The area contains a series of connected pools at different depths, like natural tidal pools. Smooth stones and shells litter the shallow areas, while deeper sections are murky and dark.",
                "This room houses what appears to be an underwater viewing area, with one wall of reinforced glass showing a darkened aquarium beyond. Puddles cover the floor from previous leaks.",
                "You step into a room designed like a boat dock, with wooden planks extending over dark water. Mooring posts, coiled ropes, and fishing equipment are scattered about."
            ],
            'mountain': [
                "The room is carved from rough stone, with jagged outcroppings creating natural pillars throughout. Loose rocks and gravel cover the uneven floor, making footing treacherous.",
                "You enter a cavern-like space where stalactites hang from the ceiling and stalagmites rise from the floor. The walls glitter with embedded crystals that catch any available light.",
                "The area resembles a narrow mountain pass with towering rock walls on either side. Large boulders are strewn about as if from an ancient avalanche.",
                "This room features multiple levels connected by rough stone ledges and natural ramps. Small crevices and caves dot the walls, providing potential hiding spots.",
                "You step into what appears to be the inside of a hollow mountain peak, with a spiraling path leading upward along the curved walls. The center drops away into darkness."
            ],
            'blizzard': [
                "You enter a frozen chamber where ice coats every surface and your breath forms clouds in the frigid air. Icicles hang from the ceiling like frozen spears, and snow drifts pile against the walls.",
                "The room is a winter wasteland with howling wind effects and artificial snow swirling through the air. Frozen sculptures of ice create obstacles, and the floor is treacherously slick.",
                "You step into what appears to be the inside of a glacier - walls of blue ice surround you, and frozen formations jut out at odd angles. Frost creeps across any exposed surface.",
                "The area resembles a frozen tundra with snow-covered ground and ice pillars rising from the floor. A bitter wind cuts through the space, and everything is coated in a layer of frost.",
                "You enter a room dominated by a massive ice wall that reaches to the ceiling. Frozen waterfalls are suspended mid-cascade, and the temperature is well below freezing."
            ],
            'underground': [
                "You descend into a cramped tunnel system with rough-hewn walls pressing in from all sides. Support beams creak ominously overhead, and the air is thick with the smell of earth and stone.",
                "The room opens into a vast underground cavern with a ceiling lost in darkness above. Phosphorescent fungi provide eerie green light, casting strange shadows across ancient rock formations.",
                "You enter what appears to be an abandoned mine shaft, with rusted rail tracks running along the floor and old mining equipment left to decay. The walls show pick marks from long-ago excavation.",
                "The area is a natural cave system with multiple passages branching off in different directions. Water drips constantly from the ceiling, forming small pools on the uneven stone floor.",
                "You step into an underground chamber that seems to be part of an ancient ruin - crumbling pillars support a low ceiling, and strange symbols are carved into the weathered stone walls."
            ]
        }
        
        theme_descriptions = descriptions.get(zone_theme, descriptions['forest'])
        # Use room number (1-5) to index into the 5 unique descriptions
        desc_index = (room_number - 1) % 5
        return theme_descriptions[desc_index]
        
    def add_msg(self, text, msg_type='normal'):
        """Add message to buffer"""
        # Handle separator specially - use CSS border instead of text
        if msg_type == 'separator':
            self.messages.append({'text': '', 'type': 'separator_line'})
        elif text:
            for line in str(text).split('\n'):
                if line.strip():
                    self.messages.append({'text': line, 'type': msg_type})
    
    def clear_msgs(self):
        """Clear message buffer"""
        self.messages = []
    
    def get_state_dict(self):
        """Convert to JSON-serializable dict"""
        print(f"DEBUG get_state_dict: current_theme='{self.current_theme}', game_state='{self.game_state}'")
        
        state = {
            'zone': self.current_zone,
            'floor': self.current_floor,
            'theme': self.current_theme,
            'game_state': self.game_state,
            'pending_input': self.pending_input,
            'messages': self.messages,
            'options': self.current_options,
            'in_combat': self.in_combat,
        }
        
        # Character info
        if self.selected_character:
            char = self.selected_character
            state['character'] = {
                'name': char.name,
                'quirk': char.quirk,
                'level': char.level,
                'hp': char.hp,
                'max_hp': char.max_hp,
                'energy': char.energy,
                'max_energy': char.max_energy,
                'attack': char.attack,
                'defense': char.defense,
                'exp': char.exp,
                'exp_to_level': char.exp_to_level,
                'skill_points': char.skill_points,
                'inventory': char.inventory,
                'abilities': {name: {'damage': data[0], 'cost': data[1], 'desc': data[3]} 
                             for name, data in char.abilities.items()}
            }
        
        # Enemy info
        if self.current_enemy:
            state['enemy'] = {
                'name': self.current_enemy.name,
                'level': self.current_enemy.level,
                'hp': self.current_enemy.hp,
                'max_hp': self.current_enemy.max_hp,
                'is_boss': isinstance(self.current_enemy, BossEnemy)
            }
        
        # Available characters count
        available = [c for c in self.characters if not c.captured and c.unlocked]
        state['active_count'] = len(available)
        state['total_count'] = len([c for c in self.characters if c.unlocked])
        
        return state
    
    def start_game(self):
        """Initialize game"""
        self.clear_msgs()
        
        # Set generic theme for intro
        self.current_theme = 'intro'
        
        self.add_msg("="*59, 'separator')
        self.add_msg("Tower Descent Simulation", 'title')
        self.add_msg("(Like Tokyo DisneySea!?)", 'subtitle')
        self.add_msg("="*59, 'separator')
        self.add_msg("")
        self.add_msg('[Aizawa]: "Listen up, all of you. You\'re about to enter the Tower Descent Simulation, otherwise known as the T.D.S. - an underground training facility that descends 20 zones deep into the earth. The deeper you go, the more challenging it becomes. Each zone presents unique environmental hazards designed to test your quirk adaptability and strategic thinking. Pay close attention to zone types - your quirks will react differently to each environment. Take Asui for example. In aquatic zones like lakes, her frog quirk gives her a significant advantage in both combat ability and maneuverability. In forest environments, her tree frog capabilities allow her to blend in and navigate with ease. However, in extreme cold like blizzard zones, she becomes sluggish and weakened - frogs don\'t do well in freezing temperatures. Similarly, intense heat in fire zones will dry her out and hinder her performance. Every student has strengths and weaknesses like this. Learn them. The simulation uses a capture system - if you fall in combat, you\'re tagged as captured and removed from the exercise. However, there\'s a possibility you might find captured students hidden within the facility during your search. If you\'re thorough in your exploration, you may be able to rescue them and return them to active duty. Each zone ends with a boss encounter that must be defeated to descend further. Boss health persists across attempts - if one student damages it but falls, the next student faces a weakened boss. Use that strategically. Your objective is to descend through all 20 zones and reach the bottom. Work together, cover each other\'s weaknesses, and don\'t embarrass U.A. Now get moving."')
        self.add_msg("")
        self.add_msg("="*59, 'separator')
        self.add_msg("A MHA fangame by: <span class='author-name'>TsuMePlz</span>", 'subtitle')
        self.add_msg("="*59, 'separator')
        self.add_msg("")
        self.add_msg("OBJECTIVE: Descend through all 20 zones!", 'success')
        self.add_msg("")
        
        self.game_state = 'ready'
        self.pending_input = 'continue'
        self.current_options = [{'key': 'continue', 'text': 'Press Enter to begin Zone 1'}]
    
    
    def begin_zone(self):
        """Start new zone"""
        self.clear_msgs()
        
        # Safety check
        if self.current_zone < 1 or self.current_zone > 20:
            self.current_zone = 1
        
        # Get zone theme from randomized sequence
        theme_id = self.zone_themes[self.current_zone - 1]
        self.current_theme = theme_id
        
        # Generate zone map
        self.zone_map = generate_zone_map()
        self.current_room = 1
        self.current_floor = 1
        self.visited_rooms = set()
        self.cleared_rooms = set()  # Reset cleared rooms for new zone
        self.rested_in_rooms = set()
        self.searched_rooms = set()  # Reset searched rooms for new zone
        self.zone_encounters = 0  # PHASE 2: Track encounters to guarantee minimum per zone
        
        # PHASE 2.5: Reset Plus Ultra for deployed character
        if self.selected_character:
            self.selected_character.plus_ultra_used_this_zone = False
        
        # Display zone info
        self.add_msg("="*59, 'separator')
        self.add_msg(f"ZONE {self.current_zone}/20 - {theme_id.upper()}", 'highlight')
        self.add_msg(f"Environmental Type: {theme_id.title()}", 'normal')
        self.add_msg("="*59, 'separator')
        self.add_msg("")
        
        # Zone description
        desc = get_zone_description(theme_id, self.current_zone)
        self.add_msg(desc)
        self.add_msg("")
        self.add_msg("="*59, 'separator')
        self.add_msg("")
        
        # Show character selection
        self.show_character_selection()
    
    def show_character_selection(self):
        """Display character selection"""
        # Don't overwrite current_theme - keep the zone theme for images!
        # Game state handles the UI state
        
        self.add_msg("SELECT STUDENT FOR DEPLOYMENT", 'highlight')
        self.add_msg("="*59, 'separator')
        self.add_msg("")
        
        available = [c for c in self.characters if c.unlocked]
        
        if not any(not c.captured for c in available):
            self.add_msg("NO STUDENTS AVAILABLE", 'warning')
            self.add_msg("GAME OVER - ALL STUDENTS CAPTURED", 'warning')
            self.game_state = 'game_over'
            self.pending_input = None
            return
        
        self.add_msg("CURRENT GLOBAL SKILL BONUSES:", 'highlight')
        self.add_msg(f"  STR: +{self.global_tree.get_attack_bonus()} | DEF: +{self.global_tree.get_defense_bonus()} | VIT: +{self.global_tree.get_hp_bonus()}")
        self.add_msg(f"  STA: +{self.global_tree.get_energy_bonus()} | EVA: +{self.global_tree.get_evasion_bonus()}%")
        self.add_msg("")
        
        self.current_options = []
        for i, char in enumerate(available):
            if char.captured:
                # Show captured characters but make them unselectable
                self.add_msg(f"{i+1:2}. CAPTURED")
            else:
                specialty = get_character_specialty(char.name)
                spec_text = f" 💡{specialty}" if specialty else ""
                status = f"Lv.{char.level}"
                
                # Calculate ACTUAL HP with global bonuses
                global_hp_bonus = self.global_tree.get_hp_bonus()
                true_max_hp = char.max_hp + global_hp_bonus
                
                # Current HP should reflect bonuses proportionally
                if char.hp >= char.max_hp:
                    # At full base health - give full bonus
                    true_current_hp = true_max_hp
                else:
                    # Partial health - scale with bonus
                    hp_percent = char.hp / char.max_hp if char.max_hp > 0 else 0
                    true_current_hp = int(true_max_hp * hp_percent)
                
                # Color code current HP based on percentage
                hp_percent = (true_current_hp / true_max_hp * 100) if true_max_hp > 0 else 0
                if hp_percent > 50:
                    hp_class = 'hp_high'
                elif hp_percent > 25:
                    hp_class = 'hp_medium'
                else:
                    hp_class = 'hp_low'
                
                hp_status = f"HP:<span class='{hp_class}'>{true_current_hp}</span>/{true_max_hp}"
                
                # PHASE 2.5: Add passive ability icon
                passive_icon = ""
                if char.unique_passive:
                    passive_type = char.unique_passive['type']
                    icons = {
                        'rescue_boost': '🏃',
                        'civilian_boost': '👥',
                        'passage_boost': '🔍',
                        'secret_detection': '🔍',
                        'item_boost': '💎',
                        'recovery_item_boost': '🍬',
                        'ambush_master': '💥',
                        'damage_reduction': '🛡️',
                        'versatile': '❄️🔥',
                        'helping_hand': '🌟',
                        'ribbit_recovery': '🐸',
                        'acid_veil': '💧',
                        'sparkle_inspire': '✨',
                        'last_stand': '🥋',
                        'stun_chance': '⚡',
                    }
                    passive_icon = f" {icons.get(passive_type, '✨')}"
                
                # PHASE 2.5: Add Plus Ultra indicator
                plus_ultra_icon = " ⚡PU" if char.plus_ultra_available else ""
                
                self.add_msg(f"{i+1:2}. {char.name:20} | {status:6} | {hp_status:20}{passive_icon}{plus_ultra_icon}{spec_text}")
                self.current_options.append({
                    'key': str(i+1),
                    'text': f"{i+1}. {char.name}",
                    'index': i
                })
        
        self.add_msg("")
        self.game_state = 'char_select'
        self.pending_input = 'character_number'
    
    def select_character(self, choice):
        """Handle character selection"""
        try:
            all_unlocked = [c for c in self.characters if c.unlocked]
            index = int(choice) - 1
            
            if 0 <= index < len(all_unlocked):
                selected_char = all_unlocked[index]
                
                # Check if captured
                if selected_char.captured:
                    self.add_msg("âŒ That student has been captured and cannot be deployed!", 'warning')
                    self.add_msg("")
                    self.show_character_selection()
                    return False
                
                self.selected_character = selected_char
                char = self.selected_character
                
                # Apply global bonuses
                self.global_tree.set_character_bonus(char.name)
                apply_global_bonuses(char, self.global_tree)
                
                # Apply zone effects FIRST (natural quirk compatibility)
                # Pass the theme directly - apply_zone_effects handles mapping internally
                effect_msg = char.apply_zone_effects(self.current_theme)
                
                # Apply special zone bonuses SECOND (additional tactical advantages)
                special_bonus_msg = self.apply_special_zone_bonuses(char, self.current_theme)
                
                # Get character dialogue
                special_dialogue = self.get_zone_entry_dialogue(char.name, self.current_theme)
                
                self.clear_msgs()
                self.add_msg("")
                self.add_msg(f"{char.name} deploys!", 'success')
                self.add_msg(f'"{char.get_deployment_dialogue()}"')
                self.add_msg(f'[Aizawa]: "{char.get_aizawa_response()}"')
                self.add_msg("")
                
                # Show natural zone effect message with appropriate styling
                if effect_msg:
                    # Check if it's a penalty (contains "struggles") or bonus
                    if "struggles" in effect_msg or "weakens" in effect_msg:
                        self.add_msg(effect_msg, 'warning')
                    else:
                        self.add_msg(effect_msg, 'highlight')
                
                # Show special bonus message with appropriate styling
                if special_bonus_msg:
                    # Check if it's a penalty or bonus
                    if "struggles" in special_bonus_msg or "weakens" in special_bonus_msg:
                        self.add_msg(special_bonus_msg, 'warning')
                    else:
                        self.add_msg(special_bonus_msg, 'highlight')
                
                # Show character dialogue
                if special_dialogue:
                    self.add_msg(f'"{special_dialogue}"', 'highlight')
                    self.add_msg("")
                elif effect_msg or special_bonus_msg:
                    # Had bonuses but no dialogue
                    self.add_msg("")
                
                self.add_msg("="*59, 'separator')
                self.add_msg("Entering zone...", 'success')
                self.add_msg("")
                
                # Start exploration
                self.start_room_exploration()
                return True
            else:
                self.add_msg("Invalid selection! Please choose a valid number.", 'warning')
                self.add_msg("")
                self.show_character_selection()
                return False
        except (ValueError, IndexError):
            self.add_msg("Invalid input! Please enter a number.", 'warning')
            self.add_msg("")
            self.show_character_selection()
            return False
    
    def start_room_exploration(self):
        """Explore current room"""
        self.visited_rooms.add(self.current_room)
        
        # Check if boss room
        if self.current_room == self.zone_map['boss_room']:
            self.show_boss_warning()
            return
        
        # Show room description
        room_desc = self.get_room_description(self.current_theme, self.current_room)
        self.add_msg(room_desc, 'normal')
        self.add_msg("")
        
        # Check if room has already been cleared
        if self.current_room in self.cleared_rooms:
            self.add_msg("You've already cleared this room.")
            self.add_msg("")
            self.show_navigation_options()
            return
        
        # Determine what happens in this room
        # PHASE 2: Guarantee at least 2 encounters per zone
        if not hasattr(self, 'zone_encounters'):
            self.zone_encounters = 0
        
        boss_room = self.zone_map['boss_room']
        rooms_remaining = boss_room - self.current_room
        encounters_needed = 2 - self.zone_encounters
        
        # Force combat if we need encounters and running out of rooms
        if encounters_needed > 0 and rooms_remaining <= encounters_needed:
            spawn_combat = True
        else:
            # Normal 40% chance
            spawn_combat = random.random() < 0.4
        
        if spawn_combat:
            self.zone_encounters += 1
            enemy = create_enemy(self.current_zone, self.current_floor)
            self.current_enemy = enemy
            self.in_combat = True
            self.combat_state = {
                'player_defense_buff': 0,
                'player_defense_buff_turns': 0,
                'enemy_stunned': 0,
                'enemy_defense_debuff': 0,
                'enemy_attack_debuff': 0
            }
            
            self.add_msg(f"⚠️  {enemy.name} (Level {enemy.level}) appears!", 'warning')
            self.add_msg("")
            self.show_combat_options()
        
        # 60% chance for empty room (increased from 30%)
        else:
            self.add_msg("The room appears clear for now.")
            self.add_msg("")
            # Mark as cleared even if empty
            self.cleared_rooms.add(self.current_room)
            
            # PHASE 1: Passive healing for benched characters
            vit_bonus = self.global_tree.get_hp_bonus()
            heal_per_room = max(1, vit_bonus // 15)
            
            # PHASE 2.5: Ochaco's Helping Hand bonus
            ochaco_bonus = 0
            if self.selected_character.unique_passive and self.selected_character.unique_passive['type'] == 'helping_hand':
                ochaco_bonus = 2
            
            # PHASE 2.5: Asui's Ribbit Recovery energy restore
            asui_energy = 0
            if self.selected_character.unique_passive and self.selected_character.unique_passive['type'] == 'ribbit_recovery':
                asui_energy = 5
            
            for character in self.characters:
                if character != self.selected_character and not character.captured:
                    character.heal(heal_per_room + ochaco_bonus)
                    if asui_energy > 0:
                        character.restore_energy(asui_energy)
            
            self.show_navigation_options()
    
    def show_combat_options(self):
        """Display combat menu"""
        self.game_state = 'combat'
        self.pending_input = 'combat_action'
        
        self.add_msg("COMBAT OPTIONS:", 'highlight')
        self.add_msg("1. Attack - Basic attack")
        self.add_msg("2. Quirk - Use quirk ability")
        self.add_msg("3. Item - Use item from inventory")
        self.add_msg("4. Skills - View/upgrade skills")
        
        # PHASE 2.5: Plus Ultra option
        char = self.selected_character
        option_number = 5
        
        if char.plus_ultra_available and not char.plus_ultra_used_this_zone:
            self.add_msg(f"{option_number}. ⚡ PLUS ULTRA! ⚡ - Full recovery (once per zone)")
            option_number += 1
        
        # TEAM-UP ATTACKS: Check for available partners
        team_ups = char.get_available_team_ups(self.characters)
        if team_ups:
            self.add_msg(f"{option_number}. 🤝 TEAM-UP ATTACK - Massive damage with partner")
        
        self.current_options = [
            {'key': '1', 'text': 'Attack'},
            {'key': '2', 'text': 'Quirk'},
            {'key': '3', 'text': 'Item'},
            {'key': '4', 'text': 'Skills'}
        ]
        
        if char.plus_ultra_available and not char.plus_ultra_used_this_zone:
            self.current_options.append({'key': '5', 'text': 'Plus Ultra'})
        
        if team_ups:
            team_up_key = '6' if (char.plus_ultra_available and not char.plus_ultra_used_this_zone) else '5'
            self.current_options.append({'key': team_up_key, 'text': 'Team-Up'})
    
    
    def show_poi_search_results(self, num_poi):
        """Show POI search results with multiple investigation points"""
        self.game_state = 'poi_search'
        self.pending_input = 'poi_investigate'
        
        self.add_msg("You carefully search the room and notice several points of interest:", 'highlight')
        self.add_msg("")
        
        # Generate POI descriptions based on zone theme
        print(f"DEBUG show_poi_search_results: current_theme = '{self.current_theme}'")
        print(f"DEBUG show_poi_search_results: zone_themes = {self.zone_themes}")
        print(f"DEBUG show_poi_search_results: current_zone = {self.current_zone}")
        
        poi_descriptions = self.generate_poi_descriptions(self.current_theme, num_poi)
        
        # Store POI for investigation
        self.current_poi_list = []
        
        for i, desc in enumerate(poi_descriptions, 1):
            self.add_msg(f"{i}. {desc}")
            # Determine what's actually in this POI (won't reveal until investigated)
            poi_content = self.determine_poi_content()
            self.current_poi_list.append(poi_content)
        
        self.add_msg("")
        self.add_msg(f"0. Don't investigate (continue navigation)")
        self.add_msg("")
        self.add_msg("Which point of interest do you want to investigate?")
        
        self.current_options = [{'key': str(i), 'text': f'Investigate {i}'} for i in range(num_poi + 1)]
    
    def generate_poi_descriptions(self, zone_theme, count):
        """Generate POI descriptions based on zone theme"""
        print(f"DEBUG: generate_poi_descriptions called with zone_theme='{zone_theme}', count={count}")
        
        poi_templates = {
            'forest': [
                "A hollow in an old tree trunk, partially concealed by hanging vines",
                "A cluster of unusually large mushrooms growing in a perfect circle",
                "A gap beneath a fallen log where the ground seems disturbed",
                "Strange markings carved into a tree at chest height",
                "A dense thicket of thorns with something glinting inside",
                "An abandoned bird's nest large enough to hold objects",
                "A burrow entrance at the base of a massive oak tree",
                "Thick undergrowth where broken branches suggest recent passage",
                "A natural hollow between tree roots filled with dead leaves",
                "A cluster of unusual flowers that seem out of place"
            ],
            'flashfire': [
                "A burning vehicle with its trunk still accessible",
                "A collapsed storefront with something visible through the flames",
                "A fire escape platform hanging at a dangerous angle",
                "An office desk drawer that survived the blaze",
                "A vending machine with its glass melted and warped",
                "A mailbox partially protected by a concrete barrier",
                "A phone booth with flames dancing around its frame",
                "A newspaper stand engulfed but structurally intact",
                "A park bench beneath a burning tree canopy",
                "A bus stop shelter with one wall still standing",
                "A storefront security gate warped by heat",
                "An ATM alcove providing slight protection from flames"
            ],
            'urban': [
                "A dumpster with its lid slightly open",
                "A boarded-up doorway with one plank hanging loose",
                "A newspaper stand with papers still inside",
                "A manhole cover shifted to one side",
                "A parked delivery truck with its back door unlocked",
                "A phone booth with the door wedged open",
                "A street vendor cart abandoned at an odd angle",
                "A mailbox with a damaged lock",
                "A maintenance access panel in the wall",
                "A storm drain with something visible inside",
                "A vending machine with a broken glass panel",
                "An electrical junction box hanging open"
            ],
            'lake': [
                "A partially submerged crate bobbing against the shore",
                "A small cave entrance just above the waterline",
                "A cluster of reeds thick enough to hide something",
                "An overturned boat resting on the bank",
                "A rope hanging down from above, disappearing into the water",
                "A fishing net tangled around submerged debris",
                "A waterlogged wooden chest caught between rocks",
                "A drainage pipe opening at the water's edge",
                "A collection of flotsam gathered in an eddy",
                "Lily pads clustered unusually thick in one area",
                "A submerged platform visible beneath the surface",
                "A hollow in the rocky shoreline below the waterline"
            ],
            'mountain': [
                "A narrow crevice in the rock face",
                "A pile of loose stones that looks recently disturbed",
                "A small cave opening partially blocked by rubble",
                "A ledge with what might be an old campsite",
                "A natural shelf in the rock where items could be hidden",
                "A crack in the floor with something visible in the depths",
                "A ring of stones arranged deliberately around a central point",
                "An overhang creating a sheltered nook in the stone",
                "A gap between two large boulders",
                "Ancient mining equipment left to rust",
                "A collapsed section of ceiling with loose rocks",
                "Crystalline formations that seem hollow inside"
            ],
            'blizzard': [
                "A snow drift piled suspiciously high against the wall",
                "An ice formation with something frozen inside",
                "A gap in the ice wall revealing a hidden alcove",
                "Frost-covered debris clustered in the corner",
                "An icicle formation hanging over a shadowed recess",
                "A section of snow that appears recently disturbed",
                "A frozen container partially visible through the ice",
                "A natural ice shelf jutting from the wall",
                "Compacted snow formed into an unnatural shape",
                "A wind-carved hollow in a snowbank",
                "Ice-encrusted equipment barely visible through frost",
                "A crevasse in the frozen floor with darkness below"
            ],
            'underground': [
                "A crack in the cave wall where loose rocks have fallen away",
                "An old mining cart tipped on its side",
                "A support beam that's partially collapsed, creating a gap",
                "A cluster of glowing fungi growing around something buried",
                "A pile of excavated earth and stone",
                "A rusted toolbox half-buried in rubble",
                "A side passage blocked by a recent cave-in",
                "An ancient wooden crate covered in mineral deposits",
                "A natural alcove hidden behind a rock formation",
                "A section of wall where the stone appears different",
                "A collapsed mine shaft with timbers still intact",
                "A pool of stagnant water with something submerged",
                "Railroad tracks that disappear into a dark tunnel",
                "A ventilation shaft ascending into darkness"
            ]
        }
        
        templates = poi_templates.get(zone_theme, [])
        if not templates:
            # Log error and use generic POI
            print(f"ERROR: No POI templates for zone_theme: {zone_theme}")
            templates = ["A suspicious area worth investigating", "Something hidden here", "An area of interest"]
        # Randomly select unique descriptions
        selected = random.sample(templates, min(count, len(templates)))
        return selected
    
    def determine_poi_content(self):
        """Determine what a POI contains"""
        roll = random.random()
        char = self.selected_character
        passive = char.unique_passive if char else None
        
        # PHASE 2.5: Check for Momo's Lucky Bag first
        if (char.name == "Momo Yaoyorozu" and 
            hasattr(char, 'can_find_lucky_bags') and 
            char.can_find_lucky_bags):
            if random.random() < 0.05:  # 5% chance when she has the skill
                return {'type': 'lucky_bag'}
        
        # PHASE 2.5: Apply passive multipliers
        rescue_chance = 0.05
        civilian_chance = 0.05
        passage_chance = 0.10
        
        if passive:
            if passive['type'] == 'rescue_boost':
                rescue_chance *= passive['value']
            elif passive['type'] == 'civilian_boost':
                civilian_chance *= passive['value']
            elif passive['type'] == 'passage_boost':
                passage_chance *= passive['value']
        
        # PHASE 2: Adjusted base rates
        if roll < 0.35:  # 35% - Nothing
            return {'type': 'nothing'}
        elif roll < 0.60:  # 25% - Items
            item_count = 1 if random.random() < 0.7 else 2
            items = []
            
            # PHASE 2.5: Sato's recovery item boost
            recovery_chance = 0.5  # Base 50% for recovery items
            if passive and passive['type'] == 'recovery_item_boost':
                recovery_chance *= passive['value']
            
            for _ in range(item_count):
                if random.random() < recovery_chance:
                    items.append(random.choice(["Health Potion", "Energy Drink"]))
                else:
                    items.append(random.choice(["Health Potion", "Energy Drink"]))
            
            return {'type': 'items', 'items': items, 'exp': random.randint(10, 20)}
        elif roll < 0.85:  # 25% - Enemy encounter
            return {'type': 'enemy'}
        elif roll < (0.85 + rescue_chance):  # Rescue (boosted by passive)
            # Check if any students are captured
            captured_students = [c for c in self.characters if c.captured and c.unlocked]
            
            if captured_students:
                return {'type': 'rescue'}
            else:
                # No one captured - could trigger Shinso event
                if self.current_zone >= 3 and not any(c.name == "Hitoshi Shinso" and c.unlocked for c in self.characters):
                    return {'type': 'shinso_unlock'}
                else:
                    civilian_exp = 100 * self.current_zone
                    return {'type': 'civilian', 'exp': civilian_exp}
        elif roll < (0.85 + rescue_chance + civilian_chance):  # Civilian (boosted by passive)
            civilian_exp = 100 * self.current_zone
            return {'type': 'civilian', 'exp': civilian_exp}
        else:  # Passage
            # Boosted by Hagakure/Mineta passive
            passage_roll = random.random()
            if passage_roll < passage_chance and self.current_zone < 20:
                return {'type': 'passage'}
            elif self.current_zone < 20:
                return {'type': 'passage'}
            else:
                # Replace with treasure if on last zone
                return {'type': 'items', 'items': ["Health Potion", "Energy Drink"], 'exp': 30}
    
    def is_civilian_location_logical(self):
        """Check if current POI makes sense for a civilian to be hiding"""
        # Civilians can appear in any zone, but we check POI context
        # This is handled in POI content determination now
        return True
    
    def show_remaining_poi(self):
        """Show remaining POI after investigating one"""
        self.add_msg("Remaining points of interest:")
        self.add_msg("")
        
        # Re-number the remaining POI
        for i in range(len(self.current_poi_list)):
            self.add_msg(f"{i+1}. (Still to investigate)")
        
        self.add_msg("")
        self.add_msg("0. Stop investigating (continue navigation)")
        self.add_msg("")
        
        self.pending_input = 'poi_investigate'
        self.current_options = [{'key': str(i), 'text': f'Investigate {i}'} for i in range(len(self.current_poi_list) + 1)]
    
    def show_poi_encounter(self, poi_type, custom_exp=None):
        """Display POI (Point of Interest) encounter"""
        self.game_state = 'poi_encounter'
        self.pending_input = 'poi_choice'
        
        if poi_type == 'treasure':
            treasure_types = [
                ('Supply Cache', 'You discover a hidden supply cache left by previous heroes.'),
                ('Emergency Stash', 'An emergency stash is hidden in the corner.'),
                ('Training Supplies', 'U.A. training supplies are stored here.'),
            ]
            treasure_name, treasure_desc = random.choice(treasure_types)
            
            self.add_msg("🎁 TREASURE DISCOVERED!", 'highlight')
            self.add_msg("")
            self.add_msg(treasure_desc)
            self.add_msg("")
            self.add_msg("Contents:")
            
            # Generate rewards
            rewards = []
            
            # Always get some EXP
            exp_reward = random.randint(15, 30)
            rewards.append(('exp', exp_reward))
            self.add_msg(f"  • {exp_reward} EXP")
            
            # 60% chance for an item
            if random.random() < 0.6:
                item = random.choice(["Health Potion", "Energy Drink"])
                rewards.append(('item', item))
                self.add_msg(f"  • {item}")
            
            # 30% chance for second item
            if random.random() < 0.3:
                item = random.choice(["Health Potion", "Energy Drink"])
                rewards.append(('item', item))
                self.add_msg(f"  • {item}")
            
            self.add_msg("")
            self.add_msg("1. Take the supplies")
            self.add_msg("2. Leave them (move on)")
            
            self.current_options = [
                {'key': '1', 'text': 'Take supplies', 'rewards': rewards},
                {'key': '2', 'text': 'Leave'}
            ]
        
        elif poi_type == 'civilian':
            civilian_types = [
                ('H.U.C. Civilian Actor (Trapped)', 'You discover an H.U.C. civilian actor trapped beneath rubble!'),
                ('H.U.C. Civilian Actor (Injured)', 'An H.U.C. civilian actor lies injured behind a collapsed wall!'),
                ('H.U.C. Civilian Actor (Lost)', 'A young H.U.C. civilian actor playing a lost child hides in a corner, calling for help!'),
                ('H.U.C. Civilian Actor (Pinned)', 'An H.U.C. civilian actor is pinned under debris near a damaged support beam!'),
                ('H.U.C. Civilian Actor (Concealed)', 'You find an H.U.C. civilian actor concealed behind overturned furniture!'),
            ]
            civilian_name, civilian_desc = random.choice(civilian_types)
            
            self.add_msg("👥 H.U.C. CIVILIAN ACTOR FOUND!", 'highlight')
            self.add_msg("")
            self.add_msg(civilian_desc)
            self.add_msg("")
            
            # Generate rewards for rescue - use custom_exp if provided (scaled by zone)
            rewards = []
            exp_reward = custom_exp if custom_exp else random.randint(20, 40)
            rewards.append(('exp', exp_reward))
            
            # Hero work sometimes gives items
            if random.random() < 0.4:
                item = random.choice(["Health Potion", "Energy Drink"])
                rewards.append(('item', item))
            
            self.add_msg("🌟 HIGH-VALUE RESCUE OPPORTUNITY! 🌟", 'highlight')
            self.add_msg("Rescuing them will earn you major recognition as a hero.")
            self.add_msg(f"Reward: {exp_reward} EXP" + (f" + {rewards[1][1]}" if len(rewards) > 1 else ""))
            self.add_msg("")
            self.add_msg("1. Rescue them (no cost)")
            self.add_msg("2. Ignore (keep moving)")
            
            self.current_options = [
                {'key': '1', 'text': 'Rescue', 'rewards': rewards},
                {'key': '2', 'text': 'Ignore'}
            ]
    
    def show_navigation_options(self):
        """Display navigation menu"""
        self.game_state = 'navigation'
        self.pending_input = 'direction'
        
        self.add_msg("NAVIGATION OPTIONS:", 'highlight')
        
        room = self.zone_map['rooms'][self.current_room]
        self.current_options = []
        
        for direction in ['north', 'south', 'east', 'west']:
            next_room = room.get(direction)
            if next_room:
                visited = " [VISITED]" if next_room in self.visited_rooms else " [UNEXPLORED]"
                boss = " ⚠️ [BOSS]" if next_room == self.zone_map['boss_room'] else ""
                
                self.add_msg(f"- Go {direction.upper()} to Room {next_room}{visited}{boss}")
                self.current_options.append({
                    'key': direction[0],  # n, s, e, w
                    'text': f"Go {direction}",
                    'direction': direction,
                    'room': next_room
                })
        
        # POI search option (if not already searched)
        if not hasattr(self, 'searched_rooms'):
            self.searched_rooms = set()
        
        if self.current_room not in self.searched_rooms:
            self.add_msg("- SEARCH - Look for Points of Interest")
            self.current_options.append({'key': 'search', 'text': 'Search for POI'})
        
        # Rest option
        if self.current_room not in self.rested_in_rooms:
            self.add_msg("- REST - Restore 15 Energy (once per room)")
            self.current_options.append({'key': 'rest', 'text': 'Rest'})
        
        # Skills option
        self.add_msg("- SKILLS - View/upgrade skills")
        self.current_options.append({'key': 'skills', 'text': 'Skills'})
        
        # PHASE 2.5: Plus Ultra option
        char = self.selected_character
        if char.plus_ultra_available and not char.plus_ultra_used_this_zone:
            self.add_msg("- ⚡ PLUS ULTRA ⚡ - Full HP & Energy recovery (once per zone)")
            self.current_options.append({'key': 'plus_ultra', 'text': 'Plus Ultra'})
    
    def show_skill_tree_main(self):
        """Show skill tree main menu"""
        # Store previous state to return to
        if not hasattr(self, 'pre_skill_state'):
            self.pre_skill_state = self.game_state
        
        self.game_state = 'skill_tree_main'
        self.pending_input = 'skill_tree_choice'
        
        char = self.selected_character
        
        self.add_msg("="*59, 'separator')
        self.add_msg(f"SKILL TREE - {char.name}", 'highlight')
        self.add_msg("="*59, 'separator')
        self.add_msg(f"Available Skill Points: {char.skill_points}", 'success')
        self.add_msg("")
        self.add_msg("1. Global Class Skills (Permanent - benefits ALL students)")
        self.add_msg("2. Personal Quirk Skills (Lost if captured)")
        self.add_msg("3. View Current Bonuses")
        self.add_msg("4. Back")
        self.add_msg("")
        
        self.current_options = [
            {'key': '1', 'text': 'Global Skills'},
            {'key': '2', 'text': 'Personal Skills'},
            {'key': '3', 'text': 'View Bonuses'},
            {'key': '4', 'text': 'Back'}
        ]
    
    def show_global_skills(self):
        """Show global skill upgrade menu"""
        self.game_state = 'global_skills'
        self.pending_input = 'global_skill_choice'
        
        char = self.selected_character
        skills = self.global_tree.skills
        
        self.add_msg("="*59, 'separator')
        self.add_msg("GLOBAL CLASS SKILLS (Benefit ALL students)", 'highlight')
        self.add_msg(f"Currently deployed: {char.name}", 'normal')
        self.add_msg("="*59, 'separator')
        self.add_msg(f"Skill Points Available: {char.skill_points}", 'success')
        self.add_msg("")
        
        self.add_msg(f"1. Strength [{skills['strength']['level']}/{skills['strength']['max']}] - {self.global_tree.get_skill_display('strength')} Attack per level")
        self.add_msg(f"2. Defense [{skills['defense']['level']}/{skills['defense']['max']}] - {self.global_tree.get_skill_display('defense')} Defense per level")
        self.add_msg(f"3. Vitality [{skills['hp']['level']}/{skills['hp']['max']}] - {self.global_tree.get_skill_display('hp')} HP per level")
        self.add_msg(f"4. Stamina [{skills['energy']['level']}/{skills['energy']['max']}] - {self.global_tree.get_skill_display('energy')} Energy per level")
        self.add_msg(f"5. Evasion [{skills['evasion']['level']}/{skills['evasion']['max']}] - {self.global_tree.get_skill_display('evasion')}% Evasion per level")
        self.add_msg(f"0. Back")
        self.add_msg("")
        
        if self.global_tree.current_character_bonus:
            self.add_msg(f"💡 {char.name}'s specialization provides bonus gains:", 'highlight')
            for skill, mult in self.global_tree.current_character_bonus.items():
                if mult > 1.0:
                    skill_display = skill.replace('_', ' ').title()
                    bonus_pct = int((mult - 1.0) * 100)
                    self.add_msg(f"   ★ {skill_display} (+{bonus_pct}% more per level!)")
        
        self.current_options = [
            {'key': '1', 'text': 'Strength'},
            {'key': '2', 'text': 'Defense'},
            {'key': '3', 'text': 'Vitality'},
            {'key': '4', 'text': 'Stamina'},
            {'key': '5', 'text': 'Evasion'},
            {'key': '0', 'text': 'Back'}
        ]
    
    def show_personal_skills(self):
        """Show personal quirk skill upgrade menu"""
        char = self.selected_character
        skill_tree = get_character_skill_tree(char.name)
        
        if not skill_tree:
            self.add_msg("⚠️  No personal skill tree available for this character.", 'warning')
            self.add_msg("")
            self.show_skill_tree_main()
            return
        
        self.game_state = 'personal_skills'
        self.pending_input = 'personal_skill_choice'
        
        self.add_msg("="*59, 'separator')
        self.add_msg(f"{char.name.upper()}'S PERSONAL QUIRK SKILLS", 'highlight')
        self.add_msg("⚠️  WARNING: These bonuses are LOST if captured!", 'warning')
        self.add_msg("="*59, 'separator')
        self.add_msg(f"Skill Points Available: {char.skill_points}", 'success')
        self.add_msg("")
        
        skills_list = list(skill_tree.items())
        for i, (skill_id, skill_data) in enumerate(skills_list, 1):
            current_level = char.personal_skills.get(skill_id, 0)
            skill_type = "⚔️ " if skill_data['type'] == 'combat' else "🔧 "
            self.add_msg(f"{i}. {skill_type}{skill_id.replace('_', ' ').title()} [{current_level}/{skill_data['max']}]")
            self.add_msg(f"   {skill_data['desc']}")
        
        self.add_msg("0. Back to Skill Tree")
        self.add_msg("")
        
        self.current_options = [{'key': str(i+1), 'text': skill_id} for i, (skill_id, _) in enumerate(skills_list)]
        self.current_options.append({'key': '0', 'text': 'Back'})
    
    def show_current_bonuses(self):
        """Display all current bonuses"""
        self.game_state = 'view_bonuses'
        self.pending_input = 'continue'
        
        char = self.selected_character
        
        self.add_msg("="*59, 'separator')
        self.add_msg(f"{char.name}'S CURRENT BONUSES", 'highlight')
        self.add_msg("="*59, 'separator')
        self.add_msg("")
        self.add_msg("📊 GLOBAL CLASS BONUSES (Permanent):", 'success')
        self.add_msg(f"   Attack: +{self.global_tree.get_attack_bonus()}")
        self.add_msg(f"   Defense: +{self.global_tree.get_defense_bonus()}")
        self.add_msg(f"   HP: +{self.global_tree.get_hp_bonus()}")
        self.add_msg(f"   Energy: +{self.global_tree.get_energy_bonus()}")
        self.add_msg(f"   Evasion: +{self.global_tree.get_evasion_bonus()}%")
        self.add_msg("")
        self.add_msg("⚔️  PERSONAL QUIRK BONUSES (Lost if captured):", 'warning')
        
        if char.personal_skills:
            skill_tree = get_character_skill_tree(char.name)
            for skill_id, level in char.personal_skills.items():
                if skill_id in skill_tree:
                    self.add_msg(f"   {skill_id.replace('_', ' ').title()}: Level {level}")
            
            self.add_msg("")
            self.add_msg("   Total Personal Bonuses:")
            if char.evasion > 0:
                self.add_msg(f"   Evasion: +{char.evasion}%")
            if char.ambush_chance > 0:
                self.add_msg(f"   Ambush Chance: +{char.ambush_chance}%")
            if char.item_find_bonus > 0:
                self.add_msg(f"   Item Find: +{char.item_find_bonus}%")
        else:
            self.add_msg("   No personal skills purchased yet")
        
        self.add_msg("")
        self.add_msg("Press Enter to continue...")
        
        self.current_options = [{'key': 'continue', 'text': 'Continue'}]
    
    def apply_special_zone_bonuses(self, char, zone_theme):
        """Apply special bonuses for characters with environmental advantages"""
        # Reset any previous special bonuses
        if hasattr(char, 'special_zone_bonus'):
            char.attack -= char.special_zone_bonus.get('attack', 0)
            char.defense -= char.special_zone_bonus.get('defense', 0)
            char.evasion -= char.special_zone_bonus.get('evasion', 0)
        
        char.special_zone_bonus = {}
        
        # Asui - Climbing bonus in Forest
        if char.name == 'Tsuyu Asui' and zone_theme == 'forest':
            char.special_zone_bonus = {'evasion': 10, 'attack': 3}
            char.evasion += 10
            char.attack += 3
        
        # Sero - Swinging/climbing bonus in Urban and Forest
        elif char.name == 'Hanta Sero' and zone_theme in ['urban', 'forest']:
            char.special_zone_bonus = {'evasion': 8, 'attack': 2}
            char.evasion += 8
            char.attack += 2
    
    def get_zone_entry_dialogue(self, char_name, zone_theme):
        """Get character-specific dialogue when entering a zone"""
        dialogue_map = {
            'Katsuki Bakugo': {
                'flashfire': "This heat's really opening up my pores! Let's blow this place sky high!",
                'blizzard': "Damn it! Can't sweat in this cold! This is gonna be annoying..."
            },
            'Tsuyu Asui': {
                'forest': "Tree Frog mode, activated! I can climb anywhere here, ribbit!",
                'lake': "Finally, some water! I feel right at home here, ribbit!",
                'blizzard': "Really? The c-cold...? Feeling sleepy... *sad ribbit*",
                'flashfire': "Too hot... ribbit... need to stay hydrated..."
            },
            'Hanta Sero': {
                'urban': "Perfect! All these buildings - I can swing between anything with my tape!",
                'forest': "Trees everywhere... perfect anchor points for my tape! Maximum mobility!"
            },
            'Shoto Todoroki': {
                'flashfire': "The heat doesn't bother me. I can regulate my temperature.",
                'blizzard': "This cold... I'm completely in my element here."
            },
            'Fumikage Tokoyami': {
                'underground': "The darkness... Dark Shadow grows stronger here!",
                'flashfire': "The light... it weakens Dark Shadow. We must be cautious."
            },
            'Denki Kaminari': {
                'lake': "Water everywhere? Great, just great... gotta be careful not to shock myself."
            }
        }
        
        char_dialogues = dialogue_map.get(char_name, {})
        return char_dialogues.get(zone_theme, None)
    
    
    def apply_special_zone_bonuses(self, character, zone_type):
        """Apply special bonuses for characters in specific zones"""
        # Define all character zone bonuses (ONLY for characters without natural zone_bonuses)
        all_bonuses = {
            # Ashido - Hot bonus
            ('Mina Ashido', 'flashfire'): {'attack': 3, 'defense': 2, 'type': 'bonus'},
            
            # Iida - Cold bonus
            ('Tenya Iida', 'blizzard'): {'attack': 3, 'defense': 2, 'type': 'bonus'},
            
            # Shoji - Urban bonus
            ('Shoji Mezo', 'urban'): {'attack': 2, 'defense': 3, 'type': 'bonus'},
            
            # Jiro - Urban bonus
            ('Kyoka Jiro', 'urban'): {'attack': 3, 'defense': 2, 'type': 'bonus'},
            
            # Sero - Urban and Forest bonuses
            ('Hanta Sero', 'urban'): {'attack': 2, 'defense': 1, 'type': 'bonus'},
            ('Hanta Sero', 'forest'): {'attack': 1, 'defense': 1, 'type': 'bonus'},
            
            # Todoroki - Underground bonus (in addition to his natural hot/cold)
            ('Shoto Todoroki', 'underground'): {'attack': 2, 'defense': 1, 'type': 'bonus'},
            
            # Mineta - Urban bonus
            ('Minoru Mineta', 'urban'): {'attack': 2, 'defense': 1, 'type': 'bonus'},
            
            # Asui - Forest and Urban bonuses (in addition to her natural lake/cold)
            ('Tsuyu Asui', 'forest'): {'attack': 2, 'defense': 2, 'type': 'bonus'},
            ('Tsuyu Asui', 'urban'): {'attack': 1, 'defense': 1, 'type': 'bonus'},
            
            # Shinso - Modest bonus in ALL zones
            ('Hitoshi Shinso', 'forest'): {'attack': 1, 'defense': 1, 'type': 'bonus'},
            ('Hitoshi Shinso', 'flashfire'): {'attack': 1, 'defense': 1, 'type': 'bonus'},
            ('Hitoshi Shinso', 'urban'): {'attack': 1, 'defense': 1, 'type': 'bonus'},
            ('Hitoshi Shinso', 'lake'): {'attack': 1, 'defense': 1, 'type': 'bonus'},
            ('Hitoshi Shinso', 'mountain'): {'attack': 1, 'defense': 1, 'type': 'bonus'},
            ('Hitoshi Shinso', 'blizzard'): {'attack': 1, 'defense': 1, 'type': 'bonus'},
            ('Hitoshi Shinso', 'underground'): {'attack': 1, 'defense': 1, 'type': 'bonus'},
        }
        
        key = (character.name, zone_type)
        if key in all_bonuses:
            bonus_data = all_bonuses[key]
            if bonus_data['type'] == 'bonus':
                character.attack += bonus_data['attack']
                character.defense += bonus_data['defense']
                return f"{character.name} excels in this environment! ATK +{bonus_data['attack']}, DEF +{bonus_data['defense']}"
            else:  # penalty
                character.attack = max(1, character.attack - bonus_data['attack'])
                character.defense = max(0, character.defense - bonus_data['defense'])
                return f"{character.name} struggles in this environment... ATK -{bonus_data['attack']}, DEF -{bonus_data['defense']}"
        return None
    
    def get_zone_entry_dialogue(self, char_name, zone_type):
        """Get special character dialogue for zone entry - indicates bonuses/penalties to player"""
        dialogues = {
            # Bakugo - Hot bonus / Cold, Water penalties
            ('Katsuki Bakugo', 'flashfire'): "This heat's really opening up my pores!",
            ('Katsuki Bakugo', 'blizzard'): "Damn it! Can't sweat in this cold!",
            ('Katsuki Bakugo', 'lake'): "Tch... Water's gonna dampen my explosions.",
            
            # Todoroki - Hot, Cold, Dark bonuses
            ('Shoto Todoroki', 'flashfire'): "My left side feels right at home here.",
            ('Shoto Todoroki', 'blizzard'): "Perfect. My right side thrives in this cold.",
            ('Shoto Todoroki', 'underground'): "I'll light the way with my flames.",
            
            # Asui - Lake, Forest bonuses / Hot, Cold penalties
            ('Tsuyu Asui', 'forest'): "Tree Frog mode, activated! Ribbit, ribbit! Can you see me?",
            ('Tsuyu Asui', 'blizzard'): "Really? The c-cold...? Feeling sleepy... *sad frog noises*",
            ('Tsuyu Asui', 'lake'): "Ribbit! This is my element!",
            ('Tsuyu Asui', 'flashfire'): "Too hot, ribbit... My skin is drying out...",
            ('Tsuyu Asui', 'urban'): "Ribbit. Plenty of surfaces to blend with.",
            
            # Sero - Urban, Forest bonuses
            ('Hanta Sero', 'urban'): "All these buildings? My tape was made for this!",
            ('Hanta Sero', 'forest'): "Tree to tree swinging, baby! This is gonna be fun!",
            
            # Tokoyami - Dark bonus / Bright penalty
            ('Fumikage Tokoyami', 'underground'): "This gloom will do nicely...",
            ('Fumikage Tokoyami', 'flashfire'): "The light... it weakens us... Dark Shadow can barely emerge.",
            
            # Ashido - Hot bonus
            ('Mina Ashido', 'flashfire'): "Acidman form protects me from the heat! Bring it on!",
            
            # Iida - Cold bonus
            ('Tenya Iida', 'blizzard'): "The cold air will cool my engines! I can run longer!",
            
            # Shoji - Urban bonus
            ('Shoji Mezo', 'urban'): "Tall buildings... perfect vantage points for reconnaissance.",
            
            # Jiro - Urban bonus
            ('Kyoka Jiro', 'urban'): "All these hard surfaces? Perfect acoustics for my quirk!",
            
            # Hagakure - Bright bonus / Dark penalty
            ('Toru Hagakure', 'flashfire'): "All this light and they still can't see me! Perfect!",
            ('Toru Hagakure', 'underground'): "Being invisible doesn't help much when it's pitch black...",
            
            # Mineta - Urban bonus
            ('Minoru Mineta', 'urban'): "City terrain! I can stick my balls to everything!",
        }
        
        return dialogues.get((char_name, zone_type), None)
    
    def show_boss_warning(self):
        """Show boss room warning"""
        self.game_state = 'boss_warning'
        self.pending_input = 'boss_decision'
        
        self.add_msg("="*59, 'separator')
        self.add_msg("⚠️  WARNING: BOSS ROOM DETECTED! ⚠️", 'warning')
        self.add_msg("="*59, 'separator')
        self.add_msg("")
        self.add_msg("You sense powerful energy ahead...")
        self.add_msg("The zone boss awaits in this room.")
        self.add_msg("")
        
        # Check if boss exists and show HP
        if self.current_zone in self.zone_bosses:
            boss = self.zone_bosses[self.current_zone]
            if not boss.defeated:
                hp_pct = (boss.hp / boss.max_hp) * 100
                self.add_msg(f"Boss Status: {boss.name} - HP: {boss.hp}/{boss.max_hp} ({hp_pct:.0f}%)")
                self.add_msg("")
        
        self.add_msg("1. Enter Boss Room")
        self.add_msg("2. Retreat to previous area")
        self.add_msg("")
        
        self.current_options = [
            {'key': '1', 'text': 'Enter Boss Room'},
            {'key': '2', 'text': 'Retreat'}
        ]
    
    # combat will continue in next part
    
@app.route('/api/start', methods=['POST'])
def start_game():
    """Start new game"""
    session_id = secrets.token_hex(8)
    game = FullWebGame(session_id)
    games[session_id] = game
    
    game.start_game()
    
    return jsonify({
        'session_id': session_id,
        'state': game.get_state_dict()
    })


def show_debug_menu(game):
    """Show hidden debug menu"""
    game.add_msg("="*59, 'separator')
    game.add_msg("🔧 DEBUG MENU 🔧", 'warning')
    game.add_msg("="*59, 'separator')
    game.add_msg("")
    game.add_msg("1. Return to Title Screen")
    game.add_msg("2. Go to Specific Floor (1-100)")
    game.add_msg("3. Unlock All Skills")
    game.add_msg("4. Max All Stat Bonuses")
    game.add_msg("5. Unlock Shinso")
    game.add_msg("6. Trigger Game Over Screen")
    game.add_msg("7. Trigger Victory Screen")
    game.add_msg("8. Enter New Zone (Choose Type)")
    game.add_msg("9. Level All Characters to 10 (Team-Up Testing)")
    game.add_msg("0. Exit Debug Menu")
    game.add_msg("")
    
    game.game_state = 'debug'
    game.pending_input = 'debug_menu'
    game.current_options = [
        {'key': '1', 'text': 'Title Screen'},
        {'key': '2', 'text': 'Go to Floor'},
        {'key': '3', 'text': 'Unlock Skills'},
        {'key': '4', 'text': 'Max Stats'},
        {'key': '5', 'text': 'Unlock Shinso'},
        {'key': '6', 'text': 'Game Over'},
        {'key': '7', 'text': 'Victory'},
        {'key': '8', 'text': 'New Zone'},
        {'key': '9', 'text': 'Level 10 All'},
        {'key': '0', 'text': 'Exit'}
    ]

def handle_debug_menu(game, choice):
    """Handle debug menu selection"""
    if choice == '0':
        # Exit debug - always return to Aizawa screen to force zone generation
        game.start_game()
    
    elif choice == '1':
        # Return to title
        game.start_game()
    
    elif choice == '2':
        # Go to specific floor
        game.add_msg("Enter floor number (1-100):", 'highlight')
        game.pending_input = 'debug_floor'
        game.current_options = []
    
    elif choice == '3':
        # Unlock all skills
        for skill_name in game.global_tree.skills:
            game.global_tree.skills[skill_name]['level'] = game.global_tree.skills[skill_name]['max']
        game.add_msg("✅ All global skills unlocked!", 'success')
        game.add_msg("")
        show_debug_menu(game)
    
    elif choice == '4':
        # Max all stat bonuses
        for char in game.characters:
            if char.unlocked:
                char.skill_points = 99
        game.add_msg("✅ All characters given 99 skill points!", 'success')
        game.add_msg("")
        show_debug_menu(game)
    
    elif choice == '5':
        # Unlock Shinso
        shinso = next((c for c in game.characters if c.name == "Hitoshi Shinso"), None)
        if shinso:
            shinso.unlocked = True
            game.add_msg("✅ Hitoshi Shinso unlocked!", 'success')
        game.add_msg("")
        show_debug_menu(game)
    
    elif choice == '6':
        # Game over screen
        handle_defeat(game)
    
    elif choice == '7':
        # Victory screen
        handle_final_victory(game)
    
    elif choice == '8':
        # New zone - choose type
        game.add_msg("Choose zone type:", 'highlight')
        game.add_msg("1. Forest")
        game.add_msg("2. Flashfire")
        game.add_msg("3. Urban")
        game.add_msg("4. Lake")
        game.add_msg("5. Mountain")
        game.add_msg("6. Blizzard")
        game.add_msg("7. Underground")
        game.add_msg("")
        game.pending_input = 'debug_zone_type'
        game.current_options = []
    
    elif choice == '9':
        # TEAM-UP TESTING: Level all characters to 10
        for char in game.characters:
            while char.level < 10:
                char.level += 1
                char.max_hp += 20
                char.hp = char.max_hp
                char.max_energy += 10
                char.energy = char.max_energy
                char.base_attack += 5
                char.base_defense += 2
                char.attack = char.base_attack
                char.defense = char.base_defense
                char.skill_points += 1
        
        game.add_msg("✅ All characters leveled to 10!", 'success')
        game.add_msg("🤝 Team-Up Attacks now available for testing!", 'highlight')
        game.add_msg("")
        show_debug_menu(game)

def handle_debug_zone_type(game, choice):
    """Handle zone type selection in debug"""
    zone_map = {
        '1': 'forest',
        '2': 'flashfire',
        '3': 'urban',
        '4': 'lake',
        '5': 'mountain',
        '6': 'blizzard',
        '7': 'underground'
    }
    
    if choice in zone_map:
        # Override current zone theme
        game.current_theme = zone_map[choice]
        game.selected_character = None
        game.show_character_selection()
    else:
        game.add_msg("Invalid choice!", 'warning')
        show_debug_menu(game)

@app.route('/api/input', methods=['POST'])
def handle_input():
    """Handle any user input"""
    data = request.json
    session_id = data.get('session_id')
    user_input = data.get('input', '').strip()
    user_input_lower = user_input.lower()
    
    if session_id not in games:
        return jsonify({'error': 'Invalid session'}), 400
    
    game = games[session_id]
    game.clear_msgs()
    
    # Check for debug command
    if user_input_lower == 'froppenheimer':
        show_debug_menu(game)
        return jsonify({'state': game.get_state_dict()})
    
    try:
        # Route input based on game state
        if game.pending_input == 'continue':
            game.begin_zone()
        
        elif game.pending_input == 'debug_menu':
            handle_debug_menu(game, user_input)
        
        elif game.pending_input == 'debug_zone_type':
            handle_debug_zone_type(game, user_input)
        
        elif game.pending_input == 'character_number':
            game.select_character(user_input_lower)
        
        elif game.pending_input == 'direction':
            handle_navigation(game, user_input_lower)
        
        elif game.pending_input == 'combat_action':
            handle_combat_action(game, user_input_lower)
        
        elif game.pending_input == 'quirk_choice':
            handle_quirk_choice(game, user_input_lower)
        
        elif game.pending_input == 'item_choice':
            handle_item_choice(game, user_input_lower)
        
        elif game.pending_input == 'team_up_choice':
            handle_team_up_choice(game, user_input_lower)
        
        elif game.pending_input == 'debug_floor':
            try:
                floor_num = int(user_input)
                if 1 <= floor_num <= 100:
                    # Calculate zone and floor
                    zone = ((floor_num - 1) // 5) + 1
                    floor_in_zone = ((floor_num - 1) % 5) + 1
                    
                    game.current_zone = zone
                    game.current_floor = floor_in_zone
                    
                    # Set the zone theme
                    theme_id = game.zone_themes[zone - 1]
                    game.current_theme = theme_id
                    
                    game.add_msg(f"✅ Jumped to Zone {zone}, Floor {floor_in_zone} (Overall Floor {floor_num})", 'success')
                    game.add_msg(f"Zone type: {theme_id.title()}", 'normal')
                    game.add_msg("")
                    show_debug_menu(game)
                else:
                    game.add_msg("Floor must be 1-100!", 'warning')
                    show_debug_menu(game)
            except ValueError:
                game.add_msg("Invalid floor number!", 'warning')
                show_debug_menu(game)
        
        elif game.pending_input == 'passage_choice':
            if user_input == '1':
                game.add_msg("You enter the secret passage...", 'success')
                game.add_msg("")
                game.current_zone += 1
                game.selected_character.heal(50)
                game.selected_character.restore_energy(30)
                game.add_msg("The passage leads you safely to the next zone!", 'success')
                game.add_msg("HP and Energy restored from the safe travel!", 'success')
                game.add_msg("")
                if game.current_zone <= 20:
                    game.begin_zone()
                else:
                    game.start_final_boss()
            else:
                game.add_msg("You decide to continue through this zone normally.", 'normal')
                game.add_msg("")
                game.show_navigation_options()
        
        elif game.pending_input == 'poi_investigate':
            handle_poi_investigation(game, user_input)
        
        elif game.pending_input == 'poi_choice':
            handle_poi_choice(game, user_input)
        
        elif game.pending_input == 'skill_tree_choice':
            if user_input == '1':
                game.show_global_skills()
            elif user_input == '2':
                game.show_personal_skills()
            elif user_input == '3':
                game.show_current_bonuses()
            elif user_input == '4':
                # Return to previous state (combat or navigation)
                if hasattr(game, 'pre_skill_state') and game.pre_skill_state == 'combat':
                    game.show_combat_options()
                elif game.in_combat:
                    game.show_combat_options()
                else:
                    # Return to navigation - show current room info
                    room_desc = game.get_room_description(game.current_theme, game.current_room)
                    game.add_msg(room_desc, 'normal')
                    game.add_msg("")
                    game.show_navigation_options()
                # Clear the stored state
                if hasattr(game, 'pre_skill_state'):
                    delattr(game, 'pre_skill_state')
        
        elif game.pending_input == 'global_skill_choice':
            handle_global_skill_choice(game, user_input)
        
        elif game.pending_input == 'personal_skill_choice':
            handle_personal_skill_choice(game, user_input)
        
        elif game.pending_input == 'continue':
            # From view bonuses screen
            if game.game_state == 'view_bonuses':
                game.show_skill_tree_main()
            else:
                # Default continue behavior
                if game.game_state == 'ready':
                    game.begin_zone()
        
        elif game.pending_input == 'boss_decision':
            if user_input == '1':
                enter_boss_room(game)
            elif user_input == '2':
                retreat_from_boss(game)
        
        else:
            game.add_msg("Waiting for input...", 'normal')
        
    except Exception as e:
        game.add_msg(f"Error: {str(e)}", 'warning')
        import traceback
        traceback.print_exc()
    
    return jsonify({'state': game.get_state_dict()})

def handle_global_skill_choice(game, choice):
    """Handle global skill upgrade"""
    char = game.selected_character
    
    if choice == '0':
        game.show_skill_tree_main()
        return
    
    skill_map = {'1': 'strength', '2': 'defense', '3': 'hp', '4': 'energy', '5': 'evasion'}
    
    if choice in skill_map and char.skill_points > 0:
        skill_name = skill_map[choice]
        if game.global_tree.upgrade_skill(skill_name):
            char.skill_points -= 1
            
            # Apply the new bonuses
            game.global_tree.set_character_bonus(char.name)
            apply_global_bonuses(char, game.global_tree)
            
            game.add_msg(f"✨ Upgraded {skill_name.capitalize()}!", 'success')
            game.add_msg("All students will benefit from this upgrade!")
            
            if game.global_tree.current_character_bonus.get(skill_name, 1.0) > 1.0:
                game.add_msg(f"🌟 {char.name}'s specialization made this upgrade more effective!", 'highlight')
            
            game.add_msg("")
            game.show_global_skills()
        else:
            game.add_msg(f"{skill_name.capitalize()} is already at maximum level!", 'warning')
            game.add_msg("")
            game.show_global_skills()
    elif char.skill_points == 0:
        game.add_msg("No skill points available!", 'warning')
        game.add_msg("")
        game.show_skill_tree_main()
    else:
        game.add_msg("Invalid choice!", 'warning')
        game.show_global_skills()

def handle_personal_skill_choice(game, choice):
    """Handle personal skill upgrade"""
    char = game.selected_character
    skill_tree = get_character_skill_tree(char.name)
    
    if choice == '0':
        game.show_skill_tree_main()
        return
    
    try:
        choice_num = int(choice)
        skills_list = list(skill_tree.items())
        
        if 1 <= choice_num <= len(skills_list) and char.skill_points > 0:
            skill_id, skill_data = skills_list[choice_num - 1]
            current_level = char.personal_skills.get(skill_id, 0)
            
            if current_level < skill_data['max']:
                char.personal_skills[skill_id] = current_level + 1
                char.skill_points -= 1
                
                # Apply bonuses
                for bonus_type, value in skill_data['bonus'].items():
                    if bonus_type == 'attack':
                        char.base_attack += value
                        char.attack += value
                    elif bonus_type == 'defense':
                        char.base_defense += value
                        char.defense += value
                    elif bonus_type == 'hp':
                        char.max_hp += value
                        char.hp += value
                    elif bonus_type == 'energy':
                        char.max_energy += value
                        char.energy += value
                    elif bonus_type == 'evasion':
                        char.evasion += value
                    elif bonus_type == 'ambush':
                        char.ambush_chance += value
                    elif bonus_type == 'item_find':
                        char.item_find_bonus += value
                    elif bonus_type == 'enemy_avoid':
                        char.enemy_avoid_chance += value
                    elif bonus_type == 'secret_detection':
                        char.secret_detection += value
                    elif bonus_type == 'rescue_boost':
                        # Stored for POI determination
                        if not hasattr(char, 'rescue_boost'):
                            char.rescue_boost = 0
                        char.rescue_boost += value
                    elif bonus_type == 'post_combat_heal':
                        # Stored for combat victory
                        if not hasattr(char, 'post_combat_heal'):
                            char.post_combat_heal = 0
                        char.post_combat_heal += value
                    elif bonus_type == 'lucky_bag':
                        # Flag for POI special content
                        char.can_find_lucky_bags = True
                    # NEW PARTY BUFF SKILLS
                    elif bonus_type == 'acid_veil':
                        char.has_acid_veil = True
                        game.add_msg("💧 ACID VEIL ACTIVATED! All characters gain damage reduction!", 'success')
                    elif bonus_type == 'ribbit_recovery':
                        char.has_ribbit_recovery = True
                        game.add_msg("🐸 RIBBIT RECOVERY ACTIVATED! All characters gain survival protection!", 'success')
                    elif bonus_type == 'cant_stop_sparkle':
                        char.has_cant_stop_sparkle = True
                        game.add_msg("✨ CAN'T STOP OUR SPARKLE! All characters gain +5% evasion!", 'success')
                    elif bonus_type == 'defensive_instinct':
                        char.has_defensive_instinct = True
                        game.add_msg("💚 DEFENSIVE INSTINCT ACTIVATED! 2x defense when HP ≤ 25%!", 'success')
                
                # Check if Plus Ultra unlocked
                if char.check_plus_ultra_unlock():
                    if not char.plus_ultra_available:
                        char.plus_ultra_available = True
                        game.add_msg("")
                        game.add_msg("="*59, 'separator')
                        game.add_msg("⚡⚡⚡ PLUS ULTRA UNLOCKED! ⚡⚡⚡", 'success')
                        game.add_msg("="*59, 'separator')
                        game.add_msg("")
                        game.add_msg(f"{char.name} has mastered all personal skills!")
                        game.add_msg("PLUS ULTRA is now available - Full HP & Energy recovery!")
                        game.add_msg("Can be used once per zone, in or out of combat.")
                        game.add_msg("="*59, 'separator')
                        game.add_msg("")
                
                game.add_msg(f"✨ Upgraded {skill_id.replace('_', ' ').title()}!", 'success')
                game.add_msg(f"⚠️  Remember: This bonus is lost if {char.name} is captured!", 'warning')
                game.add_msg("")
                game.show_personal_skills()
            else:
                game.add_msg("This skill is already at maximum level!", 'warning')
                game.add_msg("")
                game.show_personal_skills()
        elif char.skill_points == 0:
            game.add_msg("No skill points available!", 'warning')
            game.add_msg("")
            game.show_skill_tree_main()
        else:
            game.add_msg("Invalid choice!", 'warning')
            game.show_personal_skills()
    except (ValueError, IndexError):
        game.add_msg("Invalid choice!", 'warning')
        game.show_personal_skills()

def handle_poi_investigation(game, choice):
    """Handle investigating a specific POI"""
    try:
        choice_num = int(choice)
        
        if choice_num == 0:
            # Don't investigate, continue navigation
            game.add_msg("You decide not to investigate further.", 'normal')
            game.add_msg("")
            game.show_navigation_options()
            return
        
        if 1 <= choice_num <= len(game.current_poi_list):
            poi = game.current_poi_list[choice_num - 1]
            
            game.add_msg(f"You investigate point of interest #{choice_num}...")
            game.add_msg("")
            
            if poi['type'] == 'nothing':
                messages = [
                    "You find nothing of value.",
                    "It's empty.",
                    "Nothing here but dust and shadows.",
                    "A thorough search reveals nothing useful."
                ]
                game.add_msg(random.choice(messages), 'normal')
                game.add_msg("")
                # Remove this POI and show remaining
                game.current_poi_list.pop(choice_num - 1)
                if game.current_poi_list:
                    game.add_msg("Continue investigating other points of interest?")
                    game.show_remaining_poi()
                else:
                    game.add_msg("No more points of interest to investigate.")
                    game.add_msg("")
                    game.show_navigation_options()
            
            elif poi['type'] == 'items':
                game.add_msg("💎 You found supplies!", 'success')
                for item in poi['items']:
                    game.shared_inventory.append(item)
                    game.add_msg(f"  • {item}", 'success')
                
                # PHASE 2: Show level up if it occurs
                char = game.selected_character
                old_level = char.level
                leveled_up = char.gain_exp(poi['exp'])
                game.add_msg(f"  • {poi['exp']} EXP", 'success')
                
                if leveled_up:
                    game.add_msg("")
                    game.add_msg("="*59, 'separator')
                    game.add_msg("🌟 LEVEL UP! 🌟", 'success')
                    game.add_msg("")
                    game.add_msg(f"{char.name}'s experience has sharpened their abilities!")
                    game.add_msg("")
                    game.add_msg(f"Level {old_level} → Level {char.level}", 'highlight')
                    game.add_msg(f"Maximum HP: {char.max_hp} | Maximum Energy: {char.max_energy}", 'normal')
                    game.add_msg(f"Attack Power: {char.attack} | Defense: {char.defense}", 'normal')
                    game.add_msg(f"✨ Gained a skill point! Total: {char.skill_points}", 'highlight')
                    game.add_msg("="*59, 'separator')
                
                game.add_msg("")
                # Remove this POI and show remaining
                game.current_poi_list.pop(choice_num - 1)
                if game.current_poi_list:
                    game.show_remaining_poi()
                else:
                    game.show_navigation_options()
            
            elif poi['type'] == 'civilian':
                # Pass the scaled EXP reward
                civilian_exp = poi.get('exp', 100)  # Default to 100 if not set
                game.show_poi_encounter('civilian', civilian_exp)
                game.current_poi_list = []  # Clear POI list after finding civilian
            
            elif poi['type'] == 'rescue':
                # Rescue a captured student!
                captured = [c for c in game.characters if c.captured and c.unlocked]
                if captured:
                    rescued = random.choice(captured)
                    rescued.captured = False
                    rescued.hp = rescued.max_hp // 2  # Return at half health
                    rescued.energy = rescued.max_energy // 2
                    
                    game.add_msg("🎖️  STUDENT RESCUED!", 'success')
                    game.add_msg("")
                    game.add_msg(f"You found {rescued.name} trapped and managed to free them!")
                    game.add_msg(f"{rescued.name} has been returned to active duty!")
                    game.add_msg(f"HP: {rescued.hp}/{rescued.max_hp} | Energy: {rescued.energy}/{rescued.max_energy}")
                    game.add_msg("")
                    game.add_msg(f'[Aizawa]: "Good work. {rescued.name}, get back in the fight."')
                    game.add_msg("")
                game.current_poi_list = []
                game.show_navigation_options()
            
            elif poi['type'] == 'shinso_unlock':
                # Unlock Shinso!
                shinso = next((c for c in game.characters if c.name == "Hitoshi Shinso"), None)
                if shinso and not shinso.unlocked:
                    shinso.unlocked = True
                    
                    game.add_msg("❗ SPECIAL EVENT!", 'highlight')
                    game.add_msg("")
                    game.add_msg("You discover someone unexpected in the facility...")
                    game.add_msg("")
                    game.add_msg('[Mysterious Voice]: "Need a hand?"')
                    game.add_msg("")
                    game.add_msg("Hitoshi Shinso emerges from the shadows!")
                    game.add_msg("")
                    game.add_msg('[Shinso]: "Heard Class 1-A was training here. Figured I\'d prove I belong with you guys."')
                    game.add_msg("")
                    game.add_msg('[Aizawa]: "...Shinso. Fine. You can join the exercise."')
                    game.add_msg("")
                    game.add_msg("🎉 Hitoshi Shinso is now available for deployment!", 'success')
                    game.add_msg("")
                game.current_poi_list = []
                game.show_navigation_options()
            
            elif poi['type'] == 'enemy':
                # Generate logical description based on zone and POI description
                poi_desc = poi.get('description', '').lower()
                enemy = create_enemy(game.current_zone, game.current_floor)
                
                # Determine hiding action based on POI size/type
                if any(word in poi_desc for word in ['cave', 'hollow', 'crevice', 'gap', 'alcove', 'burrow', 'shelter', 'nook', 'recess']):
                    hiding_verb = "hiding in"
                elif any(word in poi_desc for word in ['behind', 'beneath', 'under', 'below']):
                    hiding_verb = "hiding behind"
                elif any(word in poi_desc for word in ['small', 'mailbox', 'box', 'drawer', 'container']):
                    # Too small for a person - they're near it
                    hiding_verb = "waiting near"
                else:
                    hiding_verb = "concealed in"
                
                game.add_msg(f"⚠️  A {enemy.name} was {hiding_verb} this location!", 'warning')
                game.add_msg("")
                
                game.current_enemy = enemy
                game.in_combat = True
                game.combat_state = {
                    'player_defense_buff': 0,
                    'player_defense_buff_turns': 0,
                    'enemy_stunned': 0,
                    'enemy_defense_debuff': 0,
                    'enemy_attack_debuff': 0
                }
                game.add_msg(f"{enemy.name} (Level {enemy.level}) attacks!", 'warning')
                game.add_msg("")
                game.show_combat_options()
                game.current_poi_list = []  # Clear POI list during combat
            
            elif poi['type'] == 'lucky_bag':
                # PHASE 2.5: Momo's Lucky Bag discovery
                game.add_msg("🎁✨ LUCKY BAG DISCOVERED! ✨🎁", 'highlight')
                game.add_msg("")
                game.add_msg("Yaoyorozu's creation knowledge reveals a hidden cache!")
                game.add_msg("")
                
                # Massive rewards!
                items = []
                for _ in range(3):  # 3 guaranteed items
                    items.append(random.choice(["Health Potion", "Energy Drink"]))
                
                exp = 200 * game.current_zone  # Huge EXP!
                
                game.add_msg("💎 CONTENTS:", 'success')
                for item in items:
                    game.add_msg(f"  • {item}")
                    game.shared_inventory.append(item)
                game.add_msg(f"  • {exp} EXP!")
                game.add_msg("")
                
                # Apply EXP with level up check
                old_level = char.level
                leveled_up = char.gain_exp(exp)
                
                if leveled_up:
                    game.add_msg("")
                    game.add_msg("="*59, 'separator')
                    game.add_msg("🌟 LEVEL UP! 🌟", 'success')
                    game.add_msg("")
                    game.add_msg(f"{char.name}'s experience has sharpened their abilities!")
                    game.add_msg("")
                    game.add_msg(f"Level {old_level} → Level {char.level}", 'highlight')
                    game.add_msg(f"Maximum HP: {char.max_hp} | Maximum Energy: {char.max_energy}", 'normal')
                    game.add_msg(f"Attack Power: {char.attack} | Defense: {char.defense}", 'normal')
                    game.add_msg(f"✨ Gained a skill point! Total: {char.skill_points}", 'highlight')
                    game.add_msg("="*59, 'separator')
                    game.add_msg("")
                
                game.current_poi_list = []
                game.show_navigation_options()
            
            elif poi['type'] == 'passage':
                game.add_msg("🌟 SECRET PASSAGE DISCOVERED!", 'highlight')
                game.add_msg("")
                game.add_msg("You've found a hidden passage that leads directly to the next zone!")
                game.add_msg("This shortcut will allow you to skip the rest of this zone.")
                game.add_msg("")
                game.add_msg("1. Take the passage (skip to next zone)")
                game.add_msg("2. Ignore it (continue normally)")
                game.pending_input = 'passage_choice'
                game.current_options = [
                    {'key': '1', 'text': 'Take passage'},
                    {'key': '2', 'text': 'Ignore'}
                ]
                game.current_poi_list = []
        else:
            game.add_msg("Invalid choice!", 'warning')
            game.show_remaining_poi()
    
    except (ValueError, IndexError):
        game.add_msg("Invalid input!", 'warning')
        game.show_remaining_poi()

def handle_poi_choice(game, choice):
    """Handle POI (Point of Interest) choices"""
    char = game.selected_character
    
    if choice == '1':
        # Accept the POI option
        option = game.current_options[0]
        
        # Apply rewards
        game.add_msg("")
        for reward_type, reward_value in option.get('rewards', []):
            if reward_type == 'exp':
                old_level = char.level
                leveled_up = char.gain_exp(reward_value)
                game.add_msg(f"✨ Gained {reward_value} EXP!", 'success')
                
                # PHASE 2: Show level up notification
                if leveled_up:
                    game.add_msg("")
                    game.add_msg("="*59, 'separator')
                    game.add_msg("🌟 LEVEL UP! 🌟", 'success')
                    game.add_msg("")
                    game.add_msg(f"{char.name}'s experience has sharpened their abilities!")
                    game.add_msg("")
                    game.add_msg(f"Level {old_level} → Level {char.level}", 'highlight')
                    game.add_msg(f"Maximum HP: {char.max_hp} | Maximum Energy: {char.max_energy}", 'normal')
                    game.add_msg(f"Attack Power: {char.attack} | Defense: {char.defense}", 'normal')
                    game.add_msg(f"✨ Gained a skill point! Total: {char.skill_points}", 'highlight')
                    game.add_msg("="*59, 'separator')
                    game.add_msg("")
                    
            elif reward_type == 'item':
                game.shared_inventory.append(reward_value)
                game.add_msg(f"💎 Received {reward_value}!", 'success')
        
        game.add_msg("")
        game.show_navigation_options()
    
    elif choice == '2':
        # Decline the POI
        game.add_msg("You move on.", 'normal')
        game.add_msg("")
        game.show_navigation_options()
    
    else:
        game.add_msg("Invalid choice!", 'warning')
        game.add_msg("")
        game.show_navigation_options()

def handle_navigation(game, direction):
    """Handle room navigation"""
    direction_map = {'n': 'north', 's': 'south', 'e': 'east', 'w': 'west'}
    direction = direction_map.get(direction, direction)
    
    if direction == 'search':
        if not hasattr(game, 'searched_rooms'):
            game.searched_rooms = set()
        
        if game.current_room in game.searched_rooms:
            game.add_msg("You've already searched this room!", 'warning')
            game.add_msg("")
            game.show_navigation_options()
        else:
            game.searched_rooms.add(game.current_room)
            
            # Determine number of POI (0-3, with 3 being rare)
            roll = random.random()
            if roll < 0.3:  # 30% chance for 0 POI
                num_poi = 0
            elif roll < 0.75:  # 45% chance for 1 POI
                num_poi = 1
            elif roll < 0.95:  # 20% chance for 2 POI
                num_poi = 2
            else:  # 5% chance for 3 POI
                num_poi = 3
            
            if num_poi == 0:
                game.add_msg("You search the room thoroughly but find nothing of interest.", 'normal')
                game.add_msg("")
                game.show_navigation_options()
            else:
                # Generate POI with descriptions
                game.show_poi_search_results(num_poi)
        return
    
    if direction == 'rest':
        if game.current_room not in game.rested_in_rooms:
            game.selected_character.restore_energy(15)
            game.rested_in_rooms.add(game.current_room)
            game.add_msg("You take a moment to catch your breath and focus...")
            game.add_msg(f"Energy restored: {game.selected_character.energy}/{game.selected_character.max_energy}", 'success')
            game.add_msg("")
            game.show_navigation_options()
        else:
            game.add_msg("You've already rested in this room!", 'warning')
            game.show_navigation_options()
        return
    
    if direction == 'skills':
        game.show_skill_tree_main()
        return
    
    if direction == 'plus_ultra':
        # PHASE 2.5: Plus Ultra in navigation
        char = game.selected_character
        if char.plus_ultra_available and not char.plus_ultra_used_this_zone:
            if char.use_plus_ultra():
                game.add_msg("")
                game.add_msg("="*59, 'separator')
                game.add_msg("⚡⚡⚡ PLUS ULTRA! ⚡⚡⚡", 'success')
                game.add_msg("="*59, 'separator')
                game.add_msg("")
                game.add_msg(f"{char.name} pushes beyond their limits!")
                game.add_msg("")
                game.add_msg(f"HP: FULLY RESTORED! ({char.hp}/{char.max_hp})", 'success')
                game.add_msg(f"Energy: FULLY RESTORED! ({char.energy}/{char.max_energy})", 'success')
                game.add_msg("")
                game.add_msg("⚠️  Plus Ultra has been used for this zone.", 'warning')
                game.add_msg("="*59, 'separator')
                game.add_msg("")
                game.show_navigation_options()
        else:
            game.add_msg("Plus Ultra not available!", 'warning')
            game.show_navigation_options()
        return
    
    room = game.zone_map['rooms'][game.current_room]
    next_room = room.get(direction)
    
    if next_room:
        game.current_room = next_room
        game.add_msg(f"Moving {direction}...", 'normal')
        game.add_msg("")
        game.start_room_exploration()
    else:
        game.add_msg("Can't go that way!", 'warning')
        game.show_navigation_options()

def handle_item_choice(game, choice):
    """Handle item selection and usage"""
    char = game.selected_character
    enemy = game.current_enemy
    
    if choice == '0':
        # Back to combat menu
        game.show_combat_options()
        return
    
    try:
        choice_num = int(choice)
        
        # Use item map if it exists, otherwise fall back to direct indexing
        if hasattr(game, 'current_item_map') and choice_num in game.current_item_map:
            item_name = game.current_item_map[choice_num]
            # Remove one instance of this item from SHARED inventory
            game.shared_inventory.remove(item_name)
            
            if "Potion" in item_name or "Health" in item_name:
                # Health potion
                old_hp = char.hp
                char.heal(40)
                healed = char.hp - old_hp
                game.add_msg(f"💊 Used {item_name}!", 'highlight')
                game.add_msg(f"❤️  Restored {healed} HP!", 'success')
                game.add_msg("")
                
            elif "Energy" in item_name or "Drink" in item_name:
                # Energy drink
                old_energy = char.energy
                char.restore_energy(30)
                restored = char.energy - old_energy
                game.add_msg(f"⚡ Used {item_name}!", 'highlight')
                game.add_msg(f"✨ Restored {restored} Energy!", 'success')
                game.add_msg("")
            
            # Enemy still attacks after item use
            if enemy.hp > 0:
                enemy_turn(game)
        else:
            game.add_msg("Invalid choice!", 'warning')
            game.show_combat_options()
    except (ValueError, KeyError):
        game.add_msg("Invalid input!", 'warning')
        game.show_combat_options()

def handle_quirk_choice(game, choice):
    """Handle quirk ability selection"""
    char = game.selected_character
    enemy = game.current_enemy
    
    if choice == '0':
        # Back to combat menu
        game.show_combat_options()
        return
    
    try:
        abilities = list(char.abilities.items())
        ability_index = int(choice) - 1
        
        if 0 <= ability_index < len(abilities):
            name, data = abilities[ability_index]
            if len(data) == 4:
                damage, cost, ability_type, desc = data
            else:
                damage, cost, desc = data
            
            if char.energy >= cost:
                char.energy -= cost
                
                # PHASE 2.5: Apply combat passives to quirk damage
                passive = char.unique_passive
                base_damage = damage + char.attack
                damage_multiplier = 1.0
                
                # Ojiro's Last Stand - 2x damage at ≤25% HP
                if passive and passive['type'] == 'last_stand':
                    hp_percent = (char.hp / char.max_hp) * 100
                    if hp_percent <= 25:
                        damage_multiplier = passive['value']
                        game.add_msg("🥋 DESPERATE STRIKE!", 'highlight')
                
                # Todoroki's Versatile - +5% damage
                elif passive and passive['type'] == 'versatile':
                    damage_multiplier = 1.0 + (passive['value'] / 100)
                
                final_damage = int(base_damage * damage_multiplier)
                actual = enemy.take_damage(final_damage)
                
                game.add_msg(f"✨ {char.name} uses {name}!", 'highlight')
                game.add_msg(f"💥 Deals {actual} damage!", 'success')
                
                # PHASE 2.5: Kaminari's Stun Chance
                if passive and passive['type'] == 'stun_chance':
                    if random.random() * 100 < passive['value']:
                        game.combat_state['enemy_stunned'] = 1
                        game.add_msg(f"⚡ ELECTRIC SHOCK! {enemy.name} is stunned!", 'highlight')
                
                game.add_msg("")
                
                if enemy.hp <= 0:
                    handle_victory(game)
                    return
                
                enemy_turn(game)
            else:
                game.add_msg("Not enough energy!", 'warning')
                game.add_msg("")
                game.show_combat_options()
        else:
            game.add_msg("Invalid choice!", 'warning')
            game.show_combat_options()
    except (ValueError, IndexError):
        game.add_msg("Invalid input!", 'warning')
        game.show_combat_options()

def handle_combat_action(game, action):
    """Handle combat actions"""
    char = game.selected_character
    enemy = game.current_enemy
    
    if action == '1':
        # Basic attack
        base_damage = char.attack + random.randint(-3, 5)
        
        # PHASE 2.5: Apply combat passives
        passive = char.unique_passive
        damage_multiplier = 1.0
        
        # Ojiro's Last Stand - 2x damage at ≤25% HP
        if passive and passive['type'] == 'last_stand':
            hp_percent = (char.hp / char.max_hp) * 100
            if hp_percent <= 25:
                damage_multiplier = passive['value']
                game.add_msg("🥋 DESPERATE STRIKE!", 'highlight')
        
        # Todoroki's Versatile - +5% damage
        elif passive and passive['type'] == 'versatile':
            damage_multiplier = 1.0 + (passive['value'] / 100)
        
        damage = int(base_damage * damage_multiplier)
        actual = enemy.take_damage(damage)
        game.add_msg(f"💥 {char.name} attacks for {actual} damage!", 'success')
        
        # PHASE 2.5: Kaminari's Stun Chance
        if passive and passive['type'] == 'stun_chance':
            if random.random() * 100 < passive['value']:
                game.combat_state['enemy_stunned'] = 1
                game.add_msg(f"⚡ ELECTRIC SHOCK! {enemy.name} is stunned!", 'highlight')
        
        if enemy.hp <= 0:
            handle_victory(game)
            return
        
        # Enemy counter (skip if stunned)
        enemy_turn(game)
        
    elif action == '2':
        # Show quirk abilities submenu
        game.game_state = 'quirk_select'
        game.pending_input = 'quirk_choice'
        
        game.add_msg("SELECT QUIRK ABILITY:", 'highlight')
        abilities = list(char.abilities.items())
        for i, (name, data) in enumerate(abilities, 1):
            if len(data) == 4:
                damage, cost, ability_type, desc = data
            else:
                damage, cost, desc = data
                ability_type = 'normal'
            game.add_msg(f"{i}. {name} ({cost} energy) - {desc}")
        game.add_msg("0. Back to combat menu")
        
        game.current_options = [{'key': str(i+1), 'text': name} for i, (name, _) in enumerate(abilities)]
        game.current_options.append({'key': '0', 'text': 'Back'})
        
    elif action == '3':
        # Show shared inventory
        if game.shared_inventory:
            game.game_state = 'item_select'
            game.pending_input = 'item_choice'
            
            game.add_msg("SHARED INVENTORY:", 'highlight')
            
            # Count item quantities
            item_counts = Counter(game.shared_inventory)
            
            # Display with quantities
            display_index = 1
            item_map = {}  # Map display number to actual item
            for item, count in sorted(item_counts.items()):
                if count > 1:
                    game.add_msg(f"{display_index}. {item} x{count}")
                else:
                    game.add_msg(f"{display_index}. {item}")
                item_map[display_index] = item
                display_index += 1
            
            game.add_msg("0. Back to combat menu")
            
            # Store item map for selection
            game.current_item_map = item_map
            game.current_options = [{'key': str(i), 'text': item} for i, item in item_map.items()]
            game.current_options.append({'key': '0', 'text': 'Back'})
        else:
            game.add_msg("No items in inventory!", 'warning')
            game.add_msg("")
            game.show_combat_options()
    
    elif action == '4':
        # Show skill tree
        game.show_skill_tree_main()
    
    elif action == '5':
        # PHASE 2.5: Plus Ultra OR Team-Up (depends on availability)
        team_ups = char.get_available_team_ups(game.characters)
        
        if char.plus_ultra_available and not char.plus_ultra_used_this_zone:
            # Action 5 is Plus Ultra
            if char.use_plus_ultra():
                game.add_msg("")
                game.add_msg("="*59, 'separator')
                game.add_msg("⚡⚡⚡ PLUS ULTRA! ⚡⚡⚡", 'success')
                game.add_msg("="*59, 'separator')
                game.add_msg("")
                game.add_msg(f"{char.name} pushes beyond their limits!")
                game.add_msg("")
                game.add_msg(f"HP: FULLY RESTORED! ({char.hp}/{char.max_hp})", 'success')
                game.add_msg(f"Energy: FULLY RESTORED! ({char.energy}/{char.max_energy})", 'success')
                game.add_msg("")
                game.add_msg("⚠️  Plus Ultra has been used for this zone.", 'warning')
                game.add_msg("="*59, 'separator')
                game.add_msg("")
                game.show_combat_options()
        elif team_ups:
            # Action 5 is Team-Up (no Plus Ultra available)
            show_team_up_menu(game, team_ups)
        else:
            game.add_msg("Not available!", 'warning')
            game.show_combat_options()
    
    elif action == '6':
        # Team-Up Attack (when Plus Ultra also available)
        team_ups = char.get_available_team_ups(game.characters)
        if team_ups:
            show_team_up_menu(game, team_ups)
        else:
            game.add_msg("No team-up attacks available!", 'warning')
            game.show_combat_options()
    
    else:
        game.add_msg("Invalid action!", 'warning')
        game.show_combat_options()

def show_team_up_menu(game, team_ups):
    """Display team-up attack selection menu"""
    game.game_state = 'team_up_select'
    game.pending_input = 'team_up_choice'
    
    game.add_msg("🤝 TEAM-UP ATTACKS AVAILABLE:", 'highlight')
    game.add_msg("")
    
    for i, (partner_name, attack_data) in enumerate(team_ups, 1):
        game.add_msg(f"{i}. {attack_data['name']} (with {partner_name})")
        game.add_msg(f"   {attack_data['damage']} damage | {attack_data['energy']} energy")
        game.add_msg(f"   {attack_data['desc']}", 'normal')
        game.add_msg("")
    
    game.add_msg("0. Back to combat menu")
    
    # Store team-ups for selection
    game.current_team_ups = team_ups
    game.current_options = [{'key': str(i+1), 'text': team_ups[i][1]['name']} for i in range(len(team_ups))]
    game.current_options.append({'key': '0', 'text': 'Back'})

def handle_team_up_choice(game, choice):
    """Handle team-up attack selection"""
    char = game.selected_character
    enemy = game.current_enemy
    
    if choice == '0':
        game.show_combat_options()
        return
    
    try:
        attack_index = int(choice) - 1
        if 0 <= attack_index < len(game.current_team_ups):
            partner_name, attack_data = game.current_team_ups[attack_index]
            
            if char.energy >= attack_data['energy']:
                char.energy -= attack_data['energy']
                
                # Apply passive bonuses to team-up damage
                passive = char.unique_passive
                base_damage = attack_data['damage'] + char.attack
                damage_multiplier = 1.0
                
                # Ojiro's Last Stand
                if passive and passive['type'] == 'last_stand':
                    hp_percent = (char.hp / char.max_hp) * 100
                    if hp_percent <= 25:
                        damage_multiplier = passive['value']
                        game.add_msg("🥋 DESPERATE STRIKE!", 'highlight')
                
                # Todoroki's Versatile
                elif passive and passive['type'] == 'versatile':
                    damage_multiplier = 1.0 + (passive['value'] / 100)
                
                final_damage = int(base_damage * damage_multiplier)
                actual = enemy.take_damage(final_damage)
                
                game.add_msg("")
                game.add_msg("="*59, 'separator')
                game.add_msg(f"🤝 TEAM-UP ATTACK: {attack_data['name'].upper()}! 🤝", 'success')
                game.add_msg("="*59, 'separator')
                game.add_msg("")
                game.add_msg(f"{char.name} & {partner_name}!", 'highlight')
                game.add_msg(attack_data['desc'], 'highlight')
                game.add_msg("")
                game.add_msg(f"💥💥 DEVASTATING DAMAGE: {actual}! 💥💥", 'success')
                game.add_msg("="*59, 'separator')
                game.add_msg("")
                
                if enemy.hp <= 0:
                    handle_victory(game)
                    return
                
                enemy_turn(game)
            else:
                game.add_msg("Not enough energy for team-up attack!", 'warning')
                game.add_msg("")
                game.show_combat_options()
        else:
            game.add_msg("Invalid choice!", 'warning')
            show_team_up_menu(game, game.current_team_ups)
    except (ValueError, IndexError):
        game.add_msg("Invalid input!", 'warning')
        show_team_up_menu(game, game.current_team_ups)

def enemy_turn(game):
    """Enemy attacks"""
    char = game.selected_character
    enemy = game.current_enemy
    passive = char.unique_passive
    
    # PHASE 2.5: Check if enemy is stunned
    if game.combat_state.get('enemy_stunned', 0) > 0:
        game.add_msg(f"⚡ {enemy.name} is stunned and cannot attack!", 'highlight')
        game.combat_state['enemy_stunned'] = 0  # Clear stun
        game.add_msg("")
        game.show_combat_options()
        return
    
    base_damage = enemy.attack + random.randint(-2, 4)
    
    # PARTY BUFF: Check for Acid Veil damage reduction (applies to ALL characters)
    acid_veil_reduction = 0
    acid_veil_char = None
    for c in game.characters:
        if hasattr(c, 'has_acid_veil') and c.has_acid_veil and not c.captured:
            acid_veil_reduction = 10
            acid_veil_char = c
            break
    
    if acid_veil_reduction > 0:
        base_damage = int(base_damage * (1.0 - acid_veil_reduction / 100))
    
    # PHASE 2.5: Kirishima's Damage Reduction (personal)
    damage_reduction = 0
    if passive and passive['type'] == 'damage_reduction':
        damage_reduction = passive['value']
        base_damage = int(base_damage * (1.0 - damage_reduction / 100))
    
    # NEW: Midoriya's Defensive Instinct - 2x defense at ≤25% HP
    char_defense = char.defense
    if hasattr(char, 'has_defensive_instinct') and char.has_defensive_instinct:
        hp_percent = (char.hp / char.max_hp) * 100
        if hp_percent <= 25:
            char_defense = char.defense * 2
            game.add_msg(f"💚 DEFENSIVE INSTINCT! {char.name}'s defense doubled!", 'highlight')
    
    # Calculate actual damage with modified defense
    actual_damage = max(1, base_damage - char_defense)
    char.hp -= actual_damage
    
    game.add_msg(f"🔴 {enemy.name} attacks for {actual_damage} damage!", 'warning')
    
    # PARTY BUFF: Acid Veil recoil damage
    if acid_veil_char and acid_veil_reduction > 0:
        # Enemy takes 5% recoil of the ORIGINAL damage (before reductions)
        original_damage = enemy.attack + random.randint(-2, 4)
        recoil = max(1, int(original_damage * 0.05))
        enemy.hp -= recoil
        game.add_msg(f"💧 ACID VEIL! {enemy.name} takes {recoil} recoil damage!", 'highlight')
        if enemy.hp <= 0:
            game.add_msg("")
            game.add_msg(f"💧 {enemy.name} melts from the acid recoil!", 'success')
            handle_victory(game)
            return
    
    game.add_msg("")
    
    # PHASE 2.5: Check for survival mechanics BEFORE defeat
    if char.hp <= 0:
        hp_before_hit = char.hp + actual_damage
        
        # PARTY BUFF: Ribbit Recovery - ALL characters survive at 1 HP
        ribbit_active = False
        for c in game.characters:
            if hasattr(c, 'has_ribbit_recovery') and c.has_ribbit_recovery and not c.captured:
                ribbit_active = True
                break
        
        if ribbit_active and hp_before_hit > 1:  # Was above 1 HP before the hit
            char.hp = 1
            game.add_msg("🐸 RIBBIT RECOVERY! 🐸", 'success')
            game.add_msg(f"Asui's tongue pulls {char.name} to safety! HP: 1", 'success')
            game.add_msg("")
            game.show_combat_options()
            return
        
        # Normal defeat
        handle_defeat(game)
    else:
        game.show_combat_options()

def handle_victory(game):
    """Handle combat victory"""
    char = game.selected_character
    enemy = game.current_enemy
    
    game.add_msg("")
    game.add_msg("🎉 VICTORY!", 'success')
    game.add_msg(f"Gained {enemy.exp_reward} EXP!")
    
    # Gain EXP
    old_level = char.level
    char.gain_exp(enemy.exp_reward)
    
    # Check if leveled up
    if char.level > old_level:
        game.add_msg("")
        game.add_msg("="*59, 'separator')
        game.add_msg("🌟 LEVEL UP! 🌟", 'success')
        game.add_msg("")
        game.add_msg(f"{char.name}'s experience with combat has sharpened their abilities!")
        game.add_msg("")
        game.add_msg(f"Level {old_level} → Level {char.level}", 'highlight')
        game.add_msg(f"Maximum HP: {char.max_hp} | Maximum Energy: {char.max_energy}", 'normal')
        game.add_msg(f"Attack Power: {char.attack} | Defense: {char.defense}", 'normal')
        game.add_msg(f"✨ Gained a skill point! Total: {char.skill_points}", 'highlight')
        game.add_msg("="*59, 'separator')
        game.add_msg("")
    
    # Check if this was All For One
    if isinstance(enemy, BossEnemy) and enemy.name == "All For One":
        handle_final_victory(game)
        return
    
    # Random item drop (30% chance)
    if random.random() < 0.3:
        item = random.choice(["Health Potion", "Energy Drink"])
        game.shared_inventory.append(item)
        game.add_msg(f"💎 Found: {item}!", 'highlight')
    
    # PHASE 2.5: Ochaco's Float Recovery
    if hasattr(char, 'post_combat_heal') and char.post_combat_heal > 0:
        char.heal(char.post_combat_heal)
        game.add_msg(f"💚 Float Recovery! {char.name} healed {char.post_combat_heal} HP!", 'success')
    
    game.add_msg("")
    game.in_combat = False
    game.current_enemy = None
    
    # Mark room as cleared and apply passive healing
    game.cleared_rooms.add(game.current_room)
    
    # PHASE 1: Passive healing for benched characters
    # Heal based on vitality: 1 HP + (vitality bonus / 15)
    vit_bonus = game.global_tree.get_hp_bonus()
    heal_per_room = max(1, vit_bonus // 15)
    
    # PHASE 2.5: Ochaco's Helping Hand bonus
    ochaco_bonus = 0
    if char.unique_passive and char.unique_passive['type'] == 'helping_hand':
        ochaco_bonus = 2
    
    # PHASE 2.5: Asui's Ribbit Recovery energy restore
    asui_energy = 0
    if char.unique_passive and char.unique_passive['type'] == 'ribbit_recovery':
        asui_energy = 5
    
    for character in game.characters:
        if character != char and not character.captured:
            old_hp = character.hp
            character.heal(heal_per_room + ochaco_bonus)
            
            # Asui's energy recovery
            if asui_energy > 0:
                character.restore_energy(asui_energy)
            # Optionally log healing (commented out to avoid spam)
            # if character.hp > old_hp:
            #     game.add_msg(f"{character.name} rests (+{character.hp - old_hp} HP)", 'normal')
    
    # Check if this was a boss
    if isinstance(enemy, BossEnemy):
        enemy.defeated = True
        
        # Boss Victory Scene
        game.add_msg("="*59, 'separator')
        game.add_msg(f"🏆 BOSS DEFEATED! 🏆", 'success')
        game.add_msg("="*59, 'separator')
        game.add_msg("")
        game.add_msg(f"{char.name} stands victorious over {enemy.name}!")
        game.add_msg("")
        
        # Bonus experience for boss (50% more than base reward)
        bonus_exp = int(enemy.exp_reward * 0.5)
        total_boss_exp = enemy.exp_reward + bonus_exp
        game.add_msg(f"Boss Bonus EXP: +{bonus_exp}", 'highlight')
        game.add_msg(f"Total Boss EXP: {total_boss_exp}", 'highlight')
        char.gain_exp(bonus_exp)  # Already got base exp earlier
        game.add_msg("")
        
        # Zone completion
        game.add_msg("="*59, 'separator')
        game.add_msg(f"✅ ZONE {game.current_zone} CLEARED!", 'success')
        game.add_msg("="*59, 'separator')
        game.add_msg("")
        game.add_msg(f"[Aizawa]: \"Zone {game.current_zone} complete. Keep descending.\"")
        game.add_msg("")
        game.add_msg("Restored 20 Energy!", 'success')
        game.add_msg("")
        
        # Only restore energy, no HP (passive healing handles that)
        char.restore_energy(20)
        
        game.current_zone += 1
        game.selected_character = None
        
        if game.current_zone > 20:
            start_final_boss(game)
        else:
            game.game_state = 'ready'
            game.pending_input = 'continue'
            game.current_options = [{'key': 'continue', 'text': f'Press Enter to begin Zone {game.current_zone}'}]
    else:
        game.show_navigation_options()

def handle_final_victory(game):
    """Handle defeating All For One - GAME COMPLETE!"""
    game.in_combat = False
    game.current_enemy = None
    game.game_state = 'victory'
    game.pending_input = None
    
    captured_count = len([c for c in game.characters if c.captured])
    
    game.clear_msgs()
    game.add_msg("="*59, 'separator')
    game.add_msg("🏆 VICTORY! 🏆", 'success')
    game.add_msg("="*59, 'separator')
    game.add_msg("")
    game.add_msg("All For One falls to his knees, defeated at last.")
    game.add_msg("")
    game.add_msg('[Aizawa]: "You did it. All 20 zones cleared."')
    game.add_msg('[Aizawa]: "You reached the bottom of the Tower Descent."')
    game.add_msg('[Aizawa]: "Class 1-A... you\'ve proven yourselves."')
    game.add_msg("")
    game.add_msg("="*59, 'separator')
    game.add_msg("EXERCISE COMPLETE!", 'highlight')
    game.add_msg("="*59, 'separator')
    game.add_msg("")
    game.add_msg(f"Students Captured: {captured_count}/21")
    game.add_msg("")
    
    if captured_count == 0:
        game.add_msg("🌟 PERFECT RUN - NO CASUALTIES! 🌟", 'success')
        game.add_msg("")
        game.add_msg('[Aizawa]: "Not a single student lost. Exceptional."')
    elif captured_count <= 5:
        game.add_msg("✨ EXCELLENT PERFORMANCE! ✨", 'success')
        game.add_msg("")
        game.add_msg('[Aizawa]: "Minimal casualties. Well done."')
    elif captured_count <= 10:
        game.add_msg("✅ MISSION SUCCESS!", 'success')
        game.add_msg("")
        game.add_msg('[Aizawa]: "You completed the objective. Good work."')
    else:
        game.add_msg("✅ MISSION COMPLETE", 'success')
        game.add_msg("")
        game.add_msg('[Aizawa]: "High casualties, but you finished. Learn from this."')
    
    game.add_msg("")
    game.add_msg("="*59, 'separator')
    game.add_msg("Thank you for playing!", 'highlight')
    game.add_msg("="*59, 'separator')

def handle_defeat(game):
    """Handle character defeat"""
    char = game.selected_character
    
    game.add_msg("")
    game.add_msg(f"💀 {char.name} was defeated!", 'warning')
    game.add_msg("CAPTURED", 'warning')
    game.add_msg("")
    
    char.captured = True
    char.reset_personal_skills()
    game.selected_character = None
    game.in_combat = False
    game.current_enemy = None
    
    # Check if all captured
    available = [c for c in game.characters if not c.captured and c.unlocked]
    if not available:
        game.add_msg("="*59, 'separator')
        game.add_msg("GAME OVER - ALL STUDENTS CAPTURED", 'warning')
        game.add_msg("="*59, 'separator')
        game.game_state = 'game_over'
        game.pending_input = None
    else:
        game.show_character_selection()

def start_final_boss(game):
    """Initiate All For One final boss encounter"""
    game.clear_msgs()
    game.current_theme = 'final_boss'
    
    game.add_msg("="*59, 'separator')
    game.add_msg("FINAL FLOOR", 'highlight')
    game.add_msg("="*59, 'separator')
    game.add_msg("")
    
    available = [c for c in game.characters if not c.captured and c.unlocked]
    
    if not available:
        game.add_msg("No students remaining...", 'warning')
        game.add_msg("")
        game.add_msg("GAME OVER", 'warning')
        game.game_state = 'game_over'
        game.pending_input = None
        return
    
    game.add_msg('[Aizawa]: "This is it. The final test."')
    game.add_msg('[Aizawa]: "All For One awaits on the top floor."')
    game.add_msg('[Aizawa]: "He\'s stolen quirks from every student you\'ve lost."')
    game.add_msg("")
    
    # Count captured students
    captured_students = [c for c in game.characters if c.captured]
    
    if not captured_students:
        game.add_msg('[Aizawa]: "Impressive. Not a single student captured."')
        game.add_msg('[Aizawa]: "All For One will have no stolen quirks to use."')
    else:
        game.add_msg(f'[Aizawa]: "Students captured: {len(captured_students)}"')
        game.add_msg('[Aizawa]: "All For One will use their quirks against you."')
    
    game.add_msg("")
    game.add_msg("="*59, 'separator')
    game.add_msg("")
    
    # Create All For One - ADAPTIVE BOSS
    num_captured = len(captured_students)
    afo = BossEnemy("All For One", 25, "The Symbol of Evil.", 21)
    
    # Scale based on captures
    afo.max_hp = 200 + (num_captured * 50)
    afo.hp = afo.max_hp
    afo.attack = 20 + (num_captured * 5)
    afo.defense = 10 + (num_captured * 2)
    afo.defeated = False
    
    game.zone_bosses[21] = afo
    
    game.add_msg("ALL FOR ONE", 'warning')
    game.add_msg("="*59, 'separator')
    game.add_msg("")
    game.add_msg("All For One stands before you, radiating malevolent power.")
    game.add_msg("")
    
    if num_captured > 0:
        game.add_msg(f"You sense {num_captured} stolen quirks within him:", 'warning')
        for student in captured_students[:5]:
            game.add_msg(f"  • {student.name}'s {student.quirk}")
        if num_captured > 5:
            game.add_msg(f"  ... and {num_captured - 5} more")
    else:
        game.add_msg("Without stolen quirks, he seems almost... ordinary.")
    
    game.add_msg("")
    game.add_msg(f"All For One - HP: {afo.hp}/{afo.max_hp} | ATK: {afo.attack} | DEF: {afo.defense}")
    game.add_msg("")
    game.add_msg("="*59, 'separator')
    game.add_msg("")
    
    # Show character selection for final battle
    game.show_character_selection()

def enter_boss_room(game):
    """Enter boss room"""
    if game.current_zone not in game.zone_bosses:
        game.zone_bosses[game.current_zone] = create_boss(game.current_zone)
    
    boss = game.zone_bosses[game.current_zone]
    
    if not boss.defeated:
        game.current_enemy = boss
        game.in_combat = True
        game.combat_state = {
            'player_defense_buff': 0,
            'player_defense_buff_turns': 0,
            'enemy_stunned': 0,
            'enemy_defense_debuff': 0,
            'enemy_attack_debuff': 0
        }
        
        game.add_msg("="*59, 'separator')
        game.add_msg(f"👹 BOSS: {boss.name}!", 'warning')
        game.add_msg("="*59, 'separator')
        game.add_msg("")
        game.add_msg(boss.description)
        game.add_msg("")
        game.show_combat_options()
    else:
        # Boss already defeated - advance zone
        game.add_msg(f"✅ Zone {game.current_zone} Boss already defeated!", 'success')
        game.add_msg("")
        
        # Heal on zone completion
        game.selected_character.heal(30)
        game.selected_character.restore_energy(20)
        game.add_msg("Moving to next zone...", 'highlight')
        game.add_msg("Restored 30 HP and 20 Energy!", 'success')
        game.add_msg("")
        
        game.current_zone += 1
        game.selected_character = None
        
        # Check if all zones cleared
        if game.current_zone > 20:
            # FINAL BOSS TIME
            start_final_boss(game)
        else:
            # Next zone
            game.begin_zone()

def retreat_from_boss(game):
    """Retreat from boss room"""
    # Go back one room (simple implementation)
    game.current_room = 1
    game.add_msg("Retreated to safer area.", 'normal')
    game.add_msg("")
    game.show_navigation_options()

@app.route('/favicon.ico')
def favicon():
    """Serve favicon"""
    try:
        return send_file('favicon.ico', mimetype='image/x-icon')
    except FileNotFoundError:
        # If favicon doesn't exist, return 404
        return '', 404

@app.route('/images/<path:filepath>')
def serve_image(filepath):
    """Serve images"""
    images_dir = Path('images')
    full_path = images_dir / filepath
    
    if full_path.exists():
        return send_from_directory(str(images_dir), filepath)
    
    placeholder = images_dir / 'placeholder.png'
    if placeholder.exists():
        return send_from_directory(str(images_dir), 'placeholder.png')
    
    return "Image not found", 404

if __name__ == '__main__':
    # Create directories
    Path("images/zones").mkdir(parents=True, exist_ok=True)
    Path("images/enemies").mkdir(parents=True, exist_ok=True)
    Path("images/bosses").mkdir(parents=True, exist_ok=True)
    
    # Create a simple placeholder image if it doesn't exist
    placeholder_path = Path("images/placeholder.png")
    if not placeholder_path.exists():
        try:
            from PIL import Image, ImageDraw, ImageFont
            # Create a simple placeholder
            img = Image.new('RGB', (720, 400), color=(60, 60, 80))
            draw = ImageDraw.Draw(img)
            
            # Draw diagonal stripes
            for i in range(0, 720 + 400, 40):
                draw.line([(i, 0), (i - 400, 400)], fill=(80, 80, 100), width=3)
            
            # Add text
            try:
                font = ImageFont.truetype("arial.ttf", 36)
            except:
                font = ImageFont.load_default()
            
            text = "Image Placeholder"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            draw.text(((720 - text_width) // 2, (400 - text_height) // 2), 
                     text, fill=(200, 200, 200), font=font)
            
            img.save(str(placeholder_path))
            print(f"Created placeholder image: {placeholder_path}")
        except ImportError:
            print("PIL not installed - placeholder image not created")
            print("Install with: pip install pillow")
    
    print("="*70)
    print("🎮 MHA ROGUELIKE - FULLY INTEGRATED WEB VERSION")
    print("="*70)
    print("\nFeatures:")
    print("✅ Complete zone descriptions")
    print("✅ Full character selection with stats")
    print("✅ Zone navigation with rest mechanics")
    print("✅ Complete combat system")
    print("✅ Boss battles with HP persistence")
    print("✅ EXP and leveling")
    print("✅ Environmental zone effects")
    print("")
    print("Open your browser: http://localhost:5000")
    print("Press CTRL+C to stop")
    print("="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
