from castervoice.lib.imports import *

_NEXUS = control.nexus()

def fix_dragon_double(nexus):
    try:
        lr = nexus.history[len(nexus.history) - 1]
        lu = " ".join(lr)
        Key("left/5:" + str(len(lu)) + ", del").execute()
    except Exception:
        utilities.simple_log(False)

def cap_dictation(dictation):
    input_list = str(dictation).split(" ")
    output_list = []
    for i in range(len(input_list)):
        if input_list[i] == "cap":
            input_list[i+1] = input_list[i+1].title()
        else:
            output_list.append(input_list[i])
    Text(" ".join(output_list)).execute()

# extras are common to both classes in this file
extras_for_whole_file = [
        Dictation("text"),
        IntegerRefST("n10", 1, 10),
        Choice("first_second_third", {
            "first": 0,
            "second": 1,
            "third": 2,
            "fourth": 3,
            "fifth": 4,
            "six": 5,
            "seventh": 6
        }),

    ]
defaults_for_whole_file = {"n10": 1, "text": "",}

class DragonRule(MergeRule):
    pronunciation = "dragon"

    mapping = {
        "format <text>":
            Function(cap_dictation, extra={"text"}),
        '(lock Dragon | deactivate)':
            R(Playback([(["go", "to", "sleep"], 0.0)])),
        '(number|numbers) mode':
            R(Playback([(["numbers", "mode", "on"], 0.0)])),
        'spell mode':
            R(Playback([(["spell", "mode", "on"], 0.0)])),
        'dictation mode':
            R(Playback([(["dictation", "mode", "on"], 0.0)])),
        'normal mode':
            R(Playback([(["normal", "mode", "on"], 0.0)])),
        '(command mode | command on | com on)':
            R(Playback([(["command", "mode", "on"], 0.0)])),
        '(command off | com off)':
            R(Playback([(["command", "mode", "off"], 0.0)])),
        "reboot dragon":
            R(Function(utilities.reboot)),
        "fix dragon double":
            R(Function(fix_dragon_double, nexus=_NEXUS)),
        "left point":
            R(Playback([(["MouseGrid"], 0.1), (["four", "four"], 0.1), (["click"], 0.0)])),
        "right point":
            R(Playback([(["MouseGrid"], 0.1), (["six", "six"], 0.1), (["click"], 0.0)])),
        "center point":
            R(Playback([(["MouseGrid"], 0.1), (["click"], 0.0)])),


        "show windows":
            R(Mimic("list", "all", "windows")),
        "cory <text>":
            R(Mimic("correct", extra="text") + WaitWindow(title="spelling window") + Mimic("choose", "one")),
        "cory that":
            R(Mimic("correct", "that") + WaitWindow(title="spelling window") + Mimic("choose", "one")),

        "make that <text>":
            R(Mimic("scratch", "that") + Mimic(extra="text")),
        "scratch [<n10>]":
            R(Playback([(["scratch", "that"], 0.03)])),

        "train word":
            R(Mimic("train", "that") + Key("a-r/200, s")),
        "word train":
            R(Key("c-c/20") + Mimic("edit", "vocabulary") + Pause("100") +
            Key("c-v/5, tab, down, up, a-t/50, enter/50, a-r/250, s/50, escape")),
        "(add train | train from add word)":
            R(Key("a-a/2, enter/300, a-s")),
    # Users may want to adjust the way time on the next four commands
        "(train from vocab | cab train)":
            R(Key("a-t/50, enter/50, a-r/250, s")),
        "(train from vocab | cab train)":
            R(Key("a-t/50, enter/50, a-r/250, s")),
        "remove from vocab":
            R(Key("c-c/5") + Mimic("edit", "vocabulary") + Pause("20") +
            Key("c-v/10, tab, down, up/5, a-d, y, escape/30, right")),
        "(add to vocab | vocab that)":
            R(Key("c-c/5") + Mimic("add", "word") + Pause("20") +
            Key("c-v, a-a/2, enter/300, a-s/30, right")),

        "recognition history":
            R(Playback([(["view", "recognition", "history"], 0.03)])),
        "peak [recognition] history":
            R(Playback([(["view", "recognition", "history"], 0.03)])
                + Pause("300") + Key("escape")),
        "[dictation] sources":
            R(Mimic("manage", "dictation", "sources")),

        # A Natlink Command
        "clear caster log":
            R(Function(utilities.clear_log)),
    }
    # see above
    extras = extras_for_whole_file
    defaults = defaults_for_whole_file


class SpellingWindowRule(MergeRule):
    mapping = {
         # todo: make these CCR
         "<first_second_third> word":
            R(Key("home, c-right:%(first_second_third)d, cs-right")),
         "last [word]":
            R(Key("right, cs-left")),
         "second [to] last word":
            R(Key("right, c-left:1, cs-left")),
         "<n10>":
            R(Mimic("choose", extra="n10")),
            # consider making the above command global so that it works when you say something like
            # "insert before 'hello'" where there are multiple instances of 'hello'
            # personally I think it's better just to have the setting where Dragon choose is the closest instance
    }

    # see above
    extras = extras_for_whole_file
    defaults = defaults_for_whole_file


if not settings.WSR:
    control.non_ccr_app_rule(DragonRule())

    context = AppContext(executable="natspeak")
    control.non_ccr_app_rule(SpellingWindowRule(), context=context)