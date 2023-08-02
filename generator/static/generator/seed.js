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
 * Get cosmetic options from json-script data.
 */
function getCosmeticOptions() {
  return JSON.parse(document.getElementById('cosmetics-options').textContent);
}

/*
 * Update the game options section of the seed page.
 */
function updateGameOptions() {
  let options = getCosmeticOptions();

  // Update the slider text boxes
  Object.entries(options).forEach(([id, option]) => {
    if (option.type == 'slider') {
      document.getElementById(id + "_text").value = document.getElementById("id_" + id).value;
    }
  });

  // Display the chosen background type.
  var selection = document.getElementById('id_background_selection').value;
  preview = document.getElementById('background_selection_preview');
  preview.className = 'menuBackground' + selection;
}

/*
 * Load cosmetic options from cookie.
 */
function loadCosmeticOptionsCookie() {
  // load cookie
  let cookie = Cookies.get('ctjot_cosmetics');
  if (!cookie) { return; }

  try {
    var cosmetics = JSON.parse(atob(cookie));
  } catch (e) {
    console.warn('Failed to parse ctjot_cosmetics cookie.', {name: e.name, message: e.message});
  }
  if (!cosmetics) { return; }

  // update items from cookie
  let options = getCosmeticOptions();
  Object.entries(options).forEach(([id, option]) => {
    let elem = document.getElementById("id_" + id);
    if (elem) {
      if (option.type == 'checked') {
        let checked = cosmetics[id];
        if (checked) { $('#id_' + id).bootstrapToggle('on'); }
        else { $('#id_' + id).bootstrapToggle('off'); }
      } else {
        elem.value = cosmetics[id];
      }
    } else {
      console.warn('Undefined cosmetics element.', {id: id});
    }
  });

  updateGameOptions();
}

/*
 * Save cosmetic options to cookie.
 */
function saveCosmeticOptionsCookie() {
  var cosmetics = {};
  let options = getCosmeticOptions();

  // read form values into object
  Object.entries(options).forEach(([id, option]) => {
    if (option.type == 'checked') {
      let checked = $('#id_' + id).is(':checked');
      cosmetics[id] = (checked) ? true : false;
    } else {
      cosmetics[id] = document.getElementById("id_" + id).value;
    }
  });

  // stringify and base64 encode JSON then write cookie
  try {
    let cookie = btoa(JSON.stringify(cosmetics));
    Cookies.set('ctjot_cosmetics', cookie, { sameSite: 'lax' });
  } catch(e) {
    console.warn('Failed to write ctjot_cosmetics cookie.', {name: e.name, message: e.message});
  }
}

/*
 * Reset cosmetic options to defaults and clear cookie.
 */
function resetCosmeticOptionsCookie() {
  let options = getCosmeticOptions();
  Object.entries(options).forEach(([id, option]) => {
    let elem = document.getElementById("id_" + id);
    if (elem) {
      if (option.type == 'checked') {
        let checked = option.default;
        if (checked) { $('#id_' + id).bootstrapToggle('on'); }
        else { $('#id_' + id).bootstrapToggle('off'); }
      } else {
        elem.value = option.default;
      }
    } else {
      console.warn('Undefined cosmetics element.', {id: id});
    }
  });

  // delete cookie
  Cookies.remove('ctjot_cosmetics');

  updateGameOptions();
}
