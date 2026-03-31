# Adding a New Language to AED Trainer

This guide walks you through the complete process of adding a new language to the AED Trainer application. The example below uses Slovak (SK) but the process is identical for any language.

---

## Overview

Adding a new language involves 4 files:

| File | What to do |
|---|---|
| `scripts/generate_voices.py` | Add voice texts, generate MP3 files |
| `index.html` | Add LANG object entries (UI texts, voice texts, log texts) |
| `scenarios/scenarios.json` | Add scenario names and descriptions |
| `resources.html` | (Optional) Add language switch button |

Estimated time: 30-60 minutes.

---

## Step 1: Generate Voice MP3 Files

### 1.1 Choose a voice

List available voices for your language:

```bash
pip install edge-tts   # if not installed
edge-tts --list-voices | grep sk-SK
```

Output example:
```
sk-SK-LukasNeural    Male
sk-SK-ViktoriaNeural Female
```

Pick one. For AED training, a calm male voice is recommended (similar to real AED devices).

### 1.2 Add voice texts to the script

Open `scripts/generate_voices.py` and add a new dictionary after `EN = { ... }`:

```python
VOICE_SK = "sk-SK-LukasNeural"

SK = {
    "start":           "Pristroj zapnuty. Prilozite elektrody na holu pokozku pacienta.",
    "pad1_prompt":     "Prilozite elektrodu cislo jedna pod pravu klucnu kost.",
    "pad1_ok":         "Elektroda jedna prilozena.",
    "pad2_prompt":     "Prilozite elektrodu cislo dva na lavy bok pacienta, pod pazuchu.",
    "pad2_ok":         "Elektroda dva prilozena.",
    "analyzing":       "Nedotykajte sa pacienta. Analyzujem srdcovy rytmus.",
    "analyze_wait":    "Nedotykajte sa pacienta.",
    "shock_advised":   "Vyboj odporucany. Nabijam. Vsetci prec od pacienta!",
    "shock_ready":     "Pristroj nabity. Stlacte oranzove tlacidlo vyboja.",
    "shock_clear":     "Vsetci prec!",
    "shock_delivered": "Vyboj podany. Okamzite zacnite KPR.",
    "no_shock":        "Vyboj neodporucany. Okamzite zacnite KPR - tridsat stlaceni, dva vdychy.",
    "cpr_start":       "Zacnite KPR. Stlacajte hrudnik do hlbky pat az sest centimetrov.",
    "cpr_depth":       "Stlacajte pevnejsie - minimalne pat centimetrov.",
    "cpr_rate":        "Udrzujte frekvenciu sto az sto dvadsat stlaceni za minutu.",
    "cpr_15":          "Patnast stlaceni - pokracujte!",
    "cpr_30":          "Tridsat stlaceni. Vykonajte dva zachranne vdychy.",
    "breaths_done":    "Pokracujte v KPR.",
    "reanalyze":       "Analyzujem srdcovy rytmus. Nedotykajte sa pacienta.",
    "rosc":            "Spontanny obeh obnoveny. Skontrolujte dychanie. Ulozte do stabilizovanej polohy.",
    "continue_cpr":    "Pokracujte v KPR. Zachranna sluzba bola privolana.",
    "shock2":          "Druhy vyboj odporucany. Vsetci prec od pacienta!",
    "shock3":          "Treti vyboj odporucany. Vsetci prec od pacienta!",
    "off":             "Pristroj vypnuty.",
    "end_session":     "Trening ukonceny. Prezrite si vysledky.",
    "low_battery":     "Bateria je slaba.",
    "pediatric_on":    "Detsky kluc vlozeny. Energia znizena na patdesiat joulov.",
}
```

### 1.3 Add the language to the main() function

In the same file, add a call to `generate()`:

```python
async def main():
    print(f"Generating Czech voice files ({VOICE_CS})...")
    await generate(VOICE_CS, "cs", CS)
    print(f"\nGenerating English voice files ({VOICE_EN})...")
    await generate(VOICE_EN, "en", EN)
    print(f"\nGenerating Slovak voice files ({VOICE_SK})...")   # NEW
    await generate(VOICE_SK, "sk", SK)                          # NEW
    print("\nDone!")
    # ... rest of the function
```

### 1.4 Run the script

```bash
python3 scripts/generate_voices.py
```

This will:
- Generate `audio/sk/*.mp3` (27 files)
- Update `audio/durations.json` with Slovak voice durations
- Voice timing in the app will automatically adapt to the new language

### 1.5 Verify

```bash
ls audio/sk/ | wc -l        # should be 27
cat audio/durations.json     # should contain "sk": { ... }
```

---

## Step 2: Add Language to index.html

### 2.1 Add LANG object entry

Open `index.html` and find the LANG object (search for `const LANG = {`). After the `en: { ... }` block, add a new block:

```javascript
const LANG = {
  cs: { ... },
  en: { ... },

  // ─────────────────────────────────────────
  //  SLOVENCINA
  // ─────────────────────────────────────────
  sk: {
    ui: {
      training_banner: 'TRENAZER \u00B7 IBA PRE VYCVIK BEZ AED ZARIADENIA',
      btn_on: 'ZAP / VYP',
      btn_shock: 'VYBOJ',
      led_ready: 'READY',
      led_charging: 'NABIJAM',
      led_shock: 'VYBOJ ODPORUCANY',
      pad1_label: 'ELEKTRODA 1',
      pad2_label: 'ELEKTRODA 2',
      pad1_hint: 'Prava klucna kost',
      pad2_hint: 'Lavy bok - axila',
      pad_mode_adult: 'Dospely',
      pad_mode_child: 'Dieta',
      // ... all other ui keys (copy from cs: block and translate)
      voice_lang: 'sk-SK',
    },

    voice: {
      start: { text: 'Pristroj zapnuty. Prilozite elektrody na holu pokozku pacienta.', priority: 'high' },
      // ... all 27 voice keys (must match exactly the keys in generate_voices.py)
    },

    log: {
      powered_on: 'Pristroj zapnuty',
      // ... all log keys
    },
  },
};
```

**Important rules:**
- Keys must be IDENTICAL to `cs` and `en` blocks — never rename keys
- `voice_lang` must be a valid BCP-47 tag (e.g. `sk-SK`, `de-DE`, `pl-PL`)
- Voice `text` values must exactly match the texts in `generate_voices.py`

### 2.2 Add language switch button

In the HTML `<header id="site-bar">`, find the `.site-controls` div and add a button:

```html
<button class="lang-btn" onclick="setLang('sk')" id="lang-sk">SK</button>
```

### 2.3 Add scenario labels (optional fallback)

In the LANG `sk.ui` section, add scenario labels:

```javascript
scenario_random: '\uD83C\uDFB2 Nahodny',
scenario_s1: 'S1 \u2014 Klasicka zastava (VF)',
scenario_s2: 'S2 \u2014 Rezistentna VF',
// ... etc
```

These are used as fallback when `scenarios.json` fails to load.

---

## Step 3: Add Language to scenarios.json

Open `scenarios/scenarios.json` and add `"sk"` to each scenario's `name` and `description`:

```json
{
  "S1": {
    "rhythm": "VF",
    "shockable": true,
    "name": {
      "cs": "S1 — Klasicka zastava (VF)",
      "en": "S1 — Classic arrest (VF)",
      "sk": "S1 — Klasicka zastava (VF)"
    },
    "description": {
      "cs": "Tento scenar predstavuje situaci...",
      "en": "This scenario presents a situation...",
      "sk": "Tento scenar predstavuje situaciu..."
    }
  }
}
```

Do this for all 7 scenarios (random + S1-S6).

---

## Step 4: Add Language to resources.html (Optional)

If you want the Resources page to support the new language:

### 4.1 Add language button

In the header `<div class="lang-switch">`, add:

```html
<button class="lang-btn" onclick="setLang('sk')">SK</button>
```

### 4.2 Add translated content

For each `<span data-lang="cs">` element, add a corresponding `<span data-lang="sk">`:

```html
<span data-lang="cs">Retezec preziti</span>
<span data-lang="en">Chain of Survival</span>
<span data-lang="sk">Retazec prezitia</span>
```

### 4.3 Update CSS language toggle

Add rules for the new language:

```css
body.lang-sk [data-lang="cs"] { display: none; }
body.lang-sk [data-lang="en"] { display: none; }
body.lang-sk [data-lang="sk"] { display: initial; }
```

Update the `setLang()` function to handle `'sk'`.

---

## Step 5: Verify

### 5.1 Voice files

Open the app and switch to your new language. Click the voice quality indicator — it should show:
- `HD` if MP3 files are found
- `TTS` if falling back to system voice

### 5.2 UI texts

All UI elements should display in the new language:
- Training banner
- Button labels (ZAP/VYP, VYBOJ)
- Pad labels (ELEKTRODA 1, ELEKTRODA 2)
- Scenario selector options
- CPR instructions
- Event log entries
- Donate modal

### 5.3 Voice timing

Run through a complete scenario (S1 recommended). Verify:
- No voice overlaps between announcements
- Each announcement finishes before the next one starts
- Charging bar duration matches the shock_advised voice length

Voice timing is automatic — `VoiceTiming` reads durations from `audio/durations.json` which was generated by the script.

### 5.4 Scenarios

Switch to the "Scenario" tab and verify all descriptions display correctly in the new language.

---

## File Checklist

After adding a new language, these files should be modified:

| File | Change |
|---|---|
| `scripts/generate_voices.py` | New voice dict + generate() call |
| `audio/{lang}/*.mp3` | 27 generated MP3 files |
| `audio/durations.json` | Auto-generated voice durations |
| `index.html` | LANG object + language button |
| `scenarios/scenarios.json` | name + description for each scenario |
| `resources.html` | (Optional) Language button + translated spans |

---

## Troubleshooting

### Voice sounds robotic
Try a different edge-tts voice. List all voices for your language:
```bash
edge-tts --list-voices | grep {lang-code}
```

### Voice timing is off
Delete `audio/durations.json` and re-run `generate_voices.py` to regenerate it. The script measures actual MP3 durations with ffprobe.

### MP3 not playing in browser
Check browser console for errors. Common issues:
- File path is wrong (must be `audio/{lang}/{key}.mp3`)
- File permission issue
- CORS when serving from `file://` (use a local HTTP server)

### Missing translations show [key]
The `t()` function falls back to Czech, then shows `[key]` if both are missing. Search for the key in LANG object and add the translation.

### Scenario descriptions empty
Check that `scenarios.json` is valid JSON (use `python3 -m json.tool scenarios/scenarios.json`). Verify your language code in `name` and `description` objects matches `currentLang`.
