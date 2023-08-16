# Python types
from __future__ import annotations
import io
import os.path
import random
import sys
import datetime

# Web types
from .forms import GenerateForm, RomForm
from django.conf import settings as conf

# Add the randomizer to the system path here.  This code assumes that the
# randomizer has been added at the site base path.
sys.path.append(os.path.join(conf.BASE_DIR, 'jetsoftime', 'sourcefiles'))

# Randomizer types
import ctenums
import bossrandotypes as rotypes
import randoconfig
import randomizer
import randosettings as rset


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

    def set_settings_and_config(self, settings: rset.Settings, config: randoconfig.RandoConfig, form: Optional[RomForm]):
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

        GF = rset.GameFlags
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

        settings.gameflags = GF(False)
        for name, flag in gameflags_dict.items():
            if form.cleaned_data[name]:
                settings.gameflags |= flag

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
            rset.GameMode.ICE_AGE: form.cleaned_data['mystery_game_mode_ia']
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
    def get_spoiler_log(cls, config: randoconfig.RandoConfig, settings: rset.Settings, hash_bytes: Optional[bytes]) -> io.StringIO:
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
    def get_json_spoiler_log(cls, config: randoconfig.RandoConfig, settings: rset.Settings, hash_bytes: Optional[bytes]) -> io.StringIO:
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
            'objectives': []
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

        return spoiler_log
    # End get_web_spoiler_log

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
    def get_share_details(cls, config: randoconfig.RandoConfig, settings: rset.Settings, hash_bytes: Optional[bytes]) -> io.StringIO:
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

