#! python2.7
'''
main Caster module
Created on Jun 29, 2014
'''

import os
import logging
logging.basicConfig()


def version_minimum():
    try:
        import pkg_resources
        version = "0.15.0"  # Version needs to be manually updated Caster requires a certain version of Dragonfly
        pkg_resources.require("dragonfly2 >= %s" % (version))
    except Exception:  # pylint: disable=broad-except
        print("\nCaster: Requires at least dragonfly2 version %s\n" % (version))


version_minimum()

import time, socket, os
from dragonfly import (Function, Grammar, Playback, Dictation, Choice, Pause, RunCommand)
from castervoice.lib.ccr.standard import SymbolSpecs


def _wait_for_wsr_activation():
    count = 1
    while True:
        try:
            from castervoice.apps.browser import firefox
            break
        except:
            print(
                "(%d) Attempting to load Caster -- WSR not loaded and listening yet..." %
                count)
            count += 1
            time.sleep(1)


_NEXUS = None
from castervoice.lib import settings  # requires nothing
if settings.SYSTEM_INFORMATION["platform"] != "win32":
    raise SystemError("Your platform is not currently supported by Caster.")
settings.WSR = __name__ == "__main__"
from castervoice.lib import utilities  # requires settings
if settings.WSR:
    _wait_for_wsr_activation()
    SymbolSpecs.set_cancel_word("escape")
from castervoice.lib import control
_NEXUS = control.nexus()
from castervoice.lib import navigation
navigation.initialize_clipboard(_NEXUS)

from castervoice.apps import __init__
from castervoice.asynch import *
from castervoice.lib.ccr import *
from castervoice.lib.ccr.recording import bringme, again, alias, history
import castervoice.lib.dev.dev
from castervoice.asynch.sikuli import sikuli

from castervoice.lib.actions import Key
from castervoice.lib.terminal import TerminalCommand
from castervoice.lib.dfplus.state.short import R
from castervoice.lib.dfplus.additions import IntegerRefST
from castervoice.lib.dfplus.merge.mergepair import MergeInf
from castervoice.lib.dfplus.merge.mergerule import MergeRule

if not globals().has_key('profile_switch_occurred'):
    # Load user rules
    _NEXUS.process_user_content()
    _NEXUS.merger.update_config()
    _NEXUS.merger.merge(MergeInf.BOOT)


# Checks if install is classic or PIP of caster
def installtype():
    directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "castervoice")
    if os.path.isdir(directory):
        return "classic"
    else:
        return "pip"


def internetcheck(host="1.1.1.1", port=53, timeout=3):
    """
    Checks for network connection via DNS resolution.
    :param host: CloudFire DNS
    :param port: 53/tcp
    :param timeout: An integer
    :return: True or False
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception as error:
        print(error.message)
        return False


# Find the pip.exe script for Python 2.7. Fallback on pip.exe.
PIP_PATH = "pip.exe"
python_scripts = os.path.join("Python27", "Scripts")
for path in os.environ["PATH"].split(";"):
    pip = os.path.join(path, "pip.exe")
    if path.endswith(python_scripts) and os.path.isfile(pip):
        PIP_PATH = pip
        break


class DependencyCheck(TerminalCommand):
    trusted = True  # Command will execute silently without ConfirmAction
    synchronous = True

    # pylint: disable=method-hidden
    def process_command(self, proc):
        update = False
        for line in iter(proc.stdout.readline, b''):
            if "INSTALLED" and "latest" in line:
                update = True

        return update


class CasterCheck(DependencyCheck):
    command = [PIP_PATH, "search", "castervoice"]

    # pylint: disable=method-hidden
    def process_command(self, proc):
        if DependencyCheck.process_command(self, proc):
            print("Caster: Caster is up-to-date")
        else:
            print("Caster: Say 'Update Caster' to update.")


class DragonflyCheck(DependencyCheck):
    command = [PIP_PATH, "search", "dragonfly2"]

    # pylint: disable=method-hidden
    def process_command(self, proc):
        if DependencyCheck.process_command(self, proc):
            print("Caster: Dragonfly is up-to-date")
        else:
            print("Caster: Say 'Update Dragonfly' to update.")


class DependencyUpdate(RunCommand):
    synchronous = True

    # pylint: disable=method-hidden
    def process_command(self, proc):
        # Process the output from the command.
        RunCommand.process_command(self, proc)

        # Only reboot dragon if the command was successful and there is an
        # internet connection; 'pip install ...' may exit successfully even
        # if there were connection errors.
        if proc.wait() == 0 and internetcheck():
            Playback([(["reboot", "dragon"], 0.0)]).execute()


if settings.SETTINGS["miscellaneous"]["online_mode"]:
    if internetcheck():
        if installtype() is "pip":
            CasterCheck().execute()
        DragonflyCheck().execute()
    else:
        print("\nCaster: Network off-line check network connection\n")
else:
    print("\nCaster: Off-line mode is enabled\n")


def change_monitor():
    if settings.SETTINGS["sikuli"]["enabled"]:
        Playback([(["monitor", "select"], 0.0)]).execute()
    else:
        print("This command requires SikuliX to be enabled in the settings file")


class MainRule(MergeRule):
    @staticmethod
    def generate_ccr_choices(nexus):
        choices = {}
        for ccr_choice in nexus.merger.global_rule_names():
            choices[ccr_choice] = ccr_choice
        return Choice("name", choices)

    @staticmethod
    def generate_sm_ccr_choices(nexus):
        choices = {}
        for ccr_choice in nexus.merger.selfmod_rule_names():
            choices[ccr_choice] = ccr_choice
        return Choice("name2", choices)

    mapping = {
        # update management
        "update caster":
            R(DependencyUpdate([PIP_PATH, "install", "--upgrade", "castervoice"])),
        "update dragonfly":
            R(DependencyUpdate([PIP_PATH, "install", "--upgrade", "dragonfly2"])),

        # hardware management
        "volume <volume_mode> [<n>]":
            R(Function(navigation.volume_control, extra={'n', 'volume_mode'})),
        "change monitor":
            R(Key("w-p") + Pause("100") + Function(change_monitor)),

        # window management
        'minimize':
            R(Playback([(["minimize", "window"], 0.0)])),
        'maximize':
            R(Playback([(["maximize", "window"], 0.0)])),
        "remax":
            R(Key("a-space/10,r/10,a-space/10,x")),

        # passwords

        # mouse alternatives
        "legion [<monitor>]":
            R(Function(navigation.mouse_alternates, mode="legion", nexus=_NEXUS)),
        "rainbow [<monitor>]":
            R(Function(navigation.mouse_alternates, mode="rainbow", nexus=_NEXUS)),
        "douglas [<monitor>]":
            R(Function(navigation.mouse_alternates, mode="douglas", nexus=_NEXUS)),

        # ccr de/activation
        "<enable> <name>":
            R(Function(_NEXUS.merger.global_rule_changer(), save=True)),
        "<enable> <name2>":
            R(Function(_NEXUS.merger.selfmod_rule_changer(), save=True)),
        "enable caster":
            R(Function(_NEXUS.merger.merge, time=MergeInf.RUN, name="numbers")),
        "disable caster":
            R(Function(_NEXUS.merger.ccr_off)),
    }
    extras = [
        IntegerRefST("n", 1, 50),
        Dictation("text"),
        Dictation("text2"),
        Dictation("text3"),
        Choice("enable", {
            "enable": True,
            "disable": False
        }),
        Choice("volume_mode", {
            "mute": "mute",
            "up": "up",
            "down": "down"
        }),
        generate_ccr_choices.__func__(_NEXUS),
        generate_sm_ccr_choices.__func__(_NEXUS),
        IntegerRefST("monitor", 1, 10)
    ]
    defaults = {"n": 1, "nnv": 1, "text": "", "volume_mode": "setsysvolume", "enable": -1}


control.non_ccr_app_rule(MainRule(), context=None, rdp=False)

if globals().has_key('profile_switch_occurred'):
    reload(sikuli)
else:
    profile_switch_occurred = None

print("\n*- Starting " + settings.SOFTWARE_NAME + " -*")

if settings.WSR:
    import pythoncom
    print("Windows Speech Recognition is garbage; it is " \
        +"recommended that you not run Caster this way. ")
    while True:
        pythoncom.PumpWaitingMessages()  # @UndefinedVariable
        time.sleep(.1)
