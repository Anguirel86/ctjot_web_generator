# Django libraries
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
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
    """
    Exception that is raised by the Jets of Time web generator when an
    invalid ROM is provided by a user during seed generation.
    """
    pass


def index(request):
    """
    Return the Index page for the Jets of Time web generator.

    This is the main page of the webapp and will direct the user to various
    resources as well as provide a link to the options page of the generator.

    :param request: Django request object
    :return: Web response with the rendered index page
    """
    return render(request, 'generator/index.html')


def tracker(request):
    """
    Return the Tracker page for the Jets of Time web generator.

    This page contains the web tracker an associated tracker logic.

    :param request: Django request object
    :return: Web response with the rendered Tracker page
    """
    return render(request, 'tracker/tracker.html')


def options(request):
    """
    Return the Options page for the Jets of Time web generator.

    This page contains the form that users fill out to generate a seed.

    :param request: Django request object
    :return: Web response with the rendered Options page
    """
    form = GenerateForm()
    context = {'form': form,
               'version': RandomizerInterface.get_randomizer_version_info()}
    return render(request, 'generator/options.html', context)


def generate(request):
    """
    Generate a seed based on the user's request in the options form.

    This method will generate a seed and send the user to the seed share page,
    listing the seeds share info, download link, and spoiler logs if applicable.

    :param request: Django request object
    :return: Web response with the rendered share page
    """
    if request.method == 'POST':
        form = GenerateForm(request.POST)
        if form.is_valid():
            # Generate a seed and create a DB entry for it.
            # Then redirect the user to the seed download page.
            game = handle_seed_generation(form)
            share_info = RandomizerInterface.get_share_details(
                pickle.loads(game.configuration), pickle.loads(game.settings))
            rom_form = RomForm()
            context = {'share_id': game.share_id,
                       'form': rom_form,
                       'spoiler_log': RandomizerInterface.get_web_spoiler_log(pickle.loads(game.configuration)),
                       'is_race_seed': game.race_seed,
                       'share_info': share_info.getvalue()}
            return render(request, 'generator/seed.html', context)
        else:
            # TODO - Form isn't valid, for now just redirect to options
            return HttpResponseRedirect('/options/')
    else:
        # This isn't a POST. Redirect to the options page.
        return HttpResponseRedirect('/options/')


def download_seed(request):
    """
    Apply the randomization and send the seed to the user.

    :param request: Django request object
    :return: Web response with the ROM object
    """
    # TODO - Error handling
    if request.method == 'POST':
        form = RomForm(request.POST, request.FILES)
        if form.is_valid():
            share_id = form.cleaned_data['share_id']
            try:
                game = Game.objects.get(share_id=share_id)
            except Game.DoesNotExist:
                return HttpResponseNotFound("Seed does not exist.")

            try:
                rom_bytes = read_and_validate_rom_file(request.FILES['rom_file'])
                interface = RandomizerInterface(rom_bytes)
                interface.set_settings_and_config(pickle.loads(game.settings), pickle.loads(game.configuration))
                patched_rom = interface.generate_rom()
                file_name = interface.get_rom_name(share_id)
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
    """
    Create and send a spoiler log to the user for the seed with the given share ID.

    :param request: Django request object
    :param share_id: Share ID of a previously created seed
    :return: Web response with the spoiler log object
    """
    try:
        game = Game.objects.get(share_id=share_id)
    except Game.DoesNotExist:
        return HttpResponseNotFound("Seed does not exist.")

    if not game.race_seed:
        spoiler_log = RandomizerInterface.get_spoiler_log(
            pickle.loads(game.configuration), pickle.loads(game.settings))
        file_name = 'spoiler_log_' + share_id + '.txt'
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=%s' % file_name
        response.write(spoiler_log.getvalue())
        return response
    else:
        return HttpResponse("No spoiler log available for this seed.")


def share(request, share_id):
    """
    Handle a share link for a previously generated game.

    :param request: Django request object
    :param share_id: Share ID of an existing seed
    :return: Web response with the rendered share page
    """
    try:
        game = Game.objects.get(share_id=share_id)
    except Game.DoesNotExist:
        return HttpResponseNotFound("Seed does not exist.")

    share_info = RandomizerInterface.get_share_details(
        pickle.loads(game.configuration), pickle.loads(game.settings))

    rom_form = RomForm()
    context = {'share_id': game.share_id,
               'form': rom_form,
               'spoiler_log': RandomizerInterface.get_web_spoiler_log(pickle.loads(game.configuration)),
               'is_race_seed': game.race_seed,
               'share_info': share_info.getvalue()}

    return render(request, 'generator/seed.html', context)


def read_and_validate_rom_file(rom_file):
    """
    Read and validate the user's ROM file.

    Handles both headered and unheadered ROMS and will raise an
    InvalidRomException if the ROM does not match a vanilla hash or
    is too large to be a valid ROM file.

    :param rom_file: File object containing a user's ROM
    :return: bytearray containing ROM data
    """
    # Validate that the file isn't too large to be a CT ROM.
    # Don't waste time reading it if it's not a CT ROM.
    if rom_file.size > 4194816:
        raise InvalidRomException()

    # Strip off the header if this is a headered ROM
    if rom_file.size == 4194816:
        rom_file.seek(0x200)
    file_bytes = bytearray(rom_file.read())

    hasher = hashlib.md5()
    hasher.update(file_bytes)
    if hasher.hexdigest() != 'a2bc447961e52fd2227baed164f729dc':
        raise InvalidRomException()

    return file_bytes


def handle_seed_generation(form) -> Game:
    """
    Create a randomized seed based on the user's request on the options form.
    The randomized config is given a share ID and stored in the database.

    :param form: Form object with user selections from the options page
    :return: Game object that has been created and stored in the database
    """
    # Create a config from the passed in data
    interface = RandomizerInterface(RandomizerInterface.get_base_rom())
    interface.configure_seed(form)

    # Get a new unique share ID for this seed
    id_exists = True
    while id_exists:
        # It is possible, though very unlikely to generate a duplicate share ID.
        # Verify this ID doesn't already exist in the database before continuing.
        share_id = nanoid.generate('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', 15)
        id_exists = Game.objects.filter(share_id=share_id).exists()

    # Store the newly generated config data in the database with its share ID
    game = Game.objects.create(
        share_id=share_id,
        race_seed=not form.cleaned_data['spoiler_log'],
        settings=pickle.dumps(interface.get_settings()),
        configuration=pickle.dumps(interface.get_config()))

    return game
