
// state enum to track which memory segment we are currently reading from.
const ReadStateType = {
  IDLE: 1,
  READ_EVENTS: 2,
  READ_PARTY: 3,
  READ_INVENTORY: 4,
  READ_EQUIPMENT: 5,
  READ_DEVICE_LIST: 6,
  READ_DEVICE_INFO: 7
}

// Type used in determining if key items have been equipped.
const EquipType = {
  WEAPON: 1,
  ACCESSORY: 2
}

// Base address for events, used to convert from RAM address to buffer address
const EVENT_BASE_ADDRESS = 0x7F0000;

/*
 * Map of key items.  Many key items can be either equipped or turned in
 * as part of a quest, so not all key items obtained will show up in 
 * the inventory memory.  For key items with special handling, callback
 * functions are provided to handle the additional processing.
 */
var KEY_ITEMS = new Map();
KEY_ITEMS.set("bentsword", {value:0x50, name:"bentsword", callback:handleItemTurnin, address:0x7F0103, flag:0x02});
KEY_ITEMS.set("benthilt", {value:0x51, name:"benthilt", callback:handleItemTurnin, address:0x7F0103, flag:0x02});
KEY_ITEMS.set("heromedal", {value:0xB3, name:"heromedal", callback:handleEquippableItem, type:EquipType.ACCESSORY});
KEY_ITEMS.set("roboribbon", {value:0xB8, name:"roboribbon", callback:handleEquippableItem, type:EquipType.ACCESSORY});
KEY_ITEMS.set("pendant", {value:0xD6, name:"pendant"});
KEY_ITEMS.set("gatekey", {value:0xD7, name:"gatekey"});
KEY_ITEMS.set("prismshard", {value:0xD8, name:"prismshard"});
KEY_ITEMS.set("ctrigger", {value:0xD9, name:"ctrigger"});
KEY_ITEMS.set("grandleon", {value:0x42, name:"grandleon", callback:handleEquippableItem, type:EquipType.WEAPON});
KEY_ITEMS.set("jerky", {value:0xDB, name:"jerky", callback:handleItemTurnin, address:0x7F01D2, flag:0x04});
KEY_ITEMS.set("dreamstone", {value:0xDC, name:"dreamstone"});
//KEY_ITEMS.set("sunstone", {value:0xDF, name:"sunstone", callback:handleMoonstone});
KEY_ITEMS.set("moonstone", {value:0xDE, name:"moonstone", callback:handleMoonstone});
KEY_ITEMS.set("rubyknife", {value:0xE0, name:"rubyknife", callback:handleItemTurnin, address:0x7F00F4, flag:0x80});
KEY_ITEMS.set("clone", {value:0xE2, name:"clone"});
KEY_ITEMS.set("tomaspop", {value:0xE3, name:"tomapop", callback:handleItemTurnin, address:0x7F01A3, flag:0x80});


var gameSocket;
var readState = ReadStateType.IDLE;
var readInterval;
var attachInterval;

// Keep track of whether or not we are in game.
// Party memory has to be read first for this to work properly.
var inGame = false;

// A number of the key items need to check event memory for turn-in flags.
// Store the most recent event memory buffer so we can look back at it.
var eventBuffer;

// Some of the key items can be equipped.  Store the the memory segment that
// holds equipped items here so we can look at it during key item parsing.
var equipBuffer;

/*
 * Add click handlers to each tracker object image on the page
 * that will toggle the grayscale on/off when clicked.
 */
$(document).ready(function() {
  $("img").click(function() {
    var id = $(this).attr('id')
    if (id) {
      // Moonstone has an additional progressive stage.
      // All other items just toggle on/off.
      if (id == "moonstone") {
        toggleMoonstoneStages(id);
      } else {
        toggleTrackerItem(id);
      }
    }
  });
});

/*
 * Connect the autotracker to QUsb2Snes.
 * This function handles connecting to QUsb2Snes and setting up
 * the socket callbacks/state machine.
 */
function connectAutotracker() {
  document.getElementById("autotracker_connect_button").disabled = true;
  gameSocket = new WebSocket("ws://localhost:8080");
  
  /*
   * Callback when the socket connection is opened.
   * Once we have established a connection, start polling QUsb2Snes
   * for the device list so that we can attach.
   */
  gameSocket.onopen = function(event) {
    addLogMessage("Connected to QUsb2Snes.");
    // Try to attach to a device every 3 seconds until we
    // make a connection.
    addLogMessage("Searching for device...");
    attachInterval = setInterval(function() {
      getDeviceList();
    }, 3000);
  }
  
  /*
   * Callback when the socket is closed. 
   * Re-enable the connect button on the main page and log
   * a message that we have disconnected from QUsb2Snes.
   */
  gameSocket.onclose = function(event) {
    document.getElementById("autotracker_connect_button").disabled = false;
    addLogMessage("Disconnected from QUsb2Snes.");
  }

  /*
   * Callback when we receive a message on the websocket.
   * This also acts as a state machine to control what
   * queries are being sent to QUsb2Snes.
   */
  gameSocket.onmessage = function(event) {
    switch (readState) {
      case ReadStateType.IDLE:
        break;
      case ReadStateType.READ_PARTY:
        parsePartyData(event.data);
        readEquipMemory();
        break;
      case ReadStateType.READ_EQUIPMENT:
        parseEquipData(event.data);
        readEventMemory();
        break;
      case ReadStateType.READ_EVENTS:
        parseEventData(event.data);
        readInventoryMemory()
        break;
      case ReadStateType.READ_INVENTORY:
        parseInventoryData(event.data);
        handleGoMode();
        readState = ReadStateType.IDLE;
        break;
      case ReadStateType.READ_DEVICE_LIST:
        var responseObj = JSON.parse(event.data);
        var deviceList = responseObj.Results;
        if (deviceList.length > 0) {
          clearInterval(attachInterval);
          addLogMessage("Attaching to: " + deviceList[0]);
          attachToDevice(deviceList[0]);
          getDeviceInfo();
        } else {
          readState = ReadStateType.IDLE;
        }
        break;
      case ReadStateType.READ_DEVICE_INFO:
        addLogMessage("Successfully attached to device.");
        addLogMessage("Starting Autotracking.");
        readInterval = setInterval(function() {
          readPartyMemory();
        }, 3000);
        readState = ReadStateType.IDLE;
        break;
    }
  }

  /*
   * Callback to handle errors with the socket connection.
   * Per QUsb2Snes documentation, if an error occurs the socket
   * is immediately closed.
   * On an error, set read state to IDLE and log a connection error.
   */
  gameSocket.onerror = function(event) {
    readState = ReadStateType.IDLE;
    addLogMessage("QUsb2Snes connection error.");
  }
}

/*
 * End the read interval and close the QUsb2Snes socket.
 */
function disconnectAutotracker() {
  clearInterval(readInterval);
  gameSocket.close();
}

/*
 * Add a log message to the autotracker log text area.
 */
function addLogMessage(message) {
  $("#autotracker_log").append(message + "\n");
}

/*
 * Read event data from a memory array.
 * This function takes in a SNES RAM address and converts it to
 * an address that can be used with the data returned from QUsb2Snes.
 */
function readEventAddress(data, address) {
  return data[address - EVENT_BASE_ADDRESS];
}

/*
 * Check whether or not the player is in go mode.
 */
 function handleGoMode() {
  if (!inGame) {
    return;
  }
  gomode = 
    (hasItem("gatekey") && hasItem("dreamstone") && hasItem("rubyknife")) ||
    (hasItem("pendant") && hasItem("clone") && hasItem("ctrigger")) ||
    (hasItem("Frog") && hasItem("benthilt") && hasItem("bentsword"));
  
  markTrackerIcon("gomode", gomode);
}

/*
 * Handle the moonstone key item.  This key item can be powered up 
 * the sun stone and requires some special handling.
 */
function handleMoonstone(keyItem) {
  // 7F013A & 0x40 goes high when you pick up the charged sunstone.
  
  if ((readEventAddress(eventBuffer, 0x7F013A) & 0x40) > 0) {
    // Set sunstone acquired
    $("#" + keyItem.name).attr("src", "/static/generate/images/sunstone.png");
    markTrackerIcon(keyItem.name, true);
  } else {
    // check if moonstone is in inventory or dropped off at Sun Keep
    $("#" + keyItem.name).attr("src", "/static/generate/images/moonstone.png");
    var droppedOff = (readEventAddress(eventBuffer, 0x7f013A) & 0x04) > 0;
    if (keyItem.found || droppedOff) {
      // Toggle moonstone on
      markTrackerIcon(keyItem.name, true);
    } else {
      markTrackerIcon(keyItem.name, false);
    }
  }
}

/*
 * Callback function to handle tracking items that may have been
 * turned in as part of a quest.
 */
function handleItemTurnin(keyItem) {
  var usedItem = (readEventAddress(eventBuffer, keyItem.address) & keyItem.flag) > 0;
  markTrackerIcon(keyItem.name, (keyItem.found || usedItem));
}

/*
 * Callback function to handle checking for key items that can be equipped.
 */
function handleEquippableItem(keyItem) {
  
  if (keyItem.found) {
    markTrackerIcon(keyItem.name, true);
    return;
  }
  
  // Determine the offset into character data that the item we are
  // are looking for will be stored.
  var offset = 0;
  if (keyItem.type == EquipType.ACCESSORY) {
    offset = 0x2A;
  } else if (keyItem.type == EquipType.WEAPON) {
    offset = 0x29;
  } else {
    // Unknown equip type - Bail out of the check.
    markTrackerIcon(keyItem.name, false);
  }
  
  // Loop through character data looking to see if the key item has
  // been equipped by someone.
  // Check everyone for the item in case the player is running with
  // the character duplication flag turned on.
  for (var i = 0; i < 7; i++) {
    var equippedItem = (equipBuffer[(0x50 * i) + offset] & 0xFF);
    if (equippedItem == keyItem.value) {
      markTrackerIcon(keyItem.name, true);
      return;
    }
  }
  
  // We didn't find the key item equipped on anyone.
  markTrackerIcon(keyItem.name, false);
}

/*
 * Check if an event bit has been set via the provided byte and flag.
 * If it has been set, remove the grayscale filter from the provided 
 * tracker id.  If not, add the grayscale filter.
 */
function markTrackerIconBitSet(id, data, flag) {
  if ((data & flag) > 0) {
    document.getElementById(id).classList.remove("tracker-grayscale");
  } else {
    document.getElementById(id).classList.add("tracker-grayscale");
  }
}

/*
 * Check if an event bit has been cleared via the provided byte and flag.
 * If it has been set, remove the grayscale filter from the provided 
 * tracker id.  If not, add the grayscale filter.
 */
function markTrackerIconBitCleared(id, data, flag) {
  if ((data & flag) == 0) {
    document.getElementById(id).classList.remove("tracker-grayscale");
  } else {
    document.getElementById(id).classList.add("tracker-grayscale");
  }
}

/*
 * Set or clear the grayscale filter from the provided tracker item 
 * based on whether the provided value is true or false.
 */
function markTrackerIcon(id, value) {
  if (value) {
    document.getElementById(id).classList.remove("tracker-grayscale");
  } else {
    document.getElementById(id).classList.add("tracker-grayscale");
  }
}

/*
 * Toggle a tracker item on/off.
 */
function toggleTrackerItem(id) {
  var trackerObject = document.getElementById(id)
  if (trackerObject.classList.contains("tracker-grayscale")) {
    trackerObject.classList.remove("tracker-grayscale");
  } else {
    trackerObject.classList.add("tracker-grayscale");
  }
}

/*
 * Handle toggling the moonstone stages when clicked.
 */
function toggleMoonstoneStages(id) {
  var trackerItem = document.getElementById(id)
  var isSunstone = $("#moonstone").attr('src').includes("sunstone");
  var isEnabled = !trackerItem.classList.contains("tracker-grayscale");
  
  if (isSunstone) {
    // reset back to uncollected
    $("#moonstone").attr('src', "/static/generate/images/moonstone.png");
    markTrackerIcon(id, false);
  } else if(isEnabled) {
    // Item is already enabled, make it the sunstone
    $("#moonstone").attr('src', "/static/generate/images/sunstone.png");
  } else {
    // Mark moonstone collected
    markTrackerIcon(id, true);
  }
}

/*
 * Check if an item has been obtained by whether or not
 * it has the grayscale filter applied.
 */
function hasItem(id) {
  var trackerObject = document.getElementById(id);
  return !(trackerObject.classList.contains("tracker-grayscale"));
}

/*
 * Parse event data from the memory blob read from the attached device.
 */
function parseEventData(blob) {
  if (!inGame) {
    return;
  }
  var reader = new FileReader();
  reader.readAsArrayBuffer(blob);
  reader.onloadend= (event) => {
    var bufferView = new Int8Array(reader.result);
    eventBuffer = bufferView;
    // Check for boss kills
    // Prehistory
    markTrackerIconBitSet("nizbel", readEventAddress(bufferView, 0x7F0105), 0x20);
    markTrackerIconBitSet("blacktyrano", readEventAddress(bufferView, 0x7F00EC), 0x80);
    
    // Dark Ages
    markTrackerIconBitSet("gigagaia", readEventAddress(bufferView, 0x7F000D), 0x01);
    markTrackerIconBitSet("golem", readEventAddress(bufferView, 0x7F0105), 0x80);
    
    // Middle Ages
    markTrackerIconBitSet("yakra", readEventAddress(bufferView, 0x7F000D), 0x01);
    markTrackerIconBitSet("masamune", readEventAddress(bufferView, 0x7F00F3), 0x20);
    markTrackerIconBitSet("retinite", readEventAddress(bufferView, 0x7F01AD), 0x04);
    markTrackerIconBitSet("rusttyrano", readEventAddress(bufferView, 0x7F01D2), 0x40);
    markTrackerIconBitSet("magusboss", readEventAddress(bufferView, 0x7F01FF), 0x04);
    // NOTE: This marks complete at the start of the Zombor fight.  There is no flag
    //       associated with finishing the fight, just starting it.
    markTrackerIconBitSet("zombor", readEventAddress(bufferView, 0x7F0101), 0x02);
    
    // Present
    markTrackerIconBitSet("heckran", readEventAddress(bufferView, 0x7F01A3), 0x08);
    markTrackerIconBitSet("dragontank", readEventAddress(bufferView, 0x7F0198), 0x08);
    markTrackerIconBitSet("yakraxiii", readEventAddress(bufferView, 0x7F0050), 0x40);
    
    // Future
    markTrackerIconBitSet("guardian", readEventAddress(bufferView, 0x7F00EC), 0x01);
    markTrackerIconBitSet("rseries", readEventAddress(bufferView, 0x7F0103), 0x40);
    markTrackerIconBitSet("sonofsun", readEventAddress(bufferView, 0x7F013A), 0x02);
    markTrackerIconBitSet("motherbrain", readEventAddress(bufferView, 0x7F013B), 0x10);
    // NOTE: This boss gets set to done at the end of Death Peak.  This is a holdover
    //       From the EmoTracker pack and will eventually be updated to complete
    //       when Zeal2 is actually killed.
    markTrackerIconBitSet("zeal", readEventAddress(bufferView, 0x7F0067), 0x07);
    
    /*
     * Masamune
     * The Masamune tracker item is activated when the player reforges the Masamune
     * after collecting the hilt and blade.  The original version of the tracker
     * tracked this via the inventory, but it can be tracked easier using the event
     * flag set high after Melchior reforges the sword.  Because it's part of event
     * memory, check for the tracker item here.
     */
    markTrackerIconBitSet("melchior", readEventAddress(bufferView, 0x7f0103), 0x02);

    /*
     * End of Time
     * Track magic here. This is determined by whether or not any character 
     * except Magus is capable of using magic. This allows magic detection to 
     * work in Lost Worlds mode, where characters don't need to meet Spekkio.
     */
    markTrackerIconBitSet("magic", readEventAddress(bufferView, 0x7F01E0), 0x3F);

    
  };
}

/*
 * Store off the data block that contains character equipment.
 * This is used later to determine if equipable key items 
 * have been acquired.
 */
function parseEquipData(data) {
  if (!inGame) {
    return;
  }
  var reader = new FileReader();
  reader.readAsArrayBuffer(data);
  reader.onloadend = (event) => {
    var bufferView = new Int8Array(reader.result)
    equipBuffer = bufferView;
  };
}

/*
 * Read the Party Memory segment and determine which characters
 * the player has acquired.
 */
function parsePartyData(data) {
  var reader = new FileReader();
  reader.readAsArrayBuffer(data);
  reader.onloadend = (event) => {
    var bufferView = new Int8Array(reader.result)
    
    // Use the character data to determine if we are in game.  Unused
    // character slots will have 0x80.  0x00 is Crono's ID, so if we have
    // Crono's ID in two slots it means that the game isn't running.
    // Store this value off so other functions can use it.
    // Parsing party data should be done first because of this.
    inGame =  !((bufferView[0] == 0) && (bufferView[1] == 0));
    if (!inGame) {
      return;
    }
    
    // Loop through the memory that stores characters and reserve characters.
    // Store which ones we find.
    var charsFound = 0;
    for (var i = 0; i < 9; i++) {
      if (bufferView[i] != -128) { // Siged value of 0x80 (empty character slot)
        charsFound = charsFound | (1 << bufferView[i]);
      }
    }
    
    // Toggle tracker icons based on what characters were found
    markTrackerIcon("Crono", ((charsFound & 0x01) != 0))
    markTrackerIcon("Marle", ((charsFound & 0x02) != 0))
    markTrackerIcon("Lucca", ((charsFound & 0x04) != 0))
    markTrackerIcon("Robo", ((charsFound & 0x08) != 0))
    markTrackerIcon("Frog", ((charsFound & 0x10) != 0))
    markTrackerIcon("Ayla",  ((charsFound & 0x20) != 0))
    markTrackerIcon("Magus", ((charsFound & 0x40) != 0))
  };
}

/*
 * Parse the contents of inventory memory for key items.
 */
function parseInventoryData(data) {
  if (!inGame) {
    return;
  }
  var reader = new FileReader();
  reader.readAsArrayBuffer(data);
  reader.onloadend = (event) => {
    var bufferView = new Int8Array(reader.result)
    
    // Reset all items to "not found"
    for (let value of KEY_ITEMS.values()) {
      value.found = false;
    }
    
    // Loop through inventory and determine which 
    // key items have been found.
    for (var i = 0; i < 0xF1; i++) {
      // Loop the key item map for each inventory item 
      // and see if it matches.
      for (let value of KEY_ITEMS.values()) {
        if (value["value"] == (bufferView[i] & 0xFF)) {
          value.found = true;
        }
      } // End map loop
    } // End inventory loop
    
    // Loop through the key items and toggle the tracker
    // icon if the item was found.  This loop takes special
    // callback functions into account for items with callbacks.
    for (let value of KEY_ITEMS.values()) {
      if (value.callback) {
        value.callback(value);
      } else {
        markTrackerIcon(value.name, value.found);
      }
    }
  };
}

/*
 * Send an Attach command to QUsb2Snes to attach to the
 * specified device.
 */
function attachToDevice(device) {
  var request = {
    Opcode: "Attach",
    Space: "SNES",
    Operands: [device]
  };
  
  gameSocket.send(JSON.stringify(request));
}

/*
 * Send a DeviceList command to QUsb2Snes to get a list of
 * all available devices.
 */
function getDeviceList() {
  var request = {
    Opcode: "DeviceList",
    Space: "SNES"
  };
  readState = ReadStateType.READ_DEVICE_LIST;
  gameSocket.send(JSON.stringify(request));
}

/*
 * Query the device info of the device that we are attached to.
 * This is used to determine if we have successfully attached to
 * a device. If this command fails, then we did not attach.
 */
function getDeviceInfo() {
  var request = {
    Opcode: "Info",
    Space: "SNES"
  };
  readState = ReadStateType.READ_DEVICE_INFO;
  gameSocket.send(JSON.stringify(request));
}

/*
 * Send a GetAddress command to QUsb2Snes to read SNES memory.
 * NOTE: Address and numBytes must be strings and in hexadecimal format.
 *       ie: readSnesMemory("0xF60000", "0x200", ReadStateType.READ_EVENTS)
 */
function readSnesMemory(address, numBytes, readType) {
  var request = {
    Opcode : "GetAddress",
    Space : "SNES",
    Operands : [address, numBytes]
  }
  readState = readType;
  gameSocket.send(JSON.stringify(request))
}

function readEventMemory() {
  readSnesMemory("0xF60000", "0x200", ReadStateType.READ_EVENTS);
}

function readPartyMemory() {
  readSnesMemory("0xF52980", "0x09", ReadStateType.READ_PARTY);
}

function readInventoryMemory() {
  readSnesMemory("0xF52400", "0xF2", ReadStateType.READ_INVENTORY);
}

function readEquipMemory() {
  readSnesMemory("0xF52600", "0x230", ReadStateType.READ_EQUIPMENT);
}

