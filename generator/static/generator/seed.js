// Change the spoiler log button between "Show" and "Hide"
$(document).on('show.bs.collapse', '#spoiler_section', function(e) {
  document.getElementById('spoiler_log_button').value = 'Hide Spoiler Log';
});

$(document).on('hide.bs.collapse', '#spoiler_section', function(e) {
  document.getElementById('spoiler_log_button').value = 'Show Spoiler Log';
});

// Change the cosmetic options button between "Show" and "Hide"
$(document).on('show.bs.collapse', '#cosmetic_section', function(e) {
  document.getElementById('cosmetic_options_button').value = 'Hide Cosmetic Options';
});

$(document).on('hide.bs.collapse', '#cosmetic_section', function(e) {
  document.getElementById('cosmetic_options_button').value = 'Show Cosmetic Options';
});

/*
 * Update the game options section of the seed page.
 */
function updateGameOptions() {

  // Update the slider text boxes
  var id_list = ['battle_speed', 'battle_message_speed', 'battle_gauge_style', 'background_selection']
  for (const id of id_list) {
    document.getElementById(id + "_text").value = document.getElementById("id_" + id).value
  }

  // Display the chosen background type.
  var selection = document.getElementById('id_background_selection').value;
  preview = document.getElementById('background_selection_preview');
  preview.className = 'menuBackground' + selection;
}
