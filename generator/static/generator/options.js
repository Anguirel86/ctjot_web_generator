/*
 * This file contains the javascript functions for working with
 * the game options, including preset and validation functions.
 */


/*
 * Reset all form inputs to default values.
 */
function resetAll() {
  // General options
  $('#id_enemy_difficulty').val('normal');
  $('#id_item_difficulty').val('normal');
  $('#id_game_mode').val('standard')
  $('#id_disable_glitches').prop('checked', false).change();
  $('#id_lost_worlds').prop('checked', false).change();
  $('#id_boss_scaling').prop('checked', false).change();
  $('#id_early_pendant').prop('checked', false).change();
  $('#id_unlocked_magic').prop('checked', false).change();
  $('#id_chronosanity').prop('checked', false).change();
  $('#id_quiet_mode').prop('checked', false).change();
  $('#id_boss_rando').prop('checked', false).change();
  $('#id_zeal').prop('checked', false).change();
  $('#id_locked_chars').prop('checked', false).change();
  $('#id_tab_treasures').prop('checked', false).change();
  $('#id_shop_prices').val('normal');
  $('#id_tech_rando').val('normal');
  $('#id_duplicate_characters').prop('checked', false).change();
  $('#id_mystery_seed').prop('checked', false).change();
  $('#id_spoiler_log').prop('checked', true).change();

  // Tabs options
  $('#id_power_tab_min').val(2).change();
  $('#id_power_tab_max').val(4).change();
  $('#id_magic_tab_min').val(1).change();
  $('#id_magic_tab_max').val(3).change();
  $('#id_speed_tab_min').val(1).change();
  $('#id_speed_tab_max').val(1).change();

  // Duplicate Characters options
  $('#id_duplicate_duals').prop('checked', false).change();
  dcCheckAll();

  // Boss Rando options
  $('#id_legacy_boss_placement').prop('checked', false).change();

  // Quality of Life options
  $('#id_sightscope_always_on').prop('checked', false).change();
  $('#id_boss_sightscope').prop('checked', false).change();
  $('#id_fast_tabs').prop('checked', false).change();
  $('#id_free_menu_glitch').prop('checked', false).change();

  // Cosmetic options
  $('#id_zenan_alt_battle_music').prop('checked', false).change();
  $('#id_death_peak_alt_music').prop('checked', false).change();

  // Experimental options
  $('#id_guaranteed_drops').prop('checked', false).change();
  $('#id_buff_x_strike').prop('checked', false).change();
  $('#id_ayla_rebalance').prop('checked', false).change();
  $('#id_black_hole_rework').prop('checked', false).change();
  $('#id_no_crisis_tackle').prop('checked', false).change();
  $('#id_healing_item_rando').prop('checked', false).change();
  $('#id_gear_rando').prop('checked', false).change();
  $('#id_bucket_fragments').prop('checked', false).change();
  $('#id_fragments_required').val(20).change();
  $('#id_extra_fragments').val(10).change();

  // Mystery Seed options
  // game modes
  $('#id_mystery_game_mode_standard').val(75).change()
  $('#id_mystery_game_mode_lw').val(25).change()
  $('#id_mystery_game_mode_loc').val(0).change()
  $('#id_mystery_game_mode_ia').val(0).change()
  // item difficulty
  $('#id_mystery_item_difficulty_easy').val(15).change()
  $('#id_mystery_item_difficulty_normal').val(70).change()
  $('#id_mystery_item_difficulty_hard').val(15).change()
  // enemy difficulty
  $('#id_mystery_enemy_difficulty_normal').val(75).change()
  $('#id_mystery_enemy_difficulty_hard').val(25).change()
  // tech order
  $('#id_mystery_tech_order_normal').val(10).change()
  $('#id_mystery_tech_order_full_random').val(80).change()
  $('#id_mystery_tech_order_balanced_random').val(10).change()
  // shop prices
  $('#id_mystery_shop_prices_normal').val(70).change()
  $('#id_mystery_shop_prices_random').val(10).change()
  $('#id_mystery_shop_prices_mostly_random').val(10).change()
  $('#id_mystery_shop_prices_free').val(10).change()
  // flag probabilities
  $('#id_mystery_tab_treasures').val(10).change()
  $('#id_mystery_unlock_magic').val(50).change()
  $('#id_mystery_bucket_fragments').val(15).change()
  $('#id_mystery_chronosanity').val(30).change()
  $('#id_mystery_boss_rando').val(50).change()
  $('#id_mystery_boss_scale').val(30).change()
  $('#id_mystery_locked_characters').val(25).change()
  $('#id_mystery_duplicate_characters').val(25).change()
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
  $('#id_game_mode').val('lost_worlds')
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
 * Check all of the duplicate character boxes.
 */
function dcCheckAll() {
  let characters = ['Crono', 'Marle', 'Lucca', 'Robo', 'Frog', 'Ayla', 'Magus'];
  for (var charId = 0; charId < characters.length; charId++) {
    for (var i = 0; i < 7; i++) {
      $('#dc_' + characters[charId] + i.toString()).prop('checked', true);
    }
  }
}

/*
 * Uncheck all of the duplicate character boxes.
 */
function dcUncheckAll() {
  let characters = ['Crono', 'Marle', 'Lucca', 'Robo', 'Frog', 'Ayla', 'Magus'];
  for (var charId = 0; charId < characters.length; charId++) {
    for (var i = 0; i < 7; i++) {
      $('#dc_' + characters[charId] + i.toString()).prop('checked', false);
    }
  }
}

/*
 * Set the visibility of the Duplicate Characters options section.
 */
function toggleDCOptions() {
  var dupCharsSelected = $('id_duplicate_characters').prop('checked')
  document.getElementById('dcOptionsButton').disabled = !(dupCharsSelected);
  
  // Hide the duplicate character options div if the duplicate characters 
  // checkbox is unselected. 
  if (!dupCharsSelected) {
    $('#dup_char_options').collapse("hide");
  }
}

/*
 * Encode the character choices into the hidden form field.
 * Each character is represented by a 2 digit hex string where the
 * bit index represents the character ID. ie:
 *   0x17 - The character can become:
 *      Crono, Marle, Lucca, or Frog. 
 */
function encodeDuplicateCharacterChoices() {
  var encodedString = "";
  let characters = ['Crono', 'Marle', 'Lucca', 'Robo', 'Frog', 'Ayla', 'Magus'];
  for (var charId = 0; charId < characters.length; charId++) {
    var currentCharValue = 0;
    for (var i = 0; i < 7; i++) {
      if ($('#dc_' + characters[charId] + i.toString()).prop('checked')) {
        currentCharValue = currentCharValue + (1 << i);
      }
    }
    
    if ((currentCharValue & 0xFF) < 0x10) {
      // Pad the string with a zero if needed so that the 
      // final string is 14 characters.
      encodedString += "0";
    }
    encodedString += (currentCharValue & 0xFF).toString(16);
  }
  
  $('#id_duplicate_char_assignments').val(encodedString);
}

/*
 * Validate that the user's choices for duplicate characters are valid.
 * Each character needs to have at least one character they can turn into.
 */
function validateDupCharChoices() {
  let characters = ['Crono', 'Marle', 'Lucca', 'Robo', 'Frog', 'Ayla', 'Magus'];
  for (var charId = 0; charId < characters.length; charId++) {
    var selectionFound = false;
    for (var i = 0; i < 7; i++) {
      if ($('#dc_' + characters[charId] + i.toString()).prop('checked')) {
        selectionFound = true;
        break;
      }
    }
    if (!selectionFound) {
      $('#character_selection_error').html("Each row must have at least one selection.");
      $('#dup_char_options').collapse("show");
      return false;
    }
  }
  $('#character_selection_error').html("");
  return true;
}

/*
 * Pre-submit preparation for the form.
 *   - Validate duplicate character choices
 *   - Populate the hidden field with duplicate character information
 */
function prepareForm() {
  if (!validateDupCharChoices()) {
    return false;
  }
  encodeDuplicateCharacterChoices();
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
 * Update the text box for the number of required bucket fragments on change of the range slider.
 */
function setFragmentsRequired() {
  document.getElementById("fragments_required_text").value = document.getElementById("id_fragments_required").value
}

/*
 * Update the text box for the number of extra bucket fragments on change of the range slider.
 */
function setExtraFragments() {
  document.getElementById("extra_fragments_text").value = document.getElementById("id_extra_fragments").value
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
  var id_list_percentage = ['mystery_tab_treasures', 'mystery_unlock_magic', 'mystery_bucket_fragments', 'mystery_chronosanity',
    'mystery_boss_rando', 'mystery_boss_scale', 'mystery_locked_characters', 'mystery_duplicate_characters'];

  for (const id of id_list_relative) {
    document.getElementById(id + "_text").value = document.getElementById("id_" + id).value
  }

  for (const id of id_list_percentage) {
    document.getElementById(id + "_text").value = document.getElementById("id_" + id).value + "%"
  }
}