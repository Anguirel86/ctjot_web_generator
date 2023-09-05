from django import forms


class RomForm(forms.Form):
    """
    This form is used to submit the ROM on the page where seeds are downloaded.
    """
    rom_file = forms.FileField(required=True)
    share_id = forms.CharField(widget=forms.HiddenInput(), required=True)

    # Cosmetic
    zenan_alt_battle_music = forms.BooleanField(required=False)
    death_peak_alt_music = forms.BooleanField(required=False)
    quiet_mode = forms.BooleanField(required=False)
    reduce_flashes = forms.BooleanField(required=False)
    auto_run = forms.BooleanField(required=False)

    # Actual character name length is limited to 5 characters in game,
    # but if an invalid name is entered the randomizer interface will
    # just use the character's default name.
    crono_name = forms.CharField(max_length=15, required=False)
    marle_name = forms.CharField(max_length=15, required=False)
    lucca_name = forms.CharField(max_length=15, required=False)
    robo_name = forms.CharField(max_length=15, required=False)
    frog_name = forms.CharField(max_length=15, required=False)
    ayla_name = forms.CharField(max_length=15, required=False)
    magus_name = forms.CharField(max_length=15, required=False)
    epoch_name = forms.CharField(max_length=15, required=False)

    # In-game options
    stereo_audio = forms.BooleanField(required=False)
    save_menu_cursor = forms.BooleanField(required=False)
    save_battle_cursor = forms.BooleanField(required=False)
    save_skill_item_cursor = forms.BooleanField(required=False)
    skill_item_info = forms.BooleanField(required=False)
    consistent_paging = forms.BooleanField(required=False)
    background_selection = forms.IntegerField(required=False)
    battle_speed = forms.IntegerField(required=False)
    battle_message_speed = forms.IntegerField(required=False)
    battle_gauge_style = forms.IntegerField(required=False)


class GenerateForm(forms.Form):
    """
    Form class for version 3.3.0 of the randomizer.
    """
    # Flag options
    disable_glitches = forms.BooleanField(required=False)

    boss_rando = forms.BooleanField(required=False)
    boss_scaling = forms.BooleanField(required=False)
    zeal = forms.BooleanField(required=False)
    early_pendant = forms.BooleanField(required=False)
    locked_chars = forms.BooleanField(required=False)
    unlocked_magic = forms.BooleanField(required=False)
    tab_treasures = forms.BooleanField(required=False)
    chronosanity = forms.BooleanField(required=False)
    char_rando = forms.BooleanField(required=False)
    mystery_seed = forms.BooleanField(required=False)
    healing_item_rando = forms.BooleanField(required=False)
    gear_rando = forms.BooleanField(required=False)
    epoch_fail = forms.BooleanField(required=False)
    enemy_difficulty = forms.CharField(max_length=6)
    item_difficulty = forms.CharField(max_length=6)
    shop_prices = forms.CharField(max_length=13)
    tech_rando = forms.CharField(max_length=15)
    game_mode = forms.CharField(max_length=15)

    # Character rando tab
    char_rando_assignments = forms.CharField(
        widget=forms.HiddenInput(), required=False
    )
    duplicate_characters = forms.BooleanField(required=False)
    duplicate_duals = forms.BooleanField(required=False)

    # Boss rando tab
    legacy_boss_placement = forms.BooleanField(required=False)
    boss_spot_hp = forms.BooleanField(required=False)

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

    # Extra
    bucket_list = forms.BooleanField(required=False)
    starters_sufficient = forms.BooleanField(required=False)
    use_antilife = forms.BooleanField(required=False)
    tackle_effects = forms.BooleanField(required=False)
    tech_damage_rando = forms.BooleanField(required=False)

    # All of the logic tweak flags on the Extra tab
    unlocked_skyways = forms.BooleanField(required=False)
    add_sunkeep_spot = forms.BooleanField(required=False)
    add_bekkler_spot = forms.BooleanField(required=False)
    add_cyrus_spot = forms.BooleanField(required=False)
    restore_tools = forms.BooleanField(required=False)
    add_ozzie_spot = forms.BooleanField(required=False)
    restore_johnny_race = forms.BooleanField(required=False)
    add_racelog_spot = forms.BooleanField(required=False)
    remove_black_omen_spot = forms.BooleanField(required=False)
    split_arris_dome = forms.BooleanField(required=False)
    rocksanity = forms.BooleanField(required=False)
    vanilla_robo_ribbon = forms.BooleanField(required=False)
    vanilla_desert = forms.BooleanField(required=False)

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
    mystery_bucket_list = forms.IntegerField()
    mystery_chronosanity = forms.IntegerField()
    mystery_boss_rando = forms.IntegerField()
    mystery_boss_scale = forms.IntegerField()
    mystery_locked_characters = forms.IntegerField()
    mystery_char_rando = forms.IntegerField()
    mystery_duplicate_characters = forms.IntegerField()
    mystery_epoch_fail = forms.IntegerField()
    mystery_gear_rando = forms.IntegerField()
    mystery_heal_rando = forms.IntegerField()

    # bucket
    bucket_num_objs = forms.IntegerField()
    bucket_num_objs_req = forms.IntegerField()
    bucket_disable_go_modes = forms.BooleanField(required=False)
    bucket_obj_win_game = forms.BooleanField(required=False)

    bucket_objective1 = forms.CharField(required=False)
    bucket_objective2 = forms.CharField(required=False)
    bucket_objective3 = forms.CharField(required=False)
    bucket_objective4 = forms.CharField(required=False)
    bucket_objective5 = forms.CharField(required=False)
    bucket_objective6 = forms.CharField(required=False)
    bucket_objective7 = forms.CharField(required=False)
    bucket_objective8 = forms.CharField(required=False)

