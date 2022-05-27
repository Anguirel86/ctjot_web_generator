from django import forms


#
# This form is used to submit the ROM on the page where seeds are downloaded.
#
class RomForm(forms.Form):
    rom_file = forms.FileField(required=True)
    share_id = forms.CharField(widget=forms.HiddenInput(), required=True)


#
# Form class for version 3.2.0 of the randomizer.
#
class GenerateForm(forms.Form):
    # Flag options
    disable_glitches = forms.BooleanField(required=False)
    quiet_mode = forms.BooleanField(required=False)

    boss_rando = forms.BooleanField(required=False)
    boss_scaling = forms.BooleanField(required=False)
    zeal = forms.BooleanField(required=False)
    early_pendant = forms.BooleanField(required=False)
    locked_chars = forms.BooleanField(required=False)
    unlocked_magic = forms.BooleanField(required=False)
    tab_treasures = forms.BooleanField(required=False)
    chronosanity = forms.BooleanField(required=False)
    duplicate_characters = forms.BooleanField(required=False)
    mystery_seed = forms.BooleanField(required=False)
    enemy_difficulty = forms.CharField(max_length=6)
    item_difficulty = forms.CharField(max_length=6)
    shop_prices = forms.CharField(max_length=13)
    tech_rando = forms.CharField(max_length=15)
    game_mode = forms.CharField(max_length=15)

    # Duplicate characters tab
    duplicate_char_assignments = forms.CharField(widget=forms.HiddenInput(), required=False)
    duplicate_duals = forms.BooleanField(required=False)

    # Boss rando tab
    legacy_boss_placement = forms.BooleanField(required=False)

    # Tab options tab
    power_tab_min = forms.IntegerField()
    power_tab_max = forms.IntegerField()
    magic_tab_min = forms.IntegerField()
    magic_tab_max = forms.IntegerField()
    speed_tab_min = forms.IntegerField()
    speed_tab_max = forms.IntegerField()

    # Quality of life
    sightscope_always_on = forms.BooleanField(required=False)
    boss_sightscope = forms.BooleanField(required=False)
    fast_tabs = forms.BooleanField(required=False)
    free_menu_glitch = forms.BooleanField(required=False)

    # Cosmetic
    zenan_alt_battle_music = forms.BooleanField(required=False)
    death_peak_alt_music = forms.BooleanField(required=False)

    # Experimental
    guaranteed_drops = forms.BooleanField(required=False)
    buff_x_strike = forms.BooleanField(required=False)
    bucket_fragments = forms.BooleanField(required=False)
    ayla_rebalance = forms.BooleanField(required=False)
    black_hole_rework = forms.BooleanField(required=False)
    no_crisis_tackle = forms.BooleanField(required=False)
    healing_item_rando = forms.BooleanField(required=False)
    gear_rando = forms.BooleanField(required=False)
    starters_sufficient = forms.BooleanField(required=False)
    epoch_fail = forms.BooleanField(required=False)
    fragments_required = forms.IntegerField()
    extra_fragments = forms.IntegerField()

    # seed and spoiler log
    seed = forms.CharField(max_length=25, required=False)
    spoiler_log = forms.BooleanField(required=False)

    # Mystery tab
    #  Game Modes
    mystery_game_mode_standard = forms.IntegerField()
    mystery_game_mode_lw = forms.IntegerField()
    mystery_game_mode_loc = forms.IntegerField()
    mystery_game_mode_ia = forms.IntegerField()
    #  Item Difficulty
    mystery_item_difficulty_easy = forms.IntegerField()
    mystery_item_difficulty_normal = forms.IntegerField()
    mystery_item_difficulty_hard = forms.IntegerField()
    #  Enemy Difficulty
    mystery_enemy_difficulty_normal = forms.IntegerField()
    mystery_enemy_difficulty_hard = forms.IntegerField()
    #  Tech Order
    mystery_tech_order_normal = forms.IntegerField()
    mystery_tech_order_full_random = forms.IntegerField()
    mystery_tech_order_balanced_random = forms.IntegerField()
    #  Shop Prices
    mystery_shop_prices_normal = forms.IntegerField()
    mystery_shop_prices_random = forms.IntegerField()
    mystery_shop_prices_mostly_random = forms.IntegerField()
    mystery_shop_prices_free = forms.IntegerField()
    #  Flags
    mystery_tab_treasures = forms.IntegerField()
    mystery_unlock_magic = forms.IntegerField()
    mystery_bucket_fragments = forms.IntegerField()
    mystery_chronosanity = forms.IntegerField()
    mystery_boss_rando = forms.IntegerField()
    mystery_boss_scale = forms.IntegerField()
    mystery_locked_characters = forms.IntegerField()
    mystery_duplicate_characters = forms.IntegerField()


