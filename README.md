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

- **Herrings** (the diadem, the Etruscan army, vote-buying, the Stoic scroll, the golden crown, the loud man) are debunked on the review screen at the end.
- **Real Reasons to Worry** is its own review category. The deposition of Octavius, the second tribunate, and the Pergamum money were real objections, and the game says so.
- The **History Behind the Story** screen separates invented characters from real ones. It also flags the one invented detail in the hand-to-the-head scene: Plutarch reports the gesture, but the pre-arranged signal is the game's invention.
- **Copy Report** at the end copies the student's five answers, verdict, and names for handing in.
- Set `DEV_TOOLS = false` near the top of the script before students play. That hides the gear (tune mode and scene jumper) and the *Skip to the Forum* shortcut.

## Art

The panoramas in `art/` are placeholder illustrations drawn by `tools/make_art.py`. The script reads the hotspot positions from `index.html` and draws each object where its hotspot sits, so the art always lines up. If you move a hotspot, rerun:

```
python3 tools/make_art.py
```

### Swapping in painted art

To replace a scene with a painted panorama, as in the Pinkerton game:

1. Generate a wide image, about **3.2 : 1** (e.g. 1600 × 500), using the brief below.
2. Put it in `art/` and change that scene's `image:` in `index.html` to the new file.
3. Open the game, press the **gear** (top left), pick the scene, and tap each hotspot's spot as it asks. Use **Copy All** and paste the new `x`/`y` values back into `index.html`.

The brief lists objects left to right, roughly in the order the hotspots expect.

**1. House of Scipio Nasica (atrium).** Roman atrium, 2nd century BC, warm daylight through a square roof opening onto a shallow marble rain pool. Walls painted to look like coloured marble blocks over a deep red dado. Left to right: a painted household shrine with two dancing Lares and a snake; four wooden cupboards of wax ancestor masks; a dark study (tablinum) with scroll shelves, a tall grey-haired senator in a toga with a purple stripe in front of it, gesturing; a long table with wax tablets (one tied with red cord and a seal); the rain pool between two columns; a balding senator holding a silver cup; an older Greek steward with a beard and tablets; a small table with a silver dish of figs; a leather satchel on the floor; an old doorkeeper slave on a stool by the bright street door.

**2. The Forum Romanum.** Sunny midsummer. Left to right: the brick Senate house with bronze doors; a columned portico with charcoal graffiti (TI GRACCHE REDDE AGRVM PVBLICVM PAVPERIBVS); the speakers' platform decorated with bronze ship-rams, a young tribune in a white toga speaking with one arm raised; the tribunes' wooden bench at its foot; a serious senator standing apart; the Palatine hill with houses behind; three sunburned country men in brown tunics; the Temple of Castor; a Greek money-changer at a table with scales and coins; the Ionic Temple of Saturn; a red-faced man shouting from a barrel; a small fenced patch of old paving in the foreground; a boy roasting chickpeas over a brazier; a city gate arch at the far right.

**3. The Subura.** A courtyard surrounded by a five-storey brick-and-timber tenement, washing on balconies, shops on the ground floor. Left to right: an alley exit; a small crossroads shrine hung with wool dolls; a widow in a doorway spinning wool on a drop spindle, a 12-year-old boy beside her; a tall empty clay grain jar; three small children playing knucklebones in the dirt; a scarred grey veteran at a table writing on wax tablets, a queue of country men; a big crack in the wall propped with timbers above; a heavy rent collector with a stick and ledger; a sly man leaning on a post; a fuller's shop with men treading cloth in vats; a stone public fountain with a lead pipe.

**4. The Via Tiburtina estate.** Golden afternoon in the Roman countryside, blue mountains behind. Left to right: an old farmer with a hoe at a crooked fence by an olive tree and bean rows; a small ruined mud-brick farmhouse with a collapsed roof; rows of vines on stakes with a small stone family tomb among them; a squat boundary stone in the foreground with a scrape mark where it was moved; a slave overseer in a good blue tunic with a whip; a line of chained field slaves hoeing; a long low stone slave barracks with high slit windows; a white villa with a colonnade on a hill among cypresses; a young Syrian shepherd with a crook and a flock of sheep; a muleteer leading pack mules down a paved road; a Roman milestone at the far right.

**5. House of the Gracchi.** A busy, lived-in Roman house in afternoon light, an open peristyle garden in the middle. Left to right: the street door, open, crowds visible outside; a dignified grey-haired woman in a high-backed chair reading a scroll (Cornelia); a small side table with an empty ivory jewel box; scribes at a long table copying wax tablets, baskets of tablets on the floor; a large linen survey map gridded into numbered lots, one block outlined in red; a young man of 21 with a surveyor's groma (measuring cross on a pole); a bearded Greek philosopher with a scroll; a reading stand with an open Greek scroll; a Greek speechwriter with a wax tablet; a gold crown shaped like city walls in a wall niche; a cedar chest bound in bronze with a star emblem; a young woman holding a small boy's hand by the doorway.

**6. The Vigil.** Night street, stars and a crescent moon, firelight. Left to right: country men sleeping in cloaks around a small fire; a grizzled veteran with tablets counting heads; the lit doorway of a great house, a young man in a dark mourning toga holding a small boy by the hand, torches on either side; an old soldier's helmet on the step; a stocky man with his hand raised to his head; a big loud man with a cup, mid-shout; a widow on a doorstep with a sleeping boy in her lap; the Capitol at the far right with the Temple of Jupiter pale in the moonlight and a small lit temple below it.

**7. The Temple of Fides.** Inside a temple portico before dawn, lamp-lit, the right side open to a grey-pink dawn sky over the Capitol. Left to right: an old consul seated alone by a bronze lamp; a bench with a wax tablet; a pile of wooden staves and sawn-off bench legs; a table with a sealed tablet and a red account book; a marble statue of the goddess Fides with her right hand held out; a tribune in a toga weighing a bench leg like a club; a slave carrying in more staves; a pen of white geese; the dawn sky with the Temple of Jupiter and a crowd gathering.

## Files

- `index.html`: the whole game, engine and story. Scenes, hotspots, and the ending text live in `GAME_DATA` near the top of the script.
- `art/*.svg`: placeholder panoramas.
- `tools/make_art.py`: regenerates the placeholder art from the hotspot positions.
- `tools/dump_scenes.js`: prints each scene's hotspot positions (used by `make_art.py`).
