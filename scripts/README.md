# scripts/

Pomocne skripty pro AED Trainer projekt.

---

## generate_voices.py

Generuje MP3 hlasove soubory pro vsechny hlasove hlasky trenazeru v cestine a anglictine.

### Jak to funguje

Skript pouziva knihovnu **edge-tts** — Python wrapper nad Microsoft Edge Neural TTS (Text-to-Speech). Tato sluzba je stejna, jakou pouziva prohlizec Microsoft Edge pro cteni webovych stranek nahlas. Hlasy jsou neuronove (AI generovane), vysoke kvality a zdarma.

#### Pouzite hlasy

| Jazyk | Hlas | Popis |
|---|---|---|
| Cestina | `cs-CZ-AntoninNeural` | Muzsky hlas, klidny a autoritativni — vhodny pro zachranare |
| Anglictina | `en-US-GuyNeural` | Muzsky hlas, jasny a profesionalni |

#### Parametry hlasu

- **rate**: `-10%` (mirne pomalejsi nez vychozi — lepsi srozumitelnost pro stresovou situaci)
- **pitch**: `-5Hz` (mirne nizsi ton — autoritativnejsi, mene roboticky)

### Co skript dela

1. Pro kazdou hlasovou hlasku (27 klicu v cestine, 27 v anglictine):
   - Zkontroluje, jestli MP3 soubor uz existuje → pokud ano, preskoci (nebude prepisovat)
   - Pokud neexistuje → vygeneruje MP3 pres Microsoft Edge TTS API
   - Ulozi do `audio/cs/{klic}.mp3` nebo `audio/en/{klic}.mp3`
2. Na konci vypise pocet vygenerovanych souboru

### Nazvy souboru

Nazev kazdeho MP3 souboru odpovida klici v LANG objektu v `index.html`:

```
audio/cs/start.mp3           ← "Pristroj zapnut. Prilozte elektrody..."
audio/cs/pad1_prompt.mp3     ← "Prilozte elektrodu cislo jedna..."
audio/cs/analyzing.mp3       ← "Nedotykejte se pacienta. Analyzuji..."
audio/cs/shock_advised.mp3   ← "Vyboj doporucen. Nabijim..."
...
```

Uplny seznam 27 hlasek je primo ve skriptu v slovnicich `CS` a `EN`.

### Instalace a spusteni

```bash
# 1. Nainstalovat edge-tts (jednorazove)
pip install edge-tts

# 2. Spustit z korene projektu
python3 scripts/generate_voices.py

# Nebo primo ze slozky scripts/
cd scripts
python3 generate_voices.py
```

### Vystup

```
Generating Czech voice files (cs-CZ-AntoninNeural)...
  GEN  cs/start.mp3 ...
  GEN  cs/pad1_prompt.mp3 ...
  SKIP cs/analyzing.mp3 (exists)
  ...

Generating English voice files (en-US-GuyNeural)...
  GEN  en/start.mp3 ...
  ...

Done!
  cs: 27 MP3 files
  en: 27 MP3 files
```

### Jak pridat novou hlasku

1. Pridejte klic a text do slovniku `CS` a `EN` ve skriptu
2. Pridejte stejny klic do `LANG.cs.voice` a `LANG.en.voice` v `index.html`
3. Spustte skript — vygeneruje jen chybejici soubory (existujici preskoci)

### Jak pregenerovat vsechny hlasky

Smazte obsah `audio/cs/` a `audio/en/` a spustte skript znovu:

```bash
rm audio/cs/*.mp3 audio/en/*.mp3
python3 scripts/generate_voices.py
```

### Jak zmenit hlas

Upravte konstanty `VOICE_CS` a `VOICE_EN` na zacatku skriptu. Seznam dostupnych hlasu:

```bash
# Vypsat vsechny dostupne hlasy
edge-tts --list-voices

# Ceske hlasy
edge-tts --list-voices | grep cs-CZ
# cs-CZ-AntoninNeural (muz)
# cs-CZ-VlastaNeural (zena)

# Anglicke hlasy (vyber)
edge-tts --list-voices | grep en-US
# en-US-GuyNeural, en-US-AriaNeural, en-US-JennyNeural, ...
```

### Pozadavky

- Python 3.8+
- `edge-tts` (`pip install edge-tts`)
- Pripojeni k internetu (hlasy se generuji online pres Microsoft API)
- Soubory se generuji jednorazove — potom funguje trenazor offline
