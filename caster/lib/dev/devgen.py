from dragonfly import MappingRule, Grammar, Config, Section, Item, Key, Text, Dictation, Mimic
from caster.lib import settings, utilities
import os

_grammar = Grammar("dev gen")


class ConfigDev(Config):
    def __init__(self, name):
        Config.__init__(self, name)
        self.cmd = Section("Language section")
        self.cmd.map = Item(
            {
                "mimic <text>": Mimic(extra="text"),
            },
            namespace={
                "Key": Key,
                "Text": Text,
            })
        self.cmd.extras = Item([Dictation("text")])
        self.cmd.defaults = Item({})

def _create_file():
    lines = [
        'from dragonfly import *',
        'from caster.lib import navigation',
        'from caster.lib.dfplus.state.short import R',
        '',
        'release = Key("shift:up, ctrl:up")',
        'noSpaceNoCaps = Mimic("\\no-caps-on") + Mimic("\\no-space-on") #this gets added on the right side',
        '',
        '# expand this rule skeleton for fast testing:',
        'cmd.map = { "some command goes here": R(Pause("100"), rdescript="test command"), }',
        'cmd.extras = []',
        'cmd.defaults = {}'
    ]
    with open(settings.SETTINGS["paths"]["CONFIGDEBUGTXT_PATH"],'w') as configdebug:
        for line in lines:
            configdebug.write(line)
            configdebug.write('\r\n')
    

def generate_rule(path):
    configuration = ConfigDev("dev")
    if not os.path.isfile(settings.SETTINGS["paths"]["CONFIGDEBUGTXT_PATH"]):
        _create_file()
    configuration.load(path)
    return MappingRule(
        exported=True,
        mapping=configuration.cmd.map,
        extras=configuration.cmd.extras,
        defaults=configuration.cmd.defaults)


# Create and load this module's grammar.
def refresh():
    global _grammar
    _grammar.unload()
    while len(_grammar.rules) > 0:
        _grammar.remove_rule(_grammar.rules[0])
    try:
        rule = generate_rule(settings.SETTINGS["paths"]["CONFIGDEBUGTXT_PATH"])
        _grammar.add_rule(rule)
        _grammar.load()
    except Exception:
        utilities.simple_log()
