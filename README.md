# Malayalam scene descriptions & Road Hazard Detection

BlindAssist can display its scene descriptions and safety alerts in Malayalam in a separate
caption window. The translation is offline and uses curated phrases for the
object labels and scene details produced by the detector. Unknown detector
labels remain in their original language; this is not a general-purpose text
translator.

Spoken Malayalam captions are enabled when Windows has a speech voice with a
Malayalam (`ml-*`) culture installed. If one is not found, the app prints a
warning and continues to show Malayalam captions without speech. Install a
compatible Windows Malayalam text-to-speech voice to enable audio.

### Navigational Warnings & Road Hazards
Navigational warnings evaluate both moving obstacles and ground-level Kerala road hazards:
1. **Dynamic Obstacles**: Tracked bounding-box growth estimates apparent approach speed for vehicles, bicycles, and people. Rapidly approaching or close obstacles trigger warnings.
2. **Open Gutters / Canals (*ഓടകൾ*)**: High-priority boundary detection monitors roadside canal and ditch edges along the left and right shoulders, warning visually impaired pedestrians to stay clear of the drop.
3. **Potholes (*കുഴികൾ*)**: Ground-level surface depression detection in the walking corridor alerts users to uneven road depressions and tripping hazards.
4. **Water Puddles (*വെള്ളക്കെട്ടുകൾ*)**: Specular reflection and surface analysis identify waterlogged patches on the path.

The highest-priority urgent warning is spoken in Malayalam, and road hazards are highlighted directly on the video feed.