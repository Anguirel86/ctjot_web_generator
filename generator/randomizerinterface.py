# Python types
from __future__ import annotations
import copy
import io
import json
import os.path
import random
import re
import sys
import datetime
import types

from collections import OrderedDict
from typing import Dict, Optional

# Web types
from .forms import GenerateForm, RomForm
from django.conf import settings as conf

# Add the randomizer to the system path here.  This code assumes that the
# randomizer has been added at the site base path.
sys.path.append(os.path.join(conf.BASE_DIR, 'jetsoftime', 'sourcefiles'))

# Randomizer types
import bossrandotypes as rotypes
import jotjson
import logicwriters as logicwriter
import randoconfig
import randomizer
import randosettings as rset
from randosettings import GameFlags as GF


game_mode_map = {
    "standard": rset.GameMode.STANDARD,
    "lost_worlds": rset.GameMode.LOST_WORLDS,
    "ice_age": rset.GameMode.ICE_AGE,
    "legacy_of_cyrus": rset.GameMode.LEGACY_OF_CYRUS,
    "vanilla_rando": rset.GameMode.VANILLA_RANDO
}

shop_price_map = {
    "normal": rset.ShopPrices.NORMAL,
    "free": rset.ShopPrices.FREE,
    "mostly_random": rset.ShopPrices.MOSTLY_RANDOM,
    "fully_random": rset.ShopPrices.FULLY_RANDOM
}

difficulty_map = {
    "easy": rset.Difficulty.EASY,
    "normal": rset.Difficulty.NORMAL,
    "hard": rset.Difficulty.HARD
}

tech_order_map = {
    "normal": rset.TechOrder.NORMAL,
    "fully_random": rset.TechOrder.FULL_RANDOM,
    "balanced_random": rset.TechOrder.BALANCED_RANDOM
}

gameflags_dict = {
    # Main
    'disable_glitches': GF.FIX_GLITCH,
    'boss_rando': GF.BOSS_RANDO,
    'boss_scaling': GF.BOSS_SCALE,
    'zeal': GF.ZEAL_END,
    'early_pendant': GF.FAST_PENDANT,
    'locked_chars': GF.LOCKED_CHARS,
    'unlocked_magic': GF.UNLOCKED_MAGIC,
    'tab_treasures': GF.TAB_TREASURES,
    'chronosanity': GF.CHRONOSANITY,
    'char_rando': GF.CHAR_RANDO,
    'healing_item_rando': GF.HEALING_ITEM_RANDO,
    'gear_rando': GF.GEAR_RANDO,
    'mystery_seed': GF.MYSTERY,
    'epoch_fail': GF.EPOCH_FAIL,
    'duplicate_characters': GF.DUPLICATE_CHARS,
    'duplicate_duals': GF.DUPLICATE_TECHS,
    # This should get moved to ROSettings.
    'boss_spot_hp': GF.BOSS_SPOT_HP,
    # Extra
    'unlocked_skyways': GF.UNLOCKED_SKYGATES,
    'add_sunkeep_spot': GF.ADD_SUNKEEP_SPOT,
    'add_bekkler_spot': GF.ADD_BEKKLER_SPOT,
    'add_cyrus_spot': GF.ADD_CYRUS_SPOT,
    'restore_tools': GF.RESTORE_TOOLS,
    'add_ozzie_spot': GF.ADD_OZZIE_SPOT,
    'restore_johnny_race': GF.RESTORE_JOHNNY_RACE,
    'add_racelog_spot': GF.ADD_RACELOG_SPOT,
    'remove_black_omen_spot': GF.REMOVE_BLACK_OMEN_SPOT,
    'split_arris_dome': GF.SPLIT_ARRIS_DOME,
    'vanilla_robo_ribbon': GF.VANILLA_ROBO_RIBBON,
    'vanilla_desert': GF.VANILLA_DESERT,
    'use_antilife': GF.USE_ANTILIFE,
    'tackle_effects': GF.TACKLE_EFFECTS_ON,
    'starters_sufficient': GF.STARTERS_SUFFICIENT,
    'bucket_list': GF.BUCKET_LIST,
    'rocksanity': GF.ROCKSANITY,
    'tech_damage_rando': GF.TECH_DAMAGE_RANDO,
    # QoL
    'sightscope_always_on': GF.VISIBLE_HEALTH,
    'boss_sightscope': GF.BOSS_SIGHTSCOPE,
    'fast_tabs': GF.FAST_TABS,
    'free_menu_glitch': GF.FREE_MENU_GLITCH,
}

# TODO: remove this and use objectivehints.get_objective_hint_aliases once merged to jetsoftime
# Mapping of objective hint aliases mapped to objective hint strings
# NOTE: this is ordered (python>=3.5) with more common random categories at the top
objective_hint_aliases: Dict[str, str] = {
    'Random': '65:quest_gated, 30:boss_nogo, 15:recruit_gated',
    'Random Gated Quest': 'quest_gated',
    'Random Hard Quest': 'quest_late',
    'Random Go Mode Quest': 'quest_go',
    'Random Gated Character Recruit': 'recruit_gated',
    'Random Boss (Includes Go Mode Dungeons)': 'boss_any',
    'Random Boss from Go Mode Dungeon': 'boss_go',
    'Random Boss (No Go Mode Dungeons)': 'boss_nogo',
    'Recruit 3 Characters (Total 5)': 'recruit_3',
    'Recruit 4 Characters (Total 6)': 'recruit_4',
    'Recruit 5 Characters (Total 7)': 'recruit_5',
    'Collect 10 of 20 Fragments': 'collect_10_fragments_20',
    'Collect 10 of 30 Fragments': 'collect_10_fragments_30',
    'Collect 3 Rocks': 'collect_3_rocks',
    'Collect 4 Rocks': 'collect_4_rocks',
    'Collect 5 Rocks': 'collect_5_rocks',
    'Forge the Masamune': 'quest_forge',
    'Charge the Moonstone': 'quest_moonstone',
    'Trade the Jerky Away': 'quest_jerky',
    'Defeat the Arris Dome Boss': 'quest_arris',
    "Visit Cyrus's Grave with Frog": 'quest_cyrus',
    "Defeat the Boss of Death's Peak": 'quest_deathpeak',
    'Defeat the Boss of Denadoro Mountains': 'quest_denadoro',
    'Gain Epoch Flight': 'quest_epoch',
    'Defeat the Boss of the Factory Ruins': 'quest_factory',
    'Defeat the Boss of the Geno Dome': 'quest_geno',
    "Defeat the Boss of the Giant's Claw": 'quest_claw',
    "Defeat the Boss of Heckran's Cave": 'quest_heckran',
    "Defeat the Boss of the King's Trial": 'quest_shard',
    'Defeat the Boss of Manoria Cathedral': 'quest_cathedral',
    'Defeat the Boss of Mount Woe': 'quest_woe',
    'Defeat the Boss of the Pendant Trial': 'quest_pendant',
    'Defeat the Boss of the Reptite Lair': 'quest_reptite',
    'Defeat the Boss of the Sun Palace': 'quest_sunpalace',
    'Defeat the Boss of the Sunken Desert': 'quest_desert',
    'Defeat the Boss in the Zeal Throneroom': 'quest_zealthrone',
    'Defeat the Boss of Zenan Bridge': 'quest_zenan',
    'Defeat the Black Tyrano': 'quest_blacktyrano',
    'Defeat the Tyrano Lair Midboss': 'quest_tyranomid',
    "Defeat the Boss in Flea's Spot": 'quest_flea',
    "Defeat the Boss in Slash's Spot": 'quest_slash',
    "Defeat Magus in Magus's Castle": 'quest_magus',
    'Defeat the Boss in the GigaMutant Spot': 'quest_omengiga',
    'Defeat the Boss in the TerraMutant Spot': 'quest_omenterra',
    'Defeat the Boss in the ElderSpawn Spot': 'quest_omenelder',
    'Defeat the Boss in the Twin Golem Spot': 'quest_twinboss',
    'Beat Johnny in a Race': 'quest_johnny',
    'Bet on a Fair Race and Win': 'quest_fairrace',
    'Play the Fair Drinking Game': 'quest_soda',
    'Defeat AtroposXR': 'boss_atropos',
    'Defeat DaltonPlus': 'boss_dalton',
    'Defeat DragonTank': 'boss_dragontank',
    'Defeat ElderSpawn': 'boss_elderspawn',
    'Defeat Flea': 'boss_flea',
    'Defeat Flea Plus': 'boss_fleaplus',
    'Defeat Giga Gaia': 'boss_gigagaia',
    'Defeat GigaMutant': 'boss_gigamutant',
    'Defeat Golem': 'boss_golem',
    'Defeat Golem Boss': 'boss_golemboss',
    'Defeat Guardian': 'boss_guardian',
    'Defeat Heckran': 'boss_heckran',
    'Defeat LavosSpawn': 'boss_lavosspawn',
    'Defeat Magus (North Cape)': 'boss_magusnc',
    'Defeat Masamune': 'boss_masamune',
    'Defeat Mother Brain': 'boss_motherbrain',
    'Defeat Mud Imp': 'boss_mudimp',
    'Defeat Nizbel': 'boss_nizbel',
    'Defeat Nizbel II': 'boss_nizbel2',
    'Defeat R-Series': 'boss_rseries',
    'Defeat Retinite': 'boss_retinite',
    'Defeat RustTyrano': 'boss_rusttyrano',
    'Defeat Slash': 'boss_slash',
    'Defeat Son of Sun': 'boss_sonofsun',
    'Defeat Super Slash': 'boss_superslash',
    'Defeat TerraMutant': 'boss_terramutant',
    # Skip twinboss b/c it's in quests
    'Defeat Yakra': 'boss_yakra',
    'Defeat Yakra XIII': 'boss_yakraxiii',
    'Defeat Zombor': 'boss_zombor'
}


class InvalidSettingsException(Exception):
    pass


class RandomizerInterface:
    """
    RandomizerInterface acts as an interface between the web application
    and the Jets of Time randomizer code.

    All calls to the randomizer or its data are handled through this class.  It contains
    the appropriate methods for creating randomizer settings/config objects and querying
    them for information needed on the web generator.
    """
    def __init__(self, rom_data: bytearray):
        """
        Constructor for the RandomizerInterface class.

        :param rom_data: bytearray containing vanilla ROM data used to construct a randomizer object
        """
        self.randomizer = randomizer.Randomizer(rom_data, is_vanilla=True)

    def configure_seed_from_form(self, form: GenerateForm) -> str:
        """
        Generate a RandoConfig from the provided GenerateForm.
        This will convert the form data into the appropriate randomizer settings and config
        objects and then tell the randomizer to generate a seed.

        :param form: GenerateForm with the user's settings

        :return: string of a nonce, if any, that was used to obfuscate the seed
        """
        self.randomizer.settings = self.__convert_form_to_settings(form)
        nonce = ''
        # If this is a race seed, modify the seed value  before sending it through
        # the randomizer.  This will ensure that race ROMs and non-race ROMs with the same
        # seed value are not identical.
        if form.cleaned_data['spoiler_log']:
            self.randomizer.set_random_config()
        else:
            # Use the current timestamp's number of microseconds as an arbitrary nonce value
            nonce = str(datetime.datetime.now().microsecond)
            seed = self.randomizer.settings.seed
            self.randomizer.settings.seed = seed + nonce
            self.randomizer.set_random_config()
            self.randomizer.settings.seed = seed
        return nonce

    def configure_seed_from_settings(self, settings: rset.Settings, is_race_seed: bool) -> str:
        """
        Generate a RandoConfig from the provided Settings object.
        This will create a new game based on existing settings.

        This method will fail if the given settings object is for a mystery seed.

        :param settings: Settings object to copy for this new game
        :param is_race_seed: Whether or not this is a race seed

        :return: string of a nonce, if any, that was used to obfuscate the seed
        """

        if rset.GameFlags.MYSTERY in settings.gameflags:
            raise InvalidSettingsException("Mystery seeds cannot be cloned.")

        self.randomizer.settings = settings
        # get a random seed value to replace the existing one
        seed = settings.seed
        new_seed = seed
        while seed == new_seed:
            new_seed = self.get_random_seed()
        settings.seed = new_seed
        nonce = ''

        # If this is a race seed, modify the seed value  before sending it through
        # the randomizer.  This will ensure that race ROMs and non-race ROMs with the same
        # seed value are not identical.
        if is_race_seed:
            nonce = str(datetime.datetime.now().microsecond)
            self.randomizer.settings.seed = new_seed + nonce
            self.randomizer.set_random_config()
            self.randomizer.settings.seed = new_seed
        else:
            self.randomizer.set_random_config()
        return nonce

    def generate_rom(self) -> bytearray:
        """
        Create a ROM from the settings and config objects previously generated or set.

        :return: bytearray object with the modified ROM data
        """
        self.randomizer.generate_rom()
        return self.randomizer.get_generated_rom()

    def get_seed_hash(self) -> bytes:
        if not self.randomizer.has_generated:
            self.generate_rom()
        return self.randomizer.hash_string_bytes

    def set_seed_hash(self, hash_bytes: bytes):
        if not self.randomizer.has_generated:
            self.randomizer.hash_string_bytes = hash_bytes

    def set_settings_and_config(
        self, settings: rset.Settings, config: randoconfig.RandoConfig, form: Optional[RomForm]
    ):
        """
        Populate the randomizer with a pre-populated RandoSettings object and a
        preconfigured RandoSettings object.

        :param settings: RandoSettings object
        :param config: RandoConfig object
        :param form: RomForm with cosmetic settings, or None
        """
        # Cosmetic settings
        cos_flag_dict: dict[str, rset.CosmeticFlags] = {
            'reduce_flashes': rset.CosmeticFlags.REDUCE_FLASH,
            'zenan_alt_battle_music': rset.CosmeticFlags.ZENAN_ALT_MUSIC,
            'death_peak_alt_music': rset.CosmeticFlags.DEATH_PEAK_ALT_MUSIC,
            'quiet_mode': rset.CosmeticFlags.QUIET_MODE,
            'auto_run': rset.CosmeticFlags.AUTORUN
        }

        if form is not None:
            cos_flags = rset.CosmeticFlags(False)
            for name, flag in cos_flag_dict.items():
                if form.cleaned_data[name]:
                    cos_flags |= flag

            settings.cosmetic_flags = cos_flags

            # Character/Epoch renames
            settings.char_names[0] = self.get_character_name(form.cleaned_data['crono_name'], 'Crono')
            settings.char_names[1] = self.get_character_name(form.cleaned_data['marle_name'], 'Marle')
            settings.char_names[2] = self.get_character_name(form.cleaned_data['lucca_name'], 'Lucca')
            settings.char_names[3] = self.get_character_name(form.cleaned_data['robo_name'], 'Robo')
            settings.char_names[4] = self.get_character_name(form.cleaned_data['frog_name'], 'Frog')
            settings.char_names[5] = self.get_character_name(form.cleaned_data['ayla_name'], 'Ayla')
            settings.char_names[6] = self.get_character_name(form.cleaned_data['magus_name'], 'Magus')
            settings.char_names[7] = self.get_character_name(form.cleaned_data['epoch_name'], 'Epoch')

            # In-game options
            # Boolean options
            if form.cleaned_data['stereo_audio'] is not None:
                settings.ctoptions.stereo_audio = form.cleaned_data['stereo_audio']

            if form.cleaned_data['save_menu_cursor'] is not None:
                settings.ctoptions.save_menu_cursor = form.cleaned_data['save_menu_cursor']

            if form.cleaned_data['save_battle_cursor'] is not None:
                settings.ctoptions.save_battle_cursor = form.cleaned_data['save_battle_cursor']

            if form.cleaned_data['skill_item_info'] is not None:
                settings.ctoptions.skill_item_info = form.cleaned_data['skill_item_info']

            if form.cleaned_data['consistent_paging'] is not None:
                settings.ctoptions.consistent_paging = form.cleaned_data['consistent_paging']

            # Integer options
            if form.cleaned_data['battle_speed']:
                settings.ctoptions.battle_speed = \
                    self.clamp((form.cleaned_data['battle_speed'] - 1), 0, 7)

            if form.cleaned_data['background_selection']:
                settings.ctoptions.menu_background = \
                    self.clamp((form.cleaned_data['background_selection'] - 1), 0, 7)

            if form.cleaned_data['battle_message_speed']:
                settings.ctoptions.battle_msg_speed = \
                    self.clamp((form.cleaned_data['battle_message_speed'] - 1), 0, 7)

            if form.cleaned_data['battle_gauge_style'] is not None:
                settings.ctoptions.battle_gauge_style = \
                    self.clamp((form.cleaned_data['battle_gauge_style']), 0, 2)

        self.randomizer.settings = settings
        self.randomizer.config = config

    def get_settings(self) -> rset.Settings:
        """
        Get the settings object used to generate the seed.

        :return: RandoSettings object used to generate the seed
        """
        return self.randomizer.settings

    def get_config(self) -> randoconfig.RandoConfig:
        """
        Get the config object used to generate the the seed.

        :return: RandoConfig object used to generate the seed
        """
        return self.randomizer.config

    def get_rom_name(self, share_id: str) -> str:
        """
        Get the ROM name for this seed

        :param share_id: Share ID os the seed in question
        :return: String containing the name of the ROM for this seed
        """
        if rset.GameFlags.MYSTERY in self.randomizer.settings.gameflags:
            return "ctjot_mystery_" + share_id + ".sfc"
        else:
            return "ctjot_" + self.randomizer.settings.get_flag_string() + "_" + share_id + ".sfc"

    @classmethod
    def __convert_form_to_settings(cls, form: GenerateForm) -> rset.Settings:
        """
        Convert flag/settings data from the web form into a RandoSettings object.

        :param form: GenerateForm object from the web interface
        :return: RandoSettings object with flags/settings from the form applied
        """

        settings = rset.Settings()

        # Seed
        if form.cleaned_data['seed'] == "":
            # get a random seed
            settings.seed = cls.get_random_seed()
        else:
            settings.seed = form.cleaned_data['seed']

        # Difficulties
        settings.item_difficulty = difficulty_map[form.cleaned_data['item_difficulty']]
        settings.enemy_difficulty = difficulty_map[form.cleaned_data['enemy_difficulty']]

        # game mode
        settings.game_mode = game_mode_map[form.cleaned_data['game_mode']]

        # shops
        settings.shopprices = shop_price_map[form.cleaned_data['shop_prices']]

        # techs
        settings.techorder = tech_order_map[form.cleaned_data['tech_rando']]

        settings.gameflags = GF(False)
        for name, flag in gameflags_dict.items():
            if form.cleaned_data[name]:
                settings.gameflags |= flag

        settings.initial_flags = copy.deepcopy(settings.gameflags)

        # Character rando
        char_choices = []
        char_rando_assignments = form.cleaned_data['char_rando_assignments']

        # character rando assignments comes in as a stringified hex number.
        # Decode the hex string into the char_choices list.
        # Loop through the characters
        for i in range(7):
            char_choices.append([])
            choices = int(char_rando_assignments[(i * 2):(i * 2) + 2], 16)
            # Loop through the assignments for the current character
            for j in range(7):
                if choices & (1 << j) > 0:
                    char_choices[i].append(j)
        settings.char_choices = char_choices

        # Boss rando settings
        # TODO - Boss and location lists are just default for now. Only update the other options.
        settings.ro_settings.flags = rset.ROFlags(False)
        if form.cleaned_data['legacy_boss_placement']:
            settings.ro_settings.flags |= rset.ROFlags.PRESERVE_PARTS

        if form.cleaned_data['boss_spot_hp']:
            settings.ro_settings.flags |= rset.ROFlags.BOSS_SPOT_HP

        # Tab randomization settings
        # TODO - Currently defaulting to UNIFORM distribution
        settings.tab_settings = rset.TabSettings(
            scheme=rset.TabRandoScheme.UNIFORM,
            binom_success=.5,
            power_min=form.cleaned_data['power_tab_min'],
            power_max=form.cleaned_data['power_tab_max'],
            magic_min=form.cleaned_data['magic_tab_min'],
            magic_max=form.cleaned_data['magic_tab_max'],
            speed_min=form.cleaned_data['speed_tab_min'],
            speed_max=form.cleaned_data['speed_tab_max']
        )

        # Bucket Settings
        disable_other_go_modes = form.cleaned_data['bucket_disable_go_modes']
        objectives_win = form.cleaned_data['bucket_obj_win_game']
        num_objectives = form.cleaned_data['bucket_num_objs']
        num_objectives_needed = form.cleaned_data['bucket_num_objs_req']

        hints = [
            form.cleaned_data['bucket_objective'+str(ind+1)]
            for ind in range(num_objectives)
        ]

        # Hints *should* only be None if bucket_list isn't checked, but let's
        # be certain.
        hints = [
            hint if hint is not None else '' for hint in hints
        ]

        settings.bucket_settings = rset.BucketSettings(
            disable_other_go_modes=disable_other_go_modes,
            objectives_win=objectives_win,
            num_objectives=num_objectives,
            num_objectives_needed=num_objectives_needed,
            hints=hints
        )

        # Mystery
        settings.mystery_settings.game_mode_freqs: dict[rset.GameMode, int] = {
            rset.GameMode.STANDARD: form.cleaned_data['mystery_game_mode_standard'],
            rset.GameMode.LOST_WORLDS: form.cleaned_data['mystery_game_mode_lw'],
            rset.GameMode.LEGACY_OF_CYRUS: form.cleaned_data['mystery_game_mode_loc'],
            rset.GameMode.ICE_AGE: form.cleaned_data['mystery_game_mode_ia'],
            rset.GameMode.VANILLA_RANDO: form.cleaned_data['mystery_game_mode_vr']
        }

        settings.mystery_settings.item_difficulty_freqs: dict[rset.Difficulty, int] = {
            rset.Difficulty.EASY: form.cleaned_data['mystery_item_difficulty_easy'],
            rset.Difficulty.NORMAL: form.cleaned_data['mystery_item_difficulty_normal'],
            rset.Difficulty.HARD: form.cleaned_data['mystery_item_difficulty_hard']
        }

        settings.mystery_settings.enemy_difficulty_freqs: dict[rset.Difficulty, int] = {
            rset.Difficulty.NORMAL: form.cleaned_data['mystery_enemy_difficulty_normal'],
            rset.Difficulty.HARD: form.cleaned_data['mystery_enemy_difficulty_hard']
        }

        settings.mystery_settings.tech_order_freqs: dict[rset.TechOrder, int] = {
            rset.TechOrder.NORMAL: form.cleaned_data['mystery_tech_order_normal'],
            rset.TechOrder.BALANCED_RANDOM: form.cleaned_data['mystery_tech_order_full_random'],
            rset.TechOrder.FULL_RANDOM: form.cleaned_data['mystery_tech_order_balanced_random']
        }

        settings.mystery_settings.shop_price_freqs: dict[rset.ShopPrices, int] = {
            rset.ShopPrices.NORMAL: form.cleaned_data['mystery_shop_prices_normal'],
            rset.ShopPrices.MOSTLY_RANDOM: form.cleaned_data['mystery_shop_prices_random'],
            rset.ShopPrices.FULLY_RANDOM: form.cleaned_data['mystery_shop_prices_mostly_random'],
            rset.ShopPrices.FREE: form.cleaned_data['mystery_shop_prices_free']
        }

        settings.mystery_settings.flag_prob_dict: dict[rset.GameFlags, int] = {
            rset.GameFlags.TAB_TREASURES: form.cleaned_data['mystery_tab_treasures']/100,
            rset.GameFlags.UNLOCKED_MAGIC: form.cleaned_data['mystery_unlock_magic']/100,
            rset.GameFlags.BUCKET_LIST: form.cleaned_data['mystery_bucket_list']/100,
            rset.GameFlags.CHRONOSANITY: form.cleaned_data['mystery_chronosanity']/100,
            rset.GameFlags.BOSS_RANDO: form.cleaned_data['mystery_boss_rando']/100,
            rset.GameFlags.BOSS_SCALE: form.cleaned_data['mystery_boss_scale']/100,
            rset.GameFlags.LOCKED_CHARS: form.cleaned_data['mystery_locked_characters']/100,
            rset.GameFlags.CHAR_RANDO: form.cleaned_data['mystery_char_rando']/100,
            rset.GameFlags.DUPLICATE_CHARS: form.cleaned_data['mystery_duplicate_characters']/100,
            rset.GameFlags.EPOCH_FAIL: form.cleaned_data['mystery_epoch_fail']/100,
            rset.GameFlags.GEAR_RANDO: form.cleaned_data['mystery_gear_rando']/100,
            rset.GameFlags.HEALING_ITEM_RANDO: form.cleaned_data['mystery_heal_rando']/100
        }

        return settings
    # End __convert_form_to_settings

    @classmethod
    def get_spoiler_log(
        cls, config: randoconfig.RandoConfig, settings: rset.Settings, hash_bytes: Optional[bytes]
    ) -> io.StringIO:
        """
        Get a spoiler log file-like object.

        :param config: RandoConfig object describing the seed
        :param settings: RandoSettings object describing the seed
        :return: File-like object with spoiler log data for the given seed data
        """
        spoiler_log = io.StringIO()
        rando = randomizer.Randomizer(cls.get_base_rom(), is_vanilla=True, settings=settings, config=config)
        if hash_bytes is not None:
            rando.hash_string_bytes = hash_bytes

        # The Randomizer.write_spoiler_log method writes directly to a file,
        # but it works if we pass a StringIO instead.
        rando.write_spoiler_log(spoiler_log)

        return spoiler_log

    @classmethod
    def get_json_spoiler_log(
        cls, config: randoconfig.RandoConfig, settings: rset.Settings, hash_bytes: Optional[bytes]
    ) -> io.StringIO:
        """
        Get a spoiler log file-like object.

        :param config: RandoConfig object describing the seed
        :param settings: RandoSettings object describing the seed
        :return: File-like object with spoiler log data for the given seed data
        """
        spoiler_log = io.StringIO()
        rando = randomizer.Randomizer(cls.get_base_rom(), is_vanilla=True, settings=settings, config=config)
        if hash_bytes is not None:
            rando.hash_string_bytes = hash_bytes

        # The Randomizer.write_spoiler_log method writes directly to a file,
        # but it works if we pass a StringIO instead.
        rando.write_json_spoiler_log(spoiler_log)

        return spoiler_log

    @staticmethod
    def get_web_spoiler_log(
            settings: rset.Settings,
            config: randoconfig.RandoConfig
    ) -> dict[str, list[dict[str, str]]]:
        """
        Get a dictionary representing the spoiler log data for the given seed.

        :param config: RandoConfig object describing the seed
        :return: Dictionary of spoiler data
        """
        spoiler_log = {
            'characters': [],
            'key_items': [],
            'bosses': [],
            'objectives': [],
            'spheres': []
        }

        if rset.GameFlags.BUCKET_LIST in settings.gameflags:
            num_objs = settings.bucket_settings.num_objectives

            for ind, objective in enumerate(config.objectives):
                if ind >= num_objs:
                    break

                spoiler_log['objectives'].append(
                    {'name': str(f"Objective {ind+1}"),
                     'desc': objective.desc}
                )

        # Character data
        for recruit_spot in config.char_assign_dict.keys():
            held_char = config.char_assign_dict[recruit_spot].held_char
            reassign_char = config.pcstats.get_character_assignment(held_char)
            char_data = {'location': str(f"{recruit_spot}"),
                         'character': str(f"{held_char}"),
                         'reassign': str(f"{reassign_char}")}
            spoiler_log['characters'].append(char_data)

        # Key item data
        for location in config.key_item_locations:
            spoiler_log['key_items'].append(
                {'location': str(f"{location.getName()}"), 'key': str(location.getKeyItem())})

        # Boss data
        for location in config.boss_assign_dict.keys():
            if config.boss_assign_dict[location] == rotypes.BossID.TWIN_BOSS:
                twin_type = config.boss_data_dict[rotypes.BossID.TWIN_BOSS].parts[0].enemy_id
                twin_name = config.enemy_dict[twin_type].name
                boss_str = "Twin " + str(twin_name)
            else:
                boss_str = str(config.boss_assign_dict[location])
            spoiler_log['bosses'].append({'location': str(location), 'boss': boss_str})

        # Sphere data
        spheres = logicwriter.get_proof_string_from_settings_config(settings, config)
        rgx = re.compile(r'((?P<sphere>GO|(\d?)):\s*)?(?P<desc>.+)')
        for line in spheres.splitlines():
            spoiler_log['spheres'].append(rgx.search(line).groupdict())

        return spoiler_log
    # End get_web_spoiler_log

    @staticmethod
    def get_gameflags_map() -> Dict[str, str]:
        """
        Get mapping of form names to gameflags to encode to JSON.
        """
        return {k: str(flag) for k, flag in gameflags_dict.items()}

    @staticmethod
    def get_obhint_map() -> OrderedDict[str, str]:
        """
        Get ordered dict of objective hints aliases mapped to objective hint strings.

        :return: OrderedDict of obhint alias strings mapped to obhint strings.
        """
        # TODO: use objectivehints.get_objective_hint_aliases once merged to jetsoftime
        return OrderedDict(objective_hint_aliases.items())

    @staticmethod
    def get_settings_defaults_json() -> str:
        """
        Get the default settings object encoded as compact JSON.

        This turns on fast tab and disables glitches by default as well.
        Even though those are not the defaults in Settings, they are used
        as "defaults" in the web GUI for improved UX, especially for new
        players.

        :return: default RandoSettings object encoded as JSON.
        """
        settings = rset.Settings()

        # turn on fast tabs and disable glitches by default
        settings.gameflags |= (
            rset.GameFlags.FIX_GLITCH | rset.GameFlags.FAST_TABS
        )

        # TODO: remove this temporary monkeypatch after jetsoftime PR merged with to_jot_json updates
        def _jot_json(self):
            return {
                "game_mode": str(self.game_mode),
                "enemy_difficulty": str(self.enemy_difficulty),
                "item_difficulty": str(self.item_difficulty),
                "techorder": str(self.techorder),
                "shopprices": str(self.shopprices),
                "mystery_settings": {
                    'game_mode_freqs': {
                        'Standard': 75,
                        'Lost worlds': 25,
                        'Legacy of cyrus': 0,
                        'Ice age': 0,
                        'Vanilla rando': 0
                    },
                    'item_difficulty_freqs': {'Easy': 15, 'Normal': 70, 'Hard': 15},
                    'enemy_difficulty_freqs': {'Normal': 75, 'Hard': 25},
                    'tech_order_freqs': {'Normal': 10, 'Balanced random': 10, 'Full random': 80},
                    'shop_price_freqs': {'Normal': 70, 'Mostly random': 10, 'Fully random': 10, 'Free': 10},
                    'flag_prob_dict': {
                        'GameFlags.TAB_TREASURES': 0.1,
                        'GameFlags.UNLOCKED_MAGIC': 0.5,
                        'GameFlags.BUCKET_LIST': 0.15,
                        'GameFlags.CHRONOSANITY': 0.5,
                        'GameFlags.BOSS_RANDO': 0.5,
                        'GameFlags.BOSS_SCALE': 0.1,
                        'GameFlags.LOCKED_CHARS': 0.25,
                        'GameFlags.CHAR_RANDO': 0.5,
                        'GameFlags.DUPLICATE_CHARS': 0.25,
                        'GameFlags.EPOCH_FAIL': 0.5,
                        'GameFlags.GEAR_RANDO': 0.25,
                        'GameFlags.HEALING_ITEM_RANDO': 0.25
                    }
                },
                "gameflags": self.gameflags,
                "bucket_settings": {
                    "disable_other_go_modes": False,
                    "objectives_win": False,
                    "num_objectives": 5,
                    "num_objectives_needed": 4,
                    "hints": [],
                },
                "tab_settings": {
                    "power_min": 2,
                    "power_max": 4,
                    "magic_min": 1,
                    "magic_max": 3,
                    "speed_min": 1,
                    "speed_max": 1,
                },
            }

        setattr(settings, '_jot_json', types.MethodType(_jot_json, settings))

        return json.dumps(settings, cls=jotjson.JOTJSONEncoder, indent=None, separators=(',', ':'))

    @staticmethod
    def get_random_seed() -> str:
        """
        Get a random seed string for a ROM.
        This seed string is built up from a list of names bundled with the randomizer.  This method
        expects the names.txt file to be accessible in the web app's root directory.

        :return: Random seed string.
        """
        with open("names.txt", "r") as names_file:
            names = names_file.readline()
            names = names.split(",")
        return "".join(random.choice(names) for i in range(2))

    @staticmethod
    def get_base_rom() -> bytearray:
        """
        Read in the server's vanilla ROM as a bytearray.
        This data is used to create a RandoConfig object to generate a seed.  It should not
        be used when applying the config and sending the seed to a user.  The user's ROM will
        be used for that process instead.

        The unheadered, vanilla Chrono Trigger ROM must be located in the web app's BASE_DIR
        and must be named ct.sfc.

        :return: bytearray containing the vanilla Chrono Trigger ROM data
        """
        with open(str("ct.sfc"), 'rb') as infile:
            rom = bytearray(infile.read())
        return rom

    @classmethod
    def get_share_details(
        cls, config: randoconfig.RandoConfig, settings: rset.Settings, hash_bytes: Optional[bytes]
    ) -> io.StringIO:
        """
        Get details about a seed for display on the seed share page.  If this is a mystery seed then
        just display "Mystery seed!".


        :param config: RandoConfig object describing this seed
        :param settings: RandoSettings object describing this seed
        :return: File-like object with seed share details
        """
        buffer = io.StringIO()
        rando = randomizer.Randomizer(cls.get_base_rom(), is_vanilla=True, settings=settings, config=config)
        if hash_bytes is not None:
            rando.hash_string_bytes = hash_bytes

        if rset.GameFlags.MYSTERY in settings.gameflags:
            # TODO - Get weights and non-mystery flags
            # NOTE - The randomizer overwrites the settings object when it is a mystery seed and wipes
            #        out the seed value and most of the probability data.  Either the "before" version
            #        of this object will need to be stored or the randomizer will need to be modified
            #        to preserve this information if we want more information here.
            buffer.write("Mystery seed!\n")
        else:
            # For now just use the settings spoiler output for the share link display.
            # TODO - Make this more comprehensive.
            buffer.write("Seed: " + settings.seed + "\n")
            rando.write_settings_spoilers(buffer)

        return buffer

    @staticmethod
    def get_character_name(name: str, default_name: str):
        """
        Given a character name and a default, validate the name and return either the
        validated name or the default value if the name is invalid.

        Valid names are five characters or less, alphanumeric characters only.

        :param name: Name selected by the user
        :param default_name: Default name of the character
        :return: Either the user's selected name or a default if the name is invalid.
        """
        if name is None or name == "" or len(name) > 5 or not name.isalnum():
            return default_name
        return name

    @staticmethod
    def clamp(value, min_val, max_val):
        return max(min_val, min(value, max_val))
