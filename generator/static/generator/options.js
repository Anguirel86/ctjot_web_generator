/*
 * This file contains the javascript functions for working with
 * the game options, including preset and validation functions.
 */

const charIdentities = ['Crono', 'Marle', 'Lucca', 'Robo', 'Frog', 'Ayla', 'Magus'];
const charModels = ['0', '1', '2', '3', '4', '5', '6'];

/*
 * Initialize some UI settings when page (re-)loaded.
 */
function initAll() {
  let options = ['char_rando', 'boss_rando', 'mystery_seed', 'bucket_list'];
  options.forEach((option) => toggleOptions(option));
  restrictFlags();
}
$(document).ready(initAll);

/*
 * Reset all form inputs to default values.
 */
function resetAll() {
  // direct focus back to General tab
  $('a[href="#options-general"]').tab('show');

  // General options
  $('#id_enemy_difficulty').val('normal');
  $('#id_item_difficulty').val('normal');
  $('#id_game_mode').val('standard').change();
  $('#id_disable_glitches').prop('checked', false).change();
  $('#id_lost_worlds').prop('checked', false).change();
  $('#id_boss_scaling').prop('checked', false).change();
  $('#id_early_pendant').prop('checked', false).change();
  $('#id_unlocked_magic').prop('checked', false).change();
  $('#id_chronosanity').prop('checked', false).change();
  $('#id_boss_rando').prop('checked', false).change();
  $('#id_zeal').prop('checked', false).change();
  $('#id_locked_chars').prop('checked', false).change();
  $('#id_tab_treasures').prop('checked', false).change();
  $('#id_shop_prices').val('normal');
  $('#id_tech_rando').val('normal');
  $('#id_char_rando').prop('checked', false).change();
  $('#id_healing_item_rando').prop('checked', false).change();
  $('#id_gear_rando').prop('checked', false).change();
  $('#id_mystery_seed').prop('checked', false).change();
  $('#id_spoiler_log').prop('checked', true).change();
  $('#id_epoch_fail').prop('checked', false).change();

  // Tabs options
  $('#id_power_tab_min').val(2).change();
  $('#id_power_tab_max').val(4).change();
  $('#id_magic_tab_min').val(1).change();
  $('#id_magic_tab_max').val(3).change();
  $('#id_speed_tab_min').val(1).change();
  $('#id_speed_tab_max').val(1).change();

  // Character Rando options
  $('#id_duplicate_characters').prop('checked', false).change();
  $('#id_duplicate_duals').prop('checked', false).change();
  rcCheckAll();

  // Boss Rando options
  $('#id_legacy_boss_placement').prop('checked', false).change();
  $('#id_boss_spot_hp').prop('checked', false).change();

  // Quality of Life options
  $('#id_sightscope_always_on').prop('checked', false).change();
  $('#id_boss_sightscope').prop('checked', false).change();
  $('#id_fast_tabs').prop('checked', false).change();
  $('#id_free_menu_glitch').prop('checked', false).change();

  // Extra options
  $('#id_use_antilife').prop('checked', false).change();
  $('#id_tackle_effects').prop('checked', false).change();
  $('#id_starters_sufficient').prop('checked', false).change();
  $('#id_bucket_list').prop('checked', false).change();
  $('#id_rocksanity').prop('checked', false).change();
  $('#id_tech_damage_rando').prop('checked', false).change();

  // Mystery Seed options
  // game modes
  $('#id_mystery_game_mode_standard').val(75).change();
  $('#id_mystery_game_mode_lw').val(25).change();
  $('#id_mystery_game_mode_loc').val(0).change();
  $('#id_mystery_game_mode_ia').val(0).change();
  // item difficulty
  $('#id_mystery_item_difficulty_easy').val(15).change();
  $('#id_mystery_item_difficulty_normal').val(70).change();
  $('#id_mystery_item_difficulty_hard').val(15).change();
  // enemy difficulty
  $('#id_mystery_enemy_difficulty_normal').val(75).change();
  $('#id_mystery_enemy_difficulty_hard').val(25).change();
  // tech order
  $('#id_mystery_tech_order_normal').val(10).change();
  $('#id_mystery_tech_order_full_random').val(80).change();
  $('#id_mystery_tech_order_balanced_random').val(10).change();
  // shop prices
  $('#id_mystery_shop_prices_normal').val(70).change();
  $('#id_mystery_shop_prices_random').val(10).change();
  $('#id_mystery_shop_prices_mostly_random').val(10).change();
  $('#id_mystery_shop_prices_free').val(10).change();
  // flag probabilities
  $('#id_mystery_tab_treasures').val(10).change();
  $('#id_mystery_unlock_magic').val(50).change();
  $('#id_mystery_bucket_list').val(15).change();
  $('#id_mystery_chronosanity').val(30).change();
  $('#id_mystery_boss_rando').val(50).change();
  $('#id_mystery_boss_scale').val(30).change();
  $('#id_mystery_locked_characters').val(25).change();
  $('#id_mystery_char_rando').val(50).change();
  $('#id_mystery_duplicate_characters').val(25).change();
  $('#id_mystery_epoch_fail').val(50).change();
  $('#id_mystery_gear_rando').val(25).change();
  $('#id_mystery_heal_rando').val(25).change();

  // Bucket Settings
  $('#id_bucket_num_objs').val(5).change();
  $('#id_bucket_num_objs_req').val(4).change();
  updateObjectiveCount();

  initAll();
}

/*
 * Populate the options form with the settings for a standard race seed.
 */
function presetRace() {
  resetAll();
  $('#id_enemy_difficulty').val('normal');
  $('#id_item_difficulty').val('normal');
  $('#id_disable_glitches').prop('checked', true).change();
  $('#id_zeal').prop('checked', true).change();
  $('#id_early_pendant').prop('checked', true).change();
  $('#id_tech_rando').val('fully_random');
}

/*
 * Populate the options form with the settings for a new player seed.
 */
function presetNewPlayer() {
  resetAll();
  $('#id_enemy_difficulty').val('normal');
  $('#id_item_difficulty').val('easy');
  $('#id_disable_glitches').prop('checked', true).change();
  $('#id_zeal').prop('checked', true).change();
  $('#id_early_pendant').prop('checked', true).change();
  $('#id_unlocked_magic').prop('checked', true).change();
  $('#id_tech_rando').val('fully_random');
}

/*
 *Populate the options form with the settings for a lost worlds seed.
 */
function presetLostWorlds() {
  resetAll();
  $('#id_enemy_difficulty').val('normal');
  $('#id_item_difficulty').val('normal');
  $('#id_game_mode').val('lost_worlds').change();
  $('#id_disable_glitches').prop('checked', true).change();
  $('#id_zeal').prop('checked', true).change();
  $('#id_tech_rando').val('fully_random');
}

/*
 *Populate the options form with the settings for a hard seed.
 */
function presetHard() {
  resetAll();
  $('#id_enemy_difficulty').val('hard');
  $('#id_item_difficulty').val('hard');
  $('#id_disable_glitches').prop('checked', true).change();
  $('#id_boss_scaling').prop('checked', true).change();
  $('#id_locked_chars').prop('checked', true).change();
  $('#id_tech_rando').val('balanced_random');
}

/*
 *Populate the options form with the settings for a hard seed.
 */
function presetLegacyOfCyrus() {
  resetAll();
  $('#id_game_mode').val('legacy_of_cyrus').change();
  $('#id_enemy_difficulty').val('normal');
  $('#id_item_difficulty').val('normal');
  $('#id_disable_glitches').prop('checked', true).change();
  $('#id_early_pendant').prop('checked', true).change();
  $('#id_unlocked_magic').prop('checked', true).change();
  $('#id_gear_rando').prop('checked', true).change();
  $('#id_fast_tabs').prop('checked', true).change();
  $('#id_tech_rando').val('fully_random');
}

/*
 * Populate the options form with the settings for a Catalack Cup tournament seed.
 * The Catalack Cup preset buttons have been removed, but the functions are being left
 * in in case they are ever needed again.
 */
 function presetTourney() {
  resetAll();
  $('#id_item_difficulty').val('normal');
  $('#id_tech_rando').val('fully_random');
  $('#id_shop_prices').val('normal');
  $('#id_disable_glitches').prop('checked', true).change();
  $('#id_zeal').prop('checked', true).change();
  $('#id_early_pendant').prop('checked', true).change();
  $('#id_boss_rando').prop('checked', true).change();
  $('#id_boss_spot_hp').prop('checked', true).change();
  $('#id_fast_tabs').prop('checked', true).change();
  $('#id_free_menu_glitch').prop('checked', true).change();
  $('#id_healing_item_rando').prop('checked', true).change();
  $('#id_gear_rando').prop('checked', true).change();
 }

 function presetTourneyTop8() {
   presetTourney();
   $('#id_item_difficulty').val('hard');
   $('#id_free_menu_glitch').prop('checked', false).change();
 }

/*
 * Check all of the character rando assignment boxes.
 */
function rcCheckAll() {
  charIdentities.forEach((identity) => {
    charModels.forEach((model) => $('#rc_' + identity + model).prop('checked', true));
  });
}

/*
 * Uncheck all of the character rando assignment boxes.
 */
function rcUncheckAll() {
  charIdentities.forEach((identity) => {
    charModels.forEach((model) => $('#rc_' + identity + model).prop('checked', false));
  });
}

/*
 * Encode the character choices into the hidden form field.
 * Each character is represented by a 2 digit hex string where the
 * bit index represents the character ID. ie:
 *   0x17 - The character can become:
 *      Crono, Marle, Lucca, or Frog.
 */
function encodeCharRandoChoices() {
  var encodedString = "";
  charIdentities.forEach((identity) => {
    let currentCharValue = 0;
    charModels.forEach((model, i) => {
      if ($('#rc_' + identity + model).prop('checked')) {
        currentCharValue = currentCharValue + (1 << i);
      }
    });

    if ((currentCharValue & 0xFF) < 0x10) {
      // Pad the string with a zero if needed so that the
      // final string is 14 characters.
      encodedString += "0";
    }
    encodedString += (currentCharValue & 0xFF).toString(16);
  });
  $('#id_char_rando_assignments').val(encodedString);
}

/*
 * Validate that the user's choices for character rando are valid.
 * Each character identity needs to have at least one character model they can turn into.
 * Unless duplicate characters is used, also ensure that each model has at
 * least one character identity they can use.
 */
function validateCharRandoChoices() {
  // ensure each character identity has at least one character model associated
  modelMissing = charIdentities.some(identity => {
    return !charModels.some(model => $('#rc_' + identity + model).prop('checked'));
  });
  if (modelMissing) {
    $('#character_selection_error').html("Each identity (row) must have at least one model (column) selected.");
    $('a[href="#options-rc"]').tab('show');
    $('#character_selection_matrix').collapse('show');
    return false;
  }

  let duplicateCharsChecked = $('#id_duplicate_characters').prop('checked');
  if (!duplicateCharsChecked) {
    // ensure each character model has at least one character identity associated
    identityMissing = charModels.some(model => {
      return !charIdentities.some(identity => $('#rc_' + identity + model).prop('checked'));
    });
    if (identityMissing) {
      $('#character_selection_error').html("Each model (column) must have at least one identity (row) selected.");
      $('a[href="#options-rc"]').tab('show');
      $('#character_selection_matrix').collapse('show');
      return false;
    }
  }
  $('#character_selection_error').html("");
  return true;
}

/*
 * Pre-submit preparation for the form.
 *   - Validate character rando choices
 *   - Populate the hidden field with character rando information
 */
function prepareForm() {
  if (!validateCharRandoChoices()) {
    return false;
  }
  encodeCharRandoChoices();

  if (!validateLogicTweaks())
      return false;

  if (!validateAndUpdateObjectives()){return false;}
  return true;
}

/*
 * Called when a tab range slider is changed.  Update all tab values on the page.
 */
function updateAllTabValues(adjustMin = false) {
  updateTabValuesFromRange("id_power_tab_min", "id_power_tab_max", "power_tab_min_text", "power_tab_max_text", adjustMin);
  updateTabValuesFromRange("id_magic_tab_min", "id_magic_tab_max", "magic_tab_min_text", "magic_tab_max_text", adjustMin);
  updateTabValuesFromRange("id_speed_tab_min", "id_speed_tab_max", "speed_tab_min_text", "speed_tab_max_text", adjustMin);
}

/*
 * Update the min/max values of a tab based on range slider input.
 * Perform some basic validation to make sure the values make sense.
 */
function updateTabValuesFromRange(rangeMin, rangeMax, textMin, textMax, adjustMin) {
  var min = document.getElementById(rangeMin).value;
  var max = document.getElementById(rangeMax).value;

  if (min > max) {
    if (adjustMin) {
      min = max
    } else {
      max = min;
    }
  }

  document.getElementById(textMin).value = min;
  document.getElementById(textMax).value = max;
  document.getElementById(rangeMin).value = min;
  document.getElementById(rangeMax).value = max;
}

/*
 * Update the mystery flags slider text boxes.
 */
function updateMysterySettings() {
  var id_list_relative = ['mystery_game_mode_standard', 'mystery_game_mode_lw', 'mystery_game_mode_loc', 'mystery_game_mode_ia',
    'mystery_item_difficulty_easy', 'mystery_item_difficulty_normal', 'mystery_item_difficulty_hard',
    'mystery_enemy_difficulty_normal', 'mystery_enemy_difficulty_hard',
    'mystery_tech_order_normal', 'mystery_tech_order_full_random', 'mystery_tech_order_balanced_random',
    'mystery_shop_prices_normal', 'mystery_shop_prices_random', 'mystery_shop_prices_mostly_random', 'mystery_shop_prices_free'];
  var id_list_percentage = ['mystery_tab_treasures', 'mystery_unlock_magic', 'mystery_bucket_list', 'mystery_chronosanity',
    'mystery_boss_rando', 'mystery_boss_scale', 'mystery_locked_characters', 'mystery_char_rando', 'mystery_duplicate_characters',
    'mystery_epoch_fail', 'mystery_gear_rando', 'mystery_heal_rando'];

  for (const id of id_list_relative) {
    document.getElementById(id + "_text").value = document.getElementById("id_" + id).value
  }

  for (const id of id_list_percentage) {
    document.getElementById(id + "_text").value = document.getElementById("id_" + id).value + "%"
  }
}

/*
 * Set the visibility of an options section.
 */
function toggleOptions(option) {
  let optionSelected = $('#id_' + option).prop('checked');
  let optionNav = $('#id_' + option + '_nav');

  if (optionSelected) {
    optionNav.removeClass('disabled');
    optionNav.prop('disabled', false);
  } else {
    optionNav.addClass('disabled');
    optionNav.prop('disabled', true);
  }
}

// All broken code goes below this line
// Adding Bucket-specific functions and data

/*
 * Ensure that the number of objectives and the
 */
function updateObjectiveCount(adjustingRequired = false){

    numObjs = document.getElementById("id_bucket_num_objs").value
    reqObjs = document.getElementById("id_bucket_num_objs_req").value

    if (reqObjs > numObjs){
        if (adjustingRequired) {numObjs = reqObjs}
        else {reqObjs = numObjs}
    }

    document.getElementById("id_bucket_num_objs").value = numObjs
    document.getElementById("numObjectivesDisp").value = numObjs
    document.getElementById("id_bucket_num_objs_req").value = reqObjs
    document.getElementById("numObjectivesRequiredDisp").value = reqObjs

    // Now enable/disable the objective entries according to numObjs
    for(var i=0; i<8; i++){
        var isDisabled = true
        if (i < numObjs){isDisabled = false}
        document.getElementById("objEntry"+(i+1)).disabled = isDisabled
    }
}

// Parsing objectives
const objectiveDict = {
    "Random": "65:quest_gated, 30:boss_nogo, 15:recruit_gated",
    "Random Gated Quest": "quest_gated",
    "Random Hard Quest": "quest_late",
    "Random Go Mode Quest": "quest_go",
    "Random Gated Character Recruit": "recruit_gated",
    "Random Boss (Includes Go Mode Dungeons)": "boss_any",
    "Random Boss from Go Mode Dungeon": "boss_go",
    "Random Boss (No Go Mode Dungeons)": "boss_nogo",
    "Recruit a Random Gated Character": "recruit_gated",
    "Recruit 3 Characters (Total 5)": "recruit_3",
    "Recruit 4 Characters (Total 6)": "recruit_4",
    "Recruit 5 Characters (Total 7)": "recruit_5",
    "Collect 10 of 20 Fragments": "collect_10_fragments_20",
    "Collect 10 of 30 Fragments": "collect_10_fragments_30",
    "Collect 3 Rocks": "collect_3_rocks",
    "Collect 4 Rocks": "collect_4_rocks",
    "Collect 5 Rocks": "collect_5_rocks",
    "Forge the Masamune": "quest_forge",
    "Charge the Moonstone": "quest_moonstone",
    "Trade the Jerky Away": "quest_jerky",
    "Defeat the Arris Dome Boss": "quest_arris",
    "Visit Cyrus's Grave with Frog": "quest_cyrus",
    "Defeat the Boss of Death's Peak": "quest_deathpeak",
    "Defeat the Boss of Denadoro Mountains": "quest_denadoro",
    "Gain Epoch Flight": "quest_epoch",
    "Defeat the Boss of the Factory Ruins": "quest_factory",
    "Defeat the Boss of the Geno Dome": "quest_geno",
    "Defeat the Boss of the Giant's Claw": "quest_claw",
    "Defeat the Boss of Heckran's Cave": "quest_heckran",
    "Defeat the Boss of the King's Trial": "quest_shard",
    "Defeat the Boss of Manoria Cathedral": "quest_cathedral",
    "Defeat the Boss of Mount Woe": "quest_woe",
    "Defeat the Boss of the Pendant Trial": "quest_pendant",
    "Defeat the Boss of the Reptite Lair": "quest_reptite",
    "Defeat the Boss of the Sun Palace": "quest_sunpalace",
    "Defeat the Boss of the Sunken Desert": "quest_desert",
    "Defeat the Boss in the Zeal Throneroom": "quest_zealthrone",
    "Defeat the Boss of Zenan Bridge": "quest_zenan",
    "Defeat the Black Tyrano": "quest_blacktyrano",
    "Defeat the Tyrano Lair Midboss": "quest_tyranomid",
    "Defeat the Boss in Flea's Spot": "quest_flea",
    "Defeat the Boss in Slash's Spot": "quest_slash",
    "Defeat Magus in Magus's Castle": "quest_magus",
    "Defeat the Boss in the GigaMutant Spot": "quest_omengiga",
    "Defeat the Boss in the TerraMutant Spot": "quest_omenterra",
    "Defeat the Boss in the ElderSpawn Spot": "quest_omenelder",
    "Defeat the Boss in the Twin Golem Spot": "quest_twinboss",
    "Beat Johnny in a Race": "quest_johnny",
    "Bet on a Fair Race and Win": "quest_fairrace",
    "Play the Fair Drinking Game": "quest_soda",
    "Defeat AtroposXR": "boss_atropos",
    "Defeat DaltonPlus": "boss_dalton",
    "Defeat DragonTank": "boss_dragontank",
    "Defeat ElderSpawn": "boss_elderspawn",
    "Defeat Flea": "boss_flea",
    "Defeat Flea Plus": "boss_fleaplus",
    "Defeat Giga Gaia": "boss_gigagaia",
    "Defeat GigaMutant": "boss_gigamutant",
    "Defeat Golem": "boss_golem",
    "Defeat Golem Boss": "boss_golemboss",
    "Defeat Guardian": "boss_guardian",
    "Defeat Heckran": "boss_heckran",
    "Defeat LavosSpawn": "boss_lavosspawn",
    "Defeat Magus (North Cape)": "boss_magusnc",
    "Defeat Masamune": "boss_masamune",
    "Defeat Mother Brain": "boss_motherbrain",
    "Defeat Mud Imp": "boss_mudimp",
    "Defeat Nizbel": "boss_nizbel",
    "Defeat Nizbel II": "boss_nizbel2",
    "Defeat R-Series": "boss_rseries",
    "Defeat Retinite": "boss_retinite",
    "Defeat RustTyrano": "boss_rusttyrano",
    "Defeat Slash": "boss_slash",
    "Defeat Son of Sun": "boss_sonofsun",
    "Defeat Super Slash": "boss_superslash",
    "Defeat TerraMutant": "boss_terramutant",
    "Defeat Yakra": "boss_yakra",
    "Defeat Yakra XIII": "boss_yakraxiii",
    "Defeat Zombor": "boss_zombor",
    "Recruit Crono": "recruit_crono",
    "Recruit Marle": "recruit_marle",
    "Recruit Lucca": "recruit_lucca",
    "Recruit Robo": "recruit_robo",
    "Recruit Frog": "recruit_frog",
    "Recruit Ayla": "recruit_ayla",
    "Recruit Magus": "recruit_magus",
    "Recruit the Guardia Castle Character": "recruit_castle",
    "Recruit the Dactyl Nest Character": "recruit_dactyl",
    "Recruit the Proto Dome Character": "recruit_proto",
    "Recruit the Frog's Burrow Character": "recruit_burrow"
}

// All quest name tags allowed by the parser.
const allowedQuestTags = [
    'free', 'gated', 'late', 'go',
    'repairmasamune', 'masamune', 'masa', 'forge',
    'chargemoon', 'moon', 'moonstone',
    'arris',
    'jerky',
    'deathpeak', 'death',
    'denadoro',
    'epoch', 'flight', 'epochflight',
    'factory', 'factoryruins',
    'geno', 'genodome',
    'claw', 'giantsclaw',
    'heckran', 'heckranscave', 'heckrancave',
    'kingstrial', 'shard', 'shardtrial', 'prismshard',
    'cathedral', 'cath', 'manoria',
    'woe', 'mtwoe',
    'ocean', 'oceanpalace',
    'ozzie', 'fort', 'ozziefort', 'ozziesfort',
    'pendant', 'pendanttrial',
    'reptite', 'reptitelair',
    'sunpalace', 'sun',
    'desert', 'sunkendesert',
    'zealthrone', 'zealpalace', 'golemspot',
    'zenan', 'bridge', 'zenanbridge',
    'tyrano', 'blacktyrano', 'azala',
    'tyranomid', 'nizbel2spot',
    'magus', 'maguscastle',
    'omengiga', 'gigamutant', 'gigaspot',
    'omenterra', 'terramutant', 'terraspot',
    'flea', 'magusflea',
    'slash', 'magusslash',
    'omenelder', 'elderspawn', 'elderspot',
    'twinboss', 'twingolem', 'twinspot',
    'cyrus', 'nr', 'northernruins',
    'johnny', 'johnnyrace',
    'fairrace', 'fairbet',
    'soda', 'drink',
]

/*
 * Helper function to parse a quest objective.
 * param questParts, Array: An objective (e.g. 'Quest_ZenanBridge') has been cleaned and turned into
 * the array ['quest', 'zenanbridge'] which is passed in as questParts.
 */
function validateQuestObjective(questParts){

    if (questParts.length != 2){
        return false
    }
    if (!allowedQuestTags.includes(questParts[1])){
        return false
    }

    return true
}

/*
 * Helper function to parse a boss objective.
 * param bossParts, Array: An objective (e.g. 'Boss_MotherBrain') has been
 * cleaned and turned into the array ['boss', 'motherbrain'] which is passed
 * in as bossParts.
 */
const allowedBossNames = [
    'any', 'go', 'nogo',
    'atropos', 'atroposxr', 'dalton', 'daltonplus', 'dalton+',
    'dragontank', 'dtank', 'elderspawn', 'elder', 'flea', 'fleaplus', 'flea+',
    'gigagaia', 'gg', 'gigamutant', 'golem', 'bossgolem', 'golemboss',
    'guardian', 'heckran', 'lavosspawn', 'magusnc', 'ncmagus', 'masamune', 'masa&mune',
    'megamutant', 'motherbrain', 'mudimp', 'nizbel', 'nizbel2', 'nizbelii',
    'rseries', 'retinite', 'rusty', 'rusttyrano', 'slash', 'sos', 'sonofsun',
    'superslash', 'terramutant', // 'twinboss', handled in quests
    'yakra', 'yakraxiii', 'yakra13', 'zombor'
]

function validateBossObjective(bossParts){
    if (bossParts.length != 2){
        return false
    }

    return allowedBossNames.includes(bossParts[1])
}

const allowedRecruitNames = [
    'any', 'gated',
    'crono', 'marle', 'lucca', 'robo', 'frog', 'ayla', 'magus',
    'castle', 'dactyl', 'proto', 'burrow',
    '1', '2', '3', '4', '5'
]

/*
 * Helper function to parse a recruit objective.
 * param recruitParts, Array: An objective (e.g. 'Recruit_Crono') has been
 * cleaned and split into an array (['recruit', 'crono']) which is passed
 * in as recruitParts.
 */
 function validateRecruitObjective(recruitParts){
    if (recruitParts.length != 2){return false}

    return allowedRecruitNames.includes(recruitParts[1])
 }

/*
 * function which determines whether the given string is actually an integer
 * which is strictly greater than some threshold (param greaterThan)
 */
function isInteger(string){
    const num = Number(string)
    return Number.isInteger(num)
}

/*
 * Helper function to parse a recruit objective.
 * param collectParts, Array: An objective (e.g. 'Collect_5_Fragments_5') has
 * been cleaned and split into an array (['collect', '5', 'fragments', '5'])
 * which is passed in as recruitParts.
 */
function validateCollectObjective(collectParts){
    if (collectParts.length < 2){
        return false
    }
    collectType = collectParts[2]
    if (collectType == 'rocks'){
        if (collectParts.length != 3){return false}
        numRocks = Number(collectParts[1])
        if (!Number.isInteger(numRocks) || numRocks < 1){return false}
    } else if (collectType == 'fragments'){
        if (collectParts.length != 4){return false}

        fragsNeeded = Number(collectParts[1])
        extraFrags = Number(collectParts[3])

        if (!Number.isInteger(fragsNeeded) || fragsNeeded < 0){return false}
        if (!Number.isInteger(extraFrags) || extraFrags < 0){return false}
    } else {
        // Unrecognized collection type
        return false
    }
    return true
}

/*
 * Validate a single objective hint.
 */
function validateObjective(objective){
    // If the user used a preset in the entry box, then use the dict above to resolve it.
    cleanedObjective = objective.toLowerCase()
    for(var key in objectiveDict){
        if (objectiveDict.hasOwnProperty(key) && key.toLowerCase() == cleanedObjective){
            return {isValid: true, result: objectiveDict[key]}
        }
    }

    // Otherwise, parse the objective
    cleanedObjective = objective.replace(/\s/g,'')

    if (cleanedObjective == ''){
        // Do something to display an error on the page for an empty objective string
        return {isValid: false, result: "Empty objective string."}
    }

    objectiveParts = cleanedObjective.split(',')
    for (var i = 0; i < objectiveParts.length; i++){
        objectivePart = objectiveParts[i]
        // split into weight:objective if possible
        weightSplit = objectivePart.split(':')
        if (weightSplit.length > 2){
            // Some error message about unexpected ':'
            return {
                isValid: false,
                result: "Too many ':' in "+objectivePart+". Format is 'weight1:obj_text1, weight2:obj_text2, ..."
            }
        } else if (weightSplit.length == 2) {
            // If there was a weight, verify it's an integer
            weight = weightSplit[0]
            if (!isInteger(weight) || Number(weight) < 0){
                return {isValid: false, result: "Weight '"+weight+"' is not a positive integer"}
            }
            // Overwrite objectivePart with just the objective, not the weight
            objectivePart = weightSplit[1]
        }

        splitObjective = objectivePart.split('_')
        objectiveType = splitObjective[0]

        if (objectiveType == 'quest'){
            ret = validateQuestObjective(splitObjective)
        } else if (objectiveType == 'boss'){
            ret = validateBossObjective(splitObjective)
        } else if (objectiveType == 'recruit'){
            ret = validateRecruitObjective(splitObjective)
        } else if (objectiveType == 'collect'){
            ret = validateCollectObjective(splitObjective)
        } else {
            // invalid objective type
            return {isValid: false, result: "Invalid objective type: "+objectiveType}
        }
        if (!ret){
            return {
                isValid: false,
                result: "Could not resolve "+objectivePart
            }
        }
    }

    return {isValid: true, result: cleanedObjective}
}

/*
 * Get the objectives from the entries, parse them, and put them in the actual
 * form fields.
 */
function validateAndUpdateObjectives(){
    var bucketList = document.getElementById("id_bucket_list").checked
    if (!bucketList){return true}

    var numObjs = document.getElementById("id_bucket_num_objs").value

    var retFalse = false
    for(var i = 0; i<Number(numObjs); i++){
        elementId = 'objEntry'+(i+1)
        objective = document.getElementById(elementId).value
        const parse = validateObjective(objective)
        const isValid = parse.isValid
        const result = parse.result

        if (isValid){
            const formElementId = 'id_bucket_objective'+(i+1)
            document.getElementById(formElementId).value = result

            const errorElementId = 'objError'+(i+1)
            document.getElementById(errorElementId).innerHTML = ""
        }
        else{
            const errorElementId = 'objError'+(i+1)
            document.getElementById(errorElementId).innerHTML = result
            $('a[href="#options-bucket"]').tab('show');
            retFalse = true
        }

    }

    if (retFalse){
        return false
    }

    for(var i=Number(numObjs); i<8; i++){
        formElementId = 'id_bucket_objective'+(i+1)
        document.getElementById(formElementId).value = 'None'
    }
    return true
}

/*
 * Ensure that there are enough KI Spots to support added KIs
 */
function validateLogicTweaks(){
    const addKiNames = ['restore_johnny_race', 'restore_tools', 'epoch_fail']
    const addSpotNames = ['add_bekkler_spot', 'add_ozzie_spot',
                          'add_racelog_spot', 'vanilla_robo_ribbon',
                          'add_cyrus_spot']

    var numKIs = 0
    for(var i=0; i<addKiNames.length; i++){
        const name = addKiNames[i]
        const id = 'id_'+name

        const isChecked = document.getElementById(id).checked
        if (isChecked){numKIs++}

    }

    var numSpots = 0
    for(var i=0; i<addSpotNames.length; i++){
        const name = addSpotNames[i]
        const id = 'id_'+name

        const isChecked = document.getElementById(id).checked
        if (isChecked){numSpots++}
    }

    // There can be one more KI than spot because we just erase Jerky
    if (numKIs-1 > numSpots){
        document.getElementById("logicTweakError").innerHTML =
            "Select Additional Key Item Spots"
        $('a[href="#options-extra"]').tab('show');
        return false
    }

    document.getElementById("logicTweakError").innerHTML = ""
    return true

}

const forceOff = {
    "standard": [],
    "lost_worlds": ["boss_scaling", "bucket_list", "epoch_fail",
                    "add_bekkler_spot", "add_cyrus_spot", "add_ozzie_spot",
                    "add_racelog_spot", "add_sunkeep_spot",
                    "restore_johnny_race", "split_arris_dome",
                    "restore_tools", "unlocked_skyways",
                    "vanilla_desert", "vanilla_robo_ribbon"],
    "ice_age": ["zeal", "boss_scaling", "bucket_list"],
    "legacy_of_cyrus": ["zeal", "boss_scale", "bucket_list",
                        "add_ozzie_spot", "add_cyrus_spot",
                        "add_sunkeep_spot", "restore_tools",
                        "restore_johnny_race", "split_arris_dome",
                        "add_racelog_spot", "add_bekkler_spot"],
    "vanilla_rando": ["boss_scaling"]
}

// Const way to iterate over the keys of forceOff?
const totalForceList = [
    ... new Set([...forceOff["standard"],
                 ...forceOff["lost_worlds"],
                 ...forceOff["ice_age"],
                 ...forceOff["legacy_of_cyrus"],
                 ...forceOff["vanilla_rando"]])
]

/*
 * Unset and disable flags based on the chosen game mode.  Restore them if the
 * mode permits.
 */
function restrictFlags(){
    var mode = document.getElementById("id_game_mode").value
    var disableList = forceOff[mode]

    for(var i=0; i<totalForceList.length; i++){
        flag = totalForceList[i]

        if(disableList.includes(flag)){
            $("#id_"+flag).parent().addClass('btn-light off disabled')
            $("#id_"+flag).parent().removeClass('btn-primary')
            $("#id_"+flag).prop('checked', false)
            $("#id_"+flag).prop('disabled', true)
        }
        else{
            $("#id_"+flag).parent().removeClass('disabled')
            $("#id_"+flag).prop('disabled', false)
        }
    }
}
