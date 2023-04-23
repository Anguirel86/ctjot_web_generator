# Django libraries
from django.http import HttpResponse
from django.shortcuts import render, redirect
from wsgiref.util import FileWrapper

# Site libraries
from django.views import View
from django.views.generic import FormView

from .forms import GenerateForm, RomForm
from .randomizerinterface import RandomizerInterface, InvalidSettingsException
from .models import Game

# Python standard libraries
import hashlib
import io
import pickle
import random

# Other libraries
import nanoid
from PIL import Image, ImageDraw


class InvalidRomException(Exception):
    """
    Exception that is raised by the Jets of Time web generator when an
    invalid ROM is provided by a user during seed generation.
    """
    pass


class InvalidGameIdException(Exception):
    """
    Exception that is raised when an invalid share ID is provided.
    """
    pass


class OptionsView(View):
    """
    Handle the Options page for the Jets of Time web generator.

    This page contains the form that users fill out to generate a seed.
    """

    @classmethod
    def get(cls, request):
        form = GenerateForm()
        context = {'form': form}
        return render(request, 'generator/options.html', context)


class GenerateView(FormView):
    """
    Generate a seed based on the user's request in the options form.

    This class will generate a seed and send the user to the seed share page
    listing the seeds share info, download link, and spoiler logs if applicable.
    """
    form_class = GenerateForm

    def form_valid(self, form):
        # Generate a seed and create a DB entry for it.
        # Then redirect the user to the seed download page.
        game = generate_seed_from_form(form)
        return redirect('/share/' + game.share_id)

    def form_invalid(self, form):
        # TODO: Replace this error handling with something better eventually.
        buffer = io.StringIO()
        buffer.write("Errors in the following form fields:\n")
        for error in form.errors:
            buffer.write(str(error) + "\n")
        return render(self.request, 'generator/error.html', {'error_text': buffer.getvalue()}, status=404)


class ShareLinkView(View):
    """
    Handle a share link for a previously generated game.
    """
    @classmethod
    def get(cls, request, share_id):
        try:
            game = Game.objects.get(share_id=share_id)
        except Game.DoesNotExist:
            return render(request, 'generator/error.html', {'error_text': 'Seed does not exist.'}, status=404)

        share_info = RandomizerInterface.get_share_details(
            pickle.loads(game.configuration), pickle.loads(game.settings))

        rom_form = RomForm()
        # No web spoiler log for AP seeds.
        context = {'share_id': game.share_id,
                   'is_permalink': True,
                   'base_uri': request.build_absolute_uri('/')[:-1],
                   'form': rom_form,
                   'spoiler_log': {},
                   'is_race_seed': game.race_seed,
                   'share_info': share_info.getvalue()}

        return render(request, 'generator/seed.html', context)


class DownloadSeedView(FormView):
    """
    Apply the randomization and send the seed to the user.
    """
    form_class = RomForm

    @classmethod
    def read_and_validate_rom_file(cls, rom_file: bytearray):
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

    def form_valid(self, form):
        share_id = form.cleaned_data['share_id']
        try:
            game = Game.objects.get(share_id=share_id)
        except Game.DoesNotExist:
            return render(self.request, 'generator/error.html', {'error_text': 'Seed does not exist.'}, status=404)

        try:
            rom_bytes = self.read_and_validate_rom_file(self.request.FILES['rom_file'])
            interface = RandomizerInterface(rom_bytes)
            interface.set_settings_and_config(pickle.loads(game.settings), pickle.loads(game.configuration), form)
            patched_rom = interface.generate_rom()
            file_name = interface.get_rom_name(share_id)
            content = FileWrapper(io.BytesIO(patched_rom))
            response = HttpResponse(content, content_type='application/octet-stream')
            response['Content-Length'] = len(patched_rom)
            response['Content-Disposition'] = 'attachment; filename=%s' % file_name
            return response
        except InvalidRomException:
            return render(self.request, 'generator/error.html',
                          {'error_text': 'You must enter a valid Chrono Trigger ROM file.'}, status=400)

    def form_invalid(self, form):
        return render(self.request, 'generator/error.html',
                      {'error_text': 'Invalid form: did you select a ROM file?'}, status=400)


class DownloadSpoilerLogView(View):
    """
    Create and send a spoiler log to the user for the seed with the given share ID.
    """
    @classmethod
    def get(cls, request, share_id):
        try:
            game = Game.objects.get(share_id=share_id)
        except Game.DoesNotExist:
            return render(request, 'generator/error.html', {'error_text': 'Seed does not exist.'}, status=404)

        if not game.race_seed:
            spoiler_log = RandomizerInterface.get_spoiler_log(
                pickle.loads(game.configuration), pickle.loads(game.settings))
            file_name = 'spoiler_log_' + share_id + '.txt'
            response = HttpResponse(content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename=%s' % file_name
            response.write(spoiler_log.getvalue())
            return response
        else:
            return render(request, 'generator/error.html', {'error_text': 'No spoiler log available for this seed.'},
                          status=404)


class DownloadAPYamlView(View):
    """
    Create and send a spoiler log to the user for the seed with the given share ID.
    """
    @classmethod
    def get(cls, request, share_id):
        try:
            game = Game.objects.get(share_id=share_id)
        except Game.DoesNotExist:
            return render(request, 'generator/error.html', {'error_text': 'Seed does not exist.'}, status=404)

        if not game.race_seed:
            ap_yaml = RandomizerInterface.get_archipelago_yaml(
                pickle.loads(game.configuration), pickle.loads(game.settings))
            file_name = 'ctjot_' + share_id + '.yaml'
            response = HttpResponse(content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename=%s' % file_name
            response.write(ap_yaml.getvalue())
            return response
        else:
            return render(request, 'generator/error.html', {'error_text': 'No Archipelago yaml available for this seed.'},
                          status=404)


class DownloadJSONSpoilerLogView(View):
    """
    Create and send a JSON spoiler log to the user for the seed with the given share ID.
    """
    @classmethod
    def get(cls, request, share_id):
        try:
            game = Game.objects.get(share_id=share_id)
        except Game.DoesNotExist:
            return render(request, 'generator/error.html', {'error_text': 'Seed does not exist.'}, status=404)

        response = HttpResponse(content_type='application/json')
        if not game.race_seed:
            spoiler_log = RandomizerInterface.get_json_spoiler_log(
                pickle.loads(game.configuration), pickle.loads(game.settings))
            response.write(spoiler_log.getvalue())
        else:
            response.write(b'{"cheating": "not_allowed"}')
        return response


class PracticeSeedView(View):
    """
    Get a practice seed with identical setting to the seed with the given share_id.
    """
    @classmethod
    def get(cls, request, share_id):
        try:
            game = generate_seed_from_id(share_id)
        except InvalidGameIdException as e:
            return render(request, 'generator/error.html', {'error_text': str(e)}, status=404)
        except InvalidSettingsException as e:
            return render(request, 'generator/error.html', {'error_text': str(e)}, status=404)

        return redirect('/share/' + game.share_id)


class SeedImageView(View):
    """
    Handle creating a random image to represent a previously-generated seed.
    """
    @classmethod
    def get(cls, request, share_id):
        try:
            game = Game.objects.get(share_id=share_id)
        except Game.DoesNotExist:
            return render(request, 'generator/error.html', {'error_text': 'Seed does not exist.'}, status=404)

        rgen = random.Random(share_id)
        img = Image.new('RGB', (200,200))
        d = ImageDraw.Draw(img)
        squaresize = 50
        for x in range(0,200,squaresize):
            for y in range(0, 200, squaresize):
                # Draw a square in a random color
                d.polygon([(x,y),(x+squaresize,y),(x+squaresize,y+squaresize),(x,y+squaresize)],
                        fill=(rgen.randint(0,31)*8, rgen.randint(0,31)*8, rgen.randint(0,31)*8))

        with io.BytesIO() as f:
            img.save(f, 'PNG')
            l = len(f.getvalue())
            response = HttpResponse(content_type='image/png')
            response['Content-Length'] = l
            response.write(f.getbuffer())
            return response


def get_share_id() -> str:
    """
    Get a unique share ID.

    :return: A unique share ID string
    """
    id_exists = True
    while id_exists:
        # It is possible, though very unlikely to generate a duplicate share ID.
        # Verify this ID doesn't already exist in the database before continuing.
        share_id = nanoid.generate('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', 15)
        id_exists = Game.objects.filter(share_id=share_id).exists()
    return share_id


def generate_seed_from_form(form: GenerateForm) -> Game:
    """
    Create a randomized seed based on the user's request on the options form.
    The randomized config is given a share ID and stored in the database.

    :param form: Form object with user selections from the options page
    :return: Game object that has been created and stored in the database
    """
    # Create a config from the passed in data
    interface = RandomizerInterface(RandomizerInterface.get_base_rom())
    nonce = interface.configure_seed_from_form(form)

    # Get a new unique share ID for this seed
    share_id = get_share_id()

    # Store the newly generated config data in the database with its share ID
    game = Game.objects.create(
        share_id=share_id,
        race_seed=not form.cleaned_data['spoiler_log'],
        seed_nonce=nonce,
        settings=pickle.dumps(interface.get_settings()),
        configuration=pickle.dumps(interface.get_config()))

    return game


def generate_seed_from_id(existing_share_id: str) -> Game:
    """
    Generate a new game object from an existing share ID with identical
    settings and a new seed value.

    :param existing_share_id: Share ID of an existing seed
    :return: Game object that has been created and stored in the database
    """
    try:
        existing_game = Game.objects.get(share_id=existing_share_id)
    except Game.DoesNotExist:
        raise InvalidGameIdException("Share ID " + existing_share_id + " does not exist.")

    new_share_id = get_share_id()
    interface = RandomizerInterface(RandomizerInterface.get_base_rom())
    # Currently only used for practice seeds, so force race mode to False.
    nonce = interface.configure_seed_from_settings(pickle.loads(existing_game.settings), False)

    new_game = Game.objects.create(
        share_id=new_share_id,
        race_seed=False,
        seed_nonce=nonce,
        settings=pickle.dumps(interface.get_settings()),
        configuration=pickle.dumps(interface.get_config())
    )

    return new_game
