// Change the spoiler log button between "Show" and "Hide"
$(document).on('show.bs.collapse', '#spoiler_section', function(e) {
  document.getElementById('spoiler_log_button').value = 'Hide Spoiler Log';
});

$(document).on('hide.bs.collapse', '#spoiler_section', function(e) {
  document.getElementById('spoiler_log_button').value = 'Show Spoiler Log';
});