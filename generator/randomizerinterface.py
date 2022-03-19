# Python types
import io
import os
import random
import sys

# Web types
from .forms import GenerateForm
from django.conf import settings as conf

# Add the randomizer to the system path here.  This code assumes that the
# randomizer has been added at the site base path.
sys.path.append(os.path.join(conf.BASE_DIR, 'jetsoftime', 'sourcefiles'))

# Randomizer types
import randoconfig
import randomizer
import randosettings as rset


game_mode_map = {
    "standard": rset.GameMode.STANDARD,
    "lost_worlds": rset.GameMode.LOST_WORLDS,
    "ice_age": rset.GameMode.ICE_AGE,
    "legacy_of_cyrus": rset.GameMode.LEGACY_OF_CYRUS
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
    def __init__(self, rom_data):
        self.randomizer = randomizer.Randomizer(rom_data, is_vanilla=True)

    def configure_seed(self, form: GenerateForm):
        self.randomizer.settings = self.__convert_form_to_settings(form)
        self.randomizer.set_random_config()

    def generate_rom(self) -> bytearray:
        self.randomizer.generate_rom()
        return self.randomizer.get_generated_rom()

    def set_settings_and_config(self, settings: rset.Settings, config: randoconfig.RandoConfig):
        self.randomizer.settings = settings
        self.randomizer.set_config(config)

    def get_settings(self) -> rset.Settings:
        return self.randomizer.settings

    def get_config(self) -> randoconfig.RandoConfig:
        return self.randomizer.config

    #
    # Convert flag/settings data from the web form into the
    # correct settings object used by the randomizer
    #
    @classmethod
    def __convert_form_to_settings(cls, form: GenerateForm) -> rset.Settings:
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

        if form.cleaned_data['quiet_mode']:
            settings.gameflags = settings.gameflags | rset.GameFlags.QUIET_MODE

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

        if form.cleaned_data['duplicate_duals']:
            settings.gameflags = settings.gameflags | rset.GameFlags.DUPLICATE_TECHS

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

        # Boss rando settings
        # TODO - Boss and location lists are just default for now. Only update the other options.
        settings.ro_settings.preserve_parts = form.cleaned_data['legacy_boss_placement']
        settings.ro_settings.enable_sightscope = form.cleaned_data['enable_sightscope']

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

        if form.cleaned_data['fast_tabs']:
            settings.gameflags = settings.gameflags | rset.GameFlags.FAST_TABS

        # Cosmetic settings
        if form.cleaned_data['zenan_alt_battle_music']:
            settings.cosmetic_flags = settings.cosmetic_flags | rset.CosmeticFlags.ZENAN_ALT_MUSIC

        if form.cleaned_data['death_peak_alt_music']:
            settings.cosmetic_flags = settings.cosmetic_flags | rset.CosmeticFlags.DEATH_PEAK_ALT_MUSIC

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
        if form.cleaned_data['guaranteed_drops']:
            settings.gameflags = settings.gameflags | rset.GameFlags.GUARANTEED_DROPS

        if form.cleaned_data['buff_x_strike']:
            settings.gameflags = settings.gameflags | rset.GameFlags.BUFF_XSTRIKE

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
            rset.GameFlags.DUPLICATE_CHARS: form.cleaned_data['mystery_duplicate_characters']/100
        }

        return settings
    # End __convert_form_to_settings

    @classmethod
    def get_spoiler_log(cls, config: randoconfig.RandoConfig, settings: rset.Settings):
        spoiler_log = io.StringIO()
        rando = randomizer.Randomizer(cls.get_base_rom(), is_vanilla=True, settings=settings, config=config)

        # The Randomizer.write_spoiler_log method writes directly to a file, so
        # recreate it here using the helper functions and pass them a StringIO
        # object instead of a file.
        rando.write_settings_spoilers(spoiler_log)
        rando.write_tab_spoilers(spoiler_log)
        rando.write_key_item_spoilers(spoiler_log)
        rando.write_boss_rando_spoilers(spoiler_log)
        rando.write_character_spoilers(spoiler_log)
        rando.write_boss_stat_spoilers(spoiler_log)
        rando.write_treasure_spoilers(spoiler_log)
        rando.write_drop_charm_spoilers(spoiler_log)
        rando.write_shop_spoilers(spoiler_log)
        rando.write_price_spoilers(spoiler_log)

        return spoiler_log

    #
    # Get a JSON string representing the spoiler log data for the given config.
    #
    @classmethod
    def get_web_spoiler_log(cls, config: randoconfig.RandoConfig):
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
            spoiler_log['bosses'].append(
                {'location': str(location), 'boss': str(config.boss_assign_dict[location])})
        return spoiler_log
    # End get_web_spoiler_log

    #
    # Generate a random seed value.
    #
    # This requires the names.txt file to be placed in the webapp's BASE_DIR.
    #
    @classmethod
    def get_random_seed(cls):
        p = open("names.txt", "r")
        names = p.readline()
        names = names.split(",")
        p.close()
        return "".join(random.choice(names) for i in range(2))

    #
    # Used to read in the server's vanilla ROM to generate the user patch.
    # The user will still have to provide a ROM when they retrieve the seed.
    #
    # This requires a valid, unheadered Chrono Trigger ROM to be placed in the
    # webapp's BASE_DIR named ct.sfc.
    #
    @classmethod
    def get_base_rom(cls):
        with open(str("ct.sfc"), 'rb') as infile:
            rom = bytearray(infile.read())
        return rom
