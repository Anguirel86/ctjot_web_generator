# Django libraries
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from wsgiref.util import FileWrapper

# Site libraries
from .forms import GenerateForm, RomForm
from .randomizerinterface import RandomizerInterface
from .models import Game

# Python standard libraries
import hashlib
import io
import pickle

# Other libraries
import nanoid


class InvalidRomException(Exception):
    pass


#
# Index page for the randomizer.
#
def index(request):
    return render(request, 'generator/index.html')


#
# Tracker for this version of the randomizer.
#
def tracker(request):
    return render(request, 'generator/tracker.html')


#
# Options page for the seed generator.
#
def options(request):
    form = GenerateForm()
    context = {'form': form}
    return render(request, 'generator/options.html', context)


#
# Generate page to take the results from the options page and generate a ROM.
#
def generate(request):
    if request.method == 'POST':
        form = GenerateForm(request.POST)
        if form.is_valid():
            # Generate a seed and create a DB entry  for it.
            # Then redirect the user to the seed download page.
            game = handle_seed_generation(form)
            rom_form = RomForm()
            context = {'share_id': game.share_id,
                       'form': rom_form,
                       'spoiler_log': RandomizerInterface.get_web_spoiler_log(pickle.loads(game.configuration))}
            return render(request, 'generator/seed.html', context)
        else:
            # TODO - Form isn't valid, for now just redirect to options
            print(form.errors)
            return HttpResponseRedirect('/options/')
    else:
        # This isn't a POST. Redirect to the options page.
        return HttpResponseRedirect('/options/')


#
# Apply the randomization and send the seed to the user.
#
def download_seed(request):
    # TODO - Error handling
    if request.method == 'POST':
        form = RomForm(request.POST, request.FILES)
        if form.is_valid():
            share_id = form.cleaned_data['share_id']
            game = Game.objects.get(share_id=share_id)  # TODO - What if it doesn't exist?
            try:
                rom_bytes = read_and_validate_rom_file(request.FILES['rom_file'])
                interface = RandomizerInterface(rom_bytes)
                interface.set_settings_and_config(pickle.loads(game.settings), pickle.loads(game.configuration))
                patched_rom = interface.generate_rom()
                file_name = share_id + '.sfc'
                content = FileWrapper(io.BytesIO(patched_rom))
                response = HttpResponse(content, content_type='application/octet-stream')
                response['Content-Length'] = len(patched_rom)
                response['Content-Disposition'] = 'attachment; filename=%s' % file_name
                return response
            except InvalidRomException:
                return HttpResponse("You must enter a valid Chrono Trigger ROM file.")
        else:
            return HttpResponse("Invalid form?.")
    else:
        # This isn't a POST. Redirect to the options page.
        return HttpResponseRedirect('/options/')


def download_spoiler_log(request, share_id):
    # TODO - Error handling
    game = Game.objects.get(share_id=share_id)  # TODO - What if it doesn't exist
    if not game.race_seed:
        spoiler_log = RandomizerInterface.get_spoiler_log(pickle.loads(game.configuration), pickle.loads(game.settings))
        file_name = share_id + '.txt'
        content = FileWrapper(spoiler_log)
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Length'] = len(spoiler_log)
        response['Content-Disposition'] = 'attachment; filename=%s' % file_name
        return response
    else:
        return HttpResponse("No spoiler log available for this seed.")


#
# Handle a share link for a previously generated game.
#
def share(request, share_id):
    rom_form = RomForm()
    context = {'share_id': share_id, 'form': rom_form}
    return render(request, 'generator/seed.html', context)


#
# Read and validate the user's ROM file.
# Handles both headered and unheadered ROMS and will raise an
# InvalidRomException if the ROM does not match a vanilla hash or
# is too large to be a valid ROM file.
#
# If the ROM is valid, return it as a bytearray.
#
def read_and_validate_rom_file(romfile):
    # Validate that the file isn't too large to be a CT ROM.
    # Don't waste time reading it if it's not a CT ROM.
    if romfile.size > 4194816:
        raise InvalidRomException()

    # Strip off the header if this is a headered ROM
    if romfile.size == 4194816:
        romfile.seed(0x200)
    file_bytes = bytearray(romfile.read())

    hasher = hashlib.md5()
    hasher.update(file_bytes)
    if hasher.hexdigest() != 'a2bc447961e52fd2227baed164f729dc':
        raise InvalidRomException()

    return file_bytes


#
# Create a randomized config based on the user request.
#
def handle_seed_generation(form) -> Game:
    # Create a config from the passed in data
    interface = RandomizerInterface(RandomizerInterface.get_base_rom())
    interface.configure_seed(form)

    # Store the newly generated config data in the database with its share ID
    share_id = nanoid.generate('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', 15)
    game = Game.objects.create(
        share_id=share_id,
        race_seed=not form.cleaned_data['spoiler_log'],
        settings=pickle.dumps(interface.get_settings()),
        configuration=pickle.dumps(interface.get_config()))

    return game
