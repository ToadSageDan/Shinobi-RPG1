"""Boss cutscene engine for Shinobi RPG.

Each of the five main-region bosses has a multi-beat cinematic intro:
  1. Environment / mood description
  2. Boss entrance lines
  3. Player dialogue choice  →  boss reacts, stance may shift
  4. Pre-battle outro

Calling ``play_boss_cutscene`` returns a result dict the caller can use
to adjust villain stance and choose the best approach opener.
"""

from __future__ import annotations

import sys
import textwrap
import time
from typing import Any, Dict, List, Tuple

# ── cosmetic constants ─────────────────────────────────────────────────────────

_DIVIDER  = "─" * 62
_THICK    = "═" * 62
_STAR     = "✦"
_SCROLL   = "≋" * 62
_PAUSE    = "  [ ENTER to continue... ]"

AFFINITY_COLOR = {
    "fire":  "🔥",
    "water": "💧",
    "earth": "🌿",
    "wind":  "💨",
}

# ── low-level print helpers ────────────────────────────────────────────────────

def _p(text: str = "") -> None:
    print(text)


def _w(text: str, indent: int = 4) -> None:
    prefix = " " * indent
    for line in text.splitlines():
        print(textwrap.fill(line, width=72, initial_indent=prefix, subsequent_indent=prefix))


def _slow(text: str, delay: float = 0.03) -> None:
    """Print ``text`` one character at a time for cinematic effect."""
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        if ch not in (" ", "\n"):
            time.sleep(delay)
    print()


def _pause() -> None:
    try:
        input(_PAUSE)
    except (EOFError, KeyboardInterrupt):
        _p()


def _scene_header(title: str) -> None:
    _p()
    _p(_THICK)
    _p(f"  {title}")
    _p(_THICK)


def _panel(lines: List[str]) -> None:
    _p(_SCROLL)
    for line in lines:
        _w(line)
    _p(_SCROLL)


def _villain_speaks(name: str, affinity_icon: str, text: str) -> None:
    _p()
    _p(f"  {affinity_icon}  {name.upper()} :")
    _w(f'"{text}"')
    _p()


def _player_speaks(text: str) -> None:
    _p(f"  YOU :  \"{text}\"")


def _pick_choice(question: str, choices: List[str]) -> int:
    _p()
    for idx, c in enumerate(choices, 1):
        _p(f"  {idx}. {c}")
    _p()
    while True:
        try:
            raw = input(f"  {question} > ").strip()
        except (EOFError, KeyboardInterrupt):
            _p("\n  [Interrupted — goodbye, shinobi.]")
            sys.exit(0)
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(choices):
                return idx
        lower = raw.lower()
        matches = [i for i, c in enumerate(choices) if c.lower().startswith(lower)]
        if len(matches) == 1:
            return matches[0]
        _p("  ✗ Enter a number or a unique label prefix.")


# ── Cutscene data ──────────────────────────────────────────────────────────────
#
# Each entry is a dict with:
#   affinity_icon  str
#   intro_beats    List[str]   — paragraphs shown before the boss speaks
#   entrance_lines List[str]   — boss appearance monologue (2-3 sentences each)
#   player_choices  List[Tuple[str, str]]
#                  — (label shown to player, player line read aloud)
#   boss_responses  List[str]  — indexed to player_choices
#   stance_deltas   List[int]  — aggression score change per choice
#   pre_battle_line str        — final line before combat
#   defeat_lines    Dict[str, str]  — per approach: kill / charm / stealth / evasion
#   taunt_lines     List[str]  — injected mid-fight (optional flavour)

BOSS_CUTSCENE_DATA: Dict[str, Dict[str, Any]] = {

    # ── 1. Kage Renda — Verdant Gate ──────────────────────────────────────────
    "Kage Renda": {
        "affinity_icon": AFFINITY_COLOR["wind"],
        "region_mood": "Verdant Gate — a highland corridor choked with wind-bent cedar and the rusted echo of old council banners.",
        "intro_beats": [
            "The upper pass falls silent the moment you crest the ridge. "
            "Cedar branches stop swaying. Even the wind seems to hold its breath.",

            "Kage Renda stands at the far end of the stone overlook, back to you, facing the "
            "valley where Leafrise once dispatched orders like edicts. His dark cloak snaps "
            "once in a returning gust, then goes still. He has known you were coming for "
            "at least an hour.",
        ],
        "entrance_lines": [
            "Without turning, he speaks — voice low, carved down to its bare edge.",

            "\"Twelve years I held a blade for people who counted loyalty as a ledger entry. "
            "When they crossed the final column, they expected grief.  "
            "I gave them vacancy.\"",

            "He turns. The spiral hilt at his hip catches the grey light — the same weapon "
            "he drilled against highland stone for five years in exile. His eyes carry the "
            "specific calm of a man who has already made every difficult choice.",

            "\"You stand where the old order stood. Tell me —\" "
            "he sets his weight on the back foot, hand drifting toward the hilt — "
            "\"do you intend to repeat its mistakes?\"",
        ],
        "player_choices": [
            ("Challenge him — I didn't come to inherit their failures.",
             "I didn't come to inherit their failures. I came to end what they started."),
            ("Acknowledge his grievance — I know what the council cost people.",
             "I know what the council cost people. That's why I'm here — to close the wound, not reopen it."),
            ("Deflect — The past belongs to the past. What matters is who controls this ridge after today.",
             "The past belongs to the past. All that matters now is who controls this ridge after today."),
        ],
        "boss_responses": [
            # Aggressive → Renda respects force
            "A ghost of approval crosses his face. \"Honest. Dangerous. "
            "Exactly what the highland needs.\" "
            "He draws the blade in a single unhurried line. "
            "\"Then come — and prove that sentence with steel.\"",

            # Diplomatic → Renda pauses, remembers
            "His hand stills on the hilt. A long silence. "
            "\"You sound like a verdict I should have trusted years ago.\" "
            "He straightens but does not draw. "
            "\"I will not give this ridge to words alone. Show me the principle holds under pressure.\"",

            # Evasive → Renda reads it as pragmatic
            "He tilts his head — a duelist reading an unfamiliar guard. "
            "\"Practical. No ideology, no sentiment. I can respect that.\" "
            "The blade slides half-free. \"Let's see if your footwork matches your philosophy.\"",
        ],
        "stance_deltas": [2, -2, 0],  # aggressive choice → +2; diplomatic → -2; neutral → 0
        "pre_battle_line": "The wind returns — and Kage Renda moves with it.",
        "defeat_lines": {
            "kill": (
                "He drops to one knee. Blood drips from the spiral blade onto the stone. "
                "\"You are... what I should have been,\" he says, and lets the sword rest. "
                "The highland is yours."
            ),
            "charm": (
                "His sword lowers an inch. Then another. "
                "\"I never thought I would hear those words from someone standing opposite me.\" "
                "He exhales — twelve years of tension leaving his shoulders all at once. "
                "\"The gate is open. Don't waste the peace I couldn't build.\" "
                "He turns and walks into the cedar dark without looking back."
            ),
            "stealth": (
                "He stands alone in the centre of the overlook, sword raised against shadows "
                "that have already moved on. When he finally lowers the blade, "
                "he speaks to the empty pass: "
                "\"No blood. No monument. Just... over.\" A pause. \"Perhaps that is mercy.\""
            ),
            "evasion": (
                "He stands at the ridge edge long after the encounter ends, staring at the valley. "
                "\"You slipped through every opening I gave you.\" He sheathes the blade. "
                "\"This ridge doesn't need a warden anymore. It needs a wall of that kind of patience.\""
            ),
        },
        "taunt_lines": [
            "\"You're moving like someone who learned the form but not the reason for it.\"",
            "\"The council sent shinobi who fought exactly like you. They are all buried below this pass.\"",
            "\"Better. Keep that angle — you almost looked like you meant it.\"",
        ],
    },

    # ── 2. General Voln — Ashen Cradle ────────────────────────────────────────
    "General Voln": {
        "affinity_icon": AFFINITY_COLOR["fire"],
        "region_mood": "Ashen Cradle — the remnant of an industrial war-port that never fully cooled.",
        "intro_beats": [
            "The heat hits you before the noise does. Cinder Port's foundry district still "
            "burns around the clock — not for manufacture now, but because General Voln ordered "
            "the forges kept hot as a symbol. This war never ended. It just changed locations.",

            "He is standing on the factory command platform when you arrive, addressing a "
            "formation of ash-grey soldiers. He does not dismiss them. He lets you walk "
            "into the middle of the briefing.",
        ],
        "entrance_lines": [
            "He finishes his sentence — something about supply corridor discipline — "
            "and only then turns to face you. The soldiers do not move.",

            "\"You walked through the outer ring alone.\" He says it the way a field surgeon "
            "notes a wound: purely clinical. \"Either you are very skilled, or you have "
            "so little respect for my perimeter that you didn't bother counting the sentries.\"",

            "He descends the platform steps — heavy boots, no ceremony. The formation parts "
            "around him without being ordered to.",

            "\"I have fought forty-three engagements in the last eight years. "
            "I have never once needed to explain why I fight.\" "
            "His gauntlets catch the forge light. "
            "\"Give me a reason to explain it to you.\"",
        ],
        "player_choices": [
            ("This ends here — the Cradle doesn't belong to your war machine.",
             "This ends here, General. The Cradle belongs to the people you're burning it for."),
            ("I know why you fight — I'm here to offer you something better.",
             "I know what's driving you. I'm here to offer you a different kind of victory."),
            ("Test me however you like. I'll still be standing when the forge goes cold.",
             "Test me however you want, General. I'll still be standing when every forge here goes cold."),
        ],
        "boss_responses": [
            # Aggressive
            "He stops walking. Studies you. "
            "\"Direct. Tactically idiotic. But honest.\" "
            "A fist closes. \"Formation — stand down. This one is mine.\" "
            "The soldiers step back. The forges roar.",

            # Diplomatic
            "He pauses mid-step. The slightest crack in the military composure. "
            "\"Better.\" The gauntlets loosen. \"Tell me what you think that looks like.\" "
            "His stance stays closed, but the forward pressure backs off half a step.",

            # Defiant
            "He actually smiles — tight, approving. "
            "\"That is the first honest thing anyone has said to me in three campaigns.\" "
            "He rolls his neck. \"I'm going to hit you hard enough to see if you mean it.\"",
        ],
        "stance_deltas": [2, -1, 1],
        "pre_battle_line": "The forge-heat doubles. General Voln exhales a column of hot air and charges.",
        "defeat_lines": {
            "kill": (
                "He goes down on both knees. The gauntlets slam into the ash floor. "
                "\"Forty-four,\" he counts quietly. Then: \"Tell them — the Cradle held. "
                "It was the warlord who failed it.\" He pitches forward into the ash."
            ),
            "charm": (
                "His forward march stops. He stands very still, looking past you at the formation. "
                "\"I built a war machine because I didn't know how to build anything else.\" "
                "He pulls the forge key from his coat and sets it on the ground between you. "
                "\"The Cradle needs engineers now. Not generals. "
                "If you can find them — use the furnaces to rebuild.\""
            ),
            "stealth": (
                "The formation holds the line — but General Voln stands at its centre alone, "
                "orders falling on absent ears. Every decisive point has already slipped. "
                "He sheathes his gauntlets and speaks to no one: "
                "\"A campaign you can't see is a campaign you've already lost.\""
            ),
            "evasion": (
                "He pursues every vector and finds nothing. When the engagement finally stills, "
                "he looks at the cold forge slots — one by one going dark. "
                "\"You didn't fight my war,\" he says, slowly. \"You made it irrelevant.\" "
                "The soldiers begin drifting toward the exits."
            ),
        },
        "taunt_lines": [
            "\"Slower on the left. Your opponents won't be so polite about it.\"",
            "\"I've crushed three shinobi cells this month alone. What makes yours different?\"",
            "\"Move! You are letting the heat own you instead of using it.\"",
        ],
    },

    # ── 3. Admiral Neris — Tideglass Basin ────────────────────────────────────
    "Admiral Neris": {
        "affinity_icon": AFFINITY_COLOR["water"],
        "region_mood": "Tideglass Basin — a coastal fortress district where salt, politics, and old debts dissolve into each other.",
        "intro_beats": [
            "Azure Rest sits where the Tideglass river fans out into the coastal shelf — "
            "a city that has changed hands three times in the last decade and wears each "
            "transition like a waterline scar. The harbour smells of brine and wet rope "
            "and something older: the residue of every command that was given and not rescinded.",

            "Admiral Neris receives you in the fleet command room — maps, tide tables, "
            "sealed orders stacked in perfect columns. She does not look up when you enter.",
        ],
        "entrance_lines": [
            "\"You are eleven minutes early,\" she says, turning a tide chart. "
            "\"Which means you scouted the route and chose to arrive before I expected you. "
            "Interesting.\"",

            "She sets the chart down and finally looks at you — pale grey eyes, "
            "fleet-officer composure, the particular stillness of someone who has issued "
            "drowning orders and lived with the arithmetic.",

            "\"The basin has been under three different flags in eight years. "
            "Each one arrived with exactly the kind of conviction you're wearing. "
            "None of them understood the tides.\"",

            "She steps around the command table. No weapon drawn — not yet. "
            "\"Tell me why this time is different.\"",
        ],
        "player_choices": [
            ("Because I'm not here to plant a flag — I'm here to end the rotation.",
             "I'm not here to plant a flag, Admiral. I'm here to end the cycle that's been drowning this basin."),
            ("Because the people of Azure Rest told me what they actually need. Did any of the others ask?",
             "Because I asked the people of Azure Rest what they actually need. Did any of the others bother?"),
            ("Because I'm the only one who made it past your outer perimeter without a map.",
             "Because I walked in here without your tide tables or your maps, and I'm still standing."),
        ],
        "boss_responses": [
            # Principled → she evaluates
            "She is quiet for four full seconds. "
            "\"Every actor who wanted to end the rotation said exactly that.\" "
            "She lifts one hand and the room's side doors open. Elite tide-guards — stationed. "
            "\"Prove the sentence. Show me what 'ending it' looks like that doesn't become the next flag.\"",

            # Empathetic → she is surprised
            "Something shifts — barely perceptible — behind the fleet composure. "
            "\"No,\" she admits, low and precise. \"None of them asked.\" "
            "A long pause. \"I will listen to what you say next very carefully.\"",

            # Skill-based → she respects competence
            "\"Twelve sentries. Three checkpoints. One false-flag transit barge.\" "
            "She almost smiles. \"You counted.\" "
            "She straightens her collar. \"Very well. Let us see if the rest of you matches your entrance.\"",
        ],
        "stance_deltas": [1, -2, 0],
        "pre_battle_line": "The tide-guard formation locks. Admiral Neris steps forward — and the basin holds its breath.",
        "defeat_lines": {
            "kill": (
                "She catches herself against the command table. The tide charts scatter. "
                "\"The basin will flood again,\" she says quietly. \"Without someone to read the water.\" "
                "She straightens as far as she can manage. \"You had better be that person.\""
            ),
            "charm": (
                "She sets both hands flat on the table — a deliberate stillness. "
                "\"I have been managing a drowning and calling it governance.\" "
                "She looks at the tide charts for a long moment. "
                "\"Take the fleet command seal. The basin needs a custodian, not an admiral. "
                "I will draft the transition orders myself.\""
            ),
            "stealth": (
                "One by one the secured positions go quiet. When Neris finally stands alone "
                "in the command room, the tide charts are unmarked — every annotation stripped. "
                "\"You moved through the basin like the water itself,\" she says to the empty room. "
                "\"I cannot contest what I cannot see.\" She sets the command seal on the table and leaves."
            ),
            "evasion": (
                "Three coordinated advances, three redirections. Neris walks the perimeter "
                "of the command room alone, reviewing the tide charts with new eyes. "
                "\"You refused every engagement I offered. That is a form of mastery, "
                "not cowardice.\" She presses the fleet seal into the table edge. \"It is yours.\""
            ),
        },
        "taunt_lines": [
            "\"You're fighting the current instead of reading it. That will cost you depth.\"",
            "\"I have coordinated fleet engagements in worse weather than this conversation.\"",
            "\"Recover faster. The tide does not wait for a shinobi to find their footing.\"",
        ],
    },

    # ── 4. Zephyr Tyrant — Stormwall Ridge ────────────────────────────────────
    "Zephyr Tyrant": {
        "affinity_icon": AFFINITY_COLOR["wind"],
        "region_mood": "Stormwall Ridge — the high crown of the continent, where the air itself takes sides.",
        "intro_beats": [
            "Nothing grows at this altitude that isn't shaped by the wind. "
            "The ridge stones are bevelled on three sides. The remaining shinobi posts here "
            "wear reinforced cloaks knotted at four points — anything looser gets torn free "
            "and never comes back.",

            "Zephyr Tyrant is not standing. He is suspended — three metres off the ridgeline, "
            "arms wide, riding a locked air current like a throne. He is already looking at you. "
            "He has been looking at you since you started climbing.",
        ],
        "entrance_lines": [
            "\"There.\" One word. A kingdom annexed by a pronoun.",

            "\"You are the third shinobi to reach the summit this season.\" "
            "He does not come down. \"The other two understood — eventually — "
            "that the ridge belongs to the storm. You look like someone who hasn't understood that yet.\"",

            "The wind picks up. Loose stone fragments lift off the path behind you.",

            "\"I don't require tribute. I don't require submission.\" "
            "He tilts one hand and the current tightens. "
            "\"I require acknowledgement. That the ridge is not yours. "
            "That the storm was here before you — and will be here long after.\" "
            "He descends, one unhurried metre at a time. \"Do you acknowledge?\"",
        ],
        "player_choices": [
            ("No. The ridge belongs to whoever can hold it. I intend to hold it.",
             "No. The ridge belongs to whoever can hold it against every storm that tests it. "
             "Today that's me."),
            ("I don't need to own it. I just need to pass through — and you can't stop that.",
             "I'm not here to claim the ridge. I'm here to pass through. "
             "The storm can have it after."),
            ("The storm shaped this ridge. But so did the people who built shelters in its shadow.",
             "The storm shaped this ridge, yes. But the people who built shelters in its shadow "
             "shaped it too. They don't deserve to lose it."),
        ],
        "boss_responses": [
            # Bold challenge → he is delighted
            "He stops mid-descent. A long, wind-split silence. "
            "\"Oh.\" His head tilts. \"You actually mean that.\" "
            "He smiles — open and dangerous in equal measure. "
            "\"Then we understand each other perfectly. Let's see if you can hold it "
            "against everything I am.\"",

            # Practical → he finds it frustrating
            "The current tightens sharply. He does not smile. "
            "\"Pass through.\" He repeats it like a flaw in the argument. "
            "\"No one 'passes through' the ridge. You walk it, you claim it, or you fall. "
            "There is no middle altitude.\"",

            # Appeal to the people → he pauses
            "He goes completely still in the air current — an unnatural stillness. "
            "Then: \"I have not thought about the shelters for a very long time.\" "
            "Something like conflict crosses his face. "
            "\"They would not thank me for this conversation. "
            "Fight for them, then. I want to see if their cause carries weight at this altitude.\"",
        ],
        "stance_deltas": [2, 0, -1],
        "pre_battle_line": "The summit wind becomes a wall of force — and Zephyr Tyrant steps into it like a crown.",
        "defeat_lines": {
            "kill": (
                "He spirals down from the air current, slow as a leaf, "
                "and lands seated on the ridgestone. "
                "\"The storm picked someone worthy this time,\" he says, without bitterness. "
                "\"Carry it well. It is heavier than it looks.\""
            ),
            "charm": (
                "The current drops. He stands on the stone for the first time — "
                "just a person, feet on ground. "
                "\"I have been the wind so long I forgot it can change direction.\" "
                "He turns away from the summit. \"The ridge is yours. "
                "Use it better than I did.\""
            ),
            "stealth": (
                "He searches the entire ridgeline — every current, every gap. "
                "You are simply not where the storm expects you to be. "
                "When the wind finally stills, he speaks into nothing: "
                "\"You moved like a gap in the gale. "
                "I can't fight a gap.\" He descends the far side of the ridge alone."
            ),
            "evasion": (
                "Every attempt to corner you turns into empty wind. "
                "He finally lands and does not lift again. "
                "\"You treated the storm like weather instead of an opponent.\" "
                "A long look at the horizon. "
                "\"That is smarter than fighting it. I should have known that earlier.\""
            ),
        },
        "taunt_lines": [
            "\"You're bracing against the wind instead of reading it. The ridge will punish that.\"",
            "\"Better. But you're still three steps behind the current.\"",
            "\"The last shinobi who fought me here fell for forty metres before the updraft caught him.\"",
        ],
    },

    # ── 5. Ashen Monarch — Sunken Hollow ──────────────────────────────────────
    "Ashen Monarch": {
        "affinity_icon": AFFINITY_COLOR["earth"],
        "region_mood": "Sunken Hollow — an underground fortress complex older than every faction claiming the surface above it.",
        "intro_beats": [
            "The descent takes twenty minutes. Each passage narrows, then widens, "
            "then narrows again — as if the hollow is testing whether you deserve to reach the bottom. "
            "Torch brackets line the walls at intervals too regular to be accidental: "
            "this darkness is managed.",

            "The Ashen Monarch is in the lowest chamber — a cathedral of compressed earth "
            "and old stone, lit by vein-fires that run through the floor like frozen lightning. "
            "He is not standing. He is seated in a throne carved directly from the bedrock. "
            "He looks like the mountain decided to develop opinions.",
        ],
        "entrance_lines": [
            "The chamber does not echo. Sound arrives and stops, absorbed.",

            "\"You are the first to reach this depth in eleven years.\" "
            "His voice is the sound of stone settling. "
            "\"The others either turned back or are part of the walls now.\"",

            "He does not rise. There is no urgency in him at any scale. "
            "He has been here longer than the factions above have existed, "
            "and he will be here after their names are forgotten.",

            "\"The surface sends someone new whenever it wants something from the deep.\" "
            "He regards you without hostility and without warmth — "
            "the way a geologist regards an interesting sample. "
            "\"What do you want from the Sunken Hollow, shinobi? "
            "Be precise. The stone records everything said here.\"",
        ],
        "player_choices": [
            ("The surface is collapsing. I need the Hollow to stop being a threat long enough to let it heal.",
             "The surface is collapsing under its own fractures. "
             "I need the Hollow to stop being a threat long enough for it to heal itself."),
            ("I want to understand what the Hollow is protecting down here — and whether it's worth protecting.",
             "I want to understand what you are actually guarding down here. "
             "And whether it is worth what it costs the surface."),
            ("I don't want anything from the Hollow. I want to make sure the Hollow doesn't want anything from us.",
             "I'm not here to take anything. I'm here to make sure the Hollow has no reason to reach upward."),
        ],
        "boss_responses": [
            # Appeal to surface → he considers it
            "A long silence — long enough that the vein-fires dim and brighten once. "
            "\"Healing.\" He tests the word. \"The surface has called many things healing. "
            "Most of them required the Hollow to pay for it.\" "
            "He rises — slowly, the way a fault line rises. \"Show me what this healing costs.\"",

            # Philosophical → he is genuinely interested
            "\"Finally.\" Something that might be approval. "
            "\"No one has asked that in eleven years.\" "
            "He steps off the throne dais. \"The Hollow protects what the surface would misuse. "
            "Whether that is 'worth it' depends entirely on what you do with the answer.\"",

            # Defensive reasoning → he respects the boundary
            "\"Self-preservation.\" He nods, once. \"A clean reason. No ideology. No conquest.\" "
            "A pause of tectonic patience. \"The Hollow respects that. "
            "Let us confirm your boundary holds under pressure.\"",
        ],
        "stance_deltas": [-1, -2, 1],
        "pre_battle_line": "The vein-fires pulse once. The Ashen Monarch raises one hand — and the stone obeys.",
        "defeat_lines": {
            "kill": (
                "He goes down like a section of cliff — slowly, "
                "with a kind of geological inevitability. "
                "\"The surface has its champion,\" he says, settling into the floor. "
                "\"Seal the deep access before something worse rises to fill the vacancy.\""
            ),
            "charm": (
                "He sits again — not from weakness, but because the argument is complete. "
                "\"You are the first surface-walker in eleven years to make a case "
                "the Hollow can accept.\" "
                "He sets the hollow seal on the stone before him. "
                "\"Take it. And remember — the deep waits for every surface promise to be kept.\""
            ),
            "stealth": (
                "He sits in the sealed chamber for hours after the encounter ends, "
                "stone-still, listening. "
                "\"A shinobi who moves through stone like water,\" he says to the vein-fires. "
                "\"The Hollow has no argument against that kind of patience.\" "
                "The seal rises from the bedrock on its own."
            ),
            "evasion": (
                "Every collapse he triggers misses. Every trap closes on empty air. "
                "He does not pursue. "
                "\"You did not fight the Hollow. You refused to be where it expected you.\" "
                "A long, considering silence. \"That is the only lesson worth teaching down here.\" "
                "The path back to the surface opens."
            ),
        },
        "taunt_lines": [
            "\"The surface breeds fighters who expect the ground to hold still. It will not.\"",
            "\"Eleven years of stillness teaches patience you cannot train into a body in a season.\"",
            "\"You are fighting well — for someone who has never contested bedrock before.\"",
        ],
    },
}

MINOR_ENCOUNTER_CUTSCENES: Dict[str, Dict[str, str]] = {
    "Mist Ronin": {
        "title": "A ronin tests the border silence",
        "beat": (
            "A lone ronin steps from the fog with one hand near the hilt and the other "
            "resting on a stolen Leafrise courier sash. This is less an ambush than a warning "
            "that the border still belongs to whoever can hold it."
        ),
    },
    "Ash Mercenaries": {
        "title": "Cinder Port's hired blades arrive first",
        "beat": (
            "Mercenaries in heat-scored armor drift out from the forge haze, checking your "
            "stance before they check their orders. Somebody in the Cradle is paying close "
            "attention to who crosses these streets."
        ),
    },
    "Stormcaller Scouts": {
        "title": "The ridge spots you before you spot it",
        "beat": (
            "Static cracks between iron prayer tags as the scouts take the high ground. "
            "They are not here to stop the story — only to make sure the storm hears your name."
        ),
    },
}


# ── Public API ─────────────────────────────────────────────────────────────────

def play_boss_cutscene(
    boss_name: str,
    player_name: str,
    player_backstory_hook: str | None = None,
    villain_relationship_arc: str = "dormant",
) -> Dict[str, Any]:
    """Run the full cinematic intro for ``boss_name`` and return a result dict.

    Returns::

        {
            "dialogue_tone": "aggressive" | "diplomatic" | "pragmatic",
            "stance_delta":  int,          # to apply to villain aggression_score
            "player_choice_index": int,    # 0-based
            "boss_name": str,
        }
    """
    data = BOSS_CUTSCENE_DATA.get(boss_name)
    if data is None:
        # Unknown boss — show a minimal placeholder
        _scene_header(f"⚔️   BOSS ENCOUNTER — {boss_name}")
        _p(f"  {boss_name} stands before you, ready to fight.")
        _pause()
        return {
            "dialogue_tone": "pragmatic",
            "stance_delta": 0,
            "player_choice_index": 0,
            "boss_name": boss_name,
        }

    icon = data["affinity_icon"]

    # ── Scene header ──────────────────────────────────────────────────────────
    _scene_header(f"{icon}  BOSS ENCOUNTER — {boss_name.upper()}")
    _p()
    _p(f"  📍 {data['region_mood']}")
    _pause()

    # ── Intro beats ───────────────────────────────────────────────────────────
    _scene_header(f"{icon}  APPROACH")
    for beat in data["intro_beats"]:
        _p()
        _w(beat)
    _pause()

    # ── Boss entrance ─────────────────────────────────────────────────────────
    _scene_header(f"{icon}  {boss_name.upper()} APPEARS")
    for line in data["entrance_lines"]:
        _p()
        _w(line)
    _pause()

    # ── Backstory hook (if the villain recognises the player's path) ──────────
    if player_backstory_hook:
        _p()
        _p(_DIVIDER)
        _p(f"  [Villain recognises your path]")
        _w(player_backstory_hook)
        _p(_DIVIDER)
        _pause()

    # ── Reformed arc line ─────────────────────────────────────────────────────
    if villain_relationship_arc == "reformed":
        _p()
        _p(_DIVIDER)
        _p("  [Something is different — the villain's arc has turned]")
        _w(
            f"{boss_name} pauses. There is something unfamiliar in their bearing — "
            "a stillness that does not belong to a fighter preparing to attack. "
            "Whatever drove the hardness in their eyes has run its course."
        )
        _p(_DIVIDER)
        _pause()

    # ── Player dialogue choice ────────────────────────────────────────────────
    _scene_header("💬  YOUR RESPONSE")
    choice_labels = [c[0] for c in data["player_choices"]]
    choice_idx = _pick_choice("How do you answer?", choice_labels)

    player_line = data["player_choices"][choice_idx][1]
    boss_reply  = data["boss_responses"][choice_idx]
    delta       = data["stance_deltas"][choice_idx]

    _p()
    _player_speaks(f"{player_name}: {player_line}")
    _p()
    _villain_speaks(boss_name, icon, boss_reply)
    _pause()

    # ── Pre-battle outro ──────────────────────────────────────────────────────
    _p()
    _panel([data["pre_battle_line"]])
    _pause()

    tone = ["aggressive", "diplomatic", "pragmatic"][choice_idx]
    return {
        "dialogue_tone": tone,
        "stance_delta": delta,
        "player_choice_index": choice_idx,
        "boss_name": boss_name,
    }


def play_boss_defeat_scene(
    boss_name: str,
    approach: str,
) -> None:
    """Display the post-combat defeat scene for ``boss_name``."""
    data = BOSS_CUTSCENE_DATA.get(boss_name)
    if data is None:
        _p(f"\n  {boss_name} has been defeated.")
        return

    icon = data["affinity_icon"]
    defeat_text = data["defeat_lines"].get(approach, data["defeat_lines"].get("kill", ""))

    _scene_header(f"{icon}  {boss_name.upper()} — AFTERMATH")
    _p()
    _w(defeat_text)
    _pause()


def get_boss_taunt(boss_name: str) -> str | None:
    """Return a random taunt line for the given boss, or None if not found."""
    import random
    data = BOSS_CUTSCENE_DATA.get(boss_name)
    if not data:
        return None
    return random.choice(data["taunt_lines"])


def list_cutscene_bosses() -> List[str]:
    """Return the list of bosses that have full cutscene data."""
    return list(BOSS_CUTSCENE_DATA.keys())


def play_minor_encounter_cutscene(
    encounter_name: str,
    region_name: str,
    *,
    player_name: str,
    threat_count: int = 1,
) -> Dict[str, Any]:
    """Render a short story beat for notable field enemies or assassin squads."""
    data = MINOR_ENCOUNTER_CUTSCENES.get(encounter_name)
    if data is None:
        title = f"Movement in {region_name}"
        beat = (
            f"{player_name} catches the shift in tempo before the strike comes. "
            f"{encounter_name} move through {region_name} like they were sent to test "
            "how quickly the region can turn violent again."
        )
    else:
        title = data["title"]
        beat = data["beat"]
    if threat_count > 1:
        beat = (
            f"{beat} More shadows fold in behind the first contact — {threat_count} threats "
            "moving at once instead of waiting their turn."
        )
    _scene_header(f"🎬  FIELD STORY — {encounter_name.upper()}")
    _panel([f"{title}.", beat])
    _pause()
    return {
        "encounter_name": encounter_name,
        "region_name": region_name,
        "threat_count": threat_count,
        "title": title,
    }
