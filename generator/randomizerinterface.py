# Python types
from __future__ import annotations
import io
import json
import os
import os.path
import random
import sys

# Web types
from .forms import GenerateForm, RomForm
from django.apps import apps
from django.conf import settings as conf


# Add the randomizer to the system path here.  This code assumes that the
# randomizer has been added at the site base path.
sys.path.append(os.path.join(conf.BASE_DIR, 'jetsoftime', 'sourcefiles'))

# Randomizer types
import ctenums
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


#
# This class acts as the interface between the web code and the randomizer.
#
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

    def configure_seed(self, form: GenerateForm):
        """
        Generate a RandoConfig from the provided GenerateForm.
        This will convert the form data into the appropriate randomizer settings and config
        objects and then tell the randomizer to generate a seed.

        :param form: GenerateForm with the user's settings
        """
        self.randomizer.settings = self.__convert_form_to_settings(form)
        # If this is a race seed, modify the seed value so that before sending it through
        # the randomizer.  This will ensure that race ROMs and non-race ROMs with the same
        # seed value are not identical.
        if form.cleaned_data['spoiler_log']:
            self.randomizer.set_random_config()
        else:
            seed = self.randomizer.settings.seed
            modifier = apps.get_app_config('generator').RACE_SEED_MODIFIER
            self.randomizer.settings.seed = seed + modifier
            self.randomizer.set_random_config()
            self.randomizer.settings.seed = seed

    def generate_rom(self) -> bytearray:
        """
        Create a ROM from the settings and config objects previously generated or set.

        :return: bytearray object with the modified ROM data
        """
        self.randomizer.generate_rom()
        return self.randomizer.get_generated_rom()

    def set_settings_and_config(self, settings: rset.Settings, config: randoconfig.RandoConfig, form: RomForm):
        """
        Populate the randomizer with a pre-populated RandoSettings object and a
        preconfigured RandoSettings object.

        :param settings: RandoSettings object
        :param config: RandoConfig object
        :param form: RomForm with cosmetic settings
        """
        # Cosmetic settings
        if form.cleaned_data['zenan_alt_battle_music']:
            settings.cosmetic_flags = settings.cosmetic_flags | rset.CosmeticFlags.ZENAN_ALT_MUSIC

        if form.cleaned_data['death_peak_alt_music']:
            settings.cosmetic_flags = settings.cosmetic_flags | rset.CosmeticFlags.DEATH_PEAK_ALT_MUSIC

        if form.cleaned_data['quiet_mode']:
            settings.cosmetic_flags = settings.cosmetic_flags | rset.CosmeticFlags.QUIET_MODE

        # Character/Epoch renames
        settings.char_names[0] = self.get_character_name(form.cleaned_data['crono_name'], 'Crono')
        settings.char_names[1] = self.get_character_name(form.cleaned_data['marle_name'], 'Marle')
        settings.char_names[2] = self.get_character_name(form.cleaned_data['lucca_name'], 'Lucca')
        settings.char_names[3] = self.get_character_name(form.cleaned_data['robo_name'], 'Robo')
        settings.char_names[4] = self.get_character_name(form.cleaned_data['frog_name'], 'Frog')
        settings.char_names[5] = self.get_character_name(form.cleaned_data['ayla_name'], 'Ayla')
        settings.char_names[6] = self.get_character_name(form.cleaned_data['magus_name'], 'Magus')
        settings.char_names[7] = self.get_character_name(form.cleaned_data['epoch_name'], 'Epoch')

        self.randomizer.settings = settings
        self.randomizer.set_config(config)

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

        if form.cleaned_data['disable_glitches']:
            settings.gameflags = settings.gameflags | rset.GameFlags.FIX_GLITCH

        if form.cleaned_data['boss_rando']:
            settings.gameflags = settings.gameflags | rset.GameFlags.BOSS_RANDO

        if form.cleaned_data['boss_scaling']:
            settings.gameflags = settings.gameflags | rset.GameFlags.BOSS_SCALE

        if form.cleaned_data['zeal']:
            settings.gameflags = settings.gameflags | rset.GameFlags.ZEAL_END

        if form.cleaned_data['early_pendant']:
            settings.gameflags = settings.gameflags | rset.GameFlags.FAST_PENDANT

        if form.cleaned_data['locked_chars']:
            settings.gameflags = settings.gameflags | rset.GameFlags.LOCKED_CHARS

        if form.cleaned_data['unlocked_magic']:
            settings.gameflags = settings.gameflags | rset.GameFlags.UNLOCKED_MAGIC

        if form.cleaned_data['tab_treasures']:
            settings.gameflags = settings.gameflags | rset.GameFlags.TAB_TREASURES

        if form.cleaned_data['chronosanity']:
            settings.gameflags = settings.gameflags | rset.GameFlags.CHRONOSANITY

        if form.cleaned_data['duplicate_characters']:
            settings.gameflags = settings.gameflags | rset.GameFlags.DUPLICATE_CHARS

        if form.cleaned_data['healing_item_rando']:
            settings.gameflags = settings.gameflags | rset.GameFlags.HEALING_ITEM_RANDO

        if form.cleaned_data['gear_rando']:
            settings.gameflags = settings.gameflags | rset.GameFlags.GEAR_RANDO

        if form.cleaned_data['mystery_seed']:
            settings.gameflags = settings.gameflags | rset.GameFlags.MYSTERY

        # Duplicate characters
        char_choices = []
        duplicate_char_assignments = form.cleaned_data['duplicate_char_assignments']
        # duplicate character assignments comes in as a stringified hex number.
        # Decode the hex string into the char_choices list.
        # Loop through the characters
        for i in range(7):
            char_choices.append([])
            choices = int(duplicate_char_assignments[(i * 2):(i * 2) + 2], 16)
            # Loop through the assignments for the current character
            for j in range(7):
                if choices & (1 << j) > 0:
                    char_choices[i].append(j)
        settings.char_choices = char_choices

        if form.cleaned_data['duplicate_duals']:
            settings.gameflags = settings.gameflags | rset.GameFlags.DUPLICATE_TECHS

        # Boss rando settings
        # TODO - Boss and location lists are just default for now. Only update the other options.
        settings.ro_settings.preserve_parts = form.cleaned_data['legacy_boss_placement']

        if form.cleaned_data['boss_spot_hp']:
            settings.gameflags = settings.gameflags | rset.GameFlags.BOSS_SPOT_HP

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

        # Quality of life settings
        if form.cleaned_data['sightscope_always_on']:
            settings.gameflags = settings.gameflags | rset.GameFlags.VISIBLE_HEALTH

        if form.cleaned_data['boss_sightscope']:
            settings.gameflags = settings.gameflags | rset.GameFlags.BOSS_SIGHTSCOPE

        if form.cleaned_data['fast_tabs']:
            settings.gameflags = settings.gameflags | rset.GameFlags.FAST_TABS

        if form.cleaned_data['free_menu_glitch']:
            settings.gameflags = settings.gameflags | rset.GameFlags.FREE_MENU_GLITCH

        # Bucket Fragments
        if form.cleaned_data['bucket_fragments']:
            settings.gameflags = settings.gameflags | rset.GameFlags.BUCKET_FRAGMENTS

        num_fragments = \
            form.cleaned_data['fragments_required'] + form.cleaned_data['extra_fragments']
        settings.bucket_settings = rset.BucketSettings(
            num_fragments=num_fragments,
            needed_fragments=form.cleaned_data['fragments_required']
        )

        # Experimental settings
        if form.cleaned_data['use_antilife']:
            settings.gameflags = settings.gameflags | rset.GameFlags.USE_ANTILIFE

        if form.cleaned_data['tackle_effects']:
            settings.gameflags = settings.gameflags | rset.GameFlags.TACKLE_EFFECTS_ON

        if form.cleaned_data['starters_sufficient']:
            settings.gameflags = settings.gameflags | rset.GameFlags.FIRST_TWO

        if form.cleaned_data['epoch_fail']:
            settings.gameflags = settings.gameflags | rset.GameFlags.EPOCH_FAIL


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
            rset.GameFlags.BUCKET_FRAGMENTS: form.cleaned_data['mystery_bucket_fragments']/100,
            rset.GameFlags.CHRONOSANITY: form.cleaned_data['mystery_chronosanity']/100,
            rset.GameFlags.BOSS_RANDO: form.cleaned_data['mystery_boss_rando']/100,
            rset.GameFlags.BOSS_SCALE: form.cleaned_data['mystery_boss_scale']/100,
            rset.GameFlags.LOCKED_CHARS: form.cleaned_data['mystery_locked_characters']/100,
            rset.GameFlags.DUPLICATE_CHARS: form.cleaned_data['mystery_duplicate_characters']/100,
            rset.GameFlags.EPOCH_FAIL: form.cleaned_data['mystery_epoch_fail']/100,
            rset.GameFlags.GEAR_RANDO: form.cleaned_data['mystery_gear_rando']/100,
            rset.GameFlags.HEALING_ITEM_RANDO: form.cleaned_data['mystery_heal_rando']/100
        }

        return settings
    # End __convert_form_to_settings

    @classmethod
    def get_spoiler_log(cls, config: randoconfig.RandoConfig, settings: rset.Settings) -> io.StringIO:
        """
        Get a spoiler log file-like object.

        :param config: RandoConfig object describing the seed
        :param settings: RandoSettings object describing the seed
        :return: File-like object with spoiler log data for the given seed data
        """
        spoiler_log = io.StringIO()
        rando = randomizer.Randomizer(cls.get_base_rom(), is_vanilla=True, settings=settings, config=config)

        # The Randomizer.write_spoiler_log method writes directly to a file,
        # but it works if we pass a StringIO instead.
        rando.write_spoiler_log(spoiler_log)

        return spoiler_log

    @classmethod
    def get_web_spoiler_log(cls, config: randoconfig.RandoConfig) -> dict[str, list[dict[str, str]]]:
        """
        Get a dictionary representing the spoiler log data for the given seed.

        :param config: RandoConfig object describing the seed
        :return: Dictionary of spoiler data
        """
        spoiler_log = {
            'characters': [],
            'key_items': [],
            'bosses': []
        }

        # Character data
        for recruit_spot in config.char_assign_dict.keys():
            held_char = config.char_assign_dict[recruit_spot].held_char
            char_data = {'location': str(f"{recruit_spot}"),
                         'character': str(f"{held_char}"),
                         'reassign': str(f"{config.char_manager.pcs[held_char].assigned_char}")}
            spoiler_log['characters'].append(char_data)

        # Key item data
        for location in config.key_item_locations:
            spoiler_log['key_items'].append(
                {'location': str(f"{location.getName()}"), 'key': str(location.getKeyItem())})

        # Boss data
        for location in config.boss_assign_dict.keys():
            if config.boss_assign_dict[location] == ctenums.BossID.TWIN_BOSS:
                twin_type = config.boss_data_dict[ctenums.BossID.TWIN_BOSS].scheme.ids[0]
                twin_name = config.enemy_dict[twin_type].name
                boss_str = "Twin " + str(twin_name)
            else:
                boss_str = str(config.boss_assign_dict[location])
            spoiler_log['bosses'].append({'location': str(location), 'boss': boss_str})

        return spoiler_log
    # End get_web_spoiler_log

    @classmethod
    def get_random_seed(cls) -> str:
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

    @classmethod
    def get_base_rom(cls) -> bytearray:
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
    def get_share_details(cls, config: randoconfig.RandoConfig, settings: rset.Settings) -> io.StringIO:
        """
        Get details about a seed for display on the seed share page.  If this is a mystery seed then
        just display "Mystery seed!".


        :param config: RandoConfig object describing this seed
        :param settings: RandoSettings object describing this seed
        :return: File-like object with seed share details
        """
        buffer = io.StringIO()
        rando = randomizer.Randomizer(cls.get_base_rom(), is_vanilla=True, settings=settings, config=config)

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

    @classmethod
    def get_character_name(cls, name: str, default_name: str):
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

    @classmethod
    def get_randomizer_version_info(cls) -> dict[str, str]:
        """
        Read version_info.json from the webapp root directory and return the
        randomizer version information.

        This method assumes that the version_info.json file will be present in the
        web app's BASE_DIR.  If it does not exist, both the date and short hash will
        return with a value of "Unknown".

        :return: Dictionary with the randomizer version info from version_info.json
        """
        # TODO - This is a beta only feature so that users can know which specific version of the
        #        randomizer is being used by the web generator.  This won't be needed for the
        #        live version of the site when 3.2 is out of beta.
        #        The version_info.json file is not part of source control.
        if os.path.exists('version_info.json'):
            with open('version_info.json') as version_file:
                return json.load(version_file)
        else:
            return {'date': 'Unknown', 'hash': 'Unknown'}

