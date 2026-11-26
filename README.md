# Regnum

A point-and-click investigation game set in Rome in the summer of 133 BC, built on the same engine as *The Pinkerton File*.

You are a freedman, a former slave of the house of Publius Cornelius Scipio Nasica, Pontifex Maximus. Your patron sends you to find proof that his cousin, the tribune Tiberius Gracchus, means to make himself king (*regnum*). You go among the tribune's people, posing as a scribe. The longer you listen to veterans, widows, farmers, and slaves, the harder it gets to write the report your patron wants.

Open `index.html` in a browser to play. Everything runs locally, with no server needed.

## How it plays

- **Drag** left and right (or use the arrows) to look around each panorama. **Click** glowing spots to talk, read, and look.
- Everything you find goes into your **Wax Tablets** (the notebook). Rate each person *No concern / Worth watching / Person of interest*, and take notes.
- After you meet your patron, a **Final Report** tab opens: *Quis, Quid, Ubi, Quando, Cur* (Who, What, Where, When, Why). You can file it once you have learned the plan for the day of the vote.
- At the end your patron asks one question, **does Tiberius mean to be king?**, and then asks for **names**. Your answer and the names you give decide what happens to the people you met, and to you.

## Scenes

| Act | Scene | What happens |
|---|---|---|
| I | House of Scipio Nasica | Your commission. Quintus Pompeius' diadem story. The steward points you to the estate. |
| II | The Forum Romanum | Tiberius' "wild beasts have dens" speech, the deposed tribune Octavius, the Pergamum money, rumours. |
| II | The Subura | Naevia the widow, Quintus Arrius the Numantia veteran who lists the country voters, rents and grain prices. |
| II | The Via Tiburtina | Your patron's estate on public land: chained gangs, a ruined farm, the last smallholder, a Syrian shepherd, an Italian ally. |
| III | House of the Gracchi | Cornelia, Gaius, Blossius, Diophanes, Claudia, the land commission's survey map, a "crown," and the chest from Pergamum. |
| III | The Vigil | The night before the vote: Tiberius in mourning with his son, the hand-to-the-head signal, a loud man shouting "king." |
| III | Temple of Fides | Before dawn on the Capitol: the consul who won't use force, the clubs, the informer's tablet, your patron's land ledger. |
| IV | The Report | The verdict, the names, the killing on the Capitol, ten years later with Gaius, the history, and a review of your inquiry. |

Three verdicts lead to three epilogues: swear he seeks a crown, tell your patron the truth, or accuse your patron (only if you found the evidence in the temple). The names you hand over decide each person's fate before the consuls' court in 132 BC, and whether the land commission's work reaches the people you met.

## Classroom notes

- **Everyday Rome.** Every scene has hotspots that build background knowledge: togas and the bulla, Roman names and why every daughter is Cornelia or Claudia, Vestal Virgins, lictors and fasces, a wrong sundial, gladiator stands, wax tablets and school, hot-food counters, chamber pots, roads and Roman numerals, olive oil and the strigil, the lack of police and street lights.
- **Women and girls have voices.** Phoebe the nurse, Claudia the Vestal, Naevia the widow, Tertia (an 11-year-old water carrier who runs messages for the movement), Philumena the enslaved vilica, Cornelia, her daughter Sempronia, Claudia the tribune's wife, and Fannia the matron, who remembers the women's protest of 195 BC. Tertia, Naevia, Philumena, Cornelia, Sempronia and Claudia can be named in the ending, and the history page has a section on Roman women.

- **Herrings** (the diadem, the Etruscan army, vote-buying, the Stoic scroll, the golden crown, the loud man) are debunked on the review screen at the end.
- **Real Reasons to Worry** is its own review category. The deposition of Octavius, the second tribunate, and the Pergamum money were real objections, and the game says so.
- The **History Behind the Story** screen separates invented characters from real ones. It also flags the one invented detail in the hand-to-the-head scene: Plutarch reports the gesture, but the pre-arranged signal is the game's invention.
- **Copy Report** at the end copies the student's five answers, verdict, and names for handing in.
- Set `DEV_TOOLS = false` near the top of the script before students play. That hides the gear (tune mode and scene jumper) and the *Skip to the Forum* shortcut.

## Art

The scenes use painted panoramas in `art/*.jpg`, made by Gemini from the reference images and prompts in `gemini/`. They were upscaled 2× and the hotspots were placed by hand.

The older placeholder drawings are still in `art/*.svg`, and `tools/make_art.py` can regenerate them. To go back to one, point that scene's `image:` at the `.svg` file.

### Replacing a painting

1. Give Gemini the reference image from `gemini/` and its prompt from `gemini/GEMINI_PROMPTS.md`, or give it the current `.jpg` with a short edit request.
2. Save the result into `art/` and point the scene's `image:` at it.
3. Open the game, press the **gear** (top left), pick the scene, and tap each hotspot's spot as it asks. Use **Copy All** and paste the new `x`/`y` values into `index.html`.

## Files

- `index.html`: the whole game, engine and story. Scenes, hotspots, and the ending text live in `GAME_DATA` near the top of the script.
- `art/*.jpg`: the painted panoramas the game uses. `art/*.svg`: the older placeholder drawings.
- `tools/make_art.py`: regenerates the placeholder art from the hotspot positions.
- `gemini/`: reference images and prompts for realistic repaints.
- `tools/dump_scenes.js`: prints each scene's hotspot positions (used by `make_art.py`).
