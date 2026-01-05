import random
import time

class Character:
    def __init__(self, name, quirk, abilities, base_stats, dialogue, aizawa_dialogue, hidden=False):
        self.name = name
        self.quirk = quirk
        self.abilities = abilities
        self.level = 1
        self.max_hp = base_stats['hp']
        self.hp = self.max_hp
        self.max_energy = base_stats['energy']
        self.energy = self.max_energy
        self.base_attack = base_stats['attack']
        self.attack = base_stats['attack']
        self.base_defense = base_stats['defense']
        self.defense = base_stats['defense']
        self.exp = 0
        self.exp_to_level = 100
        self.inventory = []
        self.captured = False
        self.dialogue = dialogue
        self.aizawa_dialogue = aizawa_dialogue
        self.hidden = hidden
        self.unlocked = not hidden
        self.zone_bonuses = base_stats.get('zone_bonuses', {})
        self.zone_penalties = base_stats.get('zone_penalties', {})
        self.skill_points = 0
        self.personal_skills = {}
        self.evasion = 0
        self.ambush_chance = 0
        self.item_find_bonus = 0
        self.enemy_avoid_chance = 0
        self.secret_detection = 0
        
        # PHASE 2.5: Unique passive abilities
        self.unique_passive = self.get_unique_passive()
        
        # PHASE 2.5: Plus Ultra ability
        self.plus_ultra_available = False
        self.plus_ultra_used_this_zone = False
        
        # TEAM-UP ATTACKS: Available when both partners are Level 10+
        self.team_up_attacks = self.get_team_up_attacks()
        
    def get_available_team_ups(self, all_characters):
        """Check which team-up attacks are available (both Level 10+, partner not captured)"""
        available = []
        if self.level < 10:
            return available
        
        for partner_name, attack_data in self.team_up_attacks.items():
            # Find the partner
            partner = next((c for c in all_characters if c.name == partner_name), None)
            if partner and partner.level >= 10 and not partner.captured and partner.unlocked:
                available.append((partner_name, attack_data))
        
        return available
    
    def get_team_up_attacks(self):
        """Define team-up attacks for this character"""
        team_ups = {
            'Ochaco Uraraka': {
                'Tsuyu Asui': {
                    'name': 'Fafrotskies',
                    'damage': 80,
                    'energy': 35,
                    'desc': "Asui's tongue swipes at debris floated by Uraraka, sending it hurtling at the enemy"
                },
                'Hanta Sero': {
                    'name': 'Meteor Barrage',
                    'damage': 75,
                    'energy': 32,
                    'desc': "Uraraka releases floated debris strung together by Sero's tape in a devastating barrage"
                },
                'Izuku Midoriya': {
                    'name': 'You Can Do It!',
                    'damage': 90,
                    'energy': 38,
                    'desc': "Uraraka floats the enemy, leaving them defenseless against a powered-up Smash from Midoriya"
                },
                'Eijiro Kirishima': {
                    'name': 'Manly Hammer',
                    'damage': 85,
                    'energy': 36,
                    'desc': "After removing gravity's effects from Kirishima, Uraraka swings his hardened form violently at the enemy"
                },
                'Mina Ashido': {
                    'name': 'Rainy Day',
                    'damage': 78,
                    'energy': 34,
                    'desc': "After having Uraraka float her, Mina splashes down a rain of corrosive acid on the enemy"
                },
                'Katsuki Bakugo': {
                    'name': 'Shotgun Blast',
                    'damage': 88,
                    'energy': 37,
                    'desc': "A pile of floated debris becomes explosive buckshot as Bakugo detonates it from behind"
                },
                'Rikido Sato': {
                    'name': 'Mochi Pounding',
                    'damage': 82,
                    'energy': 35,
                    'desc': "Equipped with weightless mochi hammers, Uraraka and Sato pulverize the enemy"
                },
            },
            'Tsuyu Asui': {
                'Ochaco Uraraka': {
                    'name': 'Fafrotskies',
                    'damage': 80,
                    'energy': 35,
                    'desc': "Asui's tongue swipes at debris floated by Uraraka, sending it hurtling at the enemy"
                },
                'Katsuki Bakugo': {
                    'name': 'Froppenheimer',
                    'damage': 95,
                    'energy': 40,
                    'desc': "Bakugo infuses his sweat with Asui's toxic mucus to create devastating sticky explosives"
                },
                'Mashirao Ojiro': {
                    'name': 'Frog Stance',
                    'damage': 77,
                    'energy': 33,
                    'desc': "Slathered in Asui's toxic mucus, Ojiro strikes the enemy's pressure points with precision"
                },
                'Minoru Mineta': {
                    'name': 'Perv Swerve',
                    'damage': 70,
                    'energy': 30,
                    'desc': "Fed up with Mineta's perverted ways, Asui sends him hurtling at the enemy like a cannonball"
                },
                'Toru Hagakure': {
                    'name': 'Covert Frops',
                    'damage': 83,
                    'energy': 36,
                    'desc': "An invisible Hagakure and camouflaged Asui wreak havoc on the unsuspecting enemy"
                },
                'Mezo Shoji': {
                    'name': 'Octo Frog',
                    'damage': 86,
                    'energy': 37,
                    'desc': "Keeping warm on Shoji's back, Asui and Shoji unleash a myriad of heteromorphic attacks (Negates Cold Penalty)"
                },
            },
            'Tenya Iida': {
                'Shoto Todoroki': {
                    'name': 'Ice Jet',
                    'damage': 92,
                    'energy': 39,
                    'desc': "Iida propels a fighter jet made of pure ice at blistering speed toward the enemy"
                },
                'Izuku Midoriya': {
                    'name': 'Race to You',
                    'damage': 87,
                    'energy': 37,
                    'desc': "Midoriya and Iida charge at full speed, sandwiching the enemy between two devastating kicks"
                },
            },
            'Momo Yaoyorozu': {
                'Denki Kaminari': {
                    'name': 'Electromagnetic Railgun',
                    'damage': 98,
                    'energy': 42,
                    'desc': "Yaoyorozu's created railgun fires with devastating force, powered by Kaminari's electricity"
                },
                'Kyoka Jiro': {
                    'name': 'Death Amp',
                    'damage': 94,
                    'energy': 40,
                    'desc': "Jiro plugs into a supersized amplifier created by Yaoyorozu for catastrophic sonic damage"
                },
                'Rikido Sato': {
                    'name': 'Sweet Tea',
                    'damage': 79,
                    'energy': 34,
                    'desc': "Yaoyorozu and Sato share sweets, replenishing their strength for an all-out combined attack"
                },
                'Fumikage Tokoyami': {
                    'name': 'Stare into the Abyss',
                    'damage': 91,
                    'energy': 38,
                    'desc': "Yaoyorozu creates night-vision goggles for Tokoyami, allowing Dark Shadow to strike with perfect precision"
                },
                'Izuku Midoriya': {
                    'name': 'Peak Midoriya',
                    'damage': 89,
                    'energy': 37,
                    'desc': "Yaoyorozu and Midoriya formulate the perfect attack targeting the enemy's weakness (May contain rambling)"
                },
            },
            'Izuku Midoriya': {
                'Katsuki Bakugo': {
                    'name': 'Howitzer Blitz',
                    'damage': 100,
                    'energy': 45,
                    'desc': "Building centrifugal force with Howitzer Impact, Bakugo hurls Midoriya for a massive explosive Smash"
                },
                'Ochaco Uraraka': {
                    'name': 'You Can Do It!',
                    'damage': 90,
                    'energy': 38,
                    'desc': "Uraraka floats the enemy, leaving them defenseless against a powered-up Smash from Midoriya"
                },
                'Tenya Iida': {
                    'name': 'Race to You',
                    'damage': 87,
                    'energy': 37,
                    'desc': "Midoriya and Iida charge at full speed, sandwiching the enemy between two devastating kicks"
                },
                'Shoto Todoroki': {
                    'name': 'Ice Shards',
                    'damage': 96,
                    'energy': 41,
                    'desc': "Todoroki unleashes his Heaven-Piercing Ice Wall, followed by Midoriya's Smash sending ice shards flying"
                },
                'Momo Yaoyorozu': {
                    'name': 'Peak Midoriya',
                    'damage': 89,
                    'energy': 37,
                    'desc': "Yaoyorozu and Midoriya formulate the perfect attack targeting the enemy's weakness (May contain rambling)"
                },
            },
            'Katsuki Bakugo': {
                'Izuku Midoriya': {
                    'name': 'Howitzer Blitz',
                    'damage': 100,
                    'energy': 45,
                    'desc': "Building centrifugal force with Howitzer Impact, Bakugo hurls Midoriya for a massive explosive Smash"
                },
                'Eijiro Kirishima': {
                    'name': 'Bombshell',
                    'damage': 93,
                    'energy': 39,
                    'desc': "Bakugo launches a fully hardened Kirishima at the enemy with a devastating explosion"
                },
                'Tsuyu Asui': {
                    'name': 'Froppenheimer',
                    'damage': 95,
                    'energy': 40,
                    'desc': "Bakugo infuses his sweat with Asui's toxic mucus to create devastating sticky explosives"
                },
                'Yuga Aoyama': {
                    'name': 'Sparkler',
                    'damage': 76,
                    'energy': 33,
                    'desc': "In an unlikely team-up, Aoyama and Bakugo dazzle the enemy with a blinding sparkling attack"
                },
                'Ochaco Uraraka': {
                    'name': 'Shotgun Blast',
                    'damage': 88,
                    'energy': 37,
                    'desc': "A pile of floated debris becomes explosive buckshot as Bakugo detonates it from behind"
                },
            },
            'Shoto Todoroki': {
                'Tenya Iida': {
                    'name': 'Ice Jet',
                    'damage': 92,
                    'energy': 39,
                    'desc': "Iida propels a fighter jet made of pure ice at blistering speed toward the enemy"
                },
                'Izuku Midoriya': {
                    'name': 'Ice Shards',
                    'damage': 96,
                    'energy': 41,
                    'desc': "Todoroki unleashes his Heaven-Piercing Ice Wall, followed by Midoriya's Smash sending ice shards flying"
                },
            },
            'Eijiro Kirishima': {
                'Katsuki Bakugo': {
                    'name': 'Bombshell',
                    'damage': 93,
                    'energy': 39,
                    'desc': "Bakugo launches a fully hardened Kirishima at the enemy with a devastating explosion"
                },
                'Ochaco Uraraka': {
                    'name': 'Manly Hammer',
                    'damage': 85,
                    'energy': 36,
                    'desc': "After removing gravity's effects from Kirishima, Uraraka swings his hardened form violently at the enemy"
                },
            },
            'Denki Kaminari': {
                'Momo Yaoyorozu': {
                    'name': 'Electromagnetic Railgun',
                    'damage': 98,
                    'energy': 42,
                    'desc': "Yaoyorozu's created railgun fires with devastating force, powered by Kaminari's electricity"
                },
                'Kyoka Jiro': {
                    'name': 'Shock Wave',
                    'damage': 90,
                    'energy': 38,
                    'desc': "A powerful combination of Jiro's sonic waves and Kaminari's shocking electricity"
                },
                'Mina Ashido': {
                    'name': 'Dumb Luck',
                    'damage': 85,
                    'energy': 36,
                    'desc': "You don't know how it worked. But it did. For massive damage. Pure chaotic energy"
                },
            },
            'Fumikage Tokoyami': {
                'Momo Yaoyorozu': {
                    'name': 'Stare into the Abyss',
                    'damage': 91,
                    'energy': 38,
                    'desc': "Yaoyorozu creates night-vision goggles for Tokoyami, allowing Dark Shadow to strike with perfect precision"
                },
            },
            'Kyoka Jiro': {
                'Momo Yaoyorozu': {
                    'name': 'Death Amp',
                    'damage': 94,
                    'energy': 40,
                    'desc': "Jiro plugs into a supersized amplifier created by Yaoyorozu for catastrophic sonic damage"
                },
                'Denki Kaminari': {
                    'name': 'Shock Wave',
                    'damage': 90,
                    'energy': 38,
                    'desc': "A powerful combination of Jiro's sonic waves and Kaminari's shocking electricity"
                },
            },
            'Hanta Sero': {
                'Ochaco Uraraka': {
                    'name': 'Meteor Barrage',
                    'damage': 75,
                    'energy': 32,
                    'desc': "Uraraka releases floated debris strung together by Sero's tape in a devastating barrage"
                },
                'Minoru Mineta': {
                    'name': 'Sticky Tape',
                    'damage': 72,
                    'energy': 31,
                    'desc': "Sero and Mineta unleash a barrage of tape and sticky balls, immobilizing the opponent for a massive strike"
                },
            },
            'Mashirao Ojiro': {
                'Toru Hagakure': {
                    'name': 'Never Saw it Coming',
                    'damage': 81,
                    'energy': 35,
                    'desc': "Hagakure stuns the enemy with her light refraction, leaving them open for an Ojiro finishing strike"
                },
                'Tsuyu Asui': {
                    'name': 'Frog Stance',
                    'damage': 77,
                    'energy': 33,
                    'desc': "Slathered in Asui's toxic mucus, Ojiro strikes the enemy's pressure points with precision"
                },
            },
            'Toru Hagakure': {
                'Yuga Aoyama': {
                    'name': 'Navel Refraction',
                    'damage': 84,
                    'energy': 36,
                    'desc': "Aoyama blasts Hagakure with a powerful beam that she refracts back for amplified damage"
                },
                'Mashirao Ojiro': {
                    'name': 'Never Saw it Coming',
                    'damage': 81,
                    'energy': 35,
                    'desc': "Hagakure stuns the enemy with her light refraction, leaving them open for an Ojiro finishing strike"
                },
                'Tsuyu Asui': {
                    'name': 'Covert Frops',
                    'damage': 83,
                    'energy': 36,
                    'desc': "An invisible Hagakure and camouflaged Asui wreak havoc on the unsuspecting enemy"
                },
            },
            'Minoru Mineta': {
                'Hanta Sero': {
                    'name': 'Sticky Tape',
                    'damage': 72,
                    'energy': 31,
                    'desc': "Sero and Mineta unleash a barrage of tape and sticky balls, immobilizing the opponent for a massive strike"
                },
                'Tsuyu Asui': {
                    'name': 'Perv Swerve',
                    'damage': 70,
                    'energy': 30,
                    'desc': "Fed up with Mineta's perverted ways, Asui sends him hurtling at the enemy like a cannonball"
                },
            },
            'Rikido Sato': {
                'Momo Yaoyorozu': {
                    'name': 'Sweet Tea',
                    'damage': 79,
                    'energy': 34,
                    'desc': "Yaoyorozu and Sato share sweets, replenishing their strength for an all-out combined attack"
                },
                'Ochaco Uraraka': {
                    'name': 'Mochi Pounding',
                    'damage': 82,
                    'energy': 35,
                    'desc': "Equipped with weightless mochi hammers, Uraraka and Sato pulverize the enemy"
                },
            },
            'Yuga Aoyama': {
                'Toru Hagakure': {
                    'name': 'Navel Refraction',
                    'damage': 84,
                    'energy': 36,
                    'desc': "Aoyama blasts Hagakure with a powerful beam that she refracts back for amplified damage"
                },
                'Katsuki Bakugo': {
                    'name': 'Sparkler',
                    'damage': 76,
                    'energy': 33,
                    'desc': "In an unlikely team-up, Aoyama and Bakugo dazzle the enemy with a blinding sparkling attack"
                },
            },
            'Mina Ashido': {
                'Ochaco Uraraka': {
                    'name': 'Rainy Day',
                    'damage': 78,
                    'energy': 34,
                    'desc': "After having Uraraka float her, Mina splashes down a rain of corrosive acid on the enemy"
                },
                'Denki Kaminari': {
                    'name': 'Dumb Luck',
                    'damage': 85,
                    'energy': 36,
                    'desc': "You don't know how it worked. But it did. For massive damage. Pure chaotic energy"
                },
            },
            'Mezo Shoji': {
                'Tsuyu Asui': {
                    'name': 'Octo Frog',
                    'damage': 86,
                    'energy': 37,
                    'desc': "Keeping warm on Shoji's back, Asui and Shoji unleash a myriad of heteromorphic attacks (Negates Cold Penalty)"
                },
            },
        }
        
        return team_ups.get(self.name, {})
        
    def get_unique_passive(self):
        """Define unique passive ability based on character"""
        passives = {
            # RESCUE SPECIALISTS
            'Tenya Iida': {
                'type': 'rescue_boost',
                'value': 2.0,
                'desc': '🏃 Recipro Search - 2x chance to find captured students'
            },
            'Mezo Shoji': {
                'type': 'civilian_boost',
                'value': 2.0,
                'desc': '👥 Dupli-Arms Scout - 2x chance to find civilians'
            },
            'Kyoka Jiro': {
                'type': 'civilian_boost',
                'value': 1.8,
                'desc': '👥 Heartbeat Detection - 1.8x chance to find civilians'
            },
            
            # EXPLORATION SPECIALISTS
            'Toru Hagakure': {
                'type': 'passage_boost',
                'value': 3.0,
                'desc': '🔍 Invisible Scout - 3x chance to find secret passages'
            },
            'Minoru Mineta': {
                'type': 'passage_boost',
                'value': 2.0,
                'desc': '🔍 Pop Off Exploration - 2x chance to find passages'
            },
            'Fumikage Tokoyami': {
                'type': 'secret_detection',
                'value': 25,
                'desc': '🔍 Dark Shadow Search - +25% POI discovery'
            },
            'Hanta Sero': {
                'type': 'civilian_boost',
                'value': 1.5,
                'desc': '🕷️ Tape Rescue - 1.5x chance to find civilians (reaches hard-to-access places)'
            },
            'Tsuyu Asui': {
                'type': 'civilian_boost',
                'value': 1.3,
                'desc': '🐸 Frog Sense - 1.3x chance to find civilians'
            },
            
            # ITEM SPECIALISTS
            'Momo Yaoyorozu': {
                'type': 'item_boost',
                'value': 2.5,
                'desc': '💎 Creation Analysis - 2.5x better item discovery'
            },
            'Koji Koda': {
                'type': 'item_boost',
                'value': 1.5,
                'desc': '💎 Animal Friends - 1.5x better item discovery'
            },
            'Rikido Sato': {
                'type': 'recovery_item_boost',
                'value': 2.0,
                'desc': '🍬 Sugar Rush Finder - 2x chance to find recovery items'
            },
            
            # COMBAT SPECIALISTS
            'Katsuki Bakugo': {
                'type': 'ambush_master',
                'value': 30,
                'desc': '💥 Explosive Entry - +30% first strike damage'
            },
            'Eijiro Kirishima': {
                'type': 'damage_reduction',
                'value': 10,
                'desc': '🛡️ Hardening Armor - -10% damage taken'
            },
            'Shoto Todoroki': {
                'type': 'versatile',
                'value': 5,
                'desc': '❄️🔥 Dual Element - +5% all combat stats'
            },
            'Mashirao Ojiro': {
                'type': 'last_stand',
                'value': 2.0,
                'desc': '🥋 Last Stand - 2x damage when HP ≤ 25%'
            },
            'Izuku Midoriya': {
                'type': 'defensive_instinct',
                'value': 2.0,
                'desc': '💚 Defensive Instinct - 2x defense when HP ≤ 25%'
            },
            'Denki Kaminari': {
                'type': 'stun_chance',
                'value': 33,
                'desc': '⚡ Electric Shock - 33% chance to stun enemy on hit'
            },
            
            # SUPPORT SPECIALIST
            'Ochaco Uraraka': {
                'type': 'helping_hand',
                'value': 1,
                'desc': '🌟 Helping Hand - All students gain +5% evasion & heal +2 HP per room'
            },
        }
        return passives.get(self.name, None)
    
    def check_plus_ultra_unlock(self):
        """Check if all personal skills are maxed"""
        from mha_roguelike_complete import get_character_skill_tree
        skill_tree = get_character_skill_tree(self.name)
        if not skill_tree:
            return False
        
        for skill_id, skill_data in skill_tree.items():
            current = self.personal_skills.get(skill_id, 0)
            if current < skill_data['max']:
                return False
        
        return True
    
    def use_plus_ultra(self):
        """PLUS ULTRA - Full recovery (once per zone)"""
        if not self.plus_ultra_available or self.plus_ultra_used_this_zone:
            return False
        
        self.hp = self.max_hp
        self.energy = self.max_energy
        self.plus_ultra_used_this_zone = True
        return True
        
    def take_damage(self, damage):
        actual_damage = max(1, damage - self.defense)
        self.hp -= actual_damage
        return actual_damage
    
    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)
    
    def restore_energy(self, amount):
        self.energy = min(self.max_energy, self.energy + amount)
    
    def gain_exp(self, amount):
        old_level = self.level
        self.exp += amount
        
        # PHASE 2: Track if level up occurred
        leveled_up = False
        while self.exp >= self.exp_to_level:
            self.level_up()
            leveled_up = True
        
        return leveled_up  # Return True if leveled up
    
    def level_up(self):
        self.level += 1
        self.exp -= self.exp_to_level
        self.exp_to_level = int(self.exp_to_level * 1.5)
        self.max_hp += 20
        self.hp = self.max_hp
        self.max_energy += 10
        self.energy = self.max_energy
        self.base_attack += 5
        self.base_defense += 2
        self.attack = self.base_attack
        self.defense = self.base_defense
        self.gain_skill_point()
        # Remove print statements - handled by game UI
    
    def gain_skill_point(self):
        self.skill_points += 1
        # Remove print - handled by game UI
    
    def reset_personal_skills(self):
        self.personal_skills = {}
        self.evasion = 0
        self.ambush_chance = 0
        self.item_find_bonus = 0
        self.enemy_avoid_chance = 0
        self.secret_detection = 0
    
    def get_deployment_dialogue(self):
        health_percent = (self.hp / self.max_hp) * 100
        if health_percent > 50:
            return random.choice(self.dialogue['high'])
        elif health_percent > 10:
            return random.choice(self.dialogue['medium'])
        else:
            return random.choice(self.dialogue['low'])
    
    def get_aizawa_response(self):
        health_percent = (self.hp / self.max_hp) * 100
        if health_percent > 50:
            return self.aizawa_dialogue['high']
        elif health_percent > 10:
            return self.aizawa_dialogue['medium']
        else:
            return self.aizawa_dialogue['low']
    
    def apply_zone_effects(self, zone_theme):
        """Apply zone bonuses/penalties based on environmental type"""
        self.attack = self.base_attack
        self.defense = self.base_defense
        
        # Map theme to environmental types (can be multiple)
        env_types = get_zone_environmental_type(zone_theme)
        
        # Check for bonuses first
        for env_type in env_types:
            if env_type in self.zone_bonuses:
                bonus = self.zone_bonuses[env_type]
                self.attack += bonus['attack']
                self.defense += bonus['defense']
                return f"{self.name}'s quirk thrives in this environment! ATK +{bonus['attack']}, DEF +{bonus['defense']}"
        
        # Then check for penalties
        for env_type in env_types:
            if env_type in self.zone_penalties:
                penalty = self.zone_penalties[env_type]
                self.attack = max(1, self.attack - penalty['attack'])
                self.defense = max(0, self.defense - penalty['defense'])
                return f"{self.name} struggles in this environment... ATK -{penalty['attack']}, DEF -{penalty['defense']}"
        
        return None

class Enemy:
    def __init__(self, name, level, enemy_type, description):
        self.name = name
        self.level = level
        self.type = enemy_type
        self.description = description
        self.hp = 30 + (level * 15)
        self.max_hp = self.hp
        self.attack = 5 + (level * 3)
        self.defense = 2 + level
        self.exp_reward = 25 * level
        self.evasion = 0
        
    def take_damage(self, damage):
        actual_damage = max(1, damage - self.defense)
        self.hp -= actual_damage
        return actual_damage

class BossEnemy:
    def __init__(self, name, level, description, zone_number):
        self.name = name
        self.level = level
        self.description = description
        self.zone = zone_number
        # PHASE 1 REBALANCE - Increased difficulty
        self.max_hp = 200 + (level * 40)  # Was 80 + level * 20
        self.hp = self.max_hp
        self.attack = 18 + (level * 6)  # Was 10 + level * 3
        self.defense = 7 + (level * 3)  # Was 3 + level
        self.exp_reward = 150 * level  # Was 100 * level
        self.defeated = False
        self.evasion = 0
        
    def take_damage(self, damage):
        actual_damage = max(1, damage - self.defense)
        self.hp -= actual_damage
        return actual_damage
    
    def get_health_description(self):
        health_percent = (self.hp / self.max_hp) * 100
        if health_percent > 75:
            return "appears unharmed, radiating menacing energy"
        elif health_percent > 50:
            return "shows signs of damage, their movements slightly hindered"
        elif health_percent > 25:
            return "is clearly wounded, breathing heavily with visible injuries"
        else:
            return "is barely standing, their body covered in severe wounds"

class GlobalSkillTree:
    def __init__(self):
        # PHASE 2: Added diminishing_bonus for levels past max
        self.skills = {
            'strength': {'level': 0, 'max': 5, 'base_bonus': 3, 'diminishing_bonus': 2},
            'defense': {'level': 0, 'max': 5, 'base_bonus': 2, 'diminishing_bonus': 1},
            'hp': {'level': 0, 'max': 5, 'base_bonus': 15, 'diminishing_bonus': 10},
            'energy': {'level': 0, 'max': 5, 'base_bonus': 8, 'diminishing_bonus': 5},
            'evasion': {'level': 0, 'max': 5, 'base_bonus': 5, 'diminishing_bonus': 3},
        }
        self.current_character_bonus = {}
    
    def set_character_bonus(self, character_name):
        # PHASE 2.5: Enhanced specializations for character diversity
        bonuses = {
            # ULTIMATE TIER - HIGHEST IN GAME (3.5x)
            'Rikido Sato': {'strength': 3.5},              # ⭐ULTIMATE STRENGTH⭐ - HIGHEST BONUS IN GAME
            
            # TIER S - MASTERS (2.5x)
            'Eijiro Kirishima': {'defense': 2.5},          # Defense MASTER
            'Toru Hagakure': {'evasion': 2.5},             # Evasion MASTER
            'Tenya Iida': {'evasion': 2.5, 'hp': 1.3},     # Speed MASTER (evasion = speed)
            'Ochaco Uraraka': {'evasion': 2.5, 'energy': 1.6, 'hp': 1.4},  # Evasion MASTER + support
            
            # TIER A - SPECIALISTS (2.0x - 1.5x)
            'Mina Ashido': {'energy': 2.0},
            'Mashirao Ojiro': {'strength': 2.0, 'hp': 1.5},  # Increased from 1.8 to bridge gap
            'Mezo Shoji': {'defense': 1.8, 'hp': 1.5},
            'Minoru Mineta': {'evasion': 1.8, 'defense': 1.5},
            'Momo Yaoyorozu': {'energy': 1.75},
            'Denki Kaminari': {'energy': 1.5},
            'Fumikage Tokoyami': {'evasion': 1.5, 'strength': 1.2},
            'Kyoka Jiro': {'evasion': 1.5, 'defense': 1.3},
            
            # TIER B - FOCUSED (1.33x - 1.3x)
            'Katsuki Bakugo': {'strength': 1.33, 'energy': 1.2},
            'Shoto Todoroki': {'defense': 1.33, 'strength': 1.2},
            'Koji Koda': {'hp': 1.4, 'defense': 1.2},
            'Hanta Sero': {'evasion': 1.3, 'energy': 1.2},
            'Yuga Aoyama': {'strength': 1.3, 'energy': 1.2},
            
            # TIER C - BALANCED (1.2x - 1.15x all stats)
            'Izuku Midoriya': {'strength': 1.2, 'defense': 1.2, 'hp': 1.2, 'energy': 1.2, 'evasion': 1.2},
            'Tsuyu Asui': {'strength': 1.15, 'defense': 1.15, 'hp': 1.15, 'energy': 1.15, 'evasion': 1.15},
            'Hitoshi Shinso': {'energy': 1.3, 'evasion': 1.3},
        }
        self.current_character_bonus = bonuses.get(character_name, {})
    
    def upgrade_skill(self, skill_name):
        # PHASE 2: Remove cap - allow unlimited upgrades with diminishing returns
        if skill_name in self.skills:
            self.skills[skill_name]['level'] += 1
            return True
        return False
    
    def get_bonus(self, skill_name):
        if skill_name not in self.skills:
            return 0
        skill = self.skills[skill_name]
        level = skill['level']
        base = skill['base_bonus']
        diminishing = skill['diminishing_bonus']
        max_level = skill['max']
        
        # PHASE 2: Diminishing returns after max level
        if level <= max_level:
            # Normal progression (levels 1-5)
            total = base * level
        else:
            # Diminishing returns (levels 6+)
            over_max = level - max_level
            normal_total = base * max_level
            extra_total = diminishing * over_max
            total = normal_total + extra_total
        
        multiplier = self.current_character_bonus.get(skill_name, 1.0)
        return int(total * multiplier)
    
    def get_attack_bonus(self):
        return self.get_bonus('strength')
    
    def get_defense_bonus(self):
        return self.get_bonus('defense')
    
    def get_hp_bonus(self):
        return self.get_bonus('hp')
    
    def get_energy_bonus(self):
        return self.get_bonus('energy')
    
    def get_evasion_bonus(self):
        return self.get_bonus('evasion')
    
    def get_skill_display(self, skill_name):
        if skill_name not in self.skills:
            return ""
        skill = self.skills[skill_name]
        level = skill['level']
        max_level = skill['max']
        base_bonus = skill['base_bonus']
        diminishing_bonus = skill['diminishing_bonus']
        multiplier = self.current_character_bonus.get(skill_name, 1.0)
        
        # PHASE 2: Show what NEXT level gives with diminishing warnings
        if level < max_level:
            # Normal progression
            actual_bonus = int(base_bonus * multiplier)
            if multiplier > 1.0:
                return f"+{actual_bonus} (★BONUS★)"
            else:
                return f"+{actual_bonus}"
        elif level == max_level:
            # At max - next level will be diminished
            actual_bonus = int(diminishing_bonus * multiplier)
            return f"+{actual_bonus} (⚠️ Diminishing)"
        else:
            # Already past max
            actual_bonus = int(diminishing_bonus * multiplier)
            return f"+{actual_bonus} (⚠️ Diminished)"


def create_class_1a():
    """Creates all 21 Class 1-A characters with updated dialogue and Aizawa responses
    Character order: Alphabetical by last name (Japanese style)"""
    characters = []
    
    # Format: (name, quirk, {abilities}, stats, dialogue, aizawa_dialogue, hidden)
    # Abilities format: "name": (damage, energy_cost, ability_type, description)
    # ability_type: "normal", "evasion_debuff", "defense_buff", "defense_debuff", "attack_debuff", "stun"
    
    class_data = [
        # 1. AOYAMA (BAL★ specialty - HIGHLY BOOSTED)
        ("Yuga Aoyama", "Navel Laser", 
         {"Navel Beam": (15, 10, "normal", "Brilliant laser from belt buckle"), 
          "Supernova": (30, 21, "normal", "Maximum capacity laser")},
         {'hp': 85, 'energy': 51, 'attack': 13, 'defense': 4, 'zone_bonuses': {}, 'zone_penalties': {}},
         {'high': ["I cannot stop twinkling!", "Time to dazzle!", "My sparkle is unstoppable!"],
          'medium': ["Mon dieu... my stomach...", "Pain in my belly...", "My laser is fading!"],
          'low': ["Cannot sparkle anymore...", "My light has gone out...", 
                  "I just wanted to twinkle like everyone else... maman... papa..."]},
         {'high': "Your classmates are behind you.", 
          'medium': "The enemy doesn't care how much your stomach hurts.", 
          'low': "I won't let any student of mine drown in despair."}, False),
        
        # 2. ASHIDO (STA specialty) - QUIRK REWORKED
        ("Mina Ashido", "Acid", 
         {"Acid Shot": (14, 10, "normal", "Secrete corrosive acid"), 
          "Acidman": (0, 12, "defense_buff", "Cover your body in protective acid, +5 defense for 3 turns")},
         {'hp': 93, 'energy': 49, 'attack': 12, 'defense': 5, 'zone_bonuses': {}, 'zone_penalties': {}},
         {'high': ["Time to show my moves!", 
                   "Let's Dance through the darkness!",
                   "Pinky's ready!"],
          'medium': ["That stings!", "Acid slowing...", "Giving up isn't my style!"],
          'low': ["Everything hurts...", 
                  "D- dehydrated...",
                  "Body's shutting down..."]},
         {'high': "Stay professional. Focus Ashido!", 
          'medium': "You can't do this half-assed!", 
          'low': "You've improved. Never stop improving."}, False),
        
        # 3. ASUI (BAL specialty)
        ("Tsuyu Asui", "Frog", 
         {"Tongue Strike": (13, 9, "normal", "Your tongue shoots out like a whip"), 
          "Camouflage Ambush": (27, 18, "normal", "Blend completely then leap from above")},
         {'hp': 98, 'energy': 46, 'attack': 11, 'defense': 6, 
          'zone_bonuses': {'water': {'attack': 3, 'defense': 2}}, 
          'zone_penalties': {'cold': {'attack': 3, 'defense': 2}}},
         {'high': ["Ribbit. I'll do what needs to be done, no matter what.", 
                   "I won't let anyone down. I'll give this everything I have, ribbit.", 
                   "My classmates are counting on me. I can't afford to fail, ribbit."],
          'medium': ["It hurts, ribbit... but I can endure this. I have to.", 
                     "I'm slowing down... but I won't stop, ribbit. Not yet.", 
                     "The pain doesn't matter, ribbit... what matters is finishing this."],
          'low': ["I'll keep going... so long as I'm still conscious, ribbit... I'll... keep...", 
                  "Can't... give up... ribbit... even if my body won't listen anymore...", 
                  "Everyone... I'm sorry, ribbit... but I tried... I really tried..."]},
         {'high': "Nothing to worry about.", 
          'medium': "Focus on fixing your mistakes, not dwelling on them.", 
          'low': "She won't stop until she's dead, will she?"}, False),
        
        # 4. IIDA (EVA specialty - UPDATED from VIT)
        ("Tenya Iida", "Engine", 
         {"Recipro Burst": (22, 15, "normal", "Your leg engines roar to life"), 
          "Recipro Extend": (38, 28, "normal", "Push your engines beyond their limits")},
         {'hp': 95, 'energy': 48, 'attack': 13, 'defense': 6, 'zone_bonuses': {}, 'zone_penalties': {}},
         {'high': ["As class representative, I shall lead!", "Full speed ahead!", "I'm ready!"],
          'medium': ["Engines overheating...", "I must persevere!", 
                     "They're still a lap ahead of me..."],
          'low': ["I can barely stand...", "Engines stalled...", "Forgive me..."]},
         {'high': "Motivated as ever I see.", 
          'medium': "Don't rush things. You don't want to burn yourself out.", 
          'low': "You need to focus on yourself, not just your classmates."}, False),
        
        # 5. URARAKA (EVA specialty)
        ("Ochaco Uraraka", "Zero Gravity", 
         {"Float": (10, 8, "normal", "Touch your target and make them weightless"), 
          "Meteor Storm": (28, 18, "normal", "Release multiple floating objects simultaneously")},
         {'hp': 90, 'energy': 50, 'attack': 10, 'defense': 4, 'zone_bonuses': {}, 'zone_penalties': {}},
         {'high': ["I'll do my best!", "For everyone!", "Time to shine!"],
          'medium': ["Getting dizzy...", "I can keep going...", "Push through..."],
          'low': ["Everything's spinning...", "So nauseous...", "Can't... give up..."]},
         {'high': "Take it slow. Don't burden yourself.", 
          'medium': "You're only barely passing. You need to focus Uraraka.", 
          'low': "Make sure this is what you want to do."}, False),
        
        # 6. OJIRO (STR★★ specialty - HIGHLY BOOSTED, UPDATED from HP)
        ("Mashirao Ojiro", "Tail", 
         {"Tail Strike": (14, 9, "normal", "Your tail whips with incredible force"), 
          "Fist of the Tail": (26, 18, "normal", "Spinning tail combo")},
         {'hp': 100, 'energy': 44, 'attack': 12, 'defense': 6, 'zone_bonuses': {}, 'zone_penalties': {}},
         {'high': ["My training prepared me!", 
                   "I'll show them I'm not ordinary!",
                   "Let's show them!"],
          'medium': ["Need to rely on technique...", "Tail's getting heavy...", "Pain is weakness leaving!"],
          'low': ["Can barely lift my tail...", "All my training...", "Can't maintain stance..."]},
         {'high': "Don't push yourself trying to keep up with your classmates. You're far stronger than you realize.", 
          'medium': "His perseverance is unparalleled.", 
          'low': "You've done well. Now finish the job."}, False),
        
        # 7. KAMINARI (STA specialty)
        ("Denki Kaminari", "Electrification", 
         {"Thunder Shock": (16, 11, "normal", "Electricity explodes outward"), 
          "Indiscriminate Shock": (34, 24, "normal", "Release full electrical output")},
         {'hp': 88, 'energy': 52, 'attack': 13, 'defense': 4, 'zone_bonuses': {}, 
          'zone_penalties': {'water': {'attack': 0, 'defense': 2}}},
         {'high': ["Let the electricity flow!", 
                   "Time for shock and awe!",
                   "Let's get electric!"],
          'medium': ["Gotta be careful...", 
                     "Getting dizzy...",
                     "Can't go full power..."],
          'low': ["Brain feels fried...", "Whey...", "Short-circuiting..."]},
         {'high': "I'm too tired for this...", 
          'medium': "Stay focused!", 
          'low': "Can you only focus when your life is on the line?"}, False),
        
        # 8. KIRISHIMA (DEF specialty)
        ("Eijiro Kirishima", "Hardening", 
         {"Red Riot": (12, 10, "normal", "Your skin turns rock-hard"), 
          "Red Riot Unbreakable": (30, 22, "normal", "Your entire body becomes impenetrable")},
         {'hp': 120, 'energy': 40, 'attack': 11, 'defense': 9, 'zone_bonuses': {}, 'zone_penalties': {}},
         {'high': ["Nothing's getting through!", "I'm rock solid!", "Let's do this!"],
          'medium': ["I'm Red Riot! No blood... flows... behind me!",
                     "My hardening is cracking!", "This is where a man shows guts!"],
          'low': ["Can't... harden anymore...", "I'm breaking...", "Not manly at all..."]},
         {'high': "Not a thought in his head is there?", 
          'medium': "Remember, be unbreakable!", 
          'low': "He's pushed himself too far..."}, False),
        
        # 9. KODA (VIT★ specialty - HIGHLY BOOSTED) - ANIMAL AFFINITY
        ("Koji Koda", "Anivoice", 
         {"Animal Swarm": (13, 10, "normal", "Command animals to attack"), 
          "Beast Stampede": (27, 19, "normal", "Summon larger animals")},
         {'hp': 96, 'energy': 50, 'attack': 9, 'defense': 7, 
          'zone_bonuses': {'animal': {'attack': 5, 'defense': 3}},
          'zone_penalties': {}},
         {'high': ["...I can do this.", "...Animals believe in me.", "...Together we're strong."],
          'medium': ["I got into U.A., didn't I?",
                     "...Animals sense weakness...", "...Must stay calm..."],
          'low': ["...Can't speak...", "...I'm sorry...", "...No voice left..."]},
         {'high': "Don't worry. The simulation won't hurt any animals you use.", 
          'medium': "Louder Koda! I want to hear that Plus Ultra spirit!", 
          'low': "So... you'll protect any living thing over your own self..."}, False),
        
        # 10. SATO (STR★★ specialty - HIGHLY BOOSTED)
        ("Rikido Sato", "Sugar Rush", 
         {"Power Punch": (16, 11, "normal", "Sugar-powered superhuman punch"), 
          "Sweet Rampage": (31, 22, "normal", "Multiple sugar cubes power boost")},
         {'hp': 108, 'energy': 43, 'attack': 14, 'defense': 7, 'zone_bonuses': {}, 'zone_penalties': {}},
         {'high': ["Sugared up!", 
                   "Sweet victory!",
                   "Sweet power!"],
          'medium': ["Need more sugar soon...", "Boost is fading...", "One more cube..."],
          'low': ["Sugar crash...", "No sugar left...", "Completely drained..."]},
         {'high': "Make sure you're stocked up before beginning.", 
          'medium': "Just because you're strong doesn't mean you can tank everything. Fight smarter, not harder.", 
          'low': "You can't be a hero if you're dead. Know when to tap out and learn from it."}, False),
        
        # 11. SHOJI (DEF specialty)
        ("Shoji Mezo", "Dupli-Arms", 
         {"Multi-Strike": (15, 10, "normal", "Multiple arms strike from different angles"), 
          "Octoblow": (29, 20, "normal", "Eight arms unleash devastating blows")},
         {'hp': 115, 'energy': 42, 'attack': 12, 'defense': 8, 'zone_bonuses': {}, 'zone_penalties': {}},
         {'high': ["My arms are ready.", "I can sense everything.", "We'll be fine."],
          'medium': ["Still can fight...", 
                     "Must protect the others...",
                     "Reaching my limit..."],
          'low': ["Limbs won't respond...", "Can't duplicate...", "Too weak..."]},
         {'high': "Remain rational and you'll be fine.", 
          'medium': "Multiple arms doesn't mean you can carry everyone's burdens. Pace yourself.", 
          'low': "Putting your body on the line without a plan isn't heroic. Pull it together."}, False),
        
        # 12. JIRO (DEF specialty - UPDATED from EVA) - QUIRK REWORKED
        ("Kyoka Jiro", "Earphone Jack", 
         {"Heartbeat Fuzz": (13, 9, "normal", "Send destructive sound waves"), 
          "Amplifier Jack": (0, 15, "defense_debuff", "Unleash a sonic boom that reduces enemy defense by 3 for rest of combat")},
         {'hp': 87, 'energy': 50, 'attack': 11, 'defense': 4, 'zone_bonuses': {}, 'zone_penalties': {}},
         {'high': ["Let's rock this!", "Turn up the volume!", "My heartbeat's steady!"],
          'medium': ["Ears are ringing...", 
                     "The Feedback is painful...",
                     "This is somehow that shock jock's fault."],
          'low': ["Can't hear...", 
                  "My eardrums...",
                  "Deaf to everything..."]},
         {'high': "What exactly did you say to Present Mic to get him so amped up?", 
          'medium': "Don't try to do too much. Focus on what you're good at.", 
          'low': "Even support specialists need to be able to hold their own."}, False),
        
        # 13. SERO (BAL★ specialty - HIGHLY BOOSTED) - QUIRK REWORKED
        ("Hanta Sero", "Tape", 
         {"Tape Shot": (11, 8, "normal", "Fire strong tape from elbows"), 
          "Tape Trap": (0, 16, "attack_debuff", "Create a web of tape that reduces enemy attack by 4")},
         {'hp': 94, 'energy': 47, 'attack': 10, 'defense': 5, 'zone_bonuses': {}, 'zone_penalties': {}},
         {'high': ["Cellophane is ready!", 
                   "Let's wrap this up!",
                   "Let's stick together!"],
          'medium': ["Running low on tape...", "Elbows are sore...", "Need to conserve..."],
          'low': ["Elbows are killing me...", 
                  "This is my coffin, huh?",
                  "Can't shoot anymore..."]},
         {'high': "Don't worry about the others. Your pace is more than enough.", 
          'medium': "You're doing good Sero. Conserve your quirk as much as you can.", 
          'low': "Stick to your plan, even if you're running on empty."}, False),
        
        # 14. TOKOYAMI (EVA specialty)
        ("Fumikage Tokoyami", "Dark Shadow", 
         {"Shadow Strike": (17, 10, "normal", "Dark Shadow lunges forward"), 
          "Black Abyss": (33, 23, "normal", "Release Dark Shadow's full power")},
         {'hp': 92, 'energy': 48, 'attack': 12, 'defense': 5, 
          'zone_bonuses': {'dark': {'attack': 4, 'defense': 2}}, 
          'zone_penalties': {'bright': {'attack': 3, 'defense': 1}}},
         {'high': ["Come! Dark Shadow!",
                   "Revelry in the dark!", 
                   "We are unflappable."],
          'medium': ["Dark Shadow grows restless...", "The light weakens us...", "Stay with me!"],
          'low': ["Can't... control...", "Darkness consumes...", "Losing myself..."]},
         {'high': "Let's see.", 
          'medium': "Don't doubt yourself. Remain focused.", 
          'low': "I'd better get Erasure ready..."}, False),
        
        # 15. TODOROKI (DEF specialty)
        ("Shoto Todoroki", "Half-Cold Half-Hot", 
         {"Ice Wall": (15, 10, "normal", "Slam your right hand down, erupting a massive glacier"), 
          "Flashfreeze Heatwave": (32, 22, "normal", "Unleash both sides of your quirk simultaneously")},
         {'hp': 105, 'energy': 55, 'attack': 14, 'defense': 7, 
          'zone_bonuses': {'cold': {'attack': 2, 'defense': 2}, 'hot': {'attack': 2, 'defense': 2}}, 
          'zone_penalties': {}},
         {'high': ["I'll handle this efficiently.", "I'll use both sides of my power.", "This suits my quirk."],
          'medium': ["I need to balance more carefully...", "My temperature is fluctuating.", "I'm overusing one side."],
          'low': ["My control is slipping...", "I can't maintain the balance...", "Too much..."]},
         {'high': "Impulsive as ever.", 
          'medium': "Find your balance.", 
          'low': "You need to manage your quirk usage better."}, False),
        
        # 16. HAGAKURE (EVA★★ specialty - HIGHLY BOOSTED) - QUIRK REWORKED
        ("Toru Hagakure", "Invisibility", 
         {"Sneak Attack": (12, 8, "normal", "Strike from their blind spot"), 
          "Light Refraction": (0, 17, "stun", "Create a blinding flash that stuns the enemy for 1 turn")},
         {'hp': 82, 'energy': 48, 'attack': 10, 'defense': 3, 
          'zone_bonuses': {'bright': {'attack': 3, 'defense': 1}}, 
          'zone_penalties': {'dark': {'attack': 2, 'defense': 0}}},
         {'high': ["They'll never saw it coming!",
                   "Invisible Girl ready!", 
                   "Say cheese!"],
          'medium': ["Even invisible, their shots aren't missing...",
                     "They can't see me struggling!", 
                     "Can't be so transparent."],
          'low': ["So tired...", 
                  "If I die here... they'll never find me...",
                  "No one can see me to help..."]},
         {'high': "Don't try to do too much. Focus on your strengths.", 
          'medium': "Avoiding conflict is an acceptable strategy.", 
          'low': "You're never alone. We see you Hagakure."}, False),
        
        # 17. BAKUGO (STR specialty)
        ("Katsuki Bakugo", "Explosion", 
         {"AP Shot": (18, 10, "normal", "Concentrate an explosion into a single piercing blast"), 
          "Howitzer Impact": (35, 25, "normal", "Spin rapidly while releasing massive explosions")},
         {'hp': 110, 'energy': 45, 'attack': 15, 'defense': 6, 
          'zone_bonuses': {'hot': {'attack': 3, 'defense': 2}}, 
          'zone_penalties': {'cold': {'attack': 3, 'defense': 1}, 'water': {'attack': 2, 'defense': 0}}},
         {'high': ["Out of my way, extras! I'll blast through every single one!", "I'm gonna be number one!", 
                   "GET WRECKED VILLAINS!"],
          'medium': ["Tch... I'm not done yet!", "These injuries won't slow me down!", "I need to save my explosions..."],
          'low': ["Damn it... my body won't move...", "I can't... fall here...", 
                  "Don't let me surpass you... Izuku..."]},
         {'high': "Try to keep property damage to a minimum.", 
          'medium': "Pace yourself. You're not invincible.", 
          'low': "Even he has his limits."}, False),
        
        # 18. MIDORIYA (BAL specialty - UPDATED)
        ("Izuku Midoriya", "One For All", 
         {"Detroit Smash": (20, 12, "normal", "Channel One For All through your fist for a devastating punch"), 
          "Full Cowling": (40, 30, "normal", "Distribute One For All's power throughout your entire body")},
         {'hp': 100, 'energy': 50, 'attack': 12, 'defense': 5, 'zone_bonuses': {}, 'zone_penalties': {}},
         {'high': ["I'll give it everything I've got! Plus Ultra!", "I've been analyzing everyone's strategies. I'm ready!", 
                   "I'll save everyone, with a smile on my face! Just like All Might!"],
          'medium': ["I need to be more careful with my quirk usage...", "My body's taking damage, but I can't stop now!", 
                     "I have to think smarter, not just hit harder..."],
          'low': ["I can barely move... but I can't give up now!", "Everyone's counting on me... I have to keep going!", 
                  "My arms... my legs... but heroes don't quit!"]},
         {'high': "It's time to earn my trust problem child.", 
          'medium': "Don't do too much on your own Midoriya.", 
          'low': "This kid..."}, False),
        
        # 19. MINETA (EVA★★ specialty - HIGHLY BOOSTED) - QUIRK REWORKED
        ("Minoru Mineta", "Pop Off", 
         {"Sticky Spheres": (0, 5, "evasion_debuff", "Throw sticky balls that reduce enemy evasion to 0, costs 5 HP"),
          "Grape Rush": (23, 16, "normal", "Barrage of sticky spheres")},
         {'hp': 80, 'energy': 48, 'attack': 8, 'defense': 4, 'zone_bonuses': {}, 'zone_penalties': {}},
         {'high': ["Time for the Freshly Picked hero to shine ladies!",
                   "Eat my sticky balls!",
                   "They'll get stuck!"],
          'medium': ["Head's getting sore!", "Running out of balls!", "Ow ow ow!"],
          'low': ["I just wanted to be popular...",
                  "My head hurts...", "I wanna go home..."]},
         {'high': "There are no female combatants. Stay focused.", 
          'medium': "Don't ask if you can. Say you will.", 
          'low': "This kid still has more fight in him..."}, False),
        
        # 20. YAOYOROZU (STA specialty)
        ("Momo Yaoyorozu", "Creation", 
         {"Tactical Creation": (14, 12, "normal", "Create weapons from your lipids"), 
          "Advanced Arsenal": (26, 20, "normal", "Manifest complex equipment")},
         {'hp': 85, 'energy': 60, 'attack': 11, 'defense': 5, 'zone_bonuses': {}, 'zone_penalties': {}},
         {'high': ["I've studied the strategies.", "My preparations are ready.", "I've calculated the approach."],
          'medium': ["Need to think carefully...", "Lipids depleting...", "Focus, Momo!"],
          'low': ["Too exhausted to create...", 
                  "Always... falling... behind...",
                  "Can't think..."]},
         {'high': "Show me what you've learnt!", 
          'medium': "You're better than this Yaoyorozu!", 
          'low': "I'd like to help boost her confidence... but she's got to do this on her own."}, False),
        
        # 21. SHINSO (STA specialty - HIDDEN) - QUIRK REWORKED
        ("Hitoshi Shinso", "Brainwashing", 
         {"Mind Control": (0, 12, "stun", "Take control of their mind, stunning them for 2 turns"),
          "Psychic Domination": (28, 22, "normal", "Assert mental dominance")},
         {'hp': 88, 'energy': 55, 'attack': 11, 'defense': 5, 'zone_bonuses': {}, 'zone_penalties': {}},
         {'high': ["I'll prove I belong.", "My quirk isn't villainous.", 
                   "Persona Chords calibrated!"],
          'medium': ["Can't let my guard down...", "Need them to respond...", "Not giving up."],
          'low': ["Why do I struggle...", 
                  "Maybe they were right about me...",
                  "I can't..."]},
         {'high': "Let's see if you're ready to transfer to the Hero Course.", 
          'medium': "It took me eight years to learn how to use my binding cloth. Don't rush yourself, you're not behind.", 
          'low': "Nobody's asking that much of you."}, True),
    ]
    
    for data in class_data:
        characters.append(Character(data[0], data[1], data[2], data[3], data[4], data[5], data[6]))
    
    return characters

def get_character_specialty(character_name):
    """Returns display specialty for character select screen - UPDATED"""
    specialties = {
        'Rikido Sato': 'STR★★', 'Mashirao Ojiro': 'STR★★',
        'Toru Hagakure': 'EVA★★', 'Minoru Mineta': 'EVA★★',
        'Hanta Sero': 'BAL★', 'Yuga Aoyama': 'BAL★', 'Koji Koda': 'VIT★',
        'Katsuki Bakugo': 'STR', 'Izuku Midoriya': 'BAL',
        'Eijiro Kirishima': 'DEF', 'Shoji Mezo': 'DEF', 'Shoto Todoroki': 'DEF',
        'Tenya Iida': 'EVA', 'Ochaco Uraraka': 'EVA',
        'Mina Ashido': 'STA', 'Momo Yaoyorozu': 'STA', 'Denki Kaminari': 'STA',
        'Fumikage Tokoyami': 'EVA', 'Kyoka Jiro': 'DEF',
        'Tsuyu Asui': 'BAL',
        'Hitoshi Shinso': 'STA'
    }
    return specialties.get(character_name, "")

def get_zone_environmental_type(theme):
    """Map zone theme to environmental type for character bonuses/penalties
    Returns a list of types since some zones can have multiple (e.g., forest has animals)"""
    mapping = {
        'forest': ['normal', 'animal'],  # Forest has animals
        'industrial': ['normal'],
        'flashfire': ['hot'],
        'lake': ['water', 'animal'],  # Lake has aquatic animals
        'blizzard': ['cold'],
        'urban': ['bright'],
        'facility': ['bright'],
        'flooded': ['water'],
        'mountain': ['bright', 'animal'],  # Mountain has animals
        'desert': ['bright'],
        'ruins': ['normal'],
        'underground': ['dark', 'animal'],  # Underground has bats, creatures
    }
    return mapping.get(theme, ['normal'])

def get_zone_themes():
    """Returns list of all zone themes"""
    return [
        'forest', 'industrial', 'flashfire', 'lake', 'blizzard', 'urban', 
        'facility', 'flooded', 'mountain', 'desert', 'ruins', 'underground'
    ]

def get_zone_theme(zone_number, previous_theme):
    """Select a theme for the zone, ensuring no consecutive repeats"""
    themes = get_zone_themes()
    available = [t for t in themes if t != previous_theme]
    return random.choice(available)

def get_zone_description(theme, zone_number):
    """Get detailed zone description based on theme - 2 variants per theme"""
    descriptions = {
        'forest': [
            f"You enter Zone {zone_number}, a dense forest simulation. Towering holographic trees cast flickering shadows across the training ground. The scent of artificial pine fills the air as rustling leaves create an eerie ambiance. Vines hang from branches like snares, and the uneven terrain is littered with fallen logs and tangled roots.",
            f"Zone {zone_number} materializes as a thick woodland environment. Ancient oaks and twisted maples form a canopy overhead, their holographic leaves filtering the harsh training lights into dappled patterns. The forest floor is carpeted with moss and ferns, hiding potential hazards beneath its verdant surface.",
        ],
        'industrial': [
            f"Zone {zone_number} transforms into an abandoned industrial complex. Rusted catwalks crisscross overhead, and the air tastes of metal and oil. Conveyor belts lie silent, and shadows pool in corners between dormant machinery. The echoing drip of condensation marks time in this mechanical graveyard.",
            f"You step into Zone {zone_number}, a sprawling factory simulation. Assembly lines stretch into darkness, their robotic arms frozen mid-motion. Steam hisses from broken pipes, and the floor is slick with synthetic coolant. Warning lights flash yellow across vacant workstations.",
        ],
        'flashfire': [
            f"Zone {zone_number} erupts into existence as an infernal flashfire zone. Walls of flame surge and recede in waves, leaving scorched earth in their wake. The air shimmers with intense heat, and the acrid smell of smoke fills your lungs. Embers dance through the air like fireflies of destruction.",
            f"You enter Zone {zone_number}, transformed into a raging firestorm environment. Controlled burns sweep across the landscape in patterns, creating corridors of flame. The temperature climbs dangerously high as fire consumes everything in its path, only to reset and burn again.",
        ],
        'lake': [
            f"Zone {zone_number} manifests as a vast lake environment. Crystal-clear water stretches to the horizon, its surface broken by jutting rock formations and wooden platforms. The air is humid and carries the scent of fresh water. Underwater currents create swirling patterns beneath the surface.",
            f"You step into Zone {zone_number}, a flooded lake simulation. A network of docks and floating platforms provides precarious footing over deep blue water. Lily pads cluster near the shore, and the gentle lap of waves against wood creates a deceptively peaceful atmosphere.",
        ],
        'blizzard': [
            f"Zone {zone_number} transforms into a frozen tundra. Biting winds howl across ice-covered terrain, and snow falls in blinding sheets. Your breath freezes in the air as you navigate between towering ice formations and frozen pillars. The temperature plummets to dangerous levels.",
            f"You enter Zone {zone_number}, a blizzard-ravaged landscape. White blankets everything, making it difficult to distinguish ground from sky. Ice crunches beneath your feet, and the cold cuts through your hero costume like knives. The wind screams across the frozen expanse.",
        ],
        'urban': [
            f"Zone {zone_number} materializes as an urban battleground. Damaged skyscrapers loom overhead, their windows shattered and walls cracked. Abandoned cars litter streets filled with rubble. Flickering streetlights cast long shadows down empty alleys.",
            f"You step into Zone {zone_number}, a devastated city simulation. High-rise buildings lean at dangerous angles, their foundations compromised. The concrete jungle is a maze of collapsed overpasses and blocked intersections. Smoke rises from ruined buildings.",
        ],
        'facility': [
            f"Zone {zone_number} appears as a high-tech research facility. Sterile white corridors stretch in every direction, lit by flickering fluorescent lights. Computer terminals line the walls, their screens displaying corrupted data. The air conditioning hums ominously overhead.",
            f"You enter Zone {zone_number}, transformed into a villainous laboratory. Experimental equipment clutters workstations, and mysterious chemicals bubble in beakers. Warning signs mark doors that lead to unknown dangers. The metallic smell of ozone fills the air.",
        ],
        'flooded': [
            f"Zone {zone_number} manifests as a flooded urban area. Water rises to waist height in what was once a city street. Submerged cars create obstacles, and furniture floats past from broken windows. The water is murky and conceals what lies beneath its surface.",
            f"You step into Zone {zone_number}, a disaster-flooded simulation. Buildings stand half-submerged, their lower floors completely underwater. Makeshift platforms provide the only dry ground in a drowned cityscape. Swift currents make movement treacherous.",
        ],
        'mountain': [
            f"Zone {zone_number} transforms into a treacherous mountain range. Narrow paths wind along cliff faces, and loose rocks skitter into abysses with every step. The air grows thin as elevation increases, and snow caps distant peaks that pierce the simulated sky.",
            f"You enter Zone {zone_number}, a mountainous terrain simulation. Steep inclines test your endurance as you climb between rocky outcroppings. Deep crevasses split the path, requiring careful navigation. The ground is uneven and treacherous.",
        ],
        'desert': [
            f"Zone {zone_number} manifests as an arid desert wasteland. Scorching heat radiates from golden sand dunes that stretch endlessly in all directions. The sun beats down mercilessly, and mirages shimmer in the distance. Wind whips sand into stinging clouds.",
            f"You step into Zone {zone_number}, a harsh desert simulation. Rocky mesas rise from seas of sand, and the dry air cracks your lips. Sandstorms blur the horizon, and the temperature climbs to dangerous levels. Heat waves distort your vision.",
        ],
        'ruins': [
            f"Zone {zone_number} appears as ancient ruins reclaimed by nature. Crumbling stone structures are overgrown with vines and moss. Collapsed pillars and broken statues create a maze of historical debris. The air is thick with the scent of decay and age.",
            f"You enter Zone {zone_number}, transformed into forgotten ruins. Weathered stone walls are covered in mysterious symbols, and broken stairs lead to partially collapsed chambers. Vegetation pushes through cracks in the ancient masonry, reclaiming what was once grand.",
        ],
        'underground': [
            f"Zone {zone_number} manifests as a deep underground cavern system. Stalactites hang from the ceiling like stone fangs, and the sound of dripping water echoes endlessly through the darkness. Bioluminescent fungi provide eerie illumination in the depths.",
            f"You step into Zone {zone_number}, a subterranean tunnel network. Rough-hewn passages split off in multiple directions, and the air is cool and damp. Underground rivers rush through channels carved in the rock. The silence is oppressive, broken only by distant water sounds.",
        ]
    }
    
    return random.choice(descriptions.get(theme, [f"You enter Zone {zone_number}."]))

def get_room_description(theme, floor):
    """Get detailed room description for exploration - 5 variants per theme"""
    rooms = {
        'forest': [
            "You stand in a small clearing surrounded by dense undergrowth. Sunlight filters through the canopy in thin beams.",
            "A narrow path winds between ancient trees. Branches creak overhead.",
            "You find yourself at the base of a massive oak tree. Mushrooms cluster around the exposed roots.",
            "The forest opens into a glade where wildflowers grow in patches of sunlight.",
            "Dense ferns carpet this section of forest. Visibility is limited.",
        ],
        'industrial': [
            "You enter a maintenance corridor lined with pipes and electrical conduits.",
            "The room is dominated by a massive piece of machinery, now silent. Hydraulic fluid pools on the floor.",
            "A storage area filled with metal shelving units. Most shelves are empty.",
            "You step onto a suspended catwalk overlooking the factory floor.",
            "A former break room. Overturned chairs surround dusty tables.",
        ],
        'flashfire': [
            "You stand in a charred clearing where flames have just passed. The ground radiates heat.",
            "A wall of fire burns steadily ahead, its intense heat pushing you back.",
            "You navigate between flame jets that erupt from the ground in timed patterns.",
            "A relatively cooler area provides brief respite, though smoke still fills the air.",
            "You cross scorched earth, embers still glowing beneath the blackened surface.",
        ],
        'lake': [
            "You stand on a floating wooden platform that rocks gently.",
            "A dock extends from the shore, partially collapsed and unstable.",
            "You wade through shallow water near the shore. The bottom is rocky.",
            "A small island rises from the lake, barely large enough to stand on.",
            "You swim in the open water, treading to stay afloat.",
        ],
        'blizzard': [
            "You push through knee-deep snow, each step an effort.",
            "A wall of ice blocks part of your path. Its surface is slick.",
            "You take shelter behind a snow drift.",
            "The ground here is solid ice. Movement is dangerous.",
            "You navigate between tall ice formations that groan ominously.",
        ],
        'urban': [
            "You stand in a debris-filled street. Broken glass crunches underfoot.",
            "A partially collapsed building looms beside you.",
            "You navigate through a narrow alley between high-rises.",
            "An intersection opens before you, streets branching in four directions.",
            "You climb over the wreckage of a collapsed overpass.",
        ],
        'facility': [
            "A sterile corridor stretches before you, lined with hazard-warning doors.",
            "You enter what appears to be a control room. Monitors display static.",
            "A laboratory workspace cluttered with beakers and scientific equipment.",
            "The hallway opens into a server room. Equipment hums with power.",
            "You stand in a decontamination chamber. Nozzles line the walls.",
        ],
        'flooded': [
            "You wade through waist-deep water in a former shopping district.",
            "A partially submerged car creates an obstacle.",
            "You climb onto a sunken vehicle's roof to get above water.",
            "The water here is deeper, forcing you to swim.",
            "You navigate around floating debris slowly drifting.",
        ],
        'mountain': [
            "A narrow ledge provides precarious footing along the cliff face.",
            "You scramble over loose scree on a steep slope.",
            "A plateau offers relatively level ground at this elevation.",
            "You navigate around a massive boulder blocking the path.",
            "An ice-covered section of trail requires extreme caution.",
        ],
        'desert': [
            "You stand atop a sand dune, surveying the endless desert.",
            "A rocky outcropping provides minimal shade.",
            "You trudge through loose sand that shifts beneath every step.",
            "A cluster of cacti rises from the desert floor.",
            "Ancient weathered stones poke from the sand.",
        ],
        'ruins': [
            "You stand in what was once a grand hall. Broken pillars line the walls.",
            "A collapsed archway partially blocks your path. Vines grow through rubble.",
            "You navigate through a maze of half-walls and foundations.",
            "A stone staircase leads upward, but steps are missing.",
            "You enter a chamber where ancient frescoes still cling to walls.",
        ],
        'underground': [
            "You stand in a vast cavern where your voice echoes endlessly.",
            "A narrow passage forces you to crouch.",
            "You find yourself beside an underground pool. The water is perfectly still.",
            "A junction of three tunnels presents a choice.",
            "You walk along the edge of an underground chasm.",
        ]
    }
    
    return random.choice(rooms.get(theme, ["You find yourself in a nondescript area."]))

def get_points_of_interest(theme):
    """Get points of interest for investigation - civilians are hidden in logical places"""
    pois = {
        'forest': [
            ("a hollow tree trunk", ["Health Potion", "Energy Drink", None, "ambush"]),
            ("a patch of disturbed earth", ["Health Potion", None, "secret_path"]),
            ("thick vines covering something", ["Energy Drink", "Health Potion", "ambush", "civilian"]),  # Can hide person
            ("a collapsed shelter", ["Health Potion", "civilian", None]),  # Can hide person
        ],
        'industrial': [
            ("a locked supply cabinet", ["Health Potion", "Energy Drink"]),
            ("a maintenance access panel", ["Energy Drink", "secret_path", None]),
            ("a pile of discarded equipment", ["Health Potion", "ambush"]),
            ("a sealed storage container", ["Health Potion", "civilian", None]),  # Can hide person
        ],
        'flashfire': [
            ("a crack in the scorched earth", ["Health Potion", "secret_path"]),
            ("heat-resistant debris", ["Energy Drink", "Health Potion"]),
            ("a suspicious flame pattern", ["ambush", "secret_path", None]),
            ("a reinforced shelter", ["Energy Drink", "civilian", None]),  # Can hide person
        ],
        'lake': [
            ("something floating in the water", ["Health Potion", "Energy Drink"]),
            ("a submerged crate", ["Health Potion", "secret_path"]),
            ("ripples on the surface", ["ambush", None]),
            ("an emergency life raft", ["Energy Drink", "civilian", None]),  # Can hide person
        ],
        'blizzard': [
            ("a snow-covered mound", ["Health Potion", "ambush"]),
            ("footprints in the snow", ["secret_path", "ambush"]),
            ("a frozen supply cache", ["Health Potion", "Energy Drink"]),
            ("an emergency shelter", ["Health Potion", "civilian", None]),  # Can hide person
        ],
        'urban': [
            ("an abandoned briefcase", ["Health Potion", "Energy Drink"]),
            ("a partially open manhole", ["secret_path", "ambush"]),
            ("a dented locker", ["Health Potion", None]),
            ("a collapsed building alcove", ["Energy Drink", "civilian", "ambush"]),  # Can hide person
        ],
        'facility': [
            ("a sealed biohazard container", ["Health Potion", "Energy Drink"]),
            ("a computer terminal", ["secret_path", "Energy Drink"]),
            ("a ventilation duct grate", ["secret_path", "ambush"]),
            ("a sealed panic room", ["Health Potion", "civilian", None]),  # Can hide person
        ],
        'flooded': [
            ("floating debris", ["Health Potion", None]),
            ("an air pocket in a building", ["Energy Drink", "secret_path", "civilian"]),  # Can hide person
            ("debris piled against a doorway", ["Health Potion", "ambush"]),
            ("an elevated platform", ["Energy Drink", "civilian", None]),  # Can hide person
        ],
        'mountain': [
            ("a cairn marking something", ["secret_path", "Health Potion"]),
            ("a mountain goat path", ["secret_path", None]),
            ("a wind-carved hollow", ["Energy Drink", "ambush"]),
            ("a mountaineer's cache", ["Health Potion", "civilian", None]),  # Can hide person
        ],
        'desert': [
            ("something half-buried in sand", ["Health Potion", "Energy Drink"]),
            ("a scorpion burrow", ["ambush", None]),
            ("a weathered supply crate", ["Health Potion", "Energy Drink"]),
            ("a covered dugout", ["Energy Drink", "civilian", None]),  # Can hide person
        ],
        'ruins': [
            ("a collapsed wall revealing a passage", ["secret_path", None]),
            ("an intact pottery vessel", ["Energy Drink", "Health Potion"]),
            ("ancient writing on the wall", ["secret_path", "ambush"]),
            ("a hidden chamber", ["Health Potion", "civilian", None]),  # Can hide person
        ],
        'underground': [
            ("a side tunnel barely visible", ["secret_path", "ambush"]),
            ("glowing mushrooms", ["Energy Drink", None]),
            ("a hollow stalagmite", ["Health Potion", "secret_path"]),
            ("a natural alcove", ["Energy Drink", "civilian", None]),  # Can hide person
        ]
    }
    
    available = pois.get(theme, [("something interesting", ["Health Potion"])])
    num_pois = random.randint(1, 3)
    return random.sample(available, min(num_pois, len(available)))

def investigate_poi(character, poi_desc, outcomes, theme):
    """Handle point of interest investigation - includes civilian rescues"""
    print(f"\nYou investigate {poi_desc}...")
    time.sleep(0.3)
    
    secret_chance = 20 + character.secret_detection
    item_chance = 60 + character.item_find_bonus
    
    outcome = random.choice(outcomes)
    
    if outcome == "civilian":
        # CIVILIAN RESCUE - Large EXP reward
        civilian_names = ["a scientist", "a worker", "a maintenance tech", "a researcher", "a security guard", "a janitor"]
        civilian = random.choice(civilian_names)
        exp_reward = random.randint(150, 250)
        
        print(f"\nYou found {civilian} trapped here!")
        print(f"You quickly help them to safety.")
        print(f"\n[Civilian]: \"Thank you! You're a real hero!\"")
        character.gain_exp(exp_reward)
        print(f"Gained {exp_reward} EXP for the rescue!")
        
    elif outcome == "secret_path":
        if random.random() * 100 < secret_chance:
            print(f"\nYou discovered a secret path! Hidden cache found!")
            character.inventory.append("Health Potion")
            character.inventory.append("Energy Drink")
            print("Found: Health Potion, Energy Drink")
        else:
            print(f"\nNothing useful here.")
            
    elif outcome == "ambush":
        print(f"\nIt's a trap! An enemy was lying in wait!")
        return "ambush"
        
    elif outcome in ["Health Potion", "Energy Drink"]:
        if random.random() * 100 < item_chance:
            character.inventory.append(outcome)
            print(f"\nYou found: {outcome}!")
        else:
            print(f"\nYou found something, but it's damaged and unusable.")
    else:
        print(f"\nNothing of value here.")
    
    return None

def create_boss(zone_number):
    """Create boss for the zone - REBALANCED with generic early bosses"""
    if zone_number <= 5:
        bosses = [
            ("Villain Thug Leader", "A hardened criminal leading this operation."),
            ("Enhanced Nomu", "A bio-engineered creature with multiple quirks."),
            ("League Enforcer", "A powerful villain enforcer."),
        ]
    elif zone_number <= 15:
        bosses = [
            ("Muscular", "A villainous mountain of augmented muscle fiber."),
            ("Moonfish", "A disturbing figure with razor-sharp teeth."),
            ("Mustard", "A young villain shrouded in toxic gas."),
            ("Magne", "A powerful villain with magnetic abilities."),
            ("Spinner", "A reptilian villain with multiple blades."),
        ]
    else:
        bosses = [
            ("Mr. Compress", "An elegant villain in a theatrical mask."),
            ("Twice", "A villain who creates perfect duplicates."),
            ("Dabi", "A scarred villain with blue flames."),
            ("Himiko Toga", "A girl with a disturbing smile and knives."),
            ("Gigantomachia", "A massive giant of living stone."),
        ]
    
    boss_data = random.choice(bosses)
    level = zone_number + 2
    return BossEnemy(boss_data[0], level, boss_data[1], zone_number)

def create_enemy(zone, floor):
    """Create regular enemy"""
    enemy_types = [
        ("Villain Thug", "A low-level criminal."),
        ("League Recruit", "An eager villain recruit."),
        ("Nomu", "A bio-engineered creature."),
    ]
    
    enemy_type = random.choice(enemy_types)
    level = zone + (floor // 2)
    return Enemy(enemy_type[0], level, enemy_type[1], enemy_type[1])

def apply_global_bonuses(character, global_tree):
    """Apply global skill tree bonuses to character"""
    character.attack = character.base_attack + global_tree.get_attack_bonus()
    character.defense = character.base_defense + global_tree.get_defense_bonus()

def check_rescue_event(characters, zone_start=False):
    """Check for rescue events - COMPLETE SYSTEM"""
    captured = [c for c in characters if c.captured]
    
    # Shinso unlock event - only if no captures
    if not any(c.captured for c in characters):
        if zone_start and random.random() < 0.05:  # 5% chance at zone start
            shinso = next((c for c in characters if c.name == "Hitoshi Shinso"), None)
            if shinso and not shinso.unlocked:
                print("\n" + "="*70)
                print("SPECIAL EVENT!")
                print("="*70)
                print("\n[Aizawa]: \"Since you've made it this far without losing anyone...\"")
                print("[Aizawa]: \"I'm adding another student to your roster.\"")
                print("\nHitoshi Shinso has joined Class 1-A!")
                shinso.unlocked = True
                shinso.hp = shinso.max_hp
                shinso.energy = shinso.max_energy
                input("\nPress Enter to continue...")
                return
    
    # Normal rescue events
    if not captured:
        return
    
    chance = 0.20 if zone_start else 0.35
    
    if random.random() < chance:
        print("\n" + "="*70)
        print("RESCUE EVENT!")
        print("="*70)
        
        if random.random() < 0.60:  # 60% choose rescue
            print("\n[Aizawa]: \"We've located some of your captured classmates.\"")
            print("[Aizawa]: \"Choose who to rescue.\"")
            print()
            
            for i, char in enumerate(captured, 1):
                print(f"{i}. {char.name}")
            
            try:
                choice = int(input("\nRescue who? "))
                if 1 <= choice <= len(captured):
                    rescued = captured[choice - 1]
                    rescued.captured = False
                    rescued.hp = rescued.max_hp // 2
                    rescued.energy = rescued.max_energy // 2
                    rescued.reset_personal_skills()
                    print(f"\n{rescued.name} has been rescued!")
                    print(f"HP: {rescued.hp}/{rescued.max_hp} | Energy: {rescued.energy}/{rescued.max_energy}")
                    print("(Personal skills have been reset)")
            except:
                pass
        else:  # 40% auto rescue
            rescued = random.choice(captured)
            rescued.captured = False
            rescued.hp = rescued.max_hp // 2
            rescued.energy = rescued.max_energy // 2
            rescued.reset_personal_skills()
            print(f"\n[Aizawa]: \"We managed to rescue {rescued.name}.\"")
            print(f"HP: {rescued.hp}/{rescued.max_hp} | Energy: {rescued.energy}/{rescued.max_energy}")
            print("(Personal skills have been reset)")
        
        input("\nPress Enter to continue...")

def select_character(available_characters, global_tree):
    """Character select with UPDATED display showing global bonuses and VIT"""
    print("\n" + "="*70)
    print("SELECT YOUR STUDENT FOR ZONE DEPLOYMENT")
    print("="*70)
    print("\n[Aizawa]: \"Choose who goes in next.\"\n")
    
    # Show global bonuses - UPDATED
    print("CURRENT GLOBAL SKILL BONUSES:")
    print(f"  STR: +{global_tree.get_attack_bonus()} | DEF: +{global_tree.get_defense_bonus()} | VIT: +{global_tree.get_hp_bonus()}")
    print(f"  STA: +{global_tree.get_energy_bonus()} | EVA: +{global_tree.get_evasion_bonus()}%")
    print()
    
    available_list = []
    for i, char in enumerate(available_characters, 1):
        if not char.unlocked:
            continue
            
        specialty = get_character_specialty(char.name)
        specialty_text = f" {specialty}" if specialty else ""
        
        if char.captured:
            # Show CAPTURED instead of removing - UPDATED
            print(f"{i:2}. {'CAPTURED':20} | {'':6} | {'':15}{specialty_text}")
        else:
            status = f"Lv.{char.level}"
            hp_status = f"HP:{char.hp}/{char.max_hp}"
            print(f"{i:2}. {char.name:20} | {status:6} | {hp_status:15}{specialty_text}")
            available_list.append((i, char))
    
    while True:
        try:
            choice = int(input("\nChoose your student: "))
            for num, char in available_list:
                if choice == num:
                    return char
            print("Invalid choice.")
        except ValueError:
            print("Please enter a number.")

def combat(character, enemy, global_tree, is_boss=False, ambush=False):
    """Combat system with REWORKED quirk abilities (stun, buffs, debuffs)"""
    print(f"\n{'='*70}")
    print(f"COMBAT!")
    print(f"{'='*70}")
    
    if is_boss:
        print(f"\nBOSS: {enemy.name} (Level {enemy.level})")
        print(enemy.description)
    else:
        print(f"\n{enemy.name} (Level {enemy.level})")
    
    # Ambush gives first free attack
    if ambush:
        print("\nYou strike first!")
        damage = character.attack + random.randint(-3, 5)
        actual = enemy.take_damage(damage)
        print(f"Dealt {actual} damage!")
    
    input("\nPress Enter to begin combat...")
    
    # Combat status effects - UPDATED for quirk reworks
    enemy_stunned = 0
    player_defense_buff = 0
    player_defense_buff_turns = 0
    enemy_defense_debuff = 0
    enemy_attack_debuff = 0
    
    while character.hp > 0 and enemy.hp > 0:
        print(f"\n{character.name} HP: {character.hp}/{character.max_hp} | Energy: {character.energy}/{character.max_energy}")
        print(f"{enemy.name} HP: {enemy.hp}/{enemy.max_hp}")
        
        if enemy_stunned > 0:
            print(f"Enemy is STUNNED for {enemy_stunned} more turns!")
        if player_defense_buff_turns > 0:
            print(f"Defense +{player_defense_buff} for {player_defense_buff_turns} more turns!")
        if enemy_defense_debuff > 0:
            print(f"Enemy Defense -{enemy_defense_debuff}!")
        if enemy_attack_debuff > 0:
            print(f"Enemy Attack -{enemy_attack_debuff}!")
        
        print("\n1. Attack  2. Quirk  3. Item  4. Skills  5. Run")
        
        choice = input("Action: ")
        
        if choice == "1":
            damage = character.attack + random.randint(-3, 5)
            actual = enemy.take_damage(damage)
            print(f"\nDealt {actual} damage!")
            
        elif choice == "2":
            abilities = list(character.abilities.items())
            for i, (name, (dmg, cost, ability_type, desc)) in enumerate(abilities, 1):
                if ability_type == "evasion_debuff":
                    print(f"{i}. {name} ({cost} HP) - {desc}")
                else:
                    print(f"{i}. {name} ({cost} energy) - {desc}")
            try:
                ab_choice = int(input("Use: ")) - 1
                if 0 <= ab_choice < len(abilities):
                    name, (dmg, cost, ability_type, desc) = abilities[ab_choice]
                    
                    # MINETA - Sticky Spheres (costs HP, removes enemy evasion)
                    if ability_type == "evasion_debuff":
                        if character.hp > cost:
                            character.hp -= cost
                            enemy.evasion = 0
                            print(f"\n{name}! Enemy evasion reduced to 0! (Cost: {cost} HP)")
                        else:
                            print("Not enough HP!")
                            continue
                    
                    # ASHIDO - Acidman (defense buff)
                    elif ability_type == "defense_buff":
                        if character.energy >= cost:
                            character.energy -= cost
                            player_defense_buff = 5
                            player_defense_buff_turns = 3
                            character.defense += player_defense_buff
                            print(f"\n{name}! Defense increased by {player_defense_buff} for 3 turns!")
                        else:
                            print("Not enough energy!")
                            continue
                    
                    # JIRO - Amplifier Jack (defense debuff)
                    elif ability_type == "defense_debuff":
                        if character.energy >= cost:
                            character.energy -= cost
                            enemy_defense_debuff = 3
                            enemy.defense = max(0, enemy.defense - 3)
                            print(f"\n{name}! Enemy defense reduced by 3!")
                        else:
                            print("Not enough energy!")
                            continue
                    
                    # SERO - Tape Trap (attack debuff)
                    elif ability_type == "attack_debuff":
                        if character.energy >= cost:
                            character.energy -= cost
                            enemy_attack_debuff = 4
                            enemy.attack = max(1, enemy.attack - 4)
                            print(f"\n{name}! Enemy attack reduced by 4!")
                        else:
                            print("Not enough energy!")
                            continue
                    
                    # HAGAKURE / SHINSO - Stun
                    elif ability_type == "stun":
                        if character.energy >= cost:
                            character.energy -= cost
                            stun_duration = 2 if "Mind Control" in name else 1
                            enemy_stunned = stun_duration
                            print(f"\n{name}! Enemy stunned for {stun_duration} turns!")
                        else:
                            print("Not enough energy!")
                            continue
                    
                    # Normal damage ability
                    else:
                        if character.energy >= cost:
                            character.energy -= cost
                            actual = enemy.take_damage(dmg + character.attack)
                            print(f"\n{name}! Dealt {actual} damage!")
                        else:
                            print("Not enough energy!")
                            continue
            except:
                continue
                
        elif choice == "3":
            if character.inventory:
                for i, item in enumerate(character.inventory, 1):
                    print(f"{i}. {item}")
                try:
                    item_choice = int(input("Use: ")) - 1
                    if 0 <= item_choice < len(character.inventory):
                        item = character.inventory.pop(item_choice)
                        if "Potion" in item:
                            character.heal(40)
                            print("Restored 40 HP!")
                        elif "Energy" in item or "Drink" in item:
                            character.restore_energy(30)
                            print("Restored 30 energy!")
                except:
                    continue
            else:
                print("No items!")
                continue
                
        elif choice == "4":
            # Skill tree access during combat
            skill_tree_menu(character, global_tree)
            apply_global_bonuses(character, global_tree)
            continue
                
        elif choice == "5":
            print("\nYou can't run from this fight!")
            continue
        
        # Enemy turn
        if enemy.hp > 0:
            if enemy_stunned > 0:
                print(f"\n{enemy.name} is stunned and can't attack!")
                enemy_stunned -= 1
            else:
                # Check evasion
                total_evasion = character.evasion + global_tree.get_evasion_bonus()
                if random.random() * 100 < total_evasion:
                    print(f"\n{character.name} evaded the attack!")
                else:
                    damage = enemy.attack + random.randint(-2, 4)
                    actual = character.take_damage(damage)
                    print(f"\nTook {actual} damage from {enemy.name}!")
        
        # Decay buffs/debuffs
        if player_defense_buff_turns > 0:
            player_defense_buff_turns -= 1
            if player_defense_buff_turns == 0:
                character.defense -= player_defense_buff
                player_defense_buff = 0
                print("\nDefense buff wore off!")
    
    if character.hp > 0:
        print(f"\nVictory!")
        character.gain_exp(enemy.exp_reward)
        
        # Random item drop
        if random.random() < 0.3:
            item = random.choice(["Health Potion", "Energy Drink"])
            character.inventory.append(item)
            print(f"Found: {item}")
        
        return True
    else:
        print(f"\nDefeated...")
        return False

def generate_zone_map():
    """Generate a 5-room map with cardinal directions
    Returns: dict with room connections and boss room location"""
    
    # Possible 5-room layouts - ALL GUARANTEE ACCESS TO BOSS ROOM
    layouts = [
        # Linear: N-N-N-N
        {
            'start': 1,
            'rooms': {
                1: {'north': 2, 'south': None, 'east': None, 'west': None, 'desc': 'entrance'},
                2: {'north': 3, 'south': 1, 'east': None, 'west': None, 'desc': 'corridor'},
                3: {'north': 4, 'south': 2, 'east': None, 'west': None, 'desc': 'chamber'},
                4: {'north': 5, 'south': 3, 'east': None, 'west': None, 'desc': 'passage'},
                5: {'north': None, 'south': 4, 'east': None, 'west': None, 'desc': 'boss room'},
            },
            'boss_room': 5
        },
        # T-shape: Start-N-Junction, then E and W
        {
            'start': 1,
            'rooms': {
                1: {'north': 2, 'south': None, 'east': None, 'west': None, 'desc': 'entrance'},
                2: {'north': 5, 'south': 1, 'east': 3, 'west': 4, 'desc': 'junction'},
                3: {'north': None, 'south': None, 'east': None, 'west': 2, 'desc': 'east wing'},
                4: {'north': None, 'south': None, 'east': 2, 'west': None, 'desc': 'west wing'},
                5: {'north': None, 'south': 2, 'east': None, 'west': None, 'desc': 'boss room'},
            },
            'boss_room': 5
        },
        # Cross shape: Center with 4 branches, boss to the north
        {
            'start': 3,
            'rooms': {
                1: {'north': None, 'south': 3, 'east': None, 'west': None, 'desc': 'north chamber'},
                2: {'north': None, 'south': None, 'east': None, 'west': 3, 'desc': 'east wing'},
                3: {'north': 1, 'south': 5, 'east': 2, 'west': 4, 'desc': 'central hub'},
                4: {'north': None, 'south': None, 'east': 3, 'west': None, 'desc': 'west passage'},
                5: {'north': 3, 'south': None, 'east': None, 'west': None, 'desc': 'boss room'},
            },
            'boss_room': 5
        },
        # L-shape with guaranteed path to boss
        {
            'start': 1,
            'rooms': {
                1: {'north': 2, 'south': None, 'east': None, 'west': None, 'desc': 'entrance'},
                2: {'north': 3, 'south': 1, 'east': None, 'west': None, 'desc': 'corridor'},
                3: {'north': None, 'south': 2, 'east': 4, 'west': None, 'desc': 'corner room'},
                4: {'north': None, 'south': None, 'east': 5, 'west': 3, 'desc': 'passage'},
                5: {'north': None, 'south': None, 'east': None, 'west': 4, 'desc': 'boss room'},
            },
            'boss_room': 5
        },
        # Square with boss accessible from two rooms
        {
            'start': 1,
            'rooms': {
                1: {'north': 2, 'south': None, 'east': 4, 'west': None, 'desc': 'entrance'},
                2: {'north': None, 'south': 1, 'east': 3, 'west': None, 'desc': 'north corridor'},
                3: {'north': None, 'south': 4, 'east': None, 'west': 2, 'desc': 'northeast room'},
                4: {'north': 3, 'south': 5, 'east': None, 'west': 1, 'desc': 'central chamber'},
                5: {'north': 4, 'south': None, 'east': None, 'west': None, 'desc': 'boss room'},
            },
            'boss_room': 5
        },
    ]
    
    return random.choice(layouts)

def display_map(zone_map, current_room, visited_rooms):
    """Display a simple ASCII map showing visited rooms and current position"""
    rooms = zone_map['rooms']
    boss_room = zone_map['boss_room']
    
    print("\n--- MAP ---")
    for room_num in sorted(rooms.keys()):
        if room_num in visited_rooms:
            status = "[BOSS]" if room_num == boss_room else "[CLEAR]"
            current = " <-- YOU ARE HERE" if room_num == current_room else ""
            room_type = rooms[room_num]['desc']
            print(f"Room {room_num}: {room_type} {status}{current}")
            
            # Show connections
            connections = []
            for direction in ['north', 'south', 'east', 'west']:
                next_room = rooms[room_num][direction]
                if next_room:
                    visited = "✓" if next_room in visited_rooms else "?"
                    connections.append(f"{direction.upper()[0]}→{next_room}{visited}")
            if connections:
                print(f"         Exits: {', '.join(connections)}")
        elif room_num == boss_room:
            print(f"Room {room_num}: ??? [BOSS - UNEXPLORED]")
    
    print("-----------\n")

def explore_floor(character, theme, floor, zone, global_tree):
    """Main exploration loop for a floor"""
    print(f"\n{'='*70}")
    print(f"FLOOR {floor} - Zone {zone}")
    print(f"{'='*70}")
    
    # Room description
    print(f"\n{get_room_description(theme, floor)}")
    
    # Check for enemy avoidance
    if random.random() * 100 < character.enemy_avoid_chance:
        print("\nYour keen instincts help you avoid an enemy encounter!")
        return True
    
    # Check for ambush
    has_enemy = random.random() < 0.6  # 60% chance of enemy
    if has_enemy and random.random() * 100 < character.ambush_chance:
        print("\nYou spot an enemy before they see you!")
        enemy = create_enemy(zone, floor)
        if not combat(character, enemy, global_tree, ambush=True):
            return False
        has_enemy = False
    
    # Points of interest
    pois = get_points_of_interest(theme)
    
    if pois:
        print("\nYou notice:")
        for i, (poi_desc, _) in enumerate(pois, 1):
            print(f"  {i}. {poi_desc}")
        print(f"  {len(pois) + 1}. Continue forward")
        
        if has_enemy:
            print(f"  {len(pois) + 2}. You sense a hostile presence nearby...")
        
        choice = input("\nWhat do you investigate? ")
        
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(pois):
                poi_desc, outcomes = pois[choice_num - 1]
                result = investigate_poi(character, poi_desc, outcomes, theme)
                if result == "ambush":
                    enemy = create_enemy(zone, floor)
                    if not combat(character, enemy, global_tree):
                        return False
            elif choice_num == len(pois) + 2 and has_enemy:
                enemy = create_enemy(zone, floor)
                if not combat(character, enemy, global_tree):
                    return False
                has_enemy = False
        except ValueError:
            pass
    
    # Regular enemy encounter if not handled
    if has_enemy:
        print("\nAn enemy appears!")
        enemy = create_enemy(zone, floor)
        if not combat(character, enemy, global_tree):
            return False
    
    return True

def navigate_zone(character, zone_map, theme, zone_number, global_tree):
    """Navigate through zone using cardinal directions - 5 rooms total"""
    current_room = zone_map['start']
    visited_rooms = {current_room}
    rested_in_rooms = set()  # Track which rooms we've rested in
    rooms = zone_map['rooms']
    boss_room = zone_map['boss_room']
    
    while True:
        room_info = rooms[current_room]
        
        # Display current status
        print(f"\n{'='*70}")
        print(f"ZONE {zone_number}/20 - ROOM {current_room}/5")
        print(f"{character.name} | HP: {character.hp}/{character.max_hp} | Energy: {character.energy}/{character.max_energy}")
        print(f"{'='*70}")
        
        # Display map
        display_map(zone_map, current_room, visited_rooms)
        
        # Room description
        print(f"\n{get_room_description(theme, current_room)}")
        
        # Check if this is the boss room
        if current_room == boss_room:
            print("\n" + "!"*70)
            print("!!! WARNING: BOSS ROOM DETECTED !!!")
            print("!"*70)
            print("\nYou sense an incredibly powerful presence beyond this point.")
            print("This is the zone boss. Are you ready?")
            
            choice = input("\n1. Enter Boss Room  2. Return to previous area\nChoice: ")
            if choice == "1":
                return "boss_fight"
            else:
                # Let player navigate back
                print("\nYou step back...")
                continue
        
        # Regular room - only explore if NOT yet visited
        if current_room not in visited_rooms or len(visited_rooms) == 1:  # Always explore first room
            if not explore_floor(character, theme, current_room, zone_number, global_tree):
                return "defeated"
            visited_rooms.add(current_room)
        else:
            print("\nYou've already cleared this room.")
        
        # Check if all non-boss rooms explored
        all_explored = all(r in visited_rooms for r in rooms.keys() if r != boss_room)
        
        # Navigation
        print(f"\n{'='*70}")
        print("NAVIGATION")
        print(f"{'='*70}")
        
        available_directions = []
        for direction in ['north', 'south', 'east', 'west']:
            next_room = room_info[direction]
            if next_room is not None:
                boss_warning = " [BOSS ROOM!]" if next_room == boss_room else ""
                visited = " (cleared)" if next_room in visited_rooms else ""
                available_directions.append((direction, next_room, boss_warning, visited))
        
        if not available_directions:
            print("No exits available! (This shouldn't happen)")
            return "error"
        
        print("\nAvailable exits:")
        for i, (direction, next_room, boss_warning, visited) in enumerate(available_directions, 1):
            print(f"{i}. Go {direction.upper()} to Room {next_room}{boss_warning}{visited}")
        
        if all_explored:
            print(f"\n✓ All rooms explored! Boss room is ready.")
        
        print(f"{len(available_directions) + 1}. View Map")
        print(f"{len(available_directions) + 2}. Skill Tree")
        
        # Rest option - only if haven't rested in this room yet
        rest_option_num = len(available_directions) + 3
        if current_room not in rested_in_rooms:
            print(f"{rest_option_num}. Rest (Restore 15 Energy)")
        
        choice = input("\nYour choice: ")
        
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(available_directions):
                direction, next_room, _, _ = available_directions[choice_num - 1]
                current_room = next_room
                print(f"\nYou head {direction}...")
                time.sleep(0.5)
            elif choice_num == len(available_directions) + 1:
                # Just view map - don't change room, continue loop
                continue
            elif choice_num == len(available_directions) + 2:
                # Access skill tree
                skill_tree_menu(character, global_tree)
                apply_global_bonuses(character, global_tree)
                continue
            elif choice_num == rest_option_num and current_room not in rested_in_rooms:
                character.restore_energy(15)
                rested_in_rooms.add(current_room)
                print("\nYou take a moment to catch your breath and focus...")
                print(f"Energy: {character.energy}/{character.max_energy}")
                print("(You can only rest once per room)")
                time.sleep(0.5)
        except ValueError:
            print("Invalid choice.")
            time.sleep(0.5)

def get_character_skill_tree(character_name):
    """Returns character-specific skill tree (simplified version)"""
    # PHASE 2: Personal skills strengthened by 1.5x (combat) to justify risk of losing them
    skill_trees = {
        "Izuku Midoriya": {
            'full_cowling_mastery': {'level': 0, 'max': 3, 'type': 'combat', 
                                     'desc': 'Increases attack by 9 per level', 
                                     'bonus': {'attack': 9}},
            'shoot_style': {'level': 0, 'max': 2, 'type': 'combat',
                           'desc': 'Increases evasion by 12% per level',
                           'bonus': {'evasion': 12}},
            'defensive_instinct': {'level': 0, 'max': 1, 'type': 'combat',
                                  'desc': 'Defensive Instinct passive activates (2x defense at ≤25% HP)',
                                  'bonus': {'defensive_instinct': 1}},
        },
        "Katsuki Bakugo": {
            'explosive_power': {'level': 0, 'max': 3, 'type': 'combat',
                               'desc': 'Increases attack by 12 per level',
                               'bonus': {'attack': 12}},  # Was 8
            'ap_shot_mastery': {'level': 0, 'max': 2, 'type': 'combat',
                               'desc': 'Increases attack by 8 per level',
                               'bonus': {'attack': 8}},  # Was 5
        },
        "Shoto Todoroki": {
            'temperature_control': {'level': 0, 'max': 3, 'type': 'combat',
                                   'desc': 'Increases attack and defense by 5 per level',
                                   'bonus': {'attack': 5, 'defense': 5}},  # Was 3/3
            'ice_wall': {'level': 0, 'max': 2, 'type': 'combat',
                        'desc': 'Increases defense by 9 per level',
                        'bonus': {'defense': 9}},  # Was 6
        },
        "Tsuyu Asui": {
            'camofrog': {'level': 0, 'max': 3, 'type': 'combat', 
                        'desc': 'Increases evasion by 18% and ambush by 12%', 
                        'bonus': {'evasion': 18, 'ambush': 12}},  # Was 12/8
            'tongue_grab': {'level': 0, 'max': 1, 'type': 'utility', 
                           'desc': '30% better items and secrets', 
                           'bonus': {'item_find': 30, 'secret_detection': 20}},  # Utility unchanged
            'ribbit_recovery': {'level': 0, 'max': 1, 'type': 'party_buff',
                               'desc': '🐸 PARTY BUFF: All characters cannot receive lethal damage unless at 1 HP (if Asui not captured)',
                               'bonus': {'ribbit_recovery': 1}},
        },
        "Ochaco Uraraka": {
            'zero_gravity_combat': {'level': 0, 'max': 3, 'type': 'combat',
                                   'desc': 'Increases evasion by 15% per level',
                                   'bonus': {'evasion': 15}},
            'rescue_training': {'level': 0, 'max': 2, 'type': 'utility',
                               'desc': 'Rescue expertise - +50% better chance to find captured students per level',
                               'bonus': {'rescue_boost': 50}},
            'float_recovery': {'level': 0, 'max': 1, 'type': 'utility',
                              'desc': 'Zero Gravity healing - Restore 20 HP after each combat victory',
                              'bonus': {'post_combat_heal': 20}},
        },
        "Tenya Iida": {
            'engine_boost': {'level': 0, 'max': 3, 'type': 'combat',
                            'desc': 'Increases attack by 9 per level',
                            'bonus': {'attack': 9}},  # Was 6
            'recipro_mastery': {'level': 0, 'max': 2, 'type': 'combat',
                               'desc': 'Increases evasion by 12% per level',
                               'bonus': {'evasion': 12}},  # Was 8
        },
        "Eijiro Kirishima": {
            'unbreakable': {'level': 0, 'max': 3, 'type': 'combat',
                           'desc': 'Increases defense by 9 per level',
                           'bonus': {'defense': 9}},  # Was 6
            'hardening_offense': {'level': 0, 'max': 2, 'type': 'combat',
                                 'desc': 'Increases attack by 8 per level',
                                 'bonus': {'attack': 8}},  # Was 5
        },
        "Momo Yaoyorozu": {
            'creation_mastery': {'level': 0, 'max': 3, 'type': 'utility',
                                'desc': 'Increases item find by 15% per level',
                                'bonus': {'item_find': 15}},
            'tactical_genius': {'level': 0, 'max': 2, 'type': 'combat',
                               'desc': 'Increases attack and defense by 6 per level',
                               'bonus': {'attack': 6, 'defense': 6}},
            'lucky_bag': {'level': 0, 'max': 1, 'type': 'utility',
                         'desc': 'Can find Lucky Bags at POI (massive rewards!)',
                         'bonus': {'lucky_bag': 1}},
        },
        "Denki Kaminari": {
            'voltage_control': {'level': 0, 'max': 3, 'type': 'combat',
                               'desc': 'Increases attack by 11 per level',
                               'bonus': {'attack': 11}},  # Was 7 (1.5x)
            'static_shield': {'level': 0, 'max': 2, 'type': 'combat',
                             'desc': 'Increases defense by 8 per level',
                             'bonus': {'defense': 8}},  # Was 5
        },
        "Fumikage Tokoyami": {
            'dark_shadow_control': {'level': 0, 'max': 3, 'type': 'combat',
                                   'desc': 'Increases attack by 11 per level',
                                   'bonus': {'attack': 11}},  # Was 7
            'shadow_cloak': {'level': 0, 'max': 2, 'type': 'combat',
                            'desc': 'Increases evasion by 15% per level',
                            'bonus': {'evasion': 15}},  # Was 10
        },
        "Shoji Mezo": {
            'dupli_power': {'level': 0, 'max': 3, 'type': 'combat',
                           'desc': 'Increases attack by 9 per level',
                           'bonus': {'attack': 9}},  # Was 6
            'sensory_enhancement': {'level': 0, 'max': 1, 'type': 'utility',
                                   'desc': 'Better secret detection',
                                   'bonus': {'secret_detection': 25}},  # Utility unchanged
        },
        "Mina Ashido": {
            'acid_control': {'level': 0, 'max': 3, 'type': 'combat',
                            'desc': 'Increases attack by 9 per level',
                            'bonus': {'attack': 9}},  # Was 6
            'acidman_armor': {'level': 0, 'max': 2, 'type': 'combat',
                             'desc': 'Increases defense by 8 per level',
                             'bonus': {'defense': 8}},  # Was 5
            'acid_veil': {'level': 0, 'max': 1, 'type': 'party_buff',
                         'desc': '💧 PARTY BUFF: All characters -10% damage taken, enemies take 5% recoil damage (if Ashido not captured)',
                         'bonus': {'acid_veil': 1}},
        },
        "Kyoka Jiro": {
            'sonic_amplification': {'level': 0, 'max': 3, 'type': 'combat',
                                   'desc': 'Increases attack by 9 per level',
                                   'bonus': {'attack': 9}},  # Was 6
            'heartbeat_sensor': {'level': 0, 'max': 1, 'type': 'utility',
                                'desc': 'Better enemy detection',
                                'bonus': {'enemy_avoid': 20}},  # Utility unchanged
        },
        "Hanta Sero": {
            'tape_mastery': {'level': 0, 'max': 3, 'type': 'combat',
                            'desc': 'Increases attack by 8 per level',
                            'bonus': {'attack': 8}},  # Was 5
            'swift_swing': {'level': 0, 'max': 2, 'type': 'combat',
                           'desc': 'Increases evasion by 12% per level',
                           'bonus': {'evasion': 12}},  # Was 8
        },
        "Mashirao Ojiro": {
            'tail_combat': {'level': 0, 'max': 3, 'type': 'combat',
                           'desc': 'Increases attack by 9 per level',
                           'bonus': {'attack': 9}},  # Was 6
            'martial_arts': {'level': 0, 'max': 2, 'type': 'combat',
                            'desc': 'Increases defense by 8 per level',
                            'bonus': {'defense': 8}},  # Was 5
        },
        "Toru Hagakure": {
            'stealth_master': {'level': 0, 'max': 3, 'type': 'combat',
                              'desc': 'Increases evasion by 18% per level',
                              'bonus': {'evasion': 18}},  # Was 12
            'ambush_tactics': {'level': 0, 'max': 2, 'type': 'combat',
                              'desc': 'Increases ambush by 15% per level',
                              'bonus': {'ambush': 15}},  # Was 10
        },
        "Koji Koda": {
            'animal_bond': {'level': 0, 'max': 3, 'type': 'combat',
                           'desc': 'Increases attack by 8 per level',
                           'bonus': {'attack': 8}},  # Was 5
            'nature_sense': {'level': 0, 'max': 1, 'type': 'utility',
                            'desc': 'Better item finding',
                            'bonus': {'item_find': 25}},  # Utility unchanged
        },
        "Rikido Sato": {
            'sugar_rush_control': {'level': 0, 'max': 3, 'type': 'combat',
                                  'desc': 'Increases attack by 11 per level',
                                  'bonus': {'attack': 11}},  # Was 7
            'sweet_defense': {'level': 0, 'max': 2, 'type': 'combat',
                             'desc': 'Increases defense by 8 per level',
                             'bonus': {'defense': 8}},  # Was 5
        },
        "Yuga Aoyama": {
            'laser_precision': {'level': 0, 'max': 3, 'type': 'combat',
                               'desc': 'Increases attack by 9 per level',
                               'bonus': {'attack': 9}},  # Was 6
            'dazzling_tactics': {'level': 0, 'max': 2, 'type': 'combat',
                                'desc': 'Increases evasion by 12% per level',
                                'bonus': {'evasion': 12}},  # Was 8
            'cant_stop_our_sparkle': {'level': 0, 'max': 1, 'type': 'party_buff',
                                     'desc': '✨ PARTY BUFF: All characters gain +5% evasion (if Aoyama not captured)',
                                     'bonus': {'cant_stop_sparkle': 1}},
        },
        "Minoru Mineta": {
            'pop_off_mastery': {'level': 0, 'max': 3, 'type': 'combat',
                               'desc': 'Increases attack by 8 per level',
                               'bonus': {'attack': 8}},  # Was 5
            'sticky_defense': {'level': 0, 'max': 2, 'type': 'combat',
                              'desc': 'Increases defense by 8 per level',
                              'bonus': {'defense': 8}},  # Was 5
        },
        "Hitoshi Shinso": {
            'brainwashing_mastery': {'level': 0, 'max': 3, 'type': 'combat',
                                    'desc': 'Increases attack by 9 per level',
                                    'bonus': {'attack': 9}},  # Was 6
            'psychological_warfare': {'level': 0, 'max': 2, 'type': 'combat',
                                     'desc': 'Increases evasion by 12% per level',
                                     'bonus': {'evasion': 12}},  # Was 8
        },
    }
    return skill_trees.get(character_name, {})

def skill_tree_menu(character, global_tree):
    """Interactive skill tree menu"""
    while True:
        print(f"\n{'='*70}")
        print(f"SKILL TREE - {character.name}")
        print(f"{'='*70}")
        print(f"Available Skill Points: {character.skill_points}")
        print(f"\n1. Global Class Skills (Shared by all students)")
        print(f"2. Personal Quirk Skills (Lost if captured)")
        print(f"3. Exit Skill Tree")
        print(f"{'='*70}")
        
        choice = input("\nSelect option: ")
        
        if choice == "1":
            global_skill_menu(character, global_tree)
        elif choice == "2":
            personal_skill_menu(character)
        elif choice == "3":
            break

def global_skill_menu(character, global_tree):
    """Menu for global skill upgrades"""
    if character.skill_points <= 0:
        print("\nNo skill points available!")
        input("Press Enter...")
        return
        
    print(f"\n{'='*70}")
    print(f"GLOBAL CLASS SKILLS")
    print(f"{'='*70}")
    print(f"Skill Points: {character.skill_points}\n")
    
    skills = global_tree.skills
    
    print(f"1. Strength [{skills['strength']['level']}/{skills['strength']['max']}] - {global_tree.get_skill_display('strength')} Attack")
    print(f"2. Defense [{skills['defense']['level']}/{skills['defense']['max']}] - {global_tree.get_skill_display('defense')} Defense")
    print(f"3. Vitality [{skills['hp']['level']}/{skills['hp']['max']}] - {global_tree.get_skill_display('hp')} HP")
    print(f"4. Stamina [{skills['energy']['level']}/{skills['energy']['max']}] - {global_tree.get_skill_display('energy')} Energy")
    print(f"5. Evasion [{skills['evasion']['level']}/{skills['evasion']['max']}] - {global_tree.get_skill_display('evasion')}% Evasion")
    print(f"6. Back")
    
    choice = input("\nUpgrade which skill? ")
    
    skill_map = {'1': 'strength', '2': 'defense', '3': 'hp', '4': 'energy', '5': 'evasion'}
    
    if choice in skill_map:
        skill_name = skill_map[choice]
        if global_tree.upgrade_skill(skill_name):
            character.skill_points -= 1
            print(f"\nUpgraded {skill_name.capitalize()}!")
            input("Press Enter...")

def personal_skill_menu(character):
    """Menu for character-specific skill upgrades"""
    skill_tree = get_character_skill_tree(character.name)
    
    if not skill_tree:
        print("\nNo personal skill tree available for this character.")
        input("Press Enter...")
        return
    
    if character.skill_points <= 0:
        print("\nNo skill points available!")
        input("Press Enter...")
        return
    
    print(f"\n{character.name}'S PERSONAL SKILLS")
    print("WARNING: Lost if captured!\n")
    
    skills_list = list(skill_tree.items())
    for i, (skill_id, skill_data) in enumerate(skills_list, 1):
        current_level = character.personal_skills.get(skill_id, 0)
        print(f"{i}. {skill_id.replace('_', ' ').title()} [{current_level}/{skill_data['max']}]")
        print(f"   {skill_data['desc']}")
    
    print(f"{len(skills_list) + 1}. Back")
    
    choice = input("\nUpgrade: ")
    
    try:
        choice_num = int(choice)
        if 1 <= choice_num <= len(skills_list):
            skill_id, skill_data = skills_list[choice_num - 1]
            current_level = character.personal_skills.get(skill_id, 0)
            
            if current_level < skill_data['max']:
                character.personal_skills[skill_id] = current_level + 1
                character.skill_points -= 1
                
                # Apply bonuses
                for bonus_type, value in skill_data['bonus'].items():
                    if bonus_type == 'attack':
                        character.base_attack += value
                        character.attack += value
                    elif bonus_type == 'evasion':
                        character.evasion += value
                    elif bonus_type == 'ambush':
                        character.ambush_chance += value
                    elif bonus_type == 'item_find':
                        character.item_find_bonus += value
                    elif bonus_type == 'secret_detection':
                        character.secret_detection += value
                
                print(f"\nUpgraded {skill_id}!")
                input("Press Enter...")
    except:
        pass

def main():
    """Main game loop with UPDATED Aizawa introduction and 100-floor system"""
    print("="*70)
    print("U.A. HIGH SCHOOL: TRAINING EXERCISE")
    print("="*70)
    
    # UPDATED AIZAWA INTRODUCTION - Addresses the class
    print("\n[Aizawa]: \"Listen up, all of you. You're about to enter Facility")
    print("13-B, a specialized training complex designed to push Class 1-A to")
    print("your absolute limits.\"")
    print("\n[Aizawa]: \"This facility has 100 floors divided into 20 distinct")
    print("zones. Each zone consists of 5 rooms with unique environmental")
    print("hazards that will test your quirk adaptability.\"")
    print("\n[Aizawa]: \"Pay attention to zone types. Some of your quirks will")
    print("thrive in certain environments while others will struggle. Bakugo")
    print("excels in heat. Tokoyami gets stronger in darkness. Asui performs")
    print("better in water but suffers in the cold. Koda can command animals")
    print("in natural habitats. Choose your deployments wisely.\"")
    print("\n[Aizawa]: \"The simulation uses a capture system - if you fall in")
    print("combat, you're tagged and removed from the exercise. Your classmates")
    print("can attempt rescues, but there are no guarantees.\"")
    print("\n[Aizawa]: \"Each zone has a boss encounter at the end. Boss health")
    print("persists across attempts. If one of you weakens a boss but falls,")
    print("the next student faces it at reduced strength. Use that to your")
    print("advantage.\"")
    print("\n[Aizawa]: \"The final floor holds the ultimate test. I won't spoil")
    print("the details, but know this: your performance throughout the exercise")
    print("determines the difficulty of that final encounter.\"")
    print("\n[Aizawa]: \"Your objective is to clear all 100 floors. Work together,")
    print("use your strengths, and don't embarrass me. Now get to it.\"")
    
    print("\nOBJECTIVE: Clear all 20 zones (100 floors)!")
    
    input("\nPress Enter to begin...")
    
    characters = create_class_1a()
    global_tree = GlobalSkillTree()
    current_zone = 1
    current_floor = 1
    zone_bosses = {}
    previous_theme = None
    current_theme = None
    
    # Main game loop - 20 zones
    selected_character = None  # Track character selected for the zone
    zone_map = None  # Track the map for current zone
    
    while current_zone <= 20:
        available = [c for c in characters if not c.captured and c.unlocked]
        if not available:
            print("\nALL STUDENTS CAPTURED")
            print(f"Zones cleared: {current_zone - 1}/20")
            break
        
        # ===== START OF NEW ZONE - Character Selection =====
        if current_floor == 1:
            check_rescue_event(characters, zone_start=True)
            current_theme = get_zone_theme(current_zone, previous_theme)
            zone_map = generate_zone_map()  # Generate new map for this zone
            
            # Display detailed zone description BEFORE character select
            print(f"\n{'='*70}")
            print(f"ENTERING ZONE {current_zone}/20")
            print(f"Zone Type: {current_theme.upper()}")
            print(f"{'='*70}")
            print(f"\n{get_zone_description(current_theme, current_zone)}")
            print(f"\n{'='*70}")
            
            input("\nPress Enter to select your student...")
            
            # CHARACTER SELECTION - Once per zone
            print(f"\n{'='*70}")
            print(f"ZONE {current_zone}/20 - {current_theme.upper()} ZONE")
            print(f"SELECT STUDENT FOR DEPLOYMENT")
            print(f"Active Students: {len(available)}/{len([c for c in characters if c.unlocked])}")
            print(f"{'='*70}")
            
            selected_character = select_character(characters, global_tree)
            global_tree.set_character_bonus(selected_character.name)
            apply_global_bonuses(selected_character, global_tree)
            zone_effect = selected_character.apply_zone_effects(current_theme)
            
            print(f"\n{selected_character.name} deploys!")
            print(f"\n\"{selected_character.get_deployment_dialogue()}\"")
            print(f"\n[Aizawa]: \"{selected_character.get_aizawa_response()}\"")
            
            if zone_effect:
                print(f"\n{zone_effect}")
            
            input("\nPress Enter to enter the zone...")
        
        # Use the character selected for this zone
        character = selected_character
        
        # ===== ZONE NAVIGATION =====
        result = navigate_zone(character, zone_map, current_theme, current_zone, global_tree)
        
        if result == "boss_fight":
            # Boss encounter
            if current_zone not in zone_bosses:
                zone_bosses[current_zone] = create_boss(current_zone)
            
            boss = zone_bosses[current_zone]
            
            if not boss.defeated:
                print("\n" + "="*70)
                print("BOSS ENCOUNTER!")
                print("="*70)
                print(f"\n{boss.description}")
                print(f"\nThe boss {boss.get_health_description()}.")
                input("\nPress Enter to fight...")
                
                if combat(character, boss, global_tree, is_boss=True):
                    boss.defeated = True
                    print(f"\n{'='*70}")
                    print(f"ZONE {current_zone} CLEARED!")
                    print(f"{'='*70}")
                    character.heal(50)
                    character.restore_energy(50)
                    
                    check_rescue_event(characters, zone_start=False)
                    
                    previous_theme = current_theme
                    current_zone += 1
                    current_floor = 1
                    selected_character = None  # Clear for next zone
                    zone_map = None  # Clear map
                    
                    input("\nPress Enter to continue...")
                else:
                    # Character defeated by boss
                    print(f"\nBoss HP remaining: {boss.hp}/{boss.max_hp}")
                    print(f"\n{character.name} - CAPTURED")
                    character.captured = True
                    character.reset_personal_skills()
                    print("Personal skills reset!")
                    current_floor = 1  # Reset to floor 1 - will select new character
                    selected_character = None  # Clear selection
                    zone_map = None  # Reset map for retry
                    input("\nPress Enter...")
            else:
                # Boss already defeated
                previous_theme = current_theme
                current_zone += 1
                current_floor = 1
                selected_character = None
                zone_map = None
                
        elif result == "defeated":
            # Character defeated during exploration
            print(f"\n{character.name} - CAPTURED")
            character.captured = True
            character.reset_personal_skills()
            print("Personal skills reset!")
            current_floor = 1  # Reset - will select new character
            selected_character = None
            zone_map = None  # Reset map for retry
            input("\nPress Enter...")
        else:
            # Error or unexpected result
            print("\nUnexpected navigation result!")
            input("\nPress Enter...")
    
    # FINAL BOSS - ALL FOR ONE
    if current_zone > 20:
        print("\n" + "="*70)
        print("FINAL FLOOR")
        print("="*70)
        
        available = [c for c in characters if not c.captured and c.unlocked]
        
        if not available:
            print("\nNo students remaining...")
            print("\nGAME OVER")
        else:
            print("\n[Aizawa]: \"This is it. The final test.\"")
            print("[Aizawa]: \"All For One awaits on the top floor.\"")
            print("[Aizawa]: \"He's stolen quirks from every student you've lost.\"")
            
            captured_students = [c for c in characters if c.captured]
            
            if not captured_students:
                print("\n[Aizawa]: \"Impressive. Not a single student captured.\"")
                print("[Aizawa]: \"All For One will have no stolen quirks to use.\"")
            else:
                print(f"\n[Aizawa]: \"Students captured: {len(captured_students)}\"")
                print("[Aizawa]: \"All For One will use their quirks against you.\"")
            
            input("\nPress Enter to face All For One...")
            
            # Create All For One - ADAPTIVE BOSS
            afo = BossEnemy("All For One", 25, "The Symbol of Evil.", 21)
            
            num_captured = len(captured_students)
            afo.max_hp = 200 + (num_captured * 50)
            afo.hp = afo.max_hp
            afo.attack = 20 + (num_captured * 5)
            afo.defense = 10 + (num_captured * 2)
            
            print(f"\n{'='*70}")
            print("ALL FOR ONE")
            print(f"{'='*70}")
            print(f"\nAll For One stands before you, radiating malevolent power.")
            
            if num_captured > 0:
                print(f"\nYou sense {num_captured} stolen quirks within him:")
                for student in captured_students[:5]:
                    print(f"  - {student.name}'s {student.quirk}")
                if num_captured > 5:
                    print(f"  ... and {num_captured - 5} more")
            else:
                print("\nWithout stolen quirks, he seems almost... ordinary.")
            
            character = select_character(characters, global_tree)
            global_tree.set_character_bonus(character.name)
            apply_global_bonuses(character, global_tree)
            
            print(f"\n{character.name} steps forward!")
            print(f"\n\"{character.get_deployment_dialogue()}\"")
            print(f"\n[Aizawa]: \"{character.get_aizawa_response()}\"")
            
            input("\nPress Enter for final battle...")
            
            if combat(character, afo, global_tree, is_boss=True):
                print("\n" + "="*70)
                print("VICTORY!")
                print("="*70)
                print("\n[Aizawa]: \"You did it. All 100 floors cleared.\"")
                print("[Aizawa]: \"Class 1-A... you've proven yourselves.\"")
                print("\nEXERCISE COMPLETE!")
                print(f"\nStudents Captured: {num_captured}/21")
                
                if num_captured == 0:
                    print("\nPERFECT RUN - NO CASUALTIES!")
            else:
                print(f"\n{character.name} - CAPTURED")
                print("\nGAME OVER")
    
    print("\nThank you for playing!")

if __name__ == "__main__":
    main()
