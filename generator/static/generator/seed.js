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
 * Update the background preview and text box.
 */
function updateBackgroundSelection() {
  var selection = document.getElementById('id_background_selection').value;
  document.getElementById('background_selection_text').value = selection;
  preview = document.getElementById('background_selection_preview');
  preview.className = 'menuBackground' + selection;
}
