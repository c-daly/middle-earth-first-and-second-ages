# Middle-earth in the First and Second Ages

An illustrated, fan-made tabletop campaign sourcebook for the years of the Siege of Angband, the voyages of Númenor, and the forging of the Rings of Power.

Narvi and Celebrimbor are still at work. Someone brings them tools, knows when they quarrel, and is among the first to walk through the door when it opens. There is room in that history for one more person.

![From Eärendil’s shoulder aboard Vingilot, Ancalagon tumbles toward the three peaks of Thangorodrim.](art/ancalagon-in-free-fall-3840x2160.png)

*The fall of Ancalagon*, the centerpiece of the illustrated edition. The Silmaril shines on Eärendil’s brow.

## A crossing in the First Age

> Refugees reach a guarded crossing after the Siege of Angband breaks. A Dwarf who helped build the crossing hears a second note in its warning bell. The captain sees her holding up the retreat and believes she wants time to fetch her family’s possessions.

That is where *The Bell at the Crossing* begins. The captain has people to get across. The Dwarf knows how the bell sounded yesterday. A traveler close enough to hear them both has to decide whose word to stake against the weight of the next cart.

## A workshop in the Second Age

> In the workshop, Galadriel asks Annatar who entrusted him with this work. Before he can speak, Celebrimbor answers for him. He shows her a piece he had spent years trying to make and explains exactly where Annatar helped him. For the first time he can see how to bring a design worthy of his grandfather to completion. Weeks later an apprentice who shared his delight can still remember that Annatar never answered her question.

This scene is the book’s imagining of a moment in Eregion. An apprentice could spend years in that workshop, believe everything she heard that day, and still be the person Galadriel most needs to speak with.

## Read the sourcebook

**[Read the book online](book/middle-earth-in-the-first-and-second-ages.md)** · [Open the illustrated PDF](book/middle-earth-in-the-first-and-second-ages.pdf) · [Browse the chapter list](book/middle-earth-in-the-first-and-second-ages.md#contents)

The history follows the shifting front in Beleriand and the fates of its survivors into the Second Age. Farther east and south, river pilots on the Sea of Rhûn and harbor families in Umbar have obligations of their own. For a game with one protagonist, the book gives the GM ways to run a dangerous encounter, let a witness be mistaken, and follow what happens after the traveler leaves. [Guidance for the gamemaster](book/middle-earth-in-the-first-and-second-ages.md#guidance-for-the-gamemaster)

Where Tolkien left several accounts, the book records which one it follows and why. The author’s note describes how AI helped with the research, prose, illustrations, and layout. [Register of campaign choices](book/middle-earth-in-the-first-and-second-ages.md#register-of-campaign-choices) · [Research notebook](book/research-notes.md) · [Author’s note](book/middle-earth-in-the-first-and-second-ages.md#a-note-from-the-author)

<details>
<summary>Rebuild the illustrated edition</summary>

The [typesetter](book/typeset.py) reads the Markdown manuscript and the illustrations in [art](art/). It runs on Windows with Python 3 and the Times New Roman, Garamond, and Palatino Linotype fonts installed in the Windows Fonts directory. From the repository root, run the following commands.

```powershell
py -m pip install reportlab Pillow
py book/typeset.py
```

The script writes the reading edition to `book/middle-earth-in-the-first-and-second-ages.pdf`.

</details>
