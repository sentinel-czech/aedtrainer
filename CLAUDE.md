# CLAUDE.md — Vstupní bod pro Claude Code

> Přečíst jako **první**, před jakýmkoliv jiným souborem.
> Obsahuje kontext, priority, hlasovou strategii, zakázané zkratky a testovací checklist.

---

## Co buduješ a proč na tom záleží

**AED Trenažér** je výcvikový simulátor defibrilátoru pro instruktory a laiky první pomoci.
Jde o vzdělávací nástroj — kvalita simulace přímo ovlivňuje, zda se člověk při reálném
zásahu zachová správně. Každý detail (hlas, barva, tvar tlačítka, pořadí kroků) musí
odpovídat realitě, protože svalová paměť z tréninku přenáší na skutečný přístroj.

**Tři simulované přístroje** — přepínač skinů mění POUZE CSS třídu na `<body>`:
- `skin-frx` → **Philips HeartStart FRx** — světle šedý, zelené ON/OFF, oranžové VÝBOJ
- `skin-zoll` → **ZOLL AED Plus** — téměř černý, obdélníkové VÝBOJ, CPR čítač místo EKG
- `skin-heartsine` → **HeartSine Samaritan PAD 360P** — bílá+oranžová, červené VÝBOJ

**Výcvikové cíle aplikace:**
1. Správné přiložení elektrod (anatomická pozice, správné pořadí)
2. Reakce na hlasové instrukce přístroje
3. Rytmus a hloubka KPR (metronom 100–120 BPM, počítadlo)
4. Bezpečnost při výboji (všichni pryč od pacienta)
5. Orientace na třech různých přístrojích (skiny)

**Výstup:** `aed-trenazor.html` + složky `audio/` a `images/` vedle něj.
Funguje offline z disku i jako statický web. Primárně Chrome/Edge na 7" tabletu (800×600 px).

---

## Pořadí čtení dokumentace

```
1. CLAUDE.md     ← tento soubor
2. aedprompt.md  ← hlavní specifikace (přečíst celý před psaním kódu)
3. tips.md       ← časté chyby implementace
4. resources.md  ← manuály FRx, ERC guidelines, API reference
```

---

## Absolutní priority

### 1. Struktura souborů
```
aed-trenazor.html       ← celá aplikace v jednom souboru
audio/
  cs/start.mp3  ...     ← 24 CZ hlášek (viz §4.4 v aedprompt.md)
  en/start.mp3  ...     ← 24 EN hlášek
images/
  revolut-qr.png        ← QR kód pro donate modal
```
Žádné oddělené `.css` nebo `.js` soubory. Žádný npm, žádný build.

### 2. Hlasová strategie — KLÍČOVÉ

Hlas je nejdůležitější výcviková složka. Implementovat v tomto pořadí:

```
PRIORITA 1: audio/cs/*.mp3 existují → AudioPlayer.play()
            (ElevenLabs Matej / Azure cs-CZ-AntoninNeural — realistický hlas)
PRIORITA 2: cs-CZ systémový hlas dostupný → Web Speech API
PRIORITA 3: jakýkoliv jiný hlas → Web Speech API + varování uživateli
```

**SpeechEngine.say(key)** je jediný způsob přehrání hlášky. Nikdy nevolat
`speechSynthesis.speak()` ani `new Audio().play()` přímo v logice.

**Dvoustupňová inicializace:**
1. `SpeechEngine.init()` v `DOMContentLoaded` — inicializuje TTS (nevyžaduje klik), indikátor zobrazí `⟳`
2. `SpeechEngine.detectMp3()` v first-click handleru — zkusí načíst `audio/cs/start.mp3`:
   - Úspěch → `mode = 'mp3'`, přednačíst všechny MP3 na pozadí, indikátor `🔊 HD`
   - Selhání → `mode = 'tts'` nebo `'tts-nonnative'`, indikátor `🔈` nebo `⚠️`

**AudioContext** inicializovat výhradně po user gesture:
```javascript
document.addEventListener('click', () => AudioEngine.init(), { once: true });
```

### 3. Třívrstvý gradient na fyzických prvcích
Každé tlačítko a plocha těla přístroje = třívrstvý `radial-gradient` +
asymetrický border + min. 3 vrstvy `box-shadow`. Vzor viz §12.2 aedprompt.md.
**Nikdy nenahrazovat jednoduchou `background: #barva`.**

### 4. Pohled obsluhy shora
`#device-panel` = tmavé radiální pozadí (podlaha/stůl).
`#frx-body` = plastový přístroj ležící na podlaze, výrazný `box-shadow`.
Žádné webové prvky uvnitř simulátoru.

### 5. State machine jako jediný zdroj pravdy
Všechny přechody výhradně přes `transitionTo(newPhase)`.
Event listener → `transitionTo()` → state machine aktualizuje UI.
Nikdy nenastavovat styl přímo z event listeneru.

### 6. Skin = pouze CSS třída na body
`setSkin('zoll')` přidá `body.skin-zoll` — nic jiného.
JS nikdy nečte `state.activeSkin` pro podmíněnou logiku.
Veškerý skin vizuál = CSS selektor `body.skin-X #element { ... }`.

---

## Inicializační sekvence (DOMContentLoaded)

```javascript
document.addEventListener('DOMContentLoaded', () => {
  // 1. Výchozí skin (před renderUI aby CSS::after texty fungovaly)
  setSkin('frx');

  // 2. Vykreslit UI texty — data-i18n, data-i18n-text, scenario options
  renderUI();

  // 3. Označit aktivní jazyk
  document.getElementById('lang-cs').classList.add('active');

  // 4. Inicializovat a spustit EKG (idle mód)
  EcgEngine.init();
  EcgEngine.start();

  // 5. Inicializovat TTS hlasový engine (synchronní část)
  SpeechEngine.init();    // načte systémové hlasy, Chrome bug workaround

  // 6. AudioContext + MP3 detekce až po user gesture (browser policy)
  document.addEventListener('click', () => {
    if (!AudioEngine.ctx) {
      AudioEngine.init();
      MetronomeEngine.ctx = AudioEngine.ctx;
      SpeechEngine.detectMp3();  // zkusí načíst audio/cs/start.mp3
                                  // → mode = 'mp3' nebo zůstane 'tts'
    }
  }, { once: true });

  // 7. Klávesové zkratky
  document.addEventListener('keydown', handleKeydown);
});
```

---

## Zakázané zkratky

| Zakázáno | Proč | Správně |
|---|---|---|
| `setInterval` pro metronom | timing drift | `AudioContext` lookahead scheduling |
| `setTimeout` pro zvuk | drift při opakování | `AudioContext.currentTime` |
| `speechSynthesis.speak()` přímo | obchází prioritní systém | `SpeechEngine.say(key)` |
| `new Audio(path).play()` přímo | obchází fallback logiku | `SpeechEngine.say(key)` |
| hardcoded string v JS logice | nelze přeložit | `t('sekce', 'klic')` |
| `element.style.X = Y` z event listeneru | obchází state machine | `transitionTo()` |
| `background: #barva` na tlačítkách | placaté | třívrstvý gradient (§12.2) |
| `innerHTML` pro log | XSS | `textContent` + `createElement` |
| `if (state.activeSkin === 'X')` v logice | porušuje CSS-only skin | CSS třída na `body` |
| `element.style.display` pro skin prvky | obchází CSS skin | `body.skin-X #el { display }` |
| `mp3` soubory pojmenované jinak než klíč voice | AudioPlayer selže | `audio/cs/{key}.mp3` |

---

## Struktura HTML souboru (pořadí závazné)

```html
<!DOCTYPE html>
<html lang="cs">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AED Trenažér</title>
  <link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@700;900
              &family=IBM+Plex+Sans:wght@400;700&display=swap" rel="stylesheet">
  <style>/* veškeré CSS inline */</style>
</head>
<body class="skin-frx">

  <!-- 1. WEBOVÁ HLAVIČKA (nad simulátorem) -->
  <header id="site-bar">
    <!-- .site-name | .skin-zone [FRx][ZOLL][SAM] | .site-controls [🔊][CZ][EN][♥] -->
  </header>
  <div id="training-banner" data-i18n="training_banner"></div>
  <div id="voice-warning" hidden></div>

  <!-- 2. SIMULÁTOR -->
  <div id="app-container">

    <!-- Levý panel: fyzický přístroj (pohled shora) -->
    <div id="device-panel">
      <div id="frx-body">
        <div id="device-header"><!-- logo + ready LED --></div>
        <div id="ecg-display">
          <canvas id="ecg-canvas"></canvas>
          <div id="skin-alt-display">
            <span id="zoll-cpr-num">--</span>
            <span class="alt-label"></span>
          </div>
        </div>
        <div id="pad-diagram"><!-- SVG torzo + elektrody --></div>
        <div id="connectors"><!-- SMART Pads II konektory --></div>
        <div id="main-buttons">
          <div id="btn-on">...</div>
          <div id="btn-info">...</div>
          <div id="btn-shock">...</div>
        </div>
        <div id="charging-bar-wrap" hidden>
          <div id="charging-bar-fill"></div>
        </div>
        <div id="led-status">
          <div class="led-item"><div id="led-ready" class="led"></div>...</div>
          <div class="led-item"><div id="led-charging" class="led"></div>...</div>
          <div class="led-item"><div id="led-shock" class="led"></div>...</div>
        </div>
        <div class="frx-serial"></div>
      </div>
    </div>

    <!-- Pravý panel: výcvikový displej -->
    <div id="instruction-panel">
      <div id="scenario-bar">
        <!-- select#scenario-selector + btn#btn-reset-scenario + span#scenario-status -->
      </div>
      <div id="main-instruction"></div>
      <div id="metronome-section"><!-- circle + BPM display + slider --></div>
      <div id="cpr-controls">
        <!-- #cpr-header (num/round/timer) + #cpr-progress + #btn-compress + #btn-breaths -->
      </div>
      <div id="event-log">
        <div class="log-title" data-i18n="log_title"></div>
        <div id="log-entries"></div>
      </div>
    </div>

  </div>

  <!-- 3. MODALY -->
  <div id="result-modal" hidden>...</div>
  <div id="donate-modal" hidden>...</div>

  <!-- 4. JAVASCRIPT (pořadí závazné) -->
  <script>
  // ── A. LANG object ──────────── editovatelné hlášky + UI texty
  // ── B. t(), setLang(), renderUI()
  // ── C. AudioEngine ──────────── AudioContext, beep(), sweep()
  // ── D. AudioPlayer ─────────── MP3 cache, preload(), play()
  // ── E. SpeechEngine ─────────── orchestrátor MP3 + TTS fallback, say()
  // ── F. EcgEngine ─────────────── canvas animace, všechny EKG módy
  // ── G. MetronomeEngine ──────── AudioContext scheduling, setBpm()
  // ── H. weightedRandom(), generateScenario(), SCENARIOS{}
  // ── I. StateMachine ──────────── transitionTo(), všechny stavy
  // ── J. UI Controller ─────────── pressPower(), connectPad(), doCompress()...
  // ── K. setSkin() ─────────────── CSS třída na body + EcgEngine.resize()
  // ── L. DOMContentLoaded ──────── init sekvence (viz výše)
  </script>

</body>
</html>
```

---

## Testovací checklist

Projít před odevzdáním — každý bod musí projít v Chrome na viewportu 800×600 px:

**Vizuál — přístroj**
- [ ] `#device-panel` má tmavé radiální pozadí (#0d1117 → #1a2030)
- [ ] `#frx-body` má výrazný stín (0 14px 45px rgba(0,0,0,0.85)) — vypadá jako ležící objekt
- [ ] FRx skin: tělo světle šedé (#a8b0bc), ON/OFF zelené kulaté, VÝBOJ oranžové kulaté
- [ ] ZOLL skin: tělo téměř černé, VÝBOJ obdélníkový 110×68px, CPR čítač místo EKG canvas
- [ ] HeartSine skin: tělo bílá→oranžová gradient, VÝBOJ červené (ne oranžové!)
- [ ] Přepnutí skinu NERUŠÍ state machine ani EKG animaci
- [ ] Tlačítka mají viditelný 3D efekt (třívrstvý gradient, asymetrický border)
- [ ] SVG elektrody: disconnected = šedé dashed, placed = zelené solid

**Funkce — přístroj**
- [ ] ON/OFF: zapnutí → BOOTING → hláška → čeká na elektrodu 1
- [ ] Klik el.1 → hláška → zezelená → čeká na el.2
- [ ] Klik el.2 → hláška → ANALYZING automaticky
- [ ] SHOCK tlačítko opacity 0.28 a `pointer-events:none` dokud není SHOCK_READY
- [ ] SHOCK_READY: tlačítko pulzuje (FRx/ZOLL oranžově, HeartSine červeně)
- [ ] Po výboji: flash celé obrazovky červenou 80 ms
- [ ] `Space` = komprese POUZE ve stavu CPR_ACTIVE

**KPR panel**
- [ ] Počítadlo `00/30` se správně inkrementuje při každém stlačení
- [ ] Progress bar se plní 0→100% při 30 stlačeních
- [ ] `Kolo 1/4` se správně aktualizuje
- [ ] Timer `00:00` tikne každou sekundu od prvního stlačení
- [ ] Metronom hraje v CPR_ACTIVE (AudioContext beep, ne setInterval)
- [ ] BPM slider mění tempo metronomu v reálném čase
- [ ] `#btn-breaths` viditelný POUZE ve stavu CPR_BREATHS

**Hlas**
- [ ] `#voice-quality` v site-baru zobrazuje `🔊 HD` nebo `🔈 Systémový` nebo `⚠️`
- [ ] Při detekci MP3 (`audio/cs/start.mp3` existuje): mode = 'mp3', přehrává MP3
- [ ] Při absenci MP3: mode = 'tts', Web Speech API s cs-CZ nebo EN fallback
- [ ] Hláška `analyzing` zaznívá PŘED analýzou, ne po ní
- [ ] Hláška `shock_clear` zaznívá těsně před výbojem (0.3s)
- [ ] Přepnutí CZ/EN přepne jazyk hlasu bez přerušení state machine
- [ ] `#voice-warning` se zobrazí pokud cs-CZ hlas není v systému

**i18n**
- [ ] Přepnutí CZ→EN: banner, popisky elektrod, tlačítka, scenario options, donate modal
- [ ] `#btn-donate` zobrazuje `♥ Podpořit` (CZ) / `♥ Support` (EN)
- [ ] Scenario selector options přeloženy při změně jazyka

**Web UI**
- [ ] Scénář lze vybrat PŘED zapnutím, selector zablokován PO zapnutí
- [ ] ↺ resetuje do IDLE s animací rotace ikony
- [ ] Donate modal: QR z `images/revolut-qr.png`, fallback SVG placeholder
- [ ] Donate modal: texty přeloženy (CZ/EN), zavírá se Escape i klikem na overlay
- [ ] Na viewportu 800×600 px vše viditelné bez vertikálního scrollu

---

*Projekt: IDDA Trainer #12392 · 4D Dive Deep Descend Down · 4dive.cz*
