"""Offline Malayalam phrases for the scene descriptions produced by BlindAssist."""


OBJECT_LABELS = {
    "person": ("വ്യക്തി", "വ്യക്തികൾ"),
    "bicycle": ("സൈക്കിൾ", "സൈക്കിളുകൾ"),
    "car": ("കാർ", "കാറുകൾ"),
    "motorcycle": ("മോട്ടോർസൈക്കിൾ", "മോട്ടോർസൈക്കിളുകൾ"),
    "airplane": ("വിമാനം", "വിമാനങ്ങൾ"),
    "bus": ("ബസ്", "ബസുകൾ"),
    "train": ("ട്രെയിൻ", "ട്രെയിനുകൾ"),
    "truck": ("ട്രക്ക്", "ട്രക്കുകൾ"),
    "boat": ("ബോട്ട്", "ബോട്ടുകൾ"),
    "traffic light": ("ട്രാഫിക് ലൈറ്റ്", "ട്രാഫിക് ലൈറ്റുകൾ"),
    "fire hydrant": ("ഫയർ ഹൈഡ്രന്റ്", "ഫയർ ഹൈഡ്രന്റുകൾ"),
    "stop sign": ("സ്റ്റോപ്പ് ബോർഡ്", "സ്റ്റോപ്പ് ബോർഡുകൾ"),
    "parking meter": ("പാർക്കിംഗ് മീറ്റർ", "പാർക്കിംഗ് മീറ്ററുകൾ"),
    "bench": ("ബെഞ്ച്", "ബെഞ്ചുകൾ"),
    "bird": ("പക്ഷി", "പക്ഷികൾ"),
    "cat": ("പൂച്ച", "പൂച്ചകൾ"),
    "dog": ("നായ", "നായ്ക്കൾ"),
    "horse": ("കുതിര", "കുതിരകൾ"),
    "sheep": ("ചെമ്മരിയാട്", "ചെമ്മരിയാടുകൾ"),
    "cow": ("പശു", "പശുക്കൾ"),
    "elephant": ("ആന", "ആനകൾ"),
    "bear": ("കരടി", "കരടികൾ"),
    "zebra": ("സീബ്ര", "സീബ്രകൾ"),
    "giraffe": ("ജിറാഫ്", "ജിറാഫുകൾ"),
    "backpack": ("ബാക്ക്പാക്ക്", "ബാക്ക്പാക്കുകൾ"),
    "umbrella": ("കുട", "കുടകൾ"),
    "handbag": ("ഹാൻഡ്ബാഗ്", "ഹാൻഡ്ബാഗുകൾ"),
    "tie": ("ടൈ", "ടൈകൾ"),
    "suitcase": ("സ്യൂട്ട്കേസ്", "സ്യൂട്ട്കേസുകൾ"),
    "frisbee": ("ഫ്രിസ്ബി", "ഫ്രിസ്ബികൾ"),
    "skis": ("സ്കീസ്", "സ്കീസുകൾ"),
    "snowboard": ("സ്നോബോർഡ്", "സ്നോബോർഡുകൾ"),
    "sports ball": ("പന്ത്", "പന്തുകൾ"),
    "kite": ("പട്ടം", "പട്ടങ്ങൾ"),
    "baseball bat": ("ബേസ്ബോൾ ബാറ്റ്", "ബേസ്ബോൾ ബാറ്റുകൾ"),
    "baseball glove": ("ബേസ്ബോൾ ഗ്ലൗസ്", "ബേസ്ബോൾ ഗ്ലൗസുകൾ"),
    "skateboard": ("സ്കേറ്റ്ബോർഡ്", "സ്കേറ്റ്ബോർഡുകൾ"),
    "surfboard": ("സർഫ്ബോർഡ്", "സർഫ്ബോർഡുകൾ"),
    "tennis racket": ("ടെന്നീസ് റാക്കറ്റ്", "ടെന്നീസ് റാക്കറ്റുകൾ"),
    "bottle": ("കുപ്പി", "കുപ്പികൾ"),
    "wine glass": ("വൈൻ ഗ്ലാസ്", "വൈൻ ഗ്ലാസുകൾ"),
    "cup": ("കപ്പ്", "കപ്പുകൾ"),
    "fork": ("ഫോർക്ക്", "ഫോർക്കുകൾ"),
    "knife": ("കത്തി", "കത്തികൾ"),
    "spoon": ("സ്പൂൺ", "സ്പൂണുകൾ"),
    "bowl": ("പാത്രം", "പാത്രങ്ങൾ"),
    "banana": ("വാഴപ്പഴം", "വാഴപ്പഴങ്ങൾ"),
    "apple": ("ആപ്പിൾ", "ആപ്പിളുകൾ"),
    "sandwich": ("സാൻഡ്‌വിച്ച്", "സാൻഡ്‌വിച്ചുകൾ"),
    "orange": ("ഓറഞ്ച്", "ഓറഞ്ചുകൾ"),
    "broccoli": ("ബ്രോക്കോളി", "ബ്രോക്കോളികൾ"),
    "carrot": ("കാരറ്റ്", "കാരറ്റുകൾ"),
    "hot dog": ("ഹോട്ട് ഡോഗ്", "ഹോട്ട് ഡോഗുകൾ"),
    "pizza": ("പിസ്സ", "പിസ്സകൾ"),
    "donut": ("ഡോണട്ട്", "ഡോണട്ടുകൾ"),
    "cake": ("കേക്ക്", "കേക്കുകൾ"),
    "chair": ("കസേര", "കസേരകൾ"),
    "couch": ("സോഫ", "സോഫകൾ"),
    "potted plant": ("ചട്ടിച്ചെടി", "ചട്ടിച്ചെടികൾ"),
    "bed": ("കട്ടിൽ", "കട്ടിലുകൾ"),
    "dining table": ("ഭക്ഷണമേശ", "ഭക്ഷണമേശകൾ"),
    "toilet": ("ടോയ്ലറ്റ്", "ടോയ്ലറ്റുകൾ"),
    "tv": ("ടെലിവിഷൻ", "ടെലിവിഷനുകൾ"),
    "laptop": ("ലാപ്ടോപ്പ്", "ലാപ്ടോപ്പുകൾ"),
    "mouse": ("മൗസ്", "മൗസുകൾ"),
    "remote": ("റിമോട്ട്", "റിമോട്ടുകൾ"),
    "keyboard": ("കീബോർഡ്", "കീബോർഡുകൾ"),
    "cell phone": ("മൊബൈൽ ഫോൺ", "മൊബൈൽ ഫോണുകൾ"),
    "microwave": ("മൈക്രോവേവ്", "മൈക്രോവേവുകൾ"),
    "oven": ("ഓവൻ", "ഓവനുകൾ"),
    "toaster": ("ടോസ്റ്റർ", "ടോസ്റ്ററുകൾ"),
    "sink": ("സിങ്ക്", "സിങ്കുകൾ"),
    "refrigerator": ("റഫ്രിജറേറ്റർ", "റഫ്രിജറേറ്ററുകൾ"),
    "book": ("പുസ്തകം", "പുസ്തകങ്ങൾ"),
    "clock": ("ഘടികാരം", "ഘടികാരങ്ങൾ"),
    "vase": ("പൂപ്പാത്രം", "പൂപ്പാത്രങ്ങൾ"),
    "scissors": ("കത്രിക", "കത്രികകൾ"),
    "teddy bear": ("ടെഡി ബെയർ", "ടെഡി ബെയറുകൾ"),
    "hair drier": ("ഹെയർ ഡ്രയർ", "ഹെയർ ഡ്രയറുകൾ"),
    "toothbrush": ("ടൂത്ത് ബ്രഷ്", "ടൂത്ത് ബ്രഷുകൾ"),
    "stairs": ("പടികൾ", "പടികൾ"),
    "door": ("വാതിൽ", "വാതിലുകൾ"),
    "pothole": ("കുഴി", "കുഴികൾ"),
    "puddle": ("വെള്ളക്കെട്ട്", "വെള്ളക്കെട്ടുകൾ"),
    "ditch": ("ഓട", "ഓടകൾ"),
    "gutter": ("ഓട", "ഓടകൾ"),
    "canal": ("ചാൽ", "ചാലുകൾ"),
}

NUMBER_WORDS = {
    1: "ഒരു",
    2: "രണ്ട്",
    3: "മൂന്ന്",
    4: "നാല്",
    5: "അഞ്ച്",
    6: "ആറ്",
    7: "ഏഴ്",
    8: "എട്ട്",
    9: "ഒൻപത്",
    10: "പത്ത്",
}

POSITIONS = {
    "left": "ഇടതുവശത്ത്",
    "center": "മധ്യത്തിൽ",
    "right": "വലതുവശത്ത്",
}

DIRECTIONS = {
    "left": "ഇടത്തേക്ക്",
    "right": "വലത്തേക്ക്",
}


def _number(count):
    return NUMBER_WORDS.get(count, str(count))


def _object_name(name, count=1):
    singular, plural = OBJECT_LABELS.get(name, (name, name))
    if name == "person" and count > 1:
        return "ആളുകൾ"
    return singular if count == 1 else plural


def _counted_object(name, count):
    if name == "person":
        noun = "വ്യക്തി" if count == 1 else "ആളുകൾ"
        number = "ഒരു" if count == 1 else _number(count)
        return f"{number} {noun}"
    return f"{_number(count)} {_object_name(name, count)}"


def describe_scene_in_malayalam(counts, positions, motions, newly_tracked):
    """Format scene details as Malayalam without an online translation service."""
    if not counts:
        return "ഫ്രെയിമിൽ ഇപ്പോൾ വസ്തുക്കളൊന്നും കണ്ടെത്തിയില്ല."

    object_summary = ", ".join(
        _counted_object(name, count) for name, count in counts
    )
    sentences = [f"ദൃശ്യത്തിൽ {object_summary} കാണപ്പെടുന്നു."]

    if positions:
        position_summary = "; ".join(
            f"{_object_name(name)} {POSITIONS.get(position, 'മധ്യത്തിൽ')}"
            for name, position in positions
        )
        sentences.append(f"സ്ഥാനം: {position_summary}.")

    if motions:
        motion_summary = "; ".join(
            f"{_object_name(name)} ചിത്രത്തിൽ "
            f"{DIRECTIONS.get(direction, 'മുന്നോട്ട്')} നീങ്ങുന്നു"
            for name, direction in motions
        )
        sentences.append(f"ചലനം: {motion_summary}.")

    if newly_tracked:
        new_objects = ", ".join(_object_name(name) for name in newly_tracked)
        sentences.append(f"പുതുതായി കണ്ടെത്തിയത്: {new_objects}.")

    return " ".join(sentences)


def format_threat_warning_in_malayalam(name, zone, approaching):
    """Create a short spoken warning for a prioritized navigational hazard."""
    zone_phrase = {
        "left": "ഇടതുവശത്ത്",
        "center": "മുന്നിൽ",
        "right": "വലതുവശത്ത്",
    }.get(zone, "മുന്നിൽ")
    name_clean = str(name).strip().lower()

    if name_clean in ("ditch", "gutter", "canal"):
        return f"ശ്രദ്ധിക്കുക. {zone_phrase} ഓടയുണ്ട്. അരികിലേക്ക് പോകരുത്."
    if name_clean == "pothole":
        return f"മുന്നറിയിപ്പ്. {zone_phrase} റോഡിൽ കുഴിയുണ്ട്. ശ്രദ്ധിച്ചു നടക്കുക."
    if name_clean == "puddle":
        return f"ശ്രദ്ധിക്കുക. {zone_phrase} വെള്ളക്കെട്ടുണ്ട്."

    object_name = _object_name(name_clean)
    if approaching:
        return f"മുന്നറിയിപ്പ്. {object_name} {zone_phrase} അതിവേഗം അടുത്തുവരുന്നു."
    return f"മുന്നറിയിപ്പ്. {object_name} {zone_phrase} വളരെ അടുത്തുണ്ട്."
