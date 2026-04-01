# AED Trenažér – Softwarová specifikace

> **Účel:** Plnohodnotná webová simulace defibrilátoru Philips HeartStart FRx  
> **Platforma:** Single-page HTML/JS/CSS (žádný backend, žádné závislosti)  
> **Cílová skupina:** Laici, záchranáři, instruktoři první pomoci  
> **Jazyky:** Čeština (výchozí) + Angličtina — přepínatelné za běhu

## Dokumentace projektu

| Soubor | Obsah | Číst jako |
|---|---|---|
| `CLAUDE.md` | Vstupní bod, priority, zakázané zkratky, init sekvence, checklist | **První** |
| `aedprompt.md` | Tato specifikace — layout, CSS, state machine, i18n, zvuk | Druhý |
| `tips.md` | Časté chyby implementace a jak se jim vyhnout | Třetí |
| `resources.md` | Manuály FRx, ERC guidelines, API reference, nasazení | Dle potřeby |

---

## 1. Kontejner a spouštění

- Celá aplikace je **jedna HTML stránka** (`aed-trenazor.html`)
- Funguje offline z lokálního disku i jako statický web (GitHub Pages, Netlify apod.)
- **Žádné npm, žádné build kroky** – čistý vanilla JS + CSS + HTML5
- Responzivní: optimalizováno pro tablet (768 px+), použitelné i na mobilu
- Prohlížeč: Chrome / Edge (plná Web Speech API), Firefox (fallback bez hlasu)

---

## 2. Vizuální podoba

### 2.1 Cílové zařízení a viewport

**Primární cíl: 7palcový tablet** — typické rozlišení 1024×600 px nebo 800×480 px.  
Aplikace se dimenzuje tak, aby celý simulátor byl viditelný **bez scrollování** na viewportu ≥ 800×480 px.

```
Celková výška po odečtení headerů:
  Viewport 600 px
  − site-bar 36 px  (o 8 px vyšší — přidán výběr scénáře)
  − training-banner 24 px
  = 540 px dostupných pro simulátor
```

CSS základna:
```css
html, body { min-width: 800px; overflow-x: auto; background: #111; }
#app-container {
  width:      800px;
  min-height: calc(100vh - 60px);
  margin:     0 auto;
}
```

---

### 2.2 Site-bar — tenká webová hlavička

Site-bar je **28 px** a obsahuje výhradně webové ovládání — přepínač skinů, jazyk, donate.
Scénář patří nad pravý panel (viz §3.5), aby zůstal v kontextu instrukčního displeje.

```
┌────────────────────────────────────────────────────────────────────────────┐  28px
│ #site-bar  (#111827, fixed top)                                             │
│  AED Trenažér · Simulator    [FRx][ZOLL][SAM]   [🔊 HD]  [CZ][EN]  [♥ Tip]│
│  .site-name                  .skin-zone   #voice-quality  .lang  #btn-donate│
└────────────────────────────────────────────────────────────────────────────┘
```

```html
<header id="site-bar">

  <span class="site-name">AED Trenažér · Simulator</span>

  <!-- Přepínač skinů — střed -->
  <div class="skin-zone">
    <button class="skin-btn active" data-skin="frx"
            onclick="setSkin('frx')" title="Philips HeartStart FRx">
      <span class="skin-dot" style="background:#a8b0bc"></span>FRx
    </button>
    <button class="skin-btn" data-skin="zoll"
            onclick="setSkin('zoll')" title="ZOLL AED Plus">
      <span class="skin-dot" style="background:#2a2a2a"></span>ZOLL
    </button>
    <button class="skin-btn" data-skin="heartsine"
            onclick="setSkin('heartsine')" title="HeartSine Samaritan PAD 360P">
      <span class="skin-dot" style="background:#f06020"></span>SAM
    </button>
  </div>

  <!-- Vpravo: kvalita hlasu, jazyk, donate -->
  <div class="site-controls">
    <span id="voice-quality"></span>
    <button class="lang-btn" onclick="setLang('cs')" id="lang-cs">CZ</button>
    <button class="lang-btn" onclick="setLang('en')" id="lang-en">EN</button>
    <button id="btn-donate" onclick="openDonateModal()">♥ Tip</button>
  </div>

</header>

<div id="training-banner" data-i18n="training_banner"></div>
```

```css
#site-bar {
  position:        fixed;
  top:             0; left: 0; right: 0;
  height:          28px;
  background:      #111827;
  display:         flex;
  align-items:     center;
  justify-content: space-between;
  padding:         0 10px;
  gap:             10px;
  z-index:         200;
  font-family:     var(--font-ui);
}

.site-name {
  font-size:      11px;
  color:          #374151;
  letter-spacing: 0.5px;
  white-space:    nowrap;
  flex-shrink:    0;
}

.skin-zone { display: flex; align-items: center; gap: 3px; flex: 1; justify-content: center; }
.skin-btn {
  background:    transparent;
  border:        1px solid #374151;
  border-radius: 3px;
  color:         #6b7280;
  font-size:     10px; font-weight: 700;
  padding:       2px 7px;
  cursor:        pointer;
  display:       flex; align-items: center; gap: 3px;
  transition:    all 0.15s;
}
.skin-btn:hover  { border-color: #6b7280; color: #d1d5db; }
.skin-btn.active { border-color: #d1d5db; color: #f1f5f9; }
.skin-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }

.site-controls { display: flex; align-items: center; gap: 4px; flex-shrink: 0; }
.lang-btn {
  background: transparent; border: 1px solid #374151; border-radius: 3px;
  color: #6b7280; font-size: 10px; font-weight: 700; padding: 2px 6px; cursor: pointer;
  transition: color 0.15s, border-color 0.15s;
}
.lang-btn:hover  { color: #f1f5f9; border-color: #6b7280; }
.lang-btn.active { color: #f1f5f9; border-color: #f1f5f9; }

#btn-donate {
  background: transparent; border: 1px solid #374151; border-radius: 3px;
  color: #6b7280; font-size: 10px; font-weight: 700; padding: 2px 8px; cursor: pointer;
  margin-left: 4px; transition: color 0.15s, border-color 0.15s;
}
#btn-donate:hover { color: #93c5fd; border-color: #93c5fd; }

#training-banner {
  position:    fixed;
  top:         28px; left: 0; right: 0;
  height:      22px;
  background:  #c2410c;
  display:     flex; align-items: center; justify-content: center;
  font-family: var(--font-device);
  font-size:   9px; font-weight: 700; color: rgba(255,255,255,0.9);
  letter-spacing: 2.5px; text-transform: uppercase;
  z-index:     199;
}

/* Celkový padding-top = site-bar + training-banner = 28 + 22 = 50px */
#app-container { padding-top: 50px; }
```

---

### 2.3 Pohled obsluhy — top-down perspektiva přístroje

**Klíčová designová změna:** Simulátor zobrazuje přístroj tak jak ho vidí zachránce —
**pohled shora dolů**, přístroj leží na zemi nebo je položen na stůl.
Toto vytváří zcela jiný vizuální dojem než frontální pohled:

- Tělo přístroje má **výrazný vnější stín** (jako objekt ležící na podlaze)
- Povrch má **lehký perspektivní gradient** — tmavší okraje, světlejší střed
- Tlačítka jsou **vystouplá směrem k divákovi** — větší `box-shadow` dole než nahoře
- Elektrody jsou **fyzické kabely** táhnoucí se z konektoru ven
- Celé `#device-panel` má tmavé pozadí simulující **podlahu nebo povrch stolu**

```
POHLED OBSLUHY — přístroj leží, díváš se shora:

    ╔═══════════════════════════════════════════╗
    ║  Stůl / podlaha (tmavý povrch)            ║
    ║                                            ║
    ║  ┌──────────────────────────────────────┐  ║
    ║  │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│  ║  ← okraj přístroje vrhá stín dolů
    ║  │  PHILIPS         HeartStart FRx  [●] │  ║
    ║  │  ┌────────────────────────────────┐  │  ║
    ║  │  │  EKG (canvas, pohled shora)    │  │  ║
    ║  │  └────────────────────────────────┘  │  ║
    ║  │                                      │  ║
    ║  │  [torzo SVG — pohled shora/přední]   │  ║
    ║  │   ①═════════╗   ②══════════╗        │  ║  ← kabely elektrod táhnou
    ║  │              ║              ║        │  ║    ze spodní části přístroje
    ║  │  ┌──[▶]──┐  [i]  ┌──[⚡]──┐│  ║
    ║  │  │ ON/OFF│       │ VÝBOJ  ││  ║
    ║  │  │       │       │        ││  ║
    ║  │  └───────┘       └────────┘│  ║
    ║  │  ● READY  ● NABÍJÍM  ● VÝBOJ  │  ║
    ║  │  M3861A  HeartStart FRx        │  ║
    ║  └──────────────────────────────────┘  ║  ← stín přístroje na podlaze
    ║                                            ║
    ╚═══════════════════════════════════════════╝
```

**CSS pro efekt ležícího přístroje:**
```css
/* Podlaha / stůl pod přístrojem */
#device-panel {
  background:
    radial-gradient(ellipse at 50% 40%,  #2a3040 0%,  #1a2030 60%,  #111827 100%);
  padding:        16px;
  display:        flex;
  flex-direction: column;
  gap:            0;
  overflow:       hidden;
  position:       relative;
}

/* Přístroj jako fyzický objekt na podlaze */
#frx-body {
  background:
    radial-gradient(ellipse at 50% 30%, rgba(255,255,255,0.09) 0%, transparent 60%),
    linear-gradient(180deg,  rgba(255,255,255,0.05) 0%, transparent          30%),
    linear-gradient(135deg,  rgba(255,255,255,0.03) 0%, rgba(0,0,0,0.15)     100%),
    linear-gradient(160deg,  #4e5670 0%, #3a4158 40%, #2e3550 70%, #252d45 100%);
  border-radius: 18px;
  border-top:    2px solid #5a6278;
  border-left:   2px solid #4a5268;
  border-right:  2px solid #1a2232;
  border-bottom: 3px solid #141c2c;   /* silnější spodní hrana = tloušťka přístroje */
  padding:       16px 16px 20px 16px;

  /* KLÍČOVÉ: stín ležícího přístroje na podlaze */
  box-shadow:
    0 12px 40px rgba(0,0,0,0.80),     /* hlavní stín na podlaze */
    0  4px 12px rgba(0,0,0,0.60),     /* blízký stín (tloušťka přístroje) */
    0  1px  3px rgba(0,0,0,0.40),     /* kontaktní stín (přesně kde leží) */
    inset 0  2px 0 rgba(255,255,255,0.08),
    inset 0 -2px 0 rgba(0,0,0,0.30);

  flex:          1;
  display:       flex;
  flex-direction: column;
  gap:           10px;
  position:      relative;
}

/* Světelný odlesk shora (jako by dopadalo světlo ze stropu) */
#frx-body::before {
  content:       '';
  position:      absolute;
  top:           0; left: 15%; right: 15%;
  height:        2px;
  background:    linear-gradient(90deg, transparent, rgba(255,255,255,0.20), transparent);
  border-radius: 0 0 4px 4px;
  pointer-events: none;
}
```

**Tlačítka — vystouplá směrem k divákovi (pohled shora):**

Při pohledu shora jsou tlačítka vystouplé kupole. Stín musí být větší na spodní straně
(bližší k divákovi) než na horní:
```css
/* Přepsat pro ON/OFF a VÝBOJ — shadow asymetrie pro top-down pohled */
#btn-on, #btn-shock {
  /* Přidej k existujícím box-shadow hodnotám: */
  box-shadow:
    0 8px 18px rgba(0,0,0,0.70),      /* hlavní stín dole = blíže k divákovi */
    0 3px  6px rgba(0,0,0,0.50),      /* sekundární stín */
    0 1px  2px rgba(0,0,0,0.40),      /* kontaktní stín */
    inset 0  2px 3px rgba(255,255,255,0.15),
    inset 0 -4px 6px rgba(0,0,0,0.50);
}
```

**Kabely elektrod — SVG vizuální detail:**

Přidat do SVG schématu elektrod zakřivené čáry simulující fyzické kabely
táhnoucí se z konektoru k místům elektrod:
```svg
<!-- Kabel elektrody 1 — zakřivená čára z konektoru (spodek přístroje) k elektrodě -->
<path id="cable1"
  d="M 162,125 C 162,115 155,100 162,62"
  fill="none" stroke="#1a2535" stroke-width="3"
  stroke-linecap="round"/>
<!-- Při placed stavu: stroke="#22c55e" -->

<!-- Kabel elektrody 2 -->
<path id="cable2"
  d="M 244,125 C 244,115 248,105 244,100"
  fill="none" stroke="#1a2535" stroke-width="3"
  stroke-linecap="round"/>
```

---

### 2.4a Celkový layout — grid přehled

```
┌────────────────────────────────────────────────────────────────────────────┐  28px
│  #site-bar: AED Trenažér  [FRx][ZOLL][SAM]   [🔊]  [CZ][EN]  [♥ Tip]     │
├────────────────────────────────────────────────────────────────────────────┤  22px
│  #training-banner: ⬛ TRENAŽÉR · POUZE PRO VÝCVIK                           │
├─────────────────────────────────────┬──────────────────────────────────────┤  ↑
│  #device-panel  (440px)             │  #instruction-panel  (360px)         │  │
│  (přístroj — pohled shora)          │  (instruktor/výcvik)                 │  │
│                                     │                                      │  550px
│  ┌── #frx-body ─────────────────┐   │  ┌──────────────────────────────┐   │  │
│  │  (ležící AED přístroj)       │   │  │ #scenario-bar                 │   │  │
│  │                              │   │  │  [S1 Klas. zástava ▼]  [↺]   │   │  │
│  │  [logo + ready light]        │   │  └──────────────────────────────┘   │  │
│  │  [EKG canvas 390×70]         │   │                                      │  │
│  │  [SVG torzo + elektrody]     │   │  ┌──────────────────────────────┐   │  │
│  │  [konektory SMART Pads]      │   │  │ #main-instruction (18–20px)   │   │  │
│  │                              │   │  └──────────────────────────────┘   │  │
│  │   ●ON/OFF  ●i  ●VÝBOJ        │   │                                      │  │
│  │  (88px)  (36px) (88px)       │   │  ┌──────────────────────────────┐   │  │
│  │                              │   │  │ #metronome-section            │   │  │
│  │  ● READY ● NABÍJÍM ● VÝBOJ   │   │  │  ○ pulz  110 BPM  [──●──]    │   │  │
│  │  M3861A HeartStart FRx       │   │  └──────────────────────────────┘   │  │
│  └──────────────────────────────┘   │                                      │  │
│                                     │  ┌──────────────────────────────┐   │  │
│                                     │  │ #cpr-controls (visible v KPR) │   │  │
│                                     │  │  [00/30]  ████░░  kolo [1/4]  │   │  │
│                                     │  │  [↓ STLAČENÍ HRUDNÍKU ↓]     │   │  │
│                                     │  │  [✓ DVA VDECHY PROVEDENY]     │   │  │
│                                     │  └──────────────────────────────┘   │  │
│                                     │                                      │  │
│                                     │  ┌──────────────────────────────┐   │  ↓
│                                     │  │ #event-log (monospace, 11px)  │   │
│                                     │  └──────────────────────────────┘   │
└─────────────────────────────────────┴──────────────────────────────────────┘
```

**Klíčový princip — dva oddělené prostory:**
- **Levý panel** = fyzický přístroj, pohled obsluhy shora. Žádné webové prvky.
- **Pravý panel** = výcvikový displej. Nahoře výběr scénáře, pak instrukce,
  metronom s BPM sliderem, počítadlo KPR, event log. Plně viditelné celou dobu.

**Responzivní chování:**
```css
#app-container {
  display:               grid;
  grid-template-columns: 440px 360px;   /* pevná šířka — tablet 800px */
  width:                 800px;
  min-width:             800px;         /* minimální šířka zachována vždy */
  height:                calc(100vh - 50px);
  min-height:            480px;         /* minimální výška */
  margin:                0 auto;
  overflow:              hidden;
}

/* Resize: při viewportu < 800px scrollovat horizontálně — akceptováno */
html, body {
  min-width:  800px;
  overflow-x: auto;
  background: #0d1117;   /* barva podlahy viditelná při scrollu */
}

/* Při viewportu > 1200px: centrovat, nezvedat šířku panelů */
@media (min-width: 1200px) {
  #app-container { width: 800px; }  /* pevná šířka i na velkém monitoru */
}
```


### 2.4 Věrná vizuální replika Philips HeartStart FRx

Implementátor musí dodržet následující vzhledové prvky reálného přístroje:

#### Logo a identifikace (horní část těla)
```css
/* Philips logo — modrý nápis */
.frx-logo-philips {
  color:          #2563c7;
  font-family:    var(--font-device);
  font-size:      15px;
  font-weight:    900;
  letter-spacing: 4px;
  text-transform: uppercase;
}
/* Model pod logem */
.frx-logo-model {
  color:       #7a8a9a;
  font-size:   9px;
  letter-spacing: 1.5px;
}
/* Sériové číslo — spodní okraj těla */
.frx-serial {
  color:       #2d3550;
  font-size:   8px;
  font-family: monospace;
  text-align:  center;
  letter-spacing: 1px;
}
```

#### Ready light (vpravo od loga)
```html
<div id="ready-zone">
  <div id="ready-light" class="led"></div>
  <span class="ready-label" data-i18n="led_ready">READY</span>
</div>
```
```css
.led {
  width: 14px; height: 14px;
  border-radius: 50%;
  border: 1px solid #111;
  background: #111;
  transition: all 0.3s;
}
.led.green        { background: #22c55e; box-shadow: 0 0 8px #22c55e; }
.led.green-blink  { background: #22c55e; animation: led-blink 1s infinite; }
.led.red-blink    { background: #ef4444; animation: led-blink 0.5s infinite; }
.led.yellow-blink { background: #eab308; animation: led-blink 0.8s infinite; }

@keyframes led-blink {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.1; }
}
```

#### EKG displej — zapuštěný displej, přesné rozměry
```css
/*
 * ZAPUŠTĚNÝ DISPLEJ — efekt LCD monitoru vsazeného do plastu:
 *   border: asymetrický — tmavší nahoře a vlevo (světlo dopadá,
 *           takže horní/levá hrana vrhá stín dovnitř)
 *           světlejší dole a vpravo (odlesk od plochy)
 *   box-shadow inset: simuluje hloubku prohlubně v těle přístroje
 *   background: téměř černá s lehkým nazelenalým nádechem (LCD)
 */
#ecg-display {
  background:    #020a05;               /* černá s LCD nádechem */
  border-top:    2px solid #050e08;     /* tmavá horní hrana = hloubka */
  border-left:   2px solid #060f09;     /* tmavá levá hrana */
  border-right:  1.5px solid #0d2015;   /* světlejší pravá = odlesk */
  border-bottom: 1.5px solid #0d2015;   /* světlejší spodní */
  border-radius: 4px;
  padding:       3px;
  position:      relative;
  box-shadow:
    inset 0   2px 6px  rgba(0,0,0,0.80),  /* hloubka nahoře */
    inset 2px 0   4px  rgba(0,0,0,0.50),  /* hloubka vlevo */
    inset 0  -1px 2px  rgba(0,0,0,0.30),  /* jemný spodní stín */
    0 0 0 1px #030810;                     /* tenký vnější obrys */
}
#ecg-canvas {
  display:      block;
  width:        100%;
  height:       70px;
  border-radius: 2px;
}
/* EKG gridlines — renderovat v JS na canvas:
   ctx.strokeStyle = '#0a1e0d'  (velmi tmavá zelená, sotva viditelná)
   horizontální linky každých 20px, vertikální každých 10px
   lineWidth = 0.5 */
```

#### Schéma elektrod — SVG torzo s anatomicky správnými pozicemi
```
SVG viewBox="0 0 390 130"

Torzo:
  <ellipse cx="195" cy="22" rx="22" ry="20"/>        ← hlava
  <path d="M155,45 Q140,52 138,75 L136,125
           Q160,132 195,132 Q230,132 254,125
           L252,75 Q250,52 235,45 Q215,38 195,38
           Q175,38 155,45 Z"/>                         ← trup

Elektroda 1 (STERNUM — pravý horní hrudník):
  <rect id="pad1-zone" x="140" y="44" width="44" height="36" rx="6"/>
  Střed: (162, 62) — anatom. správně pod pravou klíční kostí

Elektroda 2 (APEX — levý boční hrudník):
  <rect id="pad2-zone" x="222" y="82" width="44" height="36" rx="6"/>
  Střed: (244, 100) — anatom. správně pod levou axilou

Čísla elektrod:
  <text x="152" y="89" font-size="11" fill="#aaa">1</text>
  <text x="234" y="91" font-size="11" fill="#aaa">2</text>

Tečkované vodítko šipky z konektoru k elektrodě:
  Elektroda 1: stroke-dasharray="4 3", barva #334, od konektoru vlevo k rect
  Elektroda 2: stroke-dasharray="4 3", barva #334, od konektoru vpravo k rect
```

Vizuální stavy elektrod:
```css
#pad1-zone, #pad2-zone {
  fill:           #1a2535;
  stroke:         #2a3a4a;
  stroke-width:   1.5;
  stroke-dasharray: 5 3;
  cursor:         pointer;
  transition:     fill 0.2s, stroke 0.2s;
}
#pad1-zone:hover, #pad2-zone:hover {
  stroke:       #eab308;
  stroke-width: 2;
}
#pad1-zone.placed, #pad2-zone.placed {
  fill:           #052e16;
  stroke:         #22c55e;
  stroke-width:   2;
  stroke-dasharray: none;
}
```

#### Konektory SMART Pads II
```html
<div id="connectors">
  <div id="conn-left"  class="connector" onclick="connectPad(1)"
       ontouchend="connectPad(1); event.preventDefault()">
    <div class="conn-port"><div class="conn-pin"></div></div>
    <span data-i18n="pad1_label">ELEKTRODA 1</span>
    <span class="conn-hint" data-i18n="pad1_hint">Pravá klíční kost</span>
  </div>
  <div class="conn-center-label">SMART<br>Pads II</div>
  <div id="conn-right" class="connector" onclick="connectPad(2)"
       ontouchend="connectPad(2); event.preventDefault()">
    <span data-i18n="pad2_label">ELEKTRODA 2</span>
    <span class="conn-hint" data-i18n="pad2_hint">Levý bok – axila</span>
    <div class="conn-port"><div class="conn-pin"></div></div>
  </div>
</div>
```
```css
#connectors {
  display:         flex;
  justify-content: space-between;
  align-items:     center;
  background:      #0f1520;
  border-radius:   8px;
  padding:         6px 10px;
  border:          1px solid #1e2535;
}
.connector {
  display:     flex;
  align-items: center;
  gap:         6px;
  cursor:      pointer;
  padding:     4px 6px;
  border-radius: 5px;
  border:      1.5px dashed #2a3a4a;
  transition:  border-color 0.2s;
  min-width:   130px;
}
.connector:hover  { border-color: #4a6a8a; }
.connector.placed { border-style: solid; border-color: #22c55e; }

.conn-port {
  width: 26px; height: 16px;
  border-radius: 3px;
  background: #111827;
  border: 1.5px solid #2a3a4a;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.conn-pin {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: #2a3a4a;
  transition: all 0.3s;
}
.connector.placed .conn-port { background: #052e16; border-color: #22c55e; }
.connector.placed .conn-pin  { background: #4ade80; box-shadow: 0 0 5px #4ade80; }

.conn-center-label { color: #1e2a3a; font-size: 8px; text-align: center; letter-spacing: 1px; }
.conn-hint { color: #374151; font-size: 8px; display: block; }
.connector.placed .conn-hint { color: #22c55e; }
```

#### Tři hlavní tlačítka — přesné rozměry a pozice

```css
#main-buttons {
  display:         flex;
  align-items:     center;
  justify-content: space-between;
  padding:         4px 10px;
}

/* ── ON/OFF – ZELENÉ KULATÉ (∅ 88px) ── */
/*
 * 3D PLASTOVÝ EFEKT — tři gradient vrstvy:
 *   vrstva 1: bílý specular highlight vlevo nahoře (plastový lesk)
 *   vrstva 2: tmavý drop vpravo dole (hloubka, zaoblení)
 *   vrstva 3: základní barevný radial (střed světlý → okraj tmavý)
 * box-shadow:
 *   vnější: tvrdý stín pod tlačítkem (zvednutost nad povrch)
 *   inset světlá: horní hrana (světlo dopadá shora)
 *   inset tmavá: spodní hrana (stín pod zaoblením)
 */
#btn-on {
  width:          88px;
  height:         88px;
  border-radius:  50%;
  background:
    radial-gradient(circle at 32% 26%, rgba(255,255,255,0.18) 0%, transparent 55%),
    radial-gradient(circle at 68% 74%, rgba(0,0,0,0.35)       0%, transparent 50%),
    radial-gradient(circle at 40% 35%, #1c7a3a 0%, #125c2a 50%, #0a3d1c 100%);
  border:         3px solid #0e4a20;
  border-top:     3px solid #1e8a40;    /* světlejší horní hrana = světlo */
  border-bottom:  3px solid #082e14;    /* tmavší spodní hrana = stín */
  cursor:         pointer;
  display:        flex;
  flex-direction: column;
  align-items:    center;
  justify-content: center;
  gap:            3px;
  box-shadow:
    0 6px 14px rgba(0,0,0,0.65),        /* tvrdý stín pod tlačítkem */
    0 2px 4px  rgba(0,0,0,0.4),         /* měkký ambientní stín */
    inset 0  2px 3px rgba(255,255,255,0.15),  /* horní plastová hrana */
    inset 0 -3px 5px rgba(0,0,0,0.45);       /* spodní zaoblení */
  transition:     all 0.12s;
  touch-action:   manipulation;
  position:       relative;
}
#btn-on .btn-symbol { color: #6ee08a; font-size: 24px; line-height: 1; text-shadow: 0 1px 3px rgba(0,0,0,0.5); }
#btn-on .btn-label  { color: #6ee08a; font-size: 8px; font-weight: 700;
                       letter-spacing: 1px; text-transform: uppercase; }
#btn-on:active {
  transform:  scale(0.93) translateY(2px);    /* fyzický stisk = jde dolů */
  box-shadow:
    0 2px 6px  rgba(0,0,0,0.65),
    0 1px 2px  rgba(0,0,0,0.4),
    inset 0  1px 2px rgba(255,255,255,0.10),
    inset 0 -2px 4px rgba(0,0,0,0.45);
}
#btn-on.powered {
  background:
    radial-gradient(circle at 32% 26%, rgba(255,255,255,0.22) 0%, transparent 52%),
    radial-gradient(circle at 68% 74%, rgba(0,0,0,0.28)       0%, transparent 48%),
    radial-gradient(circle at 40% 35%, #22c55e 0%, #16a34a 50%, #0d6630 100%);
  border-color:  #15803d;
  border-top:    3px solid #4ade80;
  border-bottom: 3px solid #065f21;
  box-shadow:
    0 0 22px rgba(34,197,94,0.7),
    0 6px 14px rgba(0,0,0,0.55),
    inset 0  2px 3px rgba(255,255,255,0.20),
    inset 0 -3px 5px rgba(0,0,0,0.35);
}

/* ── i – MODRÉ KULATÉ (∅ 36px) ── */
/*
 * Menší tlačítko — stejný princip, ale subtilnější
 * Odpovídá reálnému malému modrému i-tlačítku FRx
 */
#btn-info {
  width:          36px;
  height:         36px;
  border-radius:  50%;
  background:
    radial-gradient(circle at 33% 28%, rgba(255,255,255,0.20) 0%, transparent 55%),
    radial-gradient(circle at 65% 72%, rgba(0,0,0,0.30)       0%, transparent 48%),
    radial-gradient(circle at 40% 38%, #2347a0 0%, #1e3a8a 50%, #152a6e 100%);
  border:         2px solid #1a3278;
  border-top:     2px solid #2d5abf;
  border-bottom:  2px solid #111e52;
  color:          #93c5fd;
  font-size:      16px;
  font-style:     italic;
  font-weight:    900;
  cursor:         pointer;
  display:        flex;
  align-items:    center;
  justify-content: center;
  box-shadow:
    0 4px 10px rgba(0,0,0,0.55),
    inset 0  1px 2px rgba(255,255,255,0.18),
    inset 0 -2px 4px rgba(0,0,0,0.40);
  transition:     all 0.12s;
  touch-action:   manipulation;
}
#btn-info:active {
  transform:  scale(0.90) translateY(1px);
  box-shadow:
    0 1px 4px rgba(0,0,0,0.55),
    inset 0 1px 1px rgba(255,255,255,0.10),
    inset 0 -1px 3px rgba(0,0,0,0.40);
}
#btn-info.blink { animation: info-blink 1s infinite; }
@keyframes info-blink {
  0%, 100% { box-shadow: 0 0 12px rgba(59,130,246,0.9), 0 4px 10px rgba(0,0,0,0.55),
                          inset 0 1px 2px rgba(255,255,255,0.18), inset 0 -2px 4px rgba(0,0,0,0.40); }
  50%       { box-shadow: 0 4px 10px rgba(0,0,0,0.55),
                          inset 0 1px 2px rgba(255,255,255,0.18), inset 0 -2px 4px rgba(0,0,0,0.40); }
}

/* ── VÝBOJ – ORANŽOVÉ KULATÉ (∅ 88px) ── */
/*
 * Neaktivní stav: ztlumená tmavá oranžová — tlačítko "spí"
 * Aktivní (shock-ready): plný oranžový 3D efekt + pulse glow
 * Stejný třívrstvý princip jako ON/OFF
 */
#btn-shock {
  width:          88px;
  height:         88px;
  border-radius:  50%;
  background:
    radial-gradient(circle at 32% 26%, rgba(255,255,255,0.08) 0%, transparent 55%),
    radial-gradient(circle at 68% 74%, rgba(0,0,0,0.40)       0%, transparent 50%),
    radial-gradient(circle at 40% 35%, #7c2d12 0%, #5a1e0a 50%, #3a1205 100%);
  border:         3px solid #5a1e0a;
  border-top:     3px solid #8b3515;
  border-bottom:  3px solid #2a0d04;
  cursor:         pointer;
  display:        flex;
  flex-direction: column;
  align-items:    center;
  justify-content: center;
  gap:            2px;
  opacity:        0.28;
  pointer-events: none;
  box-shadow:
    0 6px 14px rgba(0,0,0,0.65),
    inset 0  2px 3px rgba(255,255,255,0.06),
    inset 0 -3px 5px rgba(0,0,0,0.50);
  transition:     all 0.2s;
  touch-action:   manipulation;
}
#btn-shock .btn-symbol { color: #c2540a; font-size: 28px; line-height: 1; }
#btn-shock .btn-label  { color: #c2540a; font-size: 8px; font-weight: 700;
                          letter-spacing: 1px; text-transform: uppercase; }

/* Aktivní stav — SHOCK_READY */
#btn-shock.shock-ready {
  opacity:        1;
  pointer-events: auto;
  background:
    radial-gradient(circle at 32% 26%, rgba(255,255,255,0.22) 0%, transparent 52%),
    radial-gradient(circle at 68% 74%, rgba(0,0,0,0.30)       0%, transparent 48%),
    radial-gradient(circle at 40% 35%, #fb923c 0%, #ea580c 45%, #9a3412 100%);
  border:         3px solid #c2410c;
  border-top:     3px solid #fdba74;
  border-bottom:  3px solid #7c2d12;
  box-shadow:
    0 0 28px rgba(249,115,22,0.75),
    0 6px 14px rgba(0,0,0,0.55),
    inset 0  2px 3px rgba(255,255,255,0.25),
    inset 0 -3px 5px rgba(0,0,0,0.40);
  animation:      shock-pulse 0.9s infinite;
}
#btn-shock.shock-ready .btn-symbol { color: #fff; text-shadow: 0 0 8px rgba(255,200,100,0.8); }
#btn-shock.shock-ready .btn-label  { color: #fff; }
#btn-shock:active.shock-ready {
  transform:  scale(0.93) translateY(2px);
  box-shadow:
    0 0 14px rgba(249,115,22,0.6),
    0 2px 6px rgba(0,0,0,0.55),
    inset 0 1px 2px rgba(255,255,255,0.15),
    inset 0 -2px 4px rgba(0,0,0,0.40);
}

@keyframes shock-pulse {
  0%, 100% { box-shadow: 0 0 20px rgba(249,115,22,0.65), 0 6px 14px rgba(0,0,0,0.55),
                          inset 0 2px 3px rgba(255,255,255,0.25), inset 0 -3px 5px rgba(0,0,0,0.40); }
  50%       { box-shadow: 0 0 48px rgba(249,115,22,1.00), 0 6px 14px rgba(0,0,0,0.55),
                          inset 0 2px 3px rgba(255,255,255,0.25), inset 0 -3px 5px rgba(0,0,0,0.40); }
}
```

HTML struktura tlačítek:
```html
<div id="main-buttons">
  <div id="btn-on" onclick="pressPower()"
       ontouchend="pressPower(); event.preventDefault()"
       aria-label="Zapnout / Vypnout" data-i18n-aria="btn_on">
    <span class="btn-symbol">⏻</span>
    <span class="btn-label" data-i18n="btn_on">ZAP/VYP</span>
  </div>

  <div id="btn-info" onclick="pressInfo()"
       ontouchend="pressInfo(); event.preventDefault()"
       aria-label="Informace / KPR coaching">
    <em>i</em>
  </div>

  <div id="btn-shock" onclick="pressShock()"
       ontouchend="pressShock(); event.preventDefault()"
       aria-label="Podat výboj" data-i18n-aria="btn_shock">
    <span class="btn-symbol">⚡</span>
    <span class="btn-label" data-i18n="btn_shock">VÝBOJ</span>
  </div>
</div>
```

#### Nabíjecí progress bar (SHOCK_CHARGING)
```html
<div id="charging-bar-wrap" hidden>
  <div id="charging-bar-fill"></div>
  <span id="charging-label">NABÍJÍM…</span>
</div>
```
```css
#charging-bar-wrap {
  height:       8px;
  background:   #1a0800;
  border-radius: 4px;
  overflow:     hidden;
  position:     relative;
  border:       1px solid #4a1a08;
}
#charging-bar-fill {
  height:       100%;
  width:        0%;
  background:   linear-gradient(90deg, #c2410c, #f97316);
  border-radius: 4px;
  transition:   width 0.1s linear;
}
#charging-label {
  position:   absolute;
  right:      6px; top: -18px;
  font-size:  9px; color: #f97316;
  letter-spacing: 1px;
  font-family: var(--font-device);
}
```

#### LED statusy (spodní část těla)
```html
<div id="led-status">
  <div class="led-item">
    <div id="led-ready"    class="led"></div>
    <span data-i18n="led_ready">READY</span>
  </div>
  <div class="led-item">
    <div id="led-charging" class="led"></div>
    <span data-i18n="led_charging">NABÍJÍM</span>
  </div>
  <div class="led-item">
    <div id="led-shock"    class="led"></div>
    <span data-i18n="led_shock">VÝBOJ DOPORUČEN</span>
  </div>
</div>
```
```css
#led-status {
  display:         flex;
  justify-content: space-around;
  padding:         4px 8px;
  background:      #0a0e18;
  border-radius:   6px;
  border:          1px solid #1a2030;
}
.led-item {
  display:     flex;
  align-items: center;
  gap:         5px;
}
.led-item span {
  color:          #2d3550;
  font-size:      8px;
  font-family:    var(--font-device);
  letter-spacing: 1px;
  text-transform: uppercase;
}
.led-item:has(.led.green) span,
.led-item:has(.led.green-blink) span { color: #4ade80; }
.led-item:has(.led.red-blink) span   { color: #f87171; }
.led-item:has(.led.yellow-blink) span{ color: #fde047; }
```

### 2.5 Barevné schéma – věrná replika FRx

> ⚠️ KRITICKÉ: Reálný Philips HeartStart FRx je **světle šedý přístroj** (světlá ABS plastika).
> Implementátor musí použít níže uvedené hodnoty — dřívější tmavě modrošedá neodpovídá realitě.

| Prvek | Hex | Vizuální popis |
|---|---|---|
| **Site-bar** (webový pruh) | `#111827` | téměř černá |
| **Training banner** | `#c2410c` | bezpečnostní oranžová |
| **Podlaha pod přístrojem** (`#device-panel`) | `#0d1117` | velmi tmavá — kontrastní pozadí |
| **Tělo FRx — světlá hrana** | `#c8cdd6` | světle šedá (horní/levá hrana) |
| **Tělo FRx — střední tón** | `#a8b0bc` | základní povrch ABS plastu |
| **Tělo FRx — tmavá hrana** | `#8892a0` | stín (dolní/pravá hrana) |
| **Tělo FRx — okraje/prohlubně** | `#6b7585` | nejhlubší tón |
| **Philips logo** | `#1d4ed8` | charakteristická Philips modrá |
| **Popisky na těle** | `#374151` | tmavě šedá — čitelná na světlém těle |
| **Sériové číslo** | `#6b7280` | střední šedá |
| **ON/OFF neaktivní** | `#1a5c30 → #0d3a1c` | tmavá zelená — nevýrazná když je off |
| **ON/OFF aktivní** | `#22c55e → #16a34a` + glow | jasná zelená — svítí! |
| **VÝBOJ neaktivní** | `#92320a → #5a1e05` | dim tmavá oranžová |
| **VÝBOJ aktivní** | `#f97316 → #ea580c` + pulse | sytá oranžová — pulzuje! |
| **Tlačítko „i"** | `#1e40af → #1e3a8a` | modrá |
| **EKG displej** | `#020a05` | LCD černá se zeleným nádechem |
| **EKG mřížka** | `#0a1e0d` | sotva viditelná zelená |
| **EKG křivka klid/KPR** | `#22c55e` | jasná zelená |
| **EKG křivka VF/analýza** | `#eab308` | žlutá — varování |
| **EKG křivka výboj** | `#ef4444` | červená |
| **Konektory SMART Pads** | `#e5e7eb` bg / `#9ca3af` border | světlé/bílé konektory |
| **Pravý panel** | `#0f172a` | tmavá navy |
| **Instrukce text** | `#f1f5f9` | téměř bílá |
| **Donate tlačítko** | `#0075eb` | Revolut modrá |

**CSS proměnné — opravené pro světle šedý FRx:**
```css
:root {
  --frx-light:     #c8cdd6;   /* světlá hrana těla */
  --frx-mid:       #a8b0bc;   /* střední tón povrchu */
  --frx-dark:      #8892a0;   /* tmavá hrana */
  --frx-deep:      #6b7585;   /* nejhlubší stín */
  --frx-floor:     #0d1117;   /* podlaha pod přístrojem */
  --clr-philips:   #1d4ed8;   /* Philips logo modrá */
  --clr-on-dim:    #1a5c30;
  --clr-on-lit:    #22c55e;
  --clr-shock-dim: #92320a;
  --clr-shock-lit: #f97316;
  --clr-info-btn:  #1e40af;
  --clr-ecg-bg:    #020a05;
  --clr-ecg-grid:  #0a1e0d;
  --clr-ecg-ok:    #22c55e;
  --clr-ecg-warn:  #eab308;
  --clr-ecg-shock: #ef4444;
  --clr-panel-bg:  #0f172a;
  --clr-text:      #f1f5f9;
  --clr-training:  #c2410c;
  --clr-donate:    #0075eb;
  --font-device:   'Rajdhani', sans-serif;
  --font-ui:       'IBM Plex Sans', sans-serif;
}
```

**Opravený gradient těla FRx** (světle šedý ABS plast, pohled shora):
```css
#frx-body {
  background:
    radial-gradient(ellipse at 50% 20%, rgba(255,255,255,0.30) 0%, transparent 55%),
    linear-gradient(145deg, rgba(255,255,255,0.15) 0%, rgba(0,0,0,0.20) 100%),
    linear-gradient(160deg, #bcc3ce 0%, #a8b0bc 35%, #96a0ae 70%, #8090a0 100%);
  border-top:    2px solid #d4d9e2;
  border-left:   2px solid #cdd2db;
  border-right:  2px solid #707a88;
  border-bottom: 3px solid #606a78;
  box-shadow:
    0 14px 45px rgba(0,0,0,0.85),
    0  5px 14px rgba(0,0,0,0.65),
    0  1px  3px rgba(0,0,0,0.50),
    inset 0  2px 0 rgba(255,255,255,0.30),
    inset 0 -2px 0 rgba(0,0,0,0.25);
}
```

**Popisky a LED na světlém těle** (invertovaná logika — tmavé na světlém):
```css
.frx-logo-philips { color: #1d4ed8; }     /* Philips modrá */
.frx-logo-model   { color: #4b5563; }     /* tmavě šedá */
.frx-serial       { color: #6b7280; }
.led-item span    { color: #374151; }     /* TMAVÁ na světlém těle */
/* LED jsou výraznější — světlé pozadí = větší kontrast */
.led.green { background: #16a34a; box-shadow: 0 0 12px #22c55e, 0 0 5px #22c55e; }
.led.red-blink { background: #dc2626; box-shadow: 0 0 12px #ef4444; animation: led-blink 0.5s infinite; }
```

**Konektory na světlém těle:**
```css
#connectors { background: #dde1e8; border: 1px solid #b0b8c4; }
.connector { border: 1.5px dashed #9ca3af; }
.connector:hover { border-color: #eab308; }
.connector.placed { border-style: solid; border-color: #16a34a; background: #dcfce7; }
.conn-port { background: #f3f4f6; border: 1.5px solid #9ca3af; }
.conn-pin  { background: #9ca3af; }
.connector.placed .conn-port { background: #dcfce7; border-color: #16a34a; }
.connector.placed .conn-pin  { background: #16a34a; box-shadow: 0 0 5px #22c55e; }
.pad-connector-label { color: #374151; font-weight: 700; }
.conn-hint { color: #6b7280; }
.connector.placed .conn-hint { color: #15803d; }
```

### 2.6 Typografie

| Kontext | Font | Velikost | Poznámka |
|---|---|---|---|
| Logo PHILIPS | `'Rajdhani', sans-serif` | 15 px, weight 900 | letter-spacing 4px |
| Popisky na těle FRx | `'Rajdhani', sans-serif` | 8–10 px | uppercase, letter-spacing 1–2px |
| Aktuální instrukce | `'IBM Plex Sans', sans-serif` | 18–20 px, bold | pravý panel, čitelné na tabletu |
| Event log | `monospace` | 11 px | zelená/žlutá/červená dle závažnosti |
| Tlačítka | `'Rajdhani', sans-serif` | 8 px | uppercase, letter-spacing 1px |
| Site-bar | `'IBM Plex Sans', sans-serif` | 11 px | tlumená šedá |

---

## 2.7 Skin systém — tři AED přístroje

### Architektonický princip — CSS-only skiny, identické HTML

> ⚠️ ZÁVAZNÉ PRAVIDLO: Všechny tři skiny sdílejí **přesně stejné HTML ID a strukturu**.
> State machine, JS logika, AudioEngine a SpeechEngine jsou skin-agnostické.
> Skin mění **výhradně vizuál přes CSS třídu** na `<body>` elementu.
> JS nikdy nečte `state.activeSkin` pro rozhodování o chování — pouze pro analytiku.

```
body.skin-frx       → Philips HeartStart FRx  (výchozí)
body.skin-zoll      → ZOLL AED Plus
body.skin-heartsine → HeartSine Samaritan PAD 360P
```

**Všechny prvky mají fixed ID — nikdy se nemění:**

| ID | Popis | Viditelnost dle skinu |
|---|---|---|
| `#frx-body` | tělo přístroje | vždy — barvy dle skin CSS |
| `#btn-on` | ON/OFF tlačítko | vždy |
| `#btn-info` | informační tlačítko i | vždy |
| `#btn-shock` | VÝBOJ tlačítko | vždy — tvar/barva dle skin CSS |
| `#ecg-display` | EKG plocha | vždy — obsah dle skin CSS |
| `#ecg-canvas` | EKG canvas | `skin-frx`: visible · `skin-zoll/heartsine`: `display:none` via CSS |
| `#skin-alt-display` | alternativní plocha | `skin-frx`: `display:none` · ostatní: visible via CSS |
| `#led-ready` | LED ready | vždy |
| `#led-charging` | LED nabíjím | vždy |
| `#led-shock` | LED výboj | vždy |
| `#connectors` | konektory elektrod | vždy — styl dle skin CSS |
| `#zoll-cpr-num` | čítač KPR | vždy v DOM · `skin-zoll`: visible · ostatní: `display:none` |
| `.frx-logo-brand` | název výrobce | vždy — text dle skin CSS `content:` |
| `.frx-logo-model` | model | vždy — text dle skin CSS `content:` |

**HTML je identické pro všechny skiny:**
```html
<div id="frx-body">

  <!-- Logo — text injektován přes CSS content: na ::after -->
  <div id="device-header">
    <div class="frx-logo">
      <div class="frx-logo-brand"></div>   <!-- text přes CSS attr -->
      <div class="frx-logo-model"></div>
    </div>
    <div class="ready-zone">
      <div id="led-ready" class="led"></div>
      <span class="ready-label" data-i18n="led_ready">READY</span>
    </div>
  </div>

  <!-- EKG plocha — canvas NEBO alt-display, přepínáno CSS display -->
  <div id="ecg-display">
    <canvas id="ecg-canvas"></canvas>
    <div id="skin-alt-display">
      <!-- ZOLL: čítač KPR / HeartSine: informační text -->
      <span id="zoll-cpr-num">--</span>
      <span class="alt-label"></span>   <!-- text přes CSS content: -->
    </div>
  </div>

  <!-- SVG schéma elektrod — pozice stejné, styl dle skin CSS -->
  <div id="pad-diagram">
    <svg viewBox="0 0 390 130" id="pad-svg">
      <!-- torzo, elektrody, čísla — vždy stejné ID -->
      <ellipse id="torso-head" cx="195" cy="22" rx="22" ry="20"/>
      <path    id="torso-body" d="M155,45 Q140,52 138,75 L136,125
               Q160,132 195,132 Q230,132 254,125
               L252,75 Q250,52 235,45 Q215,38 195,38
               Q175,38 155,45 Z"/>
      <rect id="pad1-zone" x="140" y="44" width="44" height="36" rx="6"/>
      <rect id="pad2-zone" x="222" y="82" width="44" height="36" rx="6"/>
      <text id="pad1-num" x="152" y="89" font-size="11">1</text>
      <text id="pad2-num" x="234" y="91" font-size="11">2</text>
    </svg>
  </div>

  <!-- Konektory -->
  <div id="connectors">
    <div id="conn-left" class="connector"
         onclick="connectPad(1)"
         ontouchend="connectPad(1); event.preventDefault()">
      <div class="conn-port"><div class="conn-pin"></div></div>
      <div class="conn-labels">
        <span class="pad-connector-label" data-i18n="pad1_label">ELEKTRODA 1</span>
        <span class="conn-hint" data-i18n="pad1_hint">Pravá klíční kost</span>
      </div>
    </div>
    <div class="conn-center">
      <span class="conn-brand-label"></span>  <!-- SMART Pads II / CPR-D padz / PAD-PAK via CSS -->
    </div>
    <div id="conn-right" class="connector"
         onclick="connectPad(2)"
         ontouchend="connectPad(2); event.preventDefault()">
      <div class="conn-labels">
        <span class="pad-connector-label" data-i18n="pad2_label">ELEKTRODA 2</span>
        <span class="conn-hint" data-i18n="pad2_hint">Levý bok – axila</span>
      </div>
      <div class="conn-port"><div class="conn-pin"></div></div>
    </div>
  </div>

  <!-- Hlavní tlačítka — ID nikdy nemění, tvar/barva via CSS -->
  <div id="main-buttons">
    <div id="btn-on"    role="button" tabindex="0"
         onclick="pressPower()"
         ontouchend="pressPower(); event.preventDefault()">
      <span class="btn-symbol">⏻</span>
      <span class="btn-label" data-i18n="btn_on">ZAP/VYP</span>
    </div>
    <div id="btn-info"  role="button" tabindex="0"
         onclick="pressInfo()"
         ontouchend="pressInfo(); event.preventDefault()">
      <em>i</em>
    </div>
    <div id="btn-shock" role="button" tabindex="0"
         onclick="pressShock()"
         ontouchend="pressShock(); event.preventDefault()">
      <span class="btn-symbol">⚡</span>
      <span class="btn-label" data-i18n="btn_shock">VÝBOJ</span>
    </div>
  </div>

  <!-- Nabíjecí bar — vždy v DOM, viditelný jen ve správném stavu -->
  <div id="charging-bar-wrap" hidden>
    <div id="charging-bar-fill"></div>
  </div>

  <!-- LED status row -->
  <div id="led-status">
    <div class="led-item"><div id="led-ready"    class="led"></div><span data-i18n="led_ready">READY</span></div>
    <div class="led-item"><div id="led-charging" class="led"></div><span data-i18n="led_charging">NABÍJÍM</span></div>
    <div class="led-item"><div id="led-shock"    class="led"></div><span data-i18n="led_shock">VÝBOJ</span></div>
  </div>

  <!-- Sériové číslo — různý text via CSS content: -->
  <div class="frx-serial"></div>

</div>
```

**setSkin() — pouze CSS třída a data atribut, žádná DOM logika:**
```javascript
const SKINS = {
  frx:       { cls: 'skin-frx',       label: 'Philips HeartStart FRx'    },
  zoll:      { cls: 'skin-zoll',      label: 'ZOLL AED Plus'             },
  heartsine: { cls: 'skin-heartsine', label: 'HeartSine Samaritan PAD'   },
};

function setSkin(id) {
  if (!SKINS[id]) return;
  // Přepsat třídu na body — veškerý vizuál řídí CSS
  document.body.className = document.body.className
    .replace(/skin-\w+/g, '').trim() + ' ' + SKINS[id].cls;
  // Uložit pro analytiku (JS logiku NEOVLIVŇUJE)
  state.activeSkin = id;
  // Skin-btn active stav
  document.querySelectorAll('.skin-btn')
    .forEach(b => b.classList.toggle('active', b.dataset.skin === id));
  // EcgEngine: resize canvas po přepnutí (canvas mohl být skrytý)
  EcgEngine.resize();
}

// Init — výchozí skin
document.body.classList.add('skin-frx');
```

---

### CSS skin — Philips HeartStart FRx (výchozí)

```css
/* ══════════════════════════════════════════
   SKIN: Philips HeartStart FRx
   Světle šedý ABS plast, zelené + oranžové
   ══════════════════════════════════════════ */

body.skin-frx #frx-body {
  background:
    radial-gradient(ellipse at 50% 20%, rgba(255,255,255,0.30) 0%, transparent 55%),
    linear-gradient(145deg, rgba(255,255,255,0.15) 0%, rgba(0,0,0,0.20) 100%),
    linear-gradient(160deg, #bcc3ce 0%, #a8b0bc 35%, #96a0ae 70%, #8090a0 100%);
  border-top:    2px solid #d4d9e2;
  border-left:   2px solid #cdd2db;
  border-right:  2px solid #707a88;
  border-bottom: 3px solid #606a78;
}

/* Logo — CSS generuje text přes attr() není dostupné, použít data přístup */
body.skin-frx .frx-logo-brand::after { content: 'PHILIPS'; color: #1d4ed8;
  font-size: 15px; font-weight: 900; letter-spacing: 4px; }
body.skin-frx .frx-logo-model::after { content: 'HeartStart FRx';
  color: #4b5563; font-size: 9px; letter-spacing: 1.5px; }
body.skin-frx .frx-serial::after     { content: 'M3861A · HeartStart FRx · TRAINER';
  color: #6b7280; font-size: 8px; }
body.skin-frx .conn-brand-label::after { content: 'SMART Pads II';
  color: #6b7280; font-size: 8px; letter-spacing: 1px; }

/* EKG — canvas viditelný, alt-display skrytý */
body.skin-frx #ecg-canvas       { display: block; }
body.skin-frx #skin-alt-display  { display: none; }

/* Tlačítka — kulatý tvar (výchozí) */
body.skin-frx #btn-on, body.skin-frx #btn-shock {
  border-radius: 50%;
  width: 88px; height: 88px;
}
body.skin-frx #btn-info { border-radius: 50%; width: 36px; height: 36px; }

/* ON/OFF */
body.skin-frx #btn-on {
  background:
    radial-gradient(circle at 32% 26%, rgba(255,255,255,0.18) 0%, transparent 55%),
    radial-gradient(circle at 68% 74%, rgba(0,0,0,0.35)       0%, transparent 50%),
    radial-gradient(circle at 40% 35%, #1c7a3a 0%, #125c2a 50%, #0a3d1c 100%);
  border-top: 3px solid #1e8a40; border-bottom: 3px solid #082e14;
  border-left: 3px solid #0e4a20; border-right: 3px solid #0e4a20;
}
body.skin-frx #btn-on .btn-symbol { color: #6ee08a; }
body.skin-frx #btn-on .btn-label  { color: #6ee08a; }
body.skin-frx #btn-on.powered {
  background:
    radial-gradient(circle at 32% 26%, rgba(255,255,255,0.22) 0%, transparent 52%),
    radial-gradient(circle at 68% 74%, rgba(0,0,0,0.28)       0%, transparent 48%),
    radial-gradient(circle at 40% 35%, #22c55e 0%, #16a34a 50%, #0d6630 100%);
  box-shadow: 0 0 22px rgba(34,197,94,0.7), 0 6px 14px rgba(0,0,0,0.55),
              inset 0 2px 3px rgba(255,255,255,0.20), inset 0 -3px 5px rgba(0,0,0,0.35);
}

/* VÝBOJ — oranžová */
body.skin-frx #btn-shock {
  background:
    radial-gradient(circle at 32% 26%, rgba(255,255,255,0.08) 0%, transparent 55%),
    radial-gradient(circle at 68% 74%, rgba(0,0,0,0.40)       0%, transparent 50%),
    radial-gradient(circle at 40% 35%, #7c2d12 0%, #5a1e0a 50%, #3a1205 100%);
  border-top: 3px solid #8b3515; border-bottom: 3px solid #2a0d04;
  border-left: 3px solid #5a1e0a; border-right: 3px solid #5a1e0a;
  opacity: 0.28; pointer-events: none;
}
body.skin-frx #btn-shock.shock-ready {
  opacity: 1; pointer-events: auto;
  background:
    radial-gradient(circle at 32% 26%, rgba(255,255,255,0.22) 0%, transparent 52%),
    radial-gradient(circle at 68% 74%, rgba(0,0,0,0.30)       0%, transparent 48%),
    radial-gradient(circle at 40% 35%, #fb923c 0%, #ea580c 45%, #9a3412 100%);
  border-top: 3px solid #fdba74; border-bottom: 3px solid #7c2d12;
}
body.skin-frx #btn-shock .btn-symbol { color: #c2540a; }
body.skin-frx #btn-shock.shock-ready .btn-symbol { color: #fff; }

/* Konektory */
body.skin-frx #connectors     { background: #dde1e8; border: 1px solid #b0b8c4; }
body.skin-frx .connector      { border: 1.5px dashed #9ca3af; }
body.skin-frx .connector.placed { border-style: solid; border-color: #16a34a; }
body.skin-frx .conn-port      { background: #f3f4f6; border: 1.5px solid #9ca3af; }
body.skin-frx .conn-pin       { background: #9ca3af; }
body.skin-frx .pad-connector-label { color: #374151; }
body.skin-frx .conn-hint      { color: #6b7280; }

/* SVG */
body.skin-frx #torso-head, body.skin-frx #torso-body { fill: none; stroke: #8892a0; stroke-width: 1.5; }
body.skin-frx #pad1-zone, body.skin-frx #pad2-zone   { fill: #c8d0d8; stroke: #7a8898; stroke-width: 1.5; stroke-dasharray: 5 3; }
body.skin-frx #pad1-zone:hover, body.skin-frx #pad2-zone:hover { stroke: #eab308; stroke-width: 2; }
body.skin-frx #pad1-zone.placed, body.skin-frx #pad2-zone.placed { fill: #dcfce7; stroke: #16a34a; stroke-dasharray: none; }
body.skin-frx #pad1-num, body.skin-frx #pad2-num { fill: #6b7280; }

/* LED na světlém těle */
body.skin-frx .led-item span { color: #374151; }
```

---

### CSS skin — ZOLL AED Plus

```css
/* ══════════════════════════════════════════
   SKIN: ZOLL AED Plus
   Téměř černý plast, bílý text, zelené ON/OFF,
   oranžové VÝBOJ (obdélníkové), CPR čítač místo EKG
   ══════════════════════════════════════════ */

body.skin-zoll #frx-body {
  background:
    radial-gradient(ellipse at 50% 20%, rgba(255,255,255,0.08) 0%, transparent 50%),
    linear-gradient(145deg, rgba(255,255,255,0.05) 0%, rgba(0,0,0,0.25) 100%),
    linear-gradient(160deg, #2a2a2a 0%, #1e1e1e 40%, #161616 70%, #0f0f0f 100%);
  border-top:    2px solid #3a3a3a;
  border-left:   2px solid #323232;
  border-right:  2px solid #080808;
  border-bottom: 3px solid #050505;
  box-shadow:
    0 14px 45px rgba(0,0,0,0.98),
    0  5px 14px rgba(0,0,0,0.85),
    inset 0  2px 0 rgba(255,255,255,0.06),
    inset 0 -2px 0 rgba(0,0,0,0.50);
}

body.skin-zoll .frx-logo-brand::after { content: 'ZOLL'; color: #ffffff;
  font-size: 22px; font-weight: 900; letter-spacing: 6px; }
body.skin-zoll .frx-logo-model::after { content: 'AED Plus';
  color: #aaaaaa; font-size: 10px; letter-spacing: 2px; }
body.skin-zoll .frx-serial::after    { content: 'REF 8000-000901 · AED Plus · TRAINER';
  color: #333; font-size: 8px; }
body.skin-zoll .conn-brand-label::after { content: 'CPR-D padz';
  color: #555; font-size: 8px; letter-spacing: 1px; }

/* EKG — canvas skrytý, alt-display (CPR čítač) viditelný */
body.skin-zoll #ecg-canvas      { display: none; }
body.skin-zoll #skin-alt-display {
  display:         flex;
  flex-direction:  column;
  align-items:     center;
  justify-content: center;
  background:      #000;
  border:          1px solid #1a1a1a;
  height:          100%;
  gap:             2px;
}
body.skin-zoll #zoll-cpr-num   { color: #22c55e; font-size: 28px; font-weight: 900;
  font-family: monospace; display: block; line-height: 1; }
body.skin-zoll .alt-label::after { content: 'COMPRS'; color: #333;
  font-size: 8px; letter-spacing: 2px; font-family: var(--font-device); }

/* Tlačítka — ON/OFF kulatý, VÝBOJ obdélníkový */
body.skin-zoll #btn-on {
  border-radius: 50%;
  width: 88px; height: 88px;
  background:
    radial-gradient(circle at 32% 26%, rgba(255,255,255,0.20) 0%, transparent 55%),
    radial-gradient(circle at 68% 74%, rgba(0,0,0,0.40)       0%, transparent 50%),
    radial-gradient(circle at 40% 35%, #16a34a 0%, #15803d 50%, #0d6630 100%);
  border-top: 3px solid #22c55e; border-bottom: 3px solid #064e20;
  border-left: 3px solid #155a2a; border-right: 3px solid #155a2a;
}
body.skin-zoll #btn-on .btn-symbol { color: #86efac; font-size: 26px; }
body.skin-zoll #btn-on .btn-label  { color: #86efac; }
body.skin-zoll #btn-on.powered {
  background:
    radial-gradient(circle at 32% 26%, rgba(255,255,255,0.22) 0%, transparent 52%),
    radial-gradient(circle at 68% 74%, rgba(0,0,0,0.28)       0%, transparent 48%),
    radial-gradient(circle at 40% 35%, #22c55e 0%, #16a34a 50%, #0d6630 100%);
  box-shadow: 0 0 24px rgba(34,197,94,0.8), 0 8px 18px rgba(0,0,0,0.70),
              inset 0 2px 3px rgba(255,255,255,0.20), inset 0 -4px 6px rgba(0,0,0,0.50);
}

/* ZOLL VÝBOJ — obdélníkový tvar */
body.skin-zoll #btn-shock {
  border-radius: 12px;        /* obdélníkové, ne kulaté */
  width:  110px;
  height: 68px;
  background:
    radial-gradient(circle at 32% 26%, rgba(255,255,255,0.08) 0%, transparent 55%),
    radial-gradient(circle at 68% 74%, rgba(0,0,0,0.40)       0%, transparent 50%),
    linear-gradient(160deg, #7c2d12 0%, #5a1e0a 60%, #3a1205 100%);
  border-top: 2px solid #8b3515; border-bottom: 3px solid #2a0d04;
  border-left: 2px solid #5a1e0a; border-right: 2px solid #5a1e0a;
  opacity: 0.28; pointer-events: none;
}
body.skin-zoll #btn-shock.shock-ready {
  opacity: 1; pointer-events: auto;
  background:
    radial-gradient(circle at 32% 26%, rgba(255,255,255,0.22) 0%, transparent 52%),
    radial-gradient(circle at 68% 74%, rgba(0,0,0,0.30)       0%, transparent 48%),
    linear-gradient(160deg, #f97316 0%, #ea580c 60%, #c2410c 100%);
  border-top: 2px solid #fdba74; border-bottom: 3px solid #7c2d12;
  box-shadow: 0 0 28px rgba(249,115,22,0.75), 0 6px 14px rgba(0,0,0,0.70),
              inset 0 2px 3px rgba(255,255,255,0.25), inset 0 -3px 5px rgba(0,0,0,0.40);
}
body.skin-zoll #btn-shock .btn-symbol { color: #c2540a; }
body.skin-zoll #btn-shock.shock-ready .btn-symbol { color: #fff; }

/* Konektory — tmavé na tmavém těle */
body.skin-zoll #connectors     { background: #0a0a0a; border: 1px solid #2a2a2a; }
body.skin-zoll .connector      { border: 1.5px dashed #333; }
body.skin-zoll .connector.placed { border-style: solid; border-color: #22c55e; }
body.skin-zoll .conn-port      { background: #111; border: 1.5px solid #333; }
body.skin-zoll .conn-pin       { background: #444; }
body.skin-zoll .connector.placed .conn-port { background: #052e16; border-color: #22c55e; }
body.skin-zoll .connector.placed .conn-pin  { background: #4ade80; }
body.skin-zoll .pad-connector-label { color: #888; }
body.skin-zoll .conn-hint      { color: #444; }

/* SVG — tmavší torzo pro tmavé tělo */
body.skin-zoll #torso-head, body.skin-zoll #torso-body { fill: none; stroke: #444; stroke-width: 1.5; }
body.skin-zoll #pad1-zone, body.skin-zoll #pad2-zone   { fill: #1a1a1a; stroke: #444; stroke-width: 1.5; stroke-dasharray: 5 3; }
body.skin-zoll #pad1-zone:hover, body.skin-zoll #pad2-zone:hover { stroke: #eab308; stroke-width: 2; }
body.skin-zoll #pad1-zone.placed, body.skin-zoll #pad2-zone.placed { fill: #052e16; stroke: #22c55e; stroke-dasharray: none; }
body.skin-zoll #pad1-num, body.skin-zoll #pad2-num { fill: #555; }

/* LED na tmavém těle */
body.skin-zoll .led-item span { color: #666; }
body.skin-zoll .led.green { box-shadow: 0 0 14px #22c55e; }

/* JS update CPR čítače — volat z doCompress() */
/* document.getElementById('zoll-cpr-num').textContent = state.cprPresses; */
/* Reset: document.getElementById('zoll-cpr-num').textContent = '--'; */
```

---

### CSS skin — HeartSine Samaritan PAD 360P

```css
/* ══════════════════════════════════════════
   SKIN: HeartSine Samaritan PAD 360P
   Bílá horní část + oranžová spodní část
   VÝBOJ = červené tlačítko
   EKG nahrazen informační plochou
   Plně automatický (ale JS logika identická!)
   ══════════════════════════════════════════ */

/* Tělo — dvoubarevné přes gradient */
body.skin-heartsine #frx-body {
  background:
    /* horní bílá část */
    linear-gradient(180deg,
      #f5f5f2  0%,
      #eeeeea 38%,
      #f06020 42%,   /* přechod bílá→oranžová */
      #ee5500 55%,
      #cc4400 100%);
  border-top:    2px solid #e8e8e4;
  border-left:   2px solid #e0e0dc;
  border-right:  2px solid #aa3300;
  border-bottom: 3px solid #882800;
  box-shadow:
    0 14px 45px rgba(0,0,0,0.85),
    0  5px 14px rgba(0,0,0,0.65),
    inset 0  2px 0 rgba(255,255,255,0.60),
    inset 0 -2px 0 rgba(0,0,0,0.25);
}

body.skin-heartsine .frx-logo-brand::after { content: 'HeartSine'; color: #1a5fa0;
  font-size: 12px; font-weight: 900; letter-spacing: 2px; }
body.skin-heartsine .frx-logo-model::after { content: 'samaritan® PAD 360P';
  color: #555; font-size: 8px; letter-spacing: 1px; }
body.skin-heartsine .frx-serial::after    { content: 'REF 360-STR-CZ · samaritan PAD · TRAINER';
  color: #bb5533; font-size: 8px; }   /* oranžová část — světlejší text */
body.skin-heartsine .conn-brand-label::after { content: 'PAD-PAK™';
  color: #bb5533; font-size: 8px; letter-spacing: 1px; }

/* EKG — canvas skrytý, alt-display s informačním textem */
body.skin-heartsine #ecg-canvas      { display: none; }
body.skin-heartsine #skin-alt-display {
  display:         flex;
  align-items:     center;
  justify-content: center;
  background:      #f0f0ec;
  border:          1px solid #ddd;
  border-radius:   4px;
  height:          100%;
}
body.skin-heartsine #zoll-cpr-num   { display: none; }  /* čítač skrytý */
body.skin-heartsine .alt-label::after {
  content: 'samaritan PAD 360P · Fully Automatic AED';
  color: #aaa; font-size: 8px; letter-spacing: 1px;
  font-family: var(--font-device); text-align: center;
}

/* Tlačítka — obě kulatá */
body.skin-heartsine #btn-on {
  border-radius: 50%;
  width: 88px; height: 88px;
  background:
    radial-gradient(circle at 32% 26%, rgba(255,255,255,0.22) 0%, transparent 55%),
    radial-gradient(circle at 68% 74%, rgba(0,0,0,0.35)       0%, transparent 50%),
    radial-gradient(circle at 40% 35%, #1c7a3a 0%, #125c2a 50%, #0a3d1c 100%);
  border-top: 3px solid #2d9a50; border-bottom: 3px solid #082e14;
  border-left: 3px solid #0e4a20; border-right: 3px solid #0e4a20;
}
body.skin-heartsine #btn-on .btn-symbol { color: #86efac; }
body.skin-heartsine #btn-on .btn-label  { color: #86efac; }
body.skin-heartsine #btn-on.powered {
  background:
    radial-gradient(circle at 32% 26%, rgba(255,255,255,0.25) 0%, transparent 52%),
    radial-gradient(circle at 68% 74%, rgba(0,0,0,0.25)       0%, transparent 48%),
    radial-gradient(circle at 40% 35%, #22c55e 0%, #16a34a 50%, #0d6630 100%);
  box-shadow: 0 0 22px rgba(34,197,94,0.8), 0 6px 14px rgba(0,0,0,0.55),
              inset 0 2px 3px rgba(255,255,255,0.25), inset 0 -3px 5px rgba(0,0,0,0.35);
}

/* HeartSine VÝBOJ — ČERVENÉ (ne oranžové!) */
body.skin-heartsine #btn-shock {
  border-radius: 50%;
  width: 88px; height: 88px;
  background:
    radial-gradient(circle at 32% 26%, rgba(255,255,255,0.08) 0%, transparent 55%),
    radial-gradient(circle at 68% 74%, rgba(0,0,0,0.40)       0%, transparent 50%),
    radial-gradient(circle at 40% 35%, #991b1b 0%, #7f1d1d 50%, #5a1212 100%);
  border-top: 3px solid #b91c1c; border-bottom: 3px solid #450a0a;
  border-left: 3px solid #7f1d1d; border-right: 3px solid #7f1d1d;
  opacity: 0.28; pointer-events: none;
}
body.skin-heartsine #btn-shock.shock-ready {
  opacity: 1; pointer-events: auto;
  background:
    radial-gradient(circle at 32% 26%, rgba(255,255,255,0.22) 0%, transparent 52%),
    radial-gradient(circle at 68% 74%, rgba(0,0,0,0.30)       0%, transparent 48%),
    radial-gradient(circle at 40% 35%, #ef4444 0%, #dc2626 45%, #991b1b 100%);
  border-top: 3px solid #fca5a5; border-bottom: 3px solid #7f1d1d;
  box-shadow: 0 0 28px rgba(239,68,68,0.75), 0 6px 14px rgba(0,0,0,0.55),
              inset 0 2px 3px rgba(255,255,255,0.25), inset 0 -3px 5px rgba(0,0,0,0.40);
  animation: shock-pulse-red 0.9s infinite;
}
body.skin-heartsine #btn-shock .btn-symbol { color: #fca5a5; }
body.skin-heartsine #btn-shock.shock-ready .btn-symbol { color: #fff; }

@keyframes shock-pulse-red {
  0%, 100% { box-shadow: 0 0 20px rgba(239,68,68,0.65), 0 6px 14px rgba(0,0,0,0.55); }
  50%       { box-shadow: 0 0 48px rgba(239,68,68,1.00), 0 6px 14px rgba(0,0,0,0.55); }
}

/* Konektory — světlé, na přechodu bílá→oranžová */
body.skin-heartsine #connectors { background: rgba(255,255,255,0.85); border: 1px solid #ddd; }
body.skin-heartsine .connector  { border: 1.5px dashed #ccc; }
body.skin-heartsine .connector.placed { border-style: solid; border-color: #16a34a; background: rgba(220,252,231,0.9); }
body.skin-heartsine .conn-port  { background: #f8f8f6; border: 1.5px solid #bbb; }
body.skin-heartsine .conn-pin   { background: #bbb; }
body.skin-heartsine .connector.placed .conn-pin { background: #16a34a; }
body.skin-heartsine .pad-connector-label { color: #374151; }
body.skin-heartsine .conn-hint  { color: #888; }

/* SVG — světlé torzo pro bílou část */
body.skin-heartsine #torso-head, body.skin-heartsine #torso-body { fill: none; stroke: #9ca3af; stroke-width: 1.5; }
body.skin-heartsine #pad1-zone, body.skin-heartsine #pad2-zone   { fill: #f0f0ec; stroke: #bbb; stroke-width: 1.5; stroke-dasharray: 5 3; }
body.skin-heartsine #pad1-zone:hover, body.skin-heartsine #pad2-zone:hover { stroke: #f59e0b; stroke-width: 2; }
body.skin-heartsine #pad1-zone.placed, body.skin-heartsine #pad2-zone.placed { fill: #dcfce7; stroke: #16a34a; stroke-dasharray: none; }
body.skin-heartsine #pad1-num, body.skin-heartsine #pad2-num { fill: #6b7280; }

/* LED — viditelné na bílé části */
body.skin-heartsine .led-item span { color: #374151; }
body.skin-heartsine .led.green     { box-shadow: 0 0 12px #22c55e; }
```

---

### Srovnávací tabulka skinů

| Vlastnost | Philips FRx | ZOLL AED Plus | HeartSine SAM 360P |
|---|---|---|---|
| `body` class | `skin-frx` | `skin-zoll` | `skin-heartsine` |
| Barva těla | světle šedá `#a8b0bc` | téměř černá `#1e1e1e` | bílá→oranžová gradient |
| ON/OFF tvar | kulatý ∅ 88px | kulatý ∅ 88px | kulatý ∅ 88px |
| ON/OFF barva | zelená `#1c7a3a` | zelená `#16a34a` | zelená `#1c7a3a` |
| VÝBOJ tvar | kulatý ∅ 88px | **obdélník** 110×68px | kulatý ∅ 88px |
| VÝBOJ barva (ready) | **oranžová** `#f97316` | **oranžová** `#f97316` | **červená** `#ef4444` |
| VÝBOJ pulse anim | `shock-pulse` | `shock-pulse` | `shock-pulse-red` |
| EKG canvas | `display: block` | `display: none` | `display: none` |
| Alt-display | `display: none` | CPR čítač `#zoll-cpr-num` | info text |
| Logo barva | Philips modrá `#1d4ed8` | bílá `#ffffff` | HeartSine `#1a5fa0` |
| Popisky | tmavé `#374151` | světlé `#888` | tmavé `#374151` |
| Konektory pozadí | světlé `#dde1e8` | tmavé `#0a0a0a` | průhledné bílé |
| Elektroda placed fill | `#dcfce7` zelená | `#052e16` tmavě zelená | `#dcfce7` zelená |
| Brand label | `SMART Pads II` | `CPR-D padz` | `PAD-PAK™` |
| Serial text | `M3861A · HeartStart FRx` | `REF 8000-000901 · AED Plus` | `REF 360-STR-CZ · samaritan PAD` |

### JS pravidla pro skin — co SMÍ a NESMÍ

```javascript
// ✅ SMÍ — číst activeSkin pro log a analytiku
function logEvent(msg) {
  addLog(`[${state.activeSkin.toUpperCase()}] ${msg}`);
}

// ✅ SMÍ — update CPR čítače (data, ne chování)
function doCompress() {
  state.cprPresses++;
  // ZOLL CPR čítač — čistě vizuální update, ne podmíněná logika
  document.getElementById('zoll-cpr-num').textContent = state.cprPresses;
  // ... zbytek logiky stejný pro všechny skiny
}

// ❌ NESMÍ — podmíněná logika podle skinu
function pressShock() {
  // if (state.activeSkin === 'heartsine') { ... }  ← ZAKÁZÁNO
  // Všechny skiny se chovají identicky — uživatel stiskne tlačítko
  transitionTo('SHOCK_DELIVERED');
}

// ❌ NESMÍ — manipulace DOM podle skinu v JS
// document.getElementById('btn-shock').style.display = 'none';  ← ZAKÁZÁNO
// Výhradně CSS: body.skin-heartsine #btn-shock { display: none; }
```
---

## 3. Komponenty přístroje

### 3.1 EKG displej

```css
/* Canvas se dimenzuje dynamicky podle šířky #ecg-display */
/* V JS: canvas.width = canvas.offsetWidth; canvas.height = 70; */
```

**Mřížka (renderována v JS na canvas, ne CSS):**
```javascript
// EKG grid — nakreslit jednou při resize, pak překrývat křivkou
function drawGrid(ctx, w, h) {
  ctx.strokeStyle = '#0d2010';
  ctx.lineWidth   = 0.5;
  for (let x = 0; x < w; x += 20) { ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,h); ctx.stroke(); }
  for (let y = 0; y < h; y += 10) { ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(w,y); ctx.stroke(); }
}
```

**Módy EKG:**

| Mód | Křivka | Barva |
|---|---|---|
| `idle` | rovná čára | `#111` |
| `flatline` | přímka ± šum 1 px | `#0d2a10` |
| `vf` | sinus f≈5 Hz + šum, amp ±12 px | `#eab308` |
| `vf_strong` | sinus + šum, amp ±22 px | `#eab308` |
| `analyzing` | vf_strong + blikající overlay text | `#eab308` |
| `shock` | 1 s plný šum 0–výška | `#ef4444` |
| `post_shock` | PQRST f≈70/min | `#22c55e` |
| `cpr` | kompresní artefakty + QRS | `#22c55e` |
| `pea` | malé QRS f≈40/min, bez P vlny | `#22c55e` |
| `asystola` | přímka ± šum 0.5 px | `#0d2a10` |

**PQRST precomputed waveform:**
```
Perioda 51 framů (@ 60fps = 70 BPM)
Index  0–5:   baseline
Index  6–12:  P vlna (Gaussova, peak +4px v indexu 9)
Index 13–14:  Q pokles (-3px)
Index 15–18:  R spike (peak +25px v indexu 16)
Index 19–21:  S pokles (-8px → baseline)
Index 22–28:  ST segment (baseline)
Index 29–40:  T vlna (Gaussova, peak +8px v indexu 34)
Index 41–50:  baseline
```

**Overlay text ANALÝZA (stav `analyzing`):**
```javascript
// Vykreslit přes canvas jako 2D text, blikání přes JS flag
if (state.phase === 'ANALYZING' && Math.floor(Date.now()/500) % 2 === 0) {
  ctx.fillStyle = 'rgba(234,179,8,0.15)';
  ctx.fillRect(0, 0, w, h);
  ctx.fillStyle   = '#eab308';
  ctx.font        = 'bold 13px Rajdhani, sans-serif';
  ctx.textAlign   = 'center';
  ctx.letterSpacing = '3px';
  ctx.fillText('ANALÝZA RYTMU', w/2, h/2 + 5);
}
```

### 3.2 Schéma elektrod (SVG inline) — viz §2.7

Kompletní SVG HTML pro skiny viz §2.7 (HTML je identické pro všechny skiny). Anatomické pozice elektrod viz §2.4 (Věrná vizuální replika).

### 3.3 Tlačítka — viz §2.7

Kompletní CSS pro všechny tři skiny viz §2.7. HTML struktury tlačítek viz §2.7 (HTML sekce).

### 3.4 Indikátory stavu (LED row) — viz §2.7

CSS pro LED barvy dle skinu viz §2.7. LED HTML (`#led-ready`, `#led-charging`, `#led-shock`) je identické napříč skiny.

### 3.5 Pravý panel — instrukce a KPR

Pravý panel je **výcvikový displej** — vždy viditelný, zrcadlí co přístroj dělá a co
se od zachránce očekává. Obsahuje čtyři vertikální sekce:

```
#instruction-panel
├── #scenario-bar        ← výběr scénáře (vždy viditelný nahoře)
├── #main-instruction    ← aktuální instrukce (velký text)
├── #metronome-section   ← metronom + BPM slider (viditelný v CPR)
├── #cpr-controls        ← počítadlo + tlačítka (visible v CPR_ACTIVE/BREATHS)
└── #event-log           ← timeline zásahu (vždy)
```

#### Scenario-bar — výběr scénáře nad instrukcemi

```html
<div id="scenario-bar">
  <select id="scenario-selector" onchange="selectScenario(this.value)">
    <option value="random">🎲 Náhodný</option>
    <option value="S1" selected>S1 — Klasická zástava (VF)</option>
    <option value="S2">S2 — Rezistentní VF</option>
    <option value="S3">S3 — Nedefibrilovatelný (PEA)</option>
    <option value="S4">S4 — Asystola</option>
    <option value="S5">S5 — Dítě (pediatric)</option>
    <option value="S6">S6 — Pozdní příjezd</option>
  </select>
  <button id="btn-reset-scenario" onclick="resetScenario()" title="Reset scénáře">↺</button>
  <span id="scenario-status"></span>  <!-- "Aktivní · 00:32" nebo "Připraven" -->
</div>
```

```css
#scenario-bar {
  display:         flex;
  align-items:     center;
  gap:             6px;
  padding:         6px 8px;
  background:      #0a1020;
  border-bottom:   1px solid #1e2a3a;
  border-radius:   8px 8px 0 0;
  flex-shrink:     0;
}

#scenario-selector {
  flex:            1;
  background:      #111827;
  border:          1px solid #374151;
  border-radius:   4px;
  color:           #d1d5db;
  font-size:       12px;
  font-family:     var(--font-ui);
  padding:         4px 8px;
  cursor:          pointer;
  outline:         none;
}
#scenario-selector:focus  { border-color: #4b9ef5; }
/* Selector se stane read-only (pointer-events: none) po zapnutí přístroje */
body.aed-running #scenario-selector { opacity: 0.5; pointer-events: none; cursor: default; }

#btn-reset-scenario {
  background:    #111827; border: 1px solid #374151; border-radius: 4px;
  color:         #6b7280; font-size: 14px; padding: 3px 9px; cursor: pointer;
  transition:    all 0.15s; flex-shrink: 0;
}
#btn-reset-scenario:hover { color: #f87171; border-color: #f87171; }

#scenario-status {
  color:          #4b5563; font-size: 10px; font-family: monospace;
  white-space:    nowrap; flex-shrink: 0;
}
/* Po zapnutí: zelená barva + timer */
body.aed-running #scenario-status { color: #22c55e; }
```

#### Main-instruction — aktuální instrukce

```css
#main-instruction {
  background:      #0a1628;
  border:          1px solid #1e3a5f;
  border-radius:   0 0 8px 8px;   /* navazuje na scenario-bar */
  padding:         14px 14px;
  min-height:      80px;
  display:         flex;
  align-items:     center;
  justify-content: center;
  text-align:      center;
  font-family:     var(--font-ui);
  font-size:       18px;
  font-weight:     700;
  color:           #f1f5f9;
  line-height:     1.3;
  text-transform:  uppercase;
  letter-spacing:  0.5px;
  flex-shrink:     0;
}
#main-instruction.warn  { color: #fde047; border-color: #854d0e; background: #1a1100; }
#main-instruction.alert { color: #fca5a5; border-color: #7f1d1d; background: #1a0505; }
#main-instruction.ok    { color: #86efac; border-color: #14532d; background: #051a0a; }
```

#### Metronom — BPM, vizuální pulz, slider

Metronom je **vždy v DOM**, viditelný jen v KPR fázích (`CPR_ACTIVE`, `CPR_BREATHS`).

```html
<div id="metronome-section">
  <div id="metro-top">
    <div id="metro-circle"></div>        <!-- pulzující kruh -->
    <div id="metro-bpm-display">110 BPM</div>
    <div id="metro-bars">               <!-- 5 animovaných sloupků -->
      <div class="mbar"></div><div class="mbar"></div><div class="mbar"></div>
      <div class="mbar"></div><div class="mbar"></div>
    </div>
  </div>
  <div id="metro-slider-row">
    <span class="metro-label">80</span>
    <input type="range" id="metro-slider"
           min="80" max="140" step="5" value="110"
           oninput="MetronomeEngine.setBpm(+this.value)">
    <span class="metro-label">140</span>
    <span id="metro-bpm-value">110</span>
    <span class="metro-label">BPM</span>
  </div>
</div>
```

```css
#metronome-section {
  display:        none;       /* skrytý mimo CPR */
  flex-direction: column;
  gap:            6px;
  padding:        8px 10px;
  background:     #080e18;
  border:         1px solid #1e2a3a;
  border-radius:  8px;
  flex-shrink:    0;
}
#metronome-section.visible { display: flex; }

#metro-top {
  display:     flex;
  align-items: center;
  gap:         10px;
}

#metro-circle {
  width:         28px; height: 28px;
  border-radius: 50%;
  background:    #1e3a5f;
  border:        2px solid #2563c7;
  flex-shrink:   0;
  /* JS nastaví: animation: metro-pulse (60/bpm)s infinite */
}
@keyframes metro-pulse {
  0%, 100% { transform: scale(1);   background: #1e3a5f; }
  10%       { transform: scale(1.4); background: #3b82f6; box-shadow: 0 0 12px #3b82f6; }
}

#metro-bpm-display {
  font-size:      16px; font-weight: 900;
  color:          #60a5fa; font-family: monospace;
  min-width:      80px;
}

.mbar {
  width:            5px; border-radius: 3px;
  background:       #1e3a5f;
  transition:       height 0.08s, background 0.08s;
  /* JS animuje výšky v rytmu beatu: [6,10,18,10,6]px → ×1.8 na aktivní */
}

#metro-slider-row {
  display:     flex; align-items: center; gap: 6px;
}
#metro-slider { flex: 1; }
.metro-label  { color: #4b5563; font-size: 10px; flex-shrink: 0; }
#metro-bpm-value { color: #60a5fa; font-size: 12px; font-weight: 700;
  font-family: monospace; min-width: 26px; text-align: right; }
/* JS: při oninput aktualizovat #metro-bpm-value a #metro-bpm-display */
```

#### KPR počítadlo a tlačítka

```html
<div id="cpr-controls">

  <!-- Řádek 1: počítadlo + kolo + celkový čas -->
  <div id="cpr-header">
    <div id="cpr-counter">
      <span id="cpr-num">0</span><span id="cpr-denom">/30</span>
    </div>
    <div id="cpr-round-info">
      <span id="cpr-round-label">Kolo</span>
      <span id="cpr-round-val">1/4</span>
    </div>
    <div id="cpr-timer">
      <span id="cpr-elapsed">00:00</span>
    </div>
  </div>

  <!-- Řádek 2: progress bar 0–30 -->
  <div id="cpr-progress">
    <div id="cpr-progress-fill"></div>
  </div>

  <!-- Řádek 3: hlavní akční tlačítko -->
  <button id="btn-compress"
          onclick="doCompress()"
          ontouchend="doCompress(); event.preventDefault()">
    ↓ STLAČENÍ HRUDNÍKU ↓
  </button>

  <!-- Řádek 4: tlačítko vdechy (jen v CPR_BREATHS) -->
  <button id="btn-breaths"
          onclick="doBreaths()"
          ontouchend="doBreaths(); event.preventDefault()">
    ✓ DVA VDECHY PROVEDENY
  </button>

</div>
```

```css
#cpr-controls {
  display:        none;
  flex-direction: column;
  gap:            8px;
  padding:        10px 12px;
  background:     #0a0800;
  border:         2px solid #854d0e;
  border-radius:  8px;
  flex-shrink:    0;
}
#cpr-controls.visible { display: flex; }

/* Řádek 1 — tři sloupce */
#cpr-header {
  display:         flex;
  align-items:     center;
  justify-content: space-between;
}

#cpr-counter { display: flex; align-items: baseline; gap: 2px; }
#cpr-num     { font-size: 40px; font-weight: 900; color: #fbbf24;
               font-family: monospace; line-height: 1; }
#cpr-denom   { font-size: 16px; color: #78716c; font-family: monospace; }

#cpr-round-info { text-align: center; }
#cpr-round-label { color: #6b7280; font-size: 9px; letter-spacing: 1px;
                   display: block; font-family: var(--font-device); }
#cpr-round-val   { color: #fbbf24; font-size: 16px; font-weight: 700;
                   font-family: monospace; }

#cpr-timer { text-align: right; }
#cpr-elapsed { color: #4b5563; font-size: 13px; font-family: monospace; font-weight: 700; }

/* Progress bar */
#cpr-progress      { height: 5px; background: #1a1200; border-radius: 3px; overflow: hidden; }
#cpr-progress-fill { height: 100%; background: #eab308; border-radius: 3px;
                     width: 0%; transition: width 0.08s linear; }

/* Komprese — dominantní, touch-first */
#btn-compress {
  width:          100%; min-height: 72px;
  background:     #1a0d00; border: 2px solid #c2410c; border-radius: 10px;
  color:          #fed7aa; font-family: var(--font-device);
  font-size:      18px; font-weight: 700; letter-spacing: 2px;
  text-transform: uppercase; cursor: pointer;
  touch-action:   manipulation; user-select: none;
  transition:     background 0.1s, transform 0.08s;
  display:        none;
}
#btn-compress.visible { display: block; }
#btn-compress:active  { background: #3a1a00; transform: scale(0.97); }

/* Vdechy */
#btn-breaths {
  width:          100%; min-height: 52px;
  background:     #071a0a; border: 2px solid #166534; border-radius: 8px;
  color:          #86efac; font-family: var(--font-device);
  font-size:      14px; font-weight: 700; letter-spacing: 1.5px;
  text-transform: uppercase; cursor: pointer;
  touch-action:   manipulation;
  display:        none;
}
#btn-breaths.visible { display: block; }
```

**JS — KPR update (volat z `doCompress()` a `transitionTo()`):**
```javascript
function updateCprDisplay() {
  document.getElementById('cpr-num').textContent    = state.cprPresses;
  document.getElementById('cpr-progress-fill').style.width =
    Math.min(state.cprPresses / 30 * 100, 100) + '%';
  document.getElementById('cpr-round-val').textContent =
    (state.cprCycles + 1) + '/4';
  // ZOLL čítač — vždy, ne podmíněně
  document.getElementById('zoll-cpr-num').textContent = state.cprPresses;
}

function updateCprTimer() {
  if (!state.cprStart) return;
  const s = Math.floor((Date.now() - state.cprStart) / 1000);
  const mm = String(Math.floor(s / 60)).padStart(2, '0');
  const ss = String(s % 60).padStart(2, '0');
  document.getElementById('cpr-elapsed').textContent = mm + ':' + ss;
}
// Volat setInterval(updateCprTimer, 500) při vstupu do CPR_ACTIVE
```

#### Event log

```html
<div id="event-log">
  <div class="log-title" data-i18n="log_title">Průběh zásahu</div>
  <div id="log-entries">
    <!-- JS přidává řádky: addLog(key, params) -->
  </div>
</div>
```

```css
#event-log {
  flex:           1;            /* roztáhne se na zbývající výšku panelu */
  overflow-y:     auto;
  min-height:     60px;         /* minimálně viditelný i při malém viewportu */
  background:     #050810;
  border:         1px solid #111827;
  border-radius:  8px;
  padding:        6px 8px;
}
.log-title {
  color:          #374151; font-size: 9px; letter-spacing: 1.5px;
  text-transform: uppercase; font-family: var(--font-device);
  margin-bottom:  4px; border-bottom: 1px solid #111827; padding-bottom: 3px;
}
.log-entry {
  font-size:   11px; font-family: monospace;
  padding:     2px 0; border-bottom: 1px solid #0a0f1a;
  line-height: 1.4;
}
.log-entry.info    { color: #22c55e; }
.log-entry.warn    { color: #eab308; }
.log-entry.alert   { color: #ef4444; }
.log-entry.muted   { color: #374151; }
.log-entry:last-child { color: #60a5fa; border-bottom: none; }
```


---

## 4. Internacionalizace (i18n)

### 4.1 Architektura — Language Pack objekt

Veškeré texty viditelné uživateli (hlášky, UI popisky, logy, výsledky) jsou uloženy v jednom JS objektu `LANG`. Implementátor **nikdy nepoužívá hardcoded string** přímo v logice — vždy volá `t('sekce', 'klic')`.

```javascript
// ═══════════════════════════════════════════════════════════════
//  LANGUAGE PACKS  –  EDITOVATELNÁ SEKCE
//
//  Jak editovat hlášky:
//    Najdi klíč v sekci voice:{} příslušného jazyka a změň `text`.
//    Priority neměň pokud nevíš co děláš.
//
//  Jak přidat jazyk:
//    1. Zkopíruj celý blok  cs: { ui:{...}, voice:{...}, log:{...} }
//    2. Přejmenuj klíč na ISO kód (de, sk, pl, fr …)
//    3. Přelož pouze hodnoty — klíče (start, pad1_ok …) neměň
//    4. Přidej tlačítko:  <button onclick="setLang('de')">DE</button>
//    5. Nastav ui.voice_lang na správný BCP-47 tag (de-DE, sk-SK …)
// ═══════════════════════════════════════════════════════════════

const LANG = {

  // ─────────────────────────────────────────
  //  ČEŠTINA
  // ─────────────────────────────────────────
  cs: {

    // Popisky UI prvků (ne hlasové)
    ui: {
      // ── Přístroj ──────────────────────────────────────────────────
      training_banner:      'TRENAŽÉR · POUZE PRO VÝCVIK · NEPOUŽÍVAT NA PACIENTECH',
      btn_on:               'ZAP / VYP',
      btn_on_label:         'Zapnout',
      btn_shock:            'VÝBOJ',
      btn_shock_label:      'Podat výboj',
      btn_info_label:       'Nápověda / KPR',
      led_ready:            'READY',
      led_charging:         'NABÍJÍM',
      led_shock:            'VÝBOJ DOPORUČEN',
      pad1_label:           'ELEKTRODA 1',
      pad2_label:           'ELEKTRODA 2',
      pad1_hint:            'Pravá klíční kost',
      pad2_hint:            'Levý bok – axila',
      pediatric_label:      'Dětský klíč',

      // ── Scénáře ───────────────────────────────────────────────────
      scenario_label:       'Scénář',
      scenario_ready:       'Připraven',
      scenario_running:     'Aktivní',
      scenario_reset_title: 'Reset scénáře',
      scenario_random:      '🎲 Náhodný',
      scenario_s1:          'S1 — Klasická zástava (VF)',
      scenario_s2:          'S2 — Rezistentní VF',
      scenario_s3:          'S3 — Nedefibrilovatelný (PEA)',
      scenario_s4:          'S4 — Asystola',
      scenario_s5:          'S5 — Dítě (pediatric)',
      scenario_s6:          'S6 — Pozdní příjezd',

      // ── KPR panel ─────────────────────────────────────────────────
      cpr_round_label:      'Kolo',
      btn_compress:         '↓ STLAČENÍ HRUDNÍKU ↓',
      btn_breaths:          '✓ DVA VDECHY PROVEDENY',

      // ── Metronom ──────────────────────────────────────────────────
      metro_bpm:            'BPM',

      // ── Výsledky ──────────────────────────────────────────────────
      result_title:         'VÝSLEDKY TRÉNINKU',
      result_time:          'Celkový čas',
      result_shocks:        'Výboje podány',
      result_cpr:           'KPR cykly',
      result_avg_rate:      'Průměrná frekvence',
      result_longest_pause: 'Nejdelší přerušení KPR',
      btn_restart:          'Začít znovu',
      btn_print:            'Vytisknout',

      // ── Log ───────────────────────────────────────────────────────
      log_title:            'Průběh zásahu',

      // ── Web UI ────────────────────────────────────────────────────
      site_title:           'AED Trenažér · Simulator',
      donate_btn:           '♥ Podpořit',
      donate_title:         'Podpořte projekt',
      donate_desc:          'Tento trenažér vznikl jako open-source nástroj pro výcvik první pomoci. Pokud vám pomohl nebo ho používáte ve výuce, zvažte symbolický příspěvek na jeho další rozvoj.',
      donate_link_text:     'Otevřít Revolut →',
      donate_note:          'Příspěvek není podmínkou použití. Trenažér je a zůstane zdarma.',
      donate_close:         'Zavřít',

      // ── Varování ──────────────────────────────────────────────────
      no_voice_warning:     'Český hlas není dostupný. Nainstalujte jej v Nastavení → Usnadnění → Hlasový výstup.',
      voice_lang:           'cs-CZ',
    },

    // Hlasové hlášky
    // priority: 'high'   = přeruší vše co právě hraje
    //           'normal' = přidá do fronty
    //           'low'    = přidá jen pokud je fronta prázdná
    voice: {
      start:           { text: 'Přístroj zapnut. Přiložte elektrody na holou kůži pacienta.',                    priority: 'high'   },
      pad1_prompt:     { text: 'Přiložte elektrodu číslo jedna pod pravou klíční kost.',                         priority: 'normal' },
      pad1_ok:         { text: 'Elektroda jedna přiložena.',                                                      priority: 'normal' },
      pad2_prompt:     { text: 'Přiložte elektrodu číslo dvě na levý bok pacienta, pod podpaží.',                priority: 'normal' },
      pad2_ok:         { text: 'Elektroda dvě přiložena.',                                                        priority: 'normal' },
      analyzing:       { text: 'Nestýkejte se pacienta. Analyzuji srdeční rytmus.',                              priority: 'high'   },
      analyze_wait:    { text: 'Nedotýkejte se pacienta.',                                                        priority: 'low'    },
      shock_advised:   { text: 'Výboj doporučen. Nabíjím. Všichni pryč od pacienta!',                            priority: 'high'   },
      shock_ready:     { text: 'Přístroj nabit. Stiskněte oranžové tlačítko výboje.',                            priority: 'normal' },
      shock_clear:     { text: 'Všichni pryč!',                                                                   priority: 'high'   },
      shock_delivered: { text: 'Výboj podán. Okamžitě zahajte KPR.',                                             priority: 'high'   },
      no_shock:        { text: 'Výboj nedoporučen. Okamžitě zahajte KPR – třicet stlačení, dva vdechy.',        priority: 'high'   },
      cpr_start:       { text: 'Zahajte KPR. Stlačujte hrudník do hloubky pět až šest centimetrů.',             priority: 'normal' },
      cpr_depth:       { text: 'Stlačujte pevněji – minimálně pět centimetrů.',                                  priority: 'normal' },
      cpr_rate:        { text: 'Udržujte frekvenci sto až sto dvacet stlačení za minutu.',                       priority: 'normal' },
      cpr_15:          { text: 'Patnáct stlačení – pokračujte!',                                                  priority: 'low'    },
      cpr_30:          { text: 'Třicet stlačení. Proveďte dva záchranné vdechy.',                                priority: 'high'   },
      breaths_done:    { text: 'Pokračujte v KPR.',                                                               priority: 'normal' },
      reanalyze:       { text: 'Analyzuji srdeční rytmus. Nestýkejte se pacienta.',                              priority: 'high'   },
      rosc:            { text: 'Spontánní oběh obnoven. Zkontrolujte dýchání. Uložte do stabilizované polohy.', priority: 'high'   },
      continue_cpr:    { text: 'Pokračujte v KPR. Záchranná služba byla přivolána.',                             priority: 'normal' },
      shock2:          { text: 'Druhý výboj doporučen. Všichni pryč od pacienta!',                               priority: 'high'   },
      shock3:          { text: 'Třetí výboj doporučen. Všichni pryč od pacienta!',                               priority: 'high'   },
      low_battery:     { text: 'Baterie je slabá.',                                                               priority: 'low'    },
      pediatric_on:    { text: 'Dětský klíč vložen. Energie snížena na padesát joulů.',                          priority: 'high'   },
      off:             { text: 'Přístroj vypnut.',                                                                priority: 'high'   },
      end_session:     { text: 'Trénink ukončen. Prohlédněte si výsledky.',                                      priority: 'high'   },
    },

    // Krátké texty do event logu
    // %n = číslo (výboj, kolo), %j = jouly
    log: {
      powered_on:    'Přístroj zapnut',
      pad1_placed:   'Elektroda 1 přiložena',
      pad2_placed:   'Elektroda 2 přiložena',
      analyzing:     'Analýza zahájena',
      vf_detected:   'VF detekována → výboj doporučen',
      pea_detected:  'PEA detekována → KPR',
      asy_detected:  'Asystola → KPR',
      charging:      'Nabíjím…',
      shock_label:   'Výboj #%n podán (%j J)',
      cpr_start:     'KPR zahájena',
      cpr_cycle:     'KPR kolo %n/4',
      reanalyze:     'Re-analýza',
      rosc:          'ROSC – oběh obnoven',
      powered_off:   'Přístroj vypnut',
    },
  },

  // ─────────────────────────────────────────
  //  ANGLIČTINA
  // ─────────────────────────────────────────
  en: {

    ui: {
      // ── Device ────────────────────────────────────────────────────
      training_banner:      'TRAINER · FOR TRAINING USE ONLY · DO NOT USE ON PATIENTS',
      btn_on:               'ON / OFF',
      btn_on_label:         'Power on',
      btn_shock:            'SHOCK',
      btn_shock_label:      'Deliver shock',
      btn_info_label:       'Help / CPR coaching',
      led_ready:            'READY',
      led_charging:         'CHARGING',
      led_shock:            'SHOCK ADVISED',
      pad1_label:           'PAD 1',
      pad2_label:           'PAD 2',
      pad1_hint:            'Right upper chest',
      pad2_hint:            'Left side – apex',
      pediatric_label:      'Child key',

      // ── Scenarios ─────────────────────────────────────────────────
      scenario_label:       'Scenario',
      scenario_ready:       'Ready',
      scenario_running:     'Active',
      scenario_reset_title: 'Reset scenario',
      scenario_random:      '🎲 Random',
      scenario_s1:          'S1 — Classic arrest (VF)',
      scenario_s2:          'S2 — Refractory VF',
      scenario_s3:          'S3 — Non-shockable (PEA)',
      scenario_s4:          'S4 — Asystole',
      scenario_s5:          'S5 — Child (pediatric)',
      scenario_s6:          'S6 — Delayed response',

      // ── CPR panel ─────────────────────────────────────────────────
      cpr_round_label:      'Round',
      btn_compress:         '↓ CHEST COMPRESSION ↓',
      btn_breaths:          '✓ TWO RESCUE BREATHS DONE',

      // ── Metronome ─────────────────────────────────────────────────
      metro_bpm:            'BPM',

      // ── Results ───────────────────────────────────────────────────
      result_title:         'TRAINING RESULTS',
      result_time:          'Total time',
      result_shocks:        'Shocks delivered',
      result_cpr:           'CPR cycles',
      result_avg_rate:      'Average rate',
      result_longest_pause: 'Longest CPR pause',
      btn_restart:          'Start again',
      btn_print:            'Print',

      // ── Log ───────────────────────────────────────────────────────
      log_title:            'Incident timeline',

      // ── Web UI ────────────────────────────────────────────────────
      site_title:           'AED Trainer · Simulator',
      donate_btn:           '♥ Support',
      donate_title:         'Support the project',
      donate_desc:          'This trainer was created as an open-source tool for first aid training. If it helped you or you use it in teaching, consider a small contribution towards its further development.',
      donate_link_text:     'Open Revolut →',
      donate_note:          'A contribution is not a condition of use. The trainer is and will remain free.',
      donate_close:         'Close',

      // ── Warnings ──────────────────────────────────────────────────
      no_voice_warning:     'English voice not found. Install it in Settings → Accessibility → Speech.',
      voice_lang:           'en-US',
    },

    voice: {
      start:           { text: 'Unit on. Attach pads to the patient\'s bare skin.',                               priority: 'high'   },
      pad1_prompt:     { text: 'Place pad one below the right collarbone.',                                       priority: 'normal' },
      pad1_ok:         { text: 'Pad one attached.',                                                               priority: 'normal' },
      pad2_prompt:     { text: 'Place pad two on the left side of the chest, below the armpit.',                  priority: 'normal' },
      pad2_ok:         { text: 'Pad two attached.',                                                               priority: 'normal' },
      analyzing:       { text: 'Do not touch the patient. Analyzing heart rhythm.',                               priority: 'high'   },
      analyze_wait:    { text: 'Do not touch the patient.',                                                        priority: 'low'    },
      shock_advised:   { text: 'Shock advised. Charging. Stand clear of the patient!',                            priority: 'high'   },
      shock_ready:     { text: 'Unit charged. Press the orange shock button.',                                    priority: 'normal' },
      shock_clear:     { text: 'Stand clear!',                                                                    priority: 'high'   },
      shock_delivered: { text: 'Shock delivered. Start CPR immediately.',                                         priority: 'high'   },
      no_shock:        { text: 'No shock advised. Start CPR immediately – thirty compressions, two breaths.',    priority: 'high'   },
      cpr_start:       { text: 'Begin CPR. Push down five to six centimetres on the chest.',                     priority: 'normal' },
      cpr_depth:       { text: 'Push harder – at least five centimetres.',                                        priority: 'normal' },
      cpr_rate:        { text: 'Maintain a rate of one hundred to one hundred and twenty per minute.',            priority: 'normal' },
      cpr_15:          { text: 'Fifteen compressions – keep going!',                                              priority: 'low'    },
      cpr_30:          { text: 'Thirty compressions. Give two rescue breaths.',                                   priority: 'high'   },
      breaths_done:    { text: 'Continue CPR.',                                                                   priority: 'normal' },
      reanalyze:       { text: 'Analyzing heart rhythm. Do not touch the patient.',                               priority: 'high'   },
      rosc:            { text: 'Return of spontaneous circulation. Check breathing. Place in recovery position.', priority: 'high'   },
      continue_cpr:    { text: 'Continue CPR. Emergency services have been called.',                              priority: 'normal' },
      shock2:          { text: 'Second shock advised. Stand clear of the patient!',                               priority: 'high'   },
      shock3:          { text: 'Third shock advised. Stand clear of the patient!',                                priority: 'high'   },
      low_battery:     { text: 'Battery is low.',                                                                 priority: 'low'    },
      pediatric_on:    { text: 'Child key inserted. Energy reduced to fifty joules.',                             priority: 'high'   },
      off:             { text: 'Unit off.',                                                                       priority: 'high'   },
      end_session:     { text: 'Training complete. Review your results.',                                         priority: 'high'   },
    },

    log: {
      powered_on:    'Unit powered on',
      pad1_placed:   'Pad 1 placed',
      pad2_placed:   'Pad 2 placed',
      analyzing:     'Analysis started',
      vf_detected:   'VF detected → shock advised',
      pea_detected:  'PEA detected → CPR',
      asy_detected:  'Asystole → CPR',
      charging:      'Charging…',
      shock_label:   'Shock #%n delivered (%j J)',
      cpr_start:     'CPR started',
      cpr_cycle:     'CPR round %n/4',
      reanalyze:     'Re-analysis',
      rosc:          'ROSC – circulation restored',
      powered_off:   'Unit powered off',
    },
  },

}; // ═══ konec LANG objektu ═══════════════════════════════════

// Aktivní jazyk
let currentLang = 'cs';

// Překlad: t('voice', 'start') nebo t('ui', 'btn_on')
function t(section, key) {
  return LANG[currentLang]?.[section]?.[key]
      ?? LANG['cs']?.[section]?.[key]   // fallback na češtinu
      ?? `[${key}]`;                     // absolutní fallback
}

// Přepnutí jazyka za běhu (state machine a EKG pokračují)
function setLang(lang) {
  if (!LANG[lang]) return;
  currentLang = lang;
  SpeechEngine.reloadVoice();  // načíst hlas pro nový jazyk
  renderUI();                   // překreslí všechny data-i18n elementy
}
```

### 4.2 Pravidla pro přidání nového jazyka

1. Zkopíruj celý blok `cs: { … }` v objektu `LANG`
2. Přejmenuj klíč na ISO kód jazyka (např. `de`, `sk`, `pl`, `fr`)
3. Přelož pouze hodnoty (`text:`, `ui.*`) — **klíče nikdy neměň**
4. Přidej tlačítko do tréninkového pruhu: `<button onclick="setLang('de')">DE</button>`
5. Nastav `ui.voice_lang` na správný BCP-47 tag (např. `'de-DE'`, `'sk-SK'`)

### 4.3 Strategie hlasu — tříúrovňový přístup

Kvalita hlasu je klíčová pro realismus trenažéru. Implementace musí podporovat
**tři úrovně** podle dostupnosti, s automatickým fallbackem:

```
Úroveň 1 (NEJLEPŠÍ):  Předgenerované MP3 soubory — ElevenLabs / Azure / Google
Úroveň 2 (STŘEDNÍ):   Web Speech API s nejlepším dostupným cs-CZ hlasem
Úroveň 3 (ZÁLOHA):    Web Speech API s anglickým hlasem + varování
```

SpeechEngine detekuje dostupnost MP3 souborů při inicializaci a automaticky
přepne na nejlepší dostupnou úroveň. Uživatel vidí indikátor kvality hlasu.

---

### 4.4 Úroveň 1 — Předgenerované MP3 (doporučeno pro produkci)

**Proč:** ElevenLabs `eleven_multilingual_v2` nebo Microsoft Azure Neural TTS
produkují hlas nerozeznatelný od skutečného záchranáře. Web Speech API systémový
hlas zní roboticky — v záchranné situaci to podkopává důvěru v přístroj.

**Workflow pro přípravu MP3:**
1. Vygenerovat všech 24 hlášek z `LANG.cs.voice` pomocí AI TTS
2. Uložit jako `audio/cs/start.mp3`, `audio/cs/analyzing.mp3` atd.
3. Pro angličtinu: `audio/en/start.mp3` atd.
4. Celkem ~24 souborů × 2 jazyky = 48 MP3, průměrná délka 3–8 s, ~2–5 MB total

**Doporučené služby pro generování (jednorázově, zdarma nebo levně):**

| Služba | Kvalita CZ | Free tier | Poznámka |
|---|---|---|---|
| **ElevenLabs** | ★★★★★ | 10 000 znaků/měsíc | `eleven_multilingual_v2`, hlas `Matej` (CZ muž) nebo `Karolína` (CZ žena) |
| **Microsoft Azure TTS** | ★★★★☆ | 500 000 znaků/měsíc | `cs-CZ-AntoninNeural` (muž) nebo `cs-CZ-VlastaNeural` (žena) |
| **Google Cloud TTS** | ★★★☆☆ | 1 M znaků/měsíc | `cs-CZ-Wavenet-A` |
| **OpenAI TTS** | ★★★★☆ | Placené | `tts-1-hd`, `onyx` nebo `nova` — nejlepší angličtina |

**Celkový počet znaků pro všech 24 CZ hlášek:** ~1 200 znaků → vejde se do free tieru.

**Struktura souborů:**
```
aed-trenazor.html
audio/
  cs/
    start.mp3
    pad1_prompt.mp3
    pad1_ok.mp3
    pad2_prompt.mp3
    pad2_ok.mp3
    analyzing.mp3
    analyze_wait.mp3
    shock_advised.mp3
    shock_ready.mp3
    shock_clear.mp3
    shock_delivered.mp3
    no_shock.mp3
    cpr_start.mp3
    cpr_depth.mp3
    cpr_rate.mp3
    cpr_15.mp3
    cpr_30.mp3
    breaths_done.mp3
    reanalyze.mp3
    rosc.mp3
    continue_cpr.mp3
    shock2.mp3
    shock3.mp3
    off.mp3
  en/
    [stejná struktura v angličtině]
```

**Implementace AudioPlayer pro MP3:**
```javascript
const AudioPlayer = {
  cache: {},          // přednačtené Audio objekty
  current: null,      // právě přehrávané audio

  // Přednačíst všechny MP3 na pozadí — po 3 souborech najednou
  async preload(lang) {
    const keys = Object.keys(LANG[lang]?.voice ?? {});
    // Chunked loading — nezahltit síť
    for (let i = 0; i < keys.length; i += 3) {
      const chunk = keys.slice(i, i + 3);
      await Promise.allSettled(chunk.map(key => this._loadOne(lang, key)));
    }
  },

  async _loadOne(lang, key) {
    return new Promise((res) => {
      const audio = new Audio(`audio/${lang}/${key}.mp3`);
      audio.preload = 'auto';
      audio.oncanplaythrough = () => {
        this.cache[`${lang}:${key}`] = audio;
        res(true);
      };
      audio.onerror = () => res(false);   // tiše ignorovat chybějící soubory
      audio.load();
    });
  },

  play(lang, key, priority = 'normal') {
    const cacheKey = `${lang}:${key}`;
    const audio = this.cache[cacheKey];
    if (!audio) return false;           // signál: použij TTS fallback

    // 'low' priority: nehrát pokud právě něco hraje
    if (priority === 'low' && this.current && !this.current.paused) {
      return true;   // říkáme "handled" — úmyslně přeskočeno
    }

    // 'high' priority: zastavit vše aktuální
    if (priority === 'high' && this.current) {
      this.current.pause();
      this.current.currentTime = 0;
    }

    audio.currentTime = 0;
    this.current = audio;
    audio.play().catch(() => {
      // Autoplay policy — tiše ignorovat, uživatel musí nejdřív kliknout
      // (v praxi se nestane pokud AudioEngine.init() byl volán po kliku)
    });
    return true;
  },
};
```

---

### 4.5 SpeechEngine — orchestrátor s fallbackem

```javascript
const SpeechEngine = {
  mode: 'detecting',   // 'mp3' | 'tts' | 'silent'
  synth: window.speechSynthesis,
  voice: null,
  ttsQueue: [],
  ttsSpeaking: false,

  init() {
    // TTS inicializovat okamžitě (nevyžaduje user gesture)
    this._initTTS();

    // Chrome TTS bug workaround — zaseknutí synthesis po ~15s
    setInterval(() => {
      if (this.synth.speaking) { this.synth.pause(); this.synth.resume(); }
    }, 10000);

    // MP3 detekce se spustí až po prvním kliku (AudioContext policy)
    // Volat SpeechEngine.detectMp3() z AudioEngine.init() handleru
  },

  async detectMp3() {
    // Tuto metodu volat z: document.addEventListener('click', handler, {once:true})
    // Až POTÉ co AudioContext existuje — Audio() funguje i bez AC, ale play() ne
    try {
      const test = new Audio(`audio/${currentLang}/start.mp3`);
      await new Promise((res, rej) => {
        test.oncanplaythrough = res;
        test.onerror = rej;
        test.load();
        setTimeout(rej, 3000);   // 3s timeout — pomalejší připojení
      });
      this.mode = 'mp3';
      this._showModeIndicator('mp3');
      AudioPlayer.preload(currentLang);   // přednačíst vše na pozadí
    } catch {
      this.mode = this.voice ? 'tts' : 'silent';
      this._showModeIndicator(this.mode);
    }
  },

  _initTTS() {
    const load = () => {
      const voices = this.synth.getVoices();
      const lang   = t('ui', 'voice_lang');
      this.voice =
        voices.find(v => v.lang === lang)
        ?? voices.find(v => v.lang.startsWith(lang.split('-')[0]))
        ?? voices.find(v => v.lang.startsWith('en'))
        ?? voices[0];
      const hasNative = voices.some(v => v.lang === lang);
      document.getElementById('voice-warning').hidden = hasNative;
      if (!hasNative) this.mode = 'tts-nonnative';
    };
    if (this.synth.getVoices().length) load();
    this.synth.onvoiceschanged = load;
  },

  say(key, overridePriority) {
    const entry = t('voice', key);
    if (!entry || !entry.text) return;
    const priority = overridePriority ?? entry.priority ?? 'normal';

    if (this.mode === 'mp3') {
      const played = AudioPlayer.play(currentLang, key, priority);
      if (played) return;
      // MP3 pro tento klíč chybí — fallback na TTS
    }

    // TTS fallback
    if (priority === 'high')  this.synth.cancel();
    else if (priority === 'low' && this.synth.speaking) return;

    const u   = new SpeechSynthesisUtterance(entry.text);
    u.voice   = this.voice;
    u.lang    = t('ui', 'voice_lang');
    // TTS parametry pro maximální srozumitelnost
    u.rate    = 0.88;   // mírně pomalejší = jasnější výslovnost
    u.pitch   = 0.82;   // nižší tón = autoritativní, méně robotický
    u.volume  = 1.0;
    this.synth.speak(u);
  },

  reloadVoice() {
    // Vždy reinicializovat TTS pro nový jazyk (hlas se liší)
    this._initTTS();
    // Pokud jsme v MP3 módu, přednačíst soubory pro nový jazyk
    if (this.mode === 'mp3') {
      AudioPlayer.preload(currentLang);
    }
    // Aktualizovat indikátor
    this._showModeIndicator(this.mode);
  },

  // Indikátor kvality hlasu v site-baru
  // Texty záměrně hardcoded — indikátor se zobrazuje i před načtením LANG
  _showModeIndicator(mode) {
    const el = document.getElementById('voice-quality');
    if (!el) return;
    const isCz = currentLang === 'cs';
    const labels = {
      'mp3':           { text: '🔊 HD',          color: '#22c55e', title: isCz ? 'Kvalitní AI hlas (MP3)'          : 'High-quality AI voice (MP3)'     },
      'tts':           { text: '🔈 TTS',          color: '#eab308', title: isCz ? 'Systémový hlas'                  : 'System voice'                     },
      'tts-nonnative': { text: '⚠️ EN',           color: '#f97316', title: isCz ? 'Český hlas nedostupný, hraje EN' : 'Native voice unavailable'         },
      'silent':        { text: '🔇',              color: '#6b7280', title: isCz ? 'Hlas nedostupný'                 : 'Voice unavailable'                 },
      'detecting':     { text: '⟳',              color: '#4b5563', title: isCz ? 'Zjišťuji dostupnost hlasu…'      : 'Detecting voice…'                 },
    };
    const l = labels[mode] ?? labels['detecting'];
    el.textContent = l.text;
    el.style.color  = l.color;
    el.title        = l.title;
  },
};
```

**Indikátor kvality hlasu `#voice-quality`** je součástí `.site-controls` v `#site-bar`
(viz §2.2 pro kompletní HTML site-baru). Zobrazuje aktuální mód hlasu:
`🔊 HD` = MP3, `🔈 TTS` = systémový hlas, `⚠️ EN` = fallback angličtina, `🔇` = bez hlasu.

---

### 4.6 Jak vygenerovat MP3 pomocí ElevenLabs (jednorázový postup)

**Cíl:** 24 MP3 souborů v češtině, celkem ~2 MB, jednou → offline navždy.

```
1. Jdi na elevenlabs.io → přihlásit se (free účet)
2. Speech Synthesis → Text to Speech
3. Vybrat hlas:
     CZ muž:  "Matej"  (přirozený, klidný — ideální pro záchranáře)
     CZ žena: "Karolína" nebo vlastní
4. Model: eleven_multilingual_v2
5. Settings:
     Stability:  0.55  (méně stability = přirozenější intonace)
     Clarity:    0.80  (vyšší = jasnější výslovnost)
     Style:      0.20  (trochu stylu pro emoční zabarvení)
6. Pro každou hláška z LANG.cs.voice:
     - vložit text
     - Generate
     - Download jako MP3
     - uložit do audio/cs/{key}.mp3
7. Opakovat pro angličtinu (hlas "Daniel" nebo "Rachel")
```

**Celková cena na free tieru:** 0 Kč (24 hlášek × ~50 znaků průměr = ~1 200 znaků, free limit je 10 000).

**SSML tipy pro přirozenější výslovnost (pokud služba podporuje):**
```xml
<!-- Pauza pro důraz -->
<speak>Výboj doporučen. <break time="300ms"/> Nabíjím.
<break time="200ms"/> Všichni pryč od pacienta!</speak>

<!-- Důraz na klíčové slovo -->
<speak>Nestýkejte se <emphasis level="strong">pacienta</emphasis>.</speak>

<!-- Pomalejší tempo pro kritické instrukce -->
<speak><prosody rate="slow">Třicet stlačení.</prosody>
Proveďte dva záchranné vdechy.</speak>
```

---

### 4.7 Pravidla hlasové fronty (nezměněno)

```
priority: 'high'   → AudioPlayer.stop() + okamžité přehrání
priority: 'normal' → přidá do fronty (queue)
priority: 'low'    → přidá jen pokud je ticho
```

---

## 5. Stavový automat (State Machine)

```
IDLE
  └─ [ON klik] ──────────────────→ BOOTING (1.5 s animace + startup zvuk)
                                         │
                                         ▼
                                   PAD_PROMPT
                               (čeká na klik el.1 v SVG)
                                         │ [klik el.1]
                                         ▼
                                   PAD_PROMPT_2
                               (čeká na klik el.2 v SVG)
                                         │ [klik el.2]
                                         ▼
                                   ANALYZING (4–5 s)
                                    │              │
                        [VF/VT]    │              │  [PEA / ASY]
                                    ▼              ▼
                            SHOCK_CHARGING     CPR_PROMPT (2 s)
                            (progress 3 s)         │
                                    │              ▼
                                    ▼         CPR_ACTIVE ◄──────────┐
                              SHOCK_READY     (30 stlačení)         │
                                    │              │                 │
                        [klik ⚡]  │     [30 hotovo]               │
                                    ▼              ▼                 │
                            SHOCK_DELIVERED   CPR_BREATHS            │
                                    │         (max 15 s, btn)        │
                                    │              │ [potvrzeno]     │
                                    └──────→ CPR_ACTIVE (kolo +1) ──┘
                                                   │
                                        [kolo >= 4  ≈  2 min]
                                                   │
                                             REANALYZE (4 s)
                                              │         │
                                   [VF/VT]   │         │  [PEA/ASY]
                                              ▼         ▼
                                      SHOCK_CHARGING  CPR_PROMPT
                                                   │
                              [shockCount >= 3 AND shockSuccess]
                                    OR [totalCycles >= 12]
                                                   │
                                             END_SESSION
                                                   │
                                        [Reset nebo OFF]
                                                   ▼
                                                 IDLE
```

### 5.1 Detailní popis stavů

| Stav | Délka | EKG mód | LED | Klíčové akce |
|---|---|---|---|---|
| `IDLE` | — | `idle` | off | čeká na ON |
| `BOOTING` | 1.5 s | `flatline` | blink-green | startup zvuk, self-test animace |
| `PAD_PROMPT` | ∞ | `flatline` | green | instrukce el.1; klikací zóna aktivní |
| `PAD_PROMPT_2` | ∞ | `flatline` | green | instrukce el.2 |
| `ANALYZING` | 4–5 s | `analyzing` | yellow-blink | overlay „ANALÝZA"; všechna tlač. disabled |
| `SHOCK_CHARGING` | 3 s | `vf_strong` | red | progress bar nabíjení; ⚡ disabled |
| `SHOCK_READY` | ∞ | `vf_strong` | red-blink | ⚡ aktivní + pulzující; i-btn bliká 30 s |
| `SHOCK_DELIVERED` | 1 s | `shock` | red-flash | červený flash celé obrazovky 80 ms |
| `CPR_PROMPT` | 2 s | `pea` / `asystola` | green | instrukce zahájit KPR |
| `CPR_ACTIVE` | do 30 stlačení | `cpr` | green | metronom; počítadlo; btn komprese |
| `CPR_BREATHS` | max 15 s | `cpr` | green | btn „vdechy provedeny"; timeout = auto-pokračovat |
| `REANALYZE` | 4–5 s | `analyzing` | yellow-blink | totožné s ANALYZING |
| `END_SESSION` | ∞ | `post_shock` / `asystola` | green / off | modal s výsledky |

---

## 6. KPR Metronom

### 6.1 Vizuální metronom

```html
<div id="metronome">
  <div id="metro-circle"></div>
  <div id="metro-bpm">110 BPM</div>
  <input type="range" id="metro-slider"
         min="80" max="140" step="5" value="110"
         oninput="MetronomeEngine.setBpm(+this.value)">
  <div id="metro-bars">
    <div class="bar"></div><div class="bar"></div><div class="bar"></div>
    <div class="bar"></div><div class="bar"></div>
  </div>
</div>
```

```css
@keyframes metro-pulse {
  0%, 100% { transform: scale(1);    opacity: 1;   }
  50%       { transform: scale(1.35); opacity: 0.7; }
}
/* JS nastaví animation-duration dynamicky: (60/bpm)+'s' */
```

### 6.2 Audio scheduling (přesný rytmus)

```javascript
const MetronomeEngine = {
  bpm: 110,
  ctx: null,       // sdílený AudioContext
  nextBeat: 0,
  timerId: null,

  start(audioCtx) {
    this.ctx = audioCtx;
    this.nextBeat = audioCtx.currentTime + 0.05;
    this.schedule();
  },

  schedule() {
    // Lookahead 200 ms – naplánovat všechny beaty v okně
    while (this.nextBeat < this.ctx.currentTime + 0.2) {
      this._tick(this.nextBeat);
      this.nextBeat += 60 / this.bpm;
    }
    this.timerId = setTimeout(() => this.schedule(), 50);
  },

  _tick(time) {
    const osc  = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.connect(gain); gain.connect(this.ctx.destination);
    osc.frequency.value = 880; osc.type = 'sine';
    gain.gain.setValueAtTime(0.25, time);
    gain.gain.exponentialRampToValueAtTime(0.001, time + 0.08);
    osc.start(time); osc.stop(time + 0.09);
  },

  setBpm(bpm) {
    this.bpm = bpm;
    document.getElementById('metro-bpm').textContent = bpm + ' BPM';
    document.getElementById('metro-circle').style.animationDuration = (60/bpm) + 's';
  },

  stop() { clearTimeout(this.timerId); },
};
```

### 6.3 Tlačítko komprese (touch-first)

```html
<button id="btn-compress"
        onclick="doCompress()"
        ontouchend="doCompress(); event.preventDefault()">
  ↓ STLAČENÍ HRUDNÍKU ↓
</button>
```

```css
#btn-compress {
  min-height:     80px;
  min-width:      200px;
  font-size:      20px;
  touch-action:   manipulation;   /* zabrání double-tap zoom */
  user-select:    none;
}
#btn-compress:active { transform: scale(0.96); transition: transform 0.05s; }
```

```javascript
function doCompress() {
  if (state.phase !== 'CPR_ACTIVE') return;
  state.cprPresses++;
  state.compressionTimes.push(performance.now());
  if (navigator.vibrate) navigator.vibrate(40);    // haptika na mobilech
  updateCprCounter();
  if (state.cprPresses === 15) SpeechEngine.say('cpr_15');
  if (state.cprPresses >= 30)  transitionTo('CPR_BREATHS');
}
```

Klávesová zkratka: `Space` → `doCompress()` (aktivní jen ve stavu `CPR_ACTIVE`)

### 6.4 Přesná časová osa KPR cyklu

```
START CPR_ACTIVE  (timer od prvního stlačení)
│
├─ Kolo 1: 30 stlačení → CPR_BREATHS (max 15 s, nebo btn) → kolo 2
├─ Kolo 2: 30 stlačení → CPR_BREATHS → kolo 3
├─ Kolo 3: 30 stlačení → CPR_BREATHS → kolo 4
└─ Kolo 4: 30 stlačení → CPR_BREATHS → REANALYZE

Po REANALYZE:
  VF/VT   → SHOCK_CHARGING → SHOCK_READY → [výboj] → kolo 1
  PEA/ASY → CPR_PROMPT → kolo 1

Ukončení:
  shockCount >= 3 AND scenario.shockSuccess = true  → END_SESSION (ROSC)
  totalCycles    >= 12 (~6 min celkem)               → END_SESSION (ZZS v cestě)

Indikátor v instruktážním panelu:
  Kolo [2/4]  ██████░░░░  18/30  •  01:24 celkem
```

---

## 7. Timer a logování

### 7.1 Session timer

- Start: přechod `BOOTING → PAD_PROMPT` → `state.sessionStart = Date.now()`
- Zobrazení `MM:SS` v EKG displeji (pravý dolní roh)

### 7.2 Event log

- Max. 10 řádků, auto-scroll dolů; font: `monospace`
- Barvy: zelená = info, žlutá = analýza, červená = výboj/alarm
- Texty z `t('log', klíč)` — plně lokalizované
- Šablony: `t('log','shock_label').replace('%n', n).replace('%j', joules)`

### 7.3 Výsledkový modal

```html
<div id="result-modal" hidden>
  <h2 data-i18n="result_title"></h2>
  <table>
    <tr><td data-i18n="result_time"></td>          <td id="val-time"></td></tr>
    <tr><td data-i18n="result_shocks"></td>        <td id="val-shocks"></td></tr>
    <tr><td data-i18n="result_cpr"></td>           <td id="val-cpr"></td></tr>
    <tr><td data-i18n="result_avg_rate"></td>      <td id="val-rate"></td></tr>
    <tr><td data-i18n="result_longest_pause"></td> <td id="val-pause"></td></tr>
  </table>
  <button onclick="resetSession()" data-i18n="btn_restart"></button>
  <button onclick="window.print()"  data-i18n="btn_print"></button>
</div>
```

```javascript
function calcAvgRate(times) {
  if (times.length < 2) return 0;
  const intervals = [];
  for (let i = 1; i < times.length; i++) intervals.push(times[i] - times[i-1]);
  const avgMs = intervals.reduce((a,b)=>a+b,0) / intervals.length;
  return Math.round(60000 / avgMs);
}
```

---

## 8. Zvukový subsystém (AudioContext)

Všechny zvuky generovat programově – žádné audio soubory.

```javascript
const AudioEngine = {
  ctx: null,

  // Volat po prvním user gesture (klik kdekoli na stránce)
  init() {
    this.ctx = new (window.AudioContext || window.webkitAudioContext)();
  },

  beep(freq, duration, type = 'sine', volume = 0.3) {
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.connect(gain); gain.connect(this.ctx.destination);
    osc.frequency.value = freq; osc.type = type;
    gain.gain.setValueAtTime(volume, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + duration);
    osc.start(); osc.stop(this.ctx.currentTime + duration);
  },

  sweep(from, to, duration, type = 'sine', volume = 0.25) {
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.connect(gain); gain.connect(this.ctx.destination);
    osc.type = type;
    osc.frequency.setValueAtTime(from, this.ctx.currentTime);
    osc.frequency.linearRampToValueAtTime(to, this.ctx.currentTime + duration);
    gain.gain.setValueAtTime(volume, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + duration);
    osc.start(); osc.stop(this.ctx.currentTime + duration);
  },
};
```

| Zvuk | Metoda | Parametry | Trigger |
|---|---|---|---|
| Startup | `sweep` | 440→880 Hz, 0.8 s, sine | `BOOTING` |
| Analýza pípání | `beep` ×4 | 1000 Hz, 0.2 s, square (pauza 0.2 s) | `ANALYZING` |
| Nabíjení | `sweep` | 200→2000 Hz, 3 s, sawtooth | `SHOCK_CHARGING` |
| Výboj | `beep` | 150 Hz, 0.3 s, square, vol 0.6 | `SHOCK_DELIVERED` |
| Metronom klik | `_tick` | 880 Hz, 0.08 s, sine | `CPR_ACTIVE` každý beat |
| Varování baterie | `beep` ×3 | 800 Hz, 0.15 s, triangle (pauza 0.3 s) | `LOW_BATTERY` |

---

## 9. Náhodnost simulace

```javascript
function weightedRandom(weights) {
  const entries = Object.entries(weights);
  const total   = entries.reduce((s,[,w]) => s+w, 0);
  let r = Math.random() * total;
  for (const [key, w] of entries) { r -= w; if (r <= 0) return key; }
  return entries[entries.length-1][0];
}

function generateScenario() {
  const rhythm = weightedRandom({
    'VF':  0.55,   // ventrikulární fibrilace
    'VT':  0.10,   // ventrikulární tachykardie (= také shock_advised)
    'PEA': 0.20,   // pulseless electrical activity
    'ASY': 0.15,   // asystola
  });
  return {
    rhythm,
    shockable:    ['VF','VT'].includes(rhythm),
    shockSuccess: Math.random() < 0.70,
    rosc_after:   Math.floor(Math.random()*3) + 1,
  };
}
```

---

## 10. Pediatrický režim

```javascript
function togglePediatric() {
  state.pediatric = !state.pediatric;
  state.joulesToDeliver = state.pediatric ? 50 : 150;
  SpeechEngine.say('pediatric_on');
  document.getElementById('pad-diagram').classList.toggle('pediatric');
  // CSS třída .pediatric: zobrazí předozadní rozmístění el. v SVG
  // EKG vf mód: použít vyšší frekvenci ~240/min (×1.7)
}
```

---

## 11. Přístupnost a UX

- Všechna tlačítka: `aria-label` z `t('ui', klíč)`, aktualizovat v `renderUI()`
- `Space` = komprese (stav `CPR_ACTIVE`)
- `Enter` = potvrdit aktuální akci
- `R` = reset kdykoli
- `prefers-reduced-motion`: potlačit CSS animace, zachovat zvuk a hlas
- Touch targets min.: běžné = 44×44 px, kritické (komprese, výboj) = 80×80 px
- `touch-action: manipulation` na všech interaktivních prvcích

---

## 12. Technické minimum pro implementaci

### 12.1 Struktura souborů a pořadí JS modulů

**Soubory vedle HTML:**
```
aed-trenazor.html        ← celá aplikace (CSS + JS inline)
audio/
  cs/                    ← 24 CZ hlášek (názvy = klíče z LANG.cs.voice)
    start.mp3
    pad1_prompt.mp3  pad1_ok.mp3
    pad2_prompt.mp3  pad2_ok.mp3
    analyzing.mp3    analyze_wait.mp3
    shock_advised.mp3  shock_ready.mp3  shock_clear.mp3
    shock_delivered.mp3  no_shock.mp3
    cpr_start.mp3  cpr_depth.mp3  cpr_rate.mp3
    cpr_15.mp3  cpr_30.mp3  breaths_done.mp3
    reanalyze.mp3  rosc.mp3  continue_cpr.mp3
    shock2.mp3  shock3.mp3  off.mp3  end_session.mp3
  en/                    ← stejná struktura v angličtině
images/
  revolut-qr.png         ← 400×400 px, tmavá QR na světlém pozadí
```

**Pořadí JS modulů (závazné — každý závisí na předchozím):**
```
A. LANG {}              ← editovatelné hlášky, UI texty, log texty
B. t(), setLang(), renderUI()
C. AudioEngine          ← beep(), sweep() — volat init() až po user gesture
D. AudioPlayer          ← MP3 cache, preload(), play()
E. SpeechEngine         ← orchestrátor: say(), init(), detectMp3(), reloadVoice()
F. EcgEngine            ← canvas animace, precomputedWaveform, resize()
G. MetronomeEngine      ← AudioContext scheduling, setBpm(), start(), stop()
H. weightedRandom(), generateScenario(), SCENARIOS{}
I. StateMachine         ← transitionTo(), renderState()
J. UI Controller        ← pressPower(), connectPad(n), doCompress(), doBreaths()
                           selectScenario(), resetScenario(), setSkin()
K. openDonateModal(), closeDonateModal()
L. DOMContentLoaded     ← init sekvence
```

**Autoritativní HTML struktura** (viz §2.2 pro site-bar, §2.7 pro frx-body, §3.5 pro instruction-panel):
```
<body class="skin-frx">
  #site-bar (28px, fixed)
    .site-name | .skin-zone [FRx][ZOLL][SAM] | .site-controls [#voice-quality][CZ][EN][♥]
  #training-banner (22px, fixed)
  #voice-warning (hidden)
  #app-container (grid: 440px + 360px, height: calc(100vh - 50px))
    #device-panel
      #frx-body
        #device-header (.frx-logo-brand, .frx-logo-model, #led-ready)
        #ecg-display (#ecg-canvas, #skin-alt-display > #zoll-cpr-num + .alt-label)
        #pad-diagram (SVG: #torso-head, #torso-body, #pad1-zone, #pad2-zone)
        #connectors (#conn-left, .conn-center > .conn-brand-label, #conn-right)
        #main-buttons (#btn-on, #btn-info, #btn-shock)
        #charging-bar-wrap[hidden] > #charging-bar-fill
        #led-status (.led-item × 3: #led-ready, #led-charging, #led-shock)
        .frx-serial
    #instruction-panel
      #scenario-bar (#scenario-selector, #btn-reset-scenario, #scenario-status)
      #main-instruction
      #metronome-section (hidden → visible v CPR)
        #metro-top (#metro-circle, #metro-bpm-display, #metro-bars > .mbar×5)
        #metro-slider-row (#metro-slider, #metro-bpm-value)
      #cpr-controls (hidden → visible v CPR)
        #cpr-header (#cpr-counter > #cpr-num+#cpr-denom, #cpr-round-info, #cpr-timer)
        #cpr-progress > #cpr-progress-fill
        #btn-compress (hidden → visible v CPR_ACTIVE)
        #btn-breaths  (hidden → visible v CPR_BREATHS)
      #event-log (.log-title, #log-entries)
  #result-modal[hidden]
  #donate-modal[hidden]
```

**Výpočet padding-top pro `#app-container`:**
```
site-bar:         28px (fixed)
training-banner:  22px (fixed)
─────────────────────
padding-top:      50px
height:           calc(100vh - 50px)
min-height:       480px
```


### 12.2 CSS proměnné

> Autoritativní hodnoty jsou v §2.5. Tento blok je shodná kopie pro referenci při kódování.

```css
:root {
  /* Tělo FRx — světle šedý ABS plast (viz §2.5) */
  --frx-light:     #c8cdd6;
  --frx-mid:       #a8b0bc;
  --frx-dark:      #8892a0;
  --frx-deep:      #6b7585;
  --frx-floor:     #0d1117;   /* podlaha/stůl pod přístrojem */
  --clr-philips:   #1d4ed8;   /* Philips logo modrá */

  /* Tlačítka */
  --clr-on-dim:    #1a5c30;   /* ON/OFF neaktivní */
  --clr-on-lit:    #22c55e;   /* ON/OFF aktivní */
  --clr-shock-dim: #92320a;   /* VÝBOJ neaktivní */
  --clr-shock-lit: #f97316;   /* VÝBOJ aktivní */
  --clr-info-btn:  #1e40af;   /* tlačítko i */

  /* EKG */
  --clr-ecg-bg:    #020a05;
  --clr-ecg-grid:  #0a1e0d;
  --clr-ecg-ok:    #22c55e;
  --clr-ecg-warn:  #eab308;
  --clr-ecg-shock: #ef4444;

  /* Web + UI */
  --clr-panel-bg:  #0f172a;
  --clr-text:      #f1f5f9;
  --clr-muted:     #64748b;
  --clr-training:  #c2410c;
  --clr-donate:    #0075eb;
  --font-device:   'Rajdhani', sans-serif;
  --font-ui:       'IBM Plex Sans', sans-serif;
}
```

**⚠️ DŮLEŽITÉ — princip 3D gradientů v tomto projektu:**

Všechna fyzická tlačítka a plochy přístroje používají **třívrstvý gradient** místo jednoduchého `background-color`. Claude Code musí tento vzor dodržet všude — **nikdy nenahrazovat jednoduchou barvou**:

```
vrstva 1 (nahoře):  specular highlight — bílý radial vlevo nahoře, opacity 0.15–0.22
vrstva 2 (střed):   shadow depth     — tmavý radial vpravo dole,  opacity 0.28–0.40
vrstva 3 (základ):  base color radial — střed světlejší → okraj tmavší

border: asymetrický vždy:
  border-top/left:   světlejší (odkud přichází světlo)
  border-bottom/right: tmavší (ve stínu)

box-shadow: vždy minimálně 3 vrstvy:
  vnější tvrdý stín:  0 6px 14px rgba(0,0,0,0.65)   ← zvednutost
  inset horní světlo: inset 0 2px 3px rgba(255,255,255,0.15–0.22)
  inset spodní stín:  inset 0 -3px 5px rgba(0,0,0,0.40–0.50)

:active stav: vždy translateY(+2px) + zmenšit box-shadow
  → simuluje fyzický stisk tlačítka směrem dolů
```

### 12.3 Stavová proměnná

```javascript
const state = {
  phase:               'IDLE',
  pad1:                false,
  pad2:                false,
  powered:             false,
  shockReady:          false,
  shockCount:          0,
  cprPresses:          0,
  cprCycles:           0,        // kola v aktuálním bloku (4 → REANALYZE)
  totalCycles:         0,        // celkový počet kol
  sessionStart:        null,
  lastCompressionTime: null,
  compressionTimes:    [],       // pro výpočet průměrné frekvence
  scenario:            null,
  pediatric:           false,
  joulesToDeliver:     150,
  iButtonFlashEnd:     null,     // timestamp kdy přestane blikat btn i
};
```

### 12.4 `renderUI()` — data-i18n pattern

```javascript
function renderUI() {
  // 1. Standardní data-i18n textContent
  document.querySelectorAll('[data-i18n]').forEach(el => {
    el.textContent = t('ui', el.dataset.i18n);
  });

  // 2. aria-label
  document.querySelectorAll('[data-i18n-aria]').forEach(el => {
    el.setAttribute('aria-label', t('ui', el.dataset.i18nAria));
  });

  // 3. Tlačítka s ikonou (♥) — zachovat ikonu, přepsat text za ní
  document.querySelectorAll('[data-i18n-text]').forEach(el => {
    el.textContent = '♥ ' + t('ui', el.dataset.i18nText);
  });

  // 4. Scenario selector options
  const sel = document.getElementById('scenario-selector');
  if (sel) {
    const map = {
      random: 'scenario_random',
      S1: 'scenario_s1', S2: 'scenario_s2', S3: 'scenario_s3',
      S4: 'scenario_s4', S5: 'scenario_s5', S6: 'scenario_s6',
    };
    Array.from(sel.options).forEach(opt => {
      if (map[opt.value]) opt.text = t('ui', map[opt.value]);
    });
  }

  // 5. Hardcoded-text prvky v CPR panelu
  const compress = document.getElementById('btn-compress');
  if (compress) compress.textContent = t('ui', 'btn_compress');
  const breaths = document.getElementById('btn-breaths');
  if (breaths) breaths.textContent = t('ui', 'btn_breaths');
  const roundLbl = document.getElementById('cpr-round-label');
  if (roundLbl) roundLbl.textContent = t('ui', 'cpr_round_label');

  // 6. Site title + scenario status
  const siteName = document.querySelector('.site-name');
  if (siteName) siteName.textContent = t('ui', 'site_title');
  const scenStatus = document.getElementById('scenario-status');
  if (scenStatus && !state.powered) {
    scenStatus.textContent = t('ui', 'scenario_ready');
  }

  // 7. html lang atribut
  document.documentElement.lang = currentLang;

  // 8. Aktivní lang-btn
  document.querySelectorAll('.lang-btn').forEach(b => {
    b.classList.toggle('active', b.id === 'lang-' + currentLang);
  });
}
// Příklad v HTML:
// <span data-i18n="led_ready"></span>
// <button data-i18n="btn_shock" data-i18n-aria="btn_shock_label"></button>
// <button data-i18n-text="donate_btn"></button>  ← pro tlačítka s ikonou ♥
```

---

## 13. Scénáře pro výcvik (předdefinované)

**Výběr scénáře je v `#site-bar`** — viz §2.2 (HTML + CSS select elementu).
Scénář se vybírá **před** zapnutím přístroje. Po výběru a kliknutí ↺ (reset)
se načte nový scénář — state machine přejde do `IDLE`.

```javascript
function selectScenario(id) {
  // Uložit výběr, ale NEspouštět — uživatel sám stiskne ON/OFF
  state.selectedScenario = id;
  // Zvýraznit aktivní scénář v selectoru
  document.getElementById('scenario-selector').value = id;
}

function resetScenario() {
  if (state.phase !== 'IDLE') transitionTo('IDLE');
  state.selectedScenario = document.getElementById('scenario-selector').value;
  // Krátká vizuální feedback animace na ↺ tlačítku
  const btn = document.getElementById('btn-reset-scenario');
  btn.style.transform = 'rotate(360deg)';
  btn.style.transition = 'transform 0.4s';
  setTimeout(() => { btn.style.transform = ''; btn.style.transition = ''; }, 400);
}

// Scénář se aplikuje při přechodu BOOTING → PAD_PROMPT
function applyScenario() {
  const id = state.selectedScenario ?? 'random';
  if (id === 'random') {
    state.scenario = generateScenario();
  } else {
    state.scenario = SCENARIOS[id];
  }
  if (state.scenario.pediatric) togglePediatric(true);
}
```

Předdefinované scénáře jako JS objekt:

```javascript
const SCENARIOS = {
  S1: { rhythm: 'VF',  shockable: true,  shockSuccess: true,  rosc_after: 1, pediatric: false },
  S2: { rhythm: 'VF',  shockable: true,  shockSuccess: false, rosc_after: 3, pediatric: false },
  S3: { rhythm: 'PEA', shockable: false, rosc_cpr_cycles: 3, pediatric: false },  // ROSC po 3 cyklech KPR
  S4: { rhythm: 'ASY', shockable: false, rosc_cpr_cycles: 0, pediatric: false },  // bez ROSC
  S5: { rhythm: 'VF',  shockable: true,  shockSuccess: true,  rosc_after: 1, pediatric: true  },
  S6: { rhythm: 'VF',  shockable: true,  shockSuccess: true,  rosc_after: 2, pediatric: false },
        // cpr_first neimplementován — efekt simulován přes rosc_after: 2 (1. výboj selže)
};
```

| ID | Název CZ | Název EN | Rytmus | Specifika |
|---|---|---|---|---|
| `random` | Náhodný | Random | — | `generateScenario()` |
| `S1` | Klasická zástava | Classic arrest | VF | `shockSuccess: true, rosc_after: 1` |
| `S2` | Rezistentní VF | Refractory VF | VF | `shockSuccess: false` |
| `S3` | Nedefibrilovatelný | Non-shockable | PEA | ROSC po 2 cyklech |
| `S4` | Asystola | Asystole | ASY | jen KPR |
| `S5` | Dítě | Pediatric | VF | `pediatric: true, joules: 50` |
| `S6` | Pozdní příjezd | Delayed response | VF | `cpr_first: true` → CPR_FIRST stav |

**S6 implementační detail:** `cpr_first: true` → před `ANALYZING` vložit stav `CPR_FIRST`
(4 kola KPR bez elektrod). Hláška: *„Pacient je bez vědomí déle než pět minut.
Zahajte KPR, teprve poté přiložte elektrody."*

---

## 14. Nasazení

**Lokální:** uložit jako `aed-trenazor.html` → otevřít v Chrome/Edge  
**GitHub Pages:** `index.html` v root → `https://username.github.io/aed-trenazor`  
**Netlify Drop:** přetáhnout na `app.netlify.com/drop` → okamžitá URL

---

## 15. Klíčové poznámky pro implementaci

1. **AudioContext user gesture:** `AudioEngine.init()` volat při **prvním** kliku (`document.addEventListener('click', AudioEngine.init.bind(AudioEngine), {once:true})`)
2. **Chrome speech bug:** workaround pause/resume v `SpeechEngine.init()` – viz §4.3
3. **iOS Safari:** Web Speech API nespolehlivé; zobrazit banner doporučující Chrome/Edge
4. **`getVoices()` async:** vždy obalit do `synth.onvoiceschanged` – viz §4.3
5. **EKG výkon:** `requestAnimationFrame`, buffer délky `canvas.width`; nealokovat objekty v každém framu
6. **Touch na elektrodách:** `ontouchend="...; event.preventDefault()"` – zabrání ghost click 300 ms
7. **Metronom přesnost:** AudioContext lookahead scheduling – viz §6.2; nikdy ne `setInterval` pro zvuk
8. **Flash výboje:** `document.body.style.background='#ff0000'` na 80 ms; ošetřit `prefers-reduced-motion`
9. **Print CSS:** skrýt tlačítka, zobrazit jen `#result-modal` a event log (`@media print`)

---

## 16. Rozšíření (fáze 2)

- [ ] QR kód pro sdílení URL (qrcode.js z CDN)
- [ ] PDF export výsledků (`window.print()` + print CSS)
- [ ] Leaderboard v `localStorage`
- [ ] Další jazyky (SK, DE, PL) – přidat blok do `LANG`
- [ ] Instruktorský mód – ruční výběr výsledku analýzy
- [ ] CPR hloubka zpětná vazba (DeviceMotion API, experimentální)

---

## 17. Přesná časová osa KPR (shrnutí)

```
START CPR_ACTIVE  ←  timer od 1. stlačení
│
├─ Kolo 1: [Space/btn] × 30 → CPR_BREATHS → kolo 2
├─ Kolo 2: × 30 → CPR_BREATHS → kolo 3
├─ Kolo 3: × 30 → CPR_BREATHS → kolo 4
└─ Kolo 4: × 30 → CPR_BREATHS → REANALYZE
               │
   VF/VT  → SHOCK_CHARGING → SHOCK_READY → [⚡] → kolo 1
   PEA/ASY → CPR_PROMPT → kolo 1
               │
   shockCount ≥ 3 AND shockSuccess   → END_SESSION (ROSC)
   totalCycles ≥ 12 (~6 min)         → END_SESSION (ZZS)
```

Indikátor (vždy viditelný v CPR fázích):
```
Kolo [2/4]  ██████░░░░  18/30  •  01:24 celkem
```

---

## 18. Podpora projektu – Donate

### 18.1 Tlačítko v site-baru — plně lokalizované

Tlačítko je součástí `#site-bar`. Text pochází z `t('ui','donate_btn')` — přepne se
automaticky se změnou jazyka. Záměrně nevýrazné (bez výplně, stejný styl jako lang-btn).

```html
<button id="btn-donate"
        onclick="openDonateModal()"
        data-i18n-text="donate_btn">
  ♥ Podpořit
</button>
```

```css
#btn-donate {
  background:    transparent;
  border:        1px solid #374151;
  border-radius: 3px;
  color:         #6b7280;
  font-size:     10px; font-weight: 700;
  padding:       2px 8px;
  cursor:        pointer;
  margin-left:   4px;
  letter-spacing: 0.5px;
  transition:    color 0.15s, border-color 0.15s;
}
#btn-donate:hover { color: #93c5fd; border-color: #93c5fd; }
/* Revolut modrá se projeví jen uvnitř modalu, ne v site-baru */
```

**`data-i18n-text` pattern** — pro prvky kde `textContent` nelze použít přímo
(tlačítko má ikonu ♥ napevno), rozšíř `renderUI()`:
```javascript
document.querySelectorAll('[data-i18n-text]').forEach(el => {
  // Zachovat první child (ikona) a nahradit jen text
  const key  = el.dataset.i18nText;
  const text = t('ui', key);          // 'Podpořit' / 'Support'
  el.textContent = '♥ ' + text;
});
```

---

### 18.2 Donate modal — plně lokalizovaný HTML

Veškerý text pochází z `LANG[currentLang].ui.*`. Modal se aktualizuje při `setLang()`.

```html
<div id="donate-modal" hidden
     role="dialog" aria-modal="true"
     aria-labelledby="donate-title">
  <div id="donate-content">

    <button id="donate-close"
            onclick="closeDonateModal()"
            data-i18n-aria="donate_close">✕</button>

    <h2 id="donate-title" data-i18n="donate_title">Podpořte projekt</h2>

    <p id="donate-desc" data-i18n="donate_desc">
      <!-- Text vloží renderUI() z LANG.ui.donate_desc -->
    </p>

    <!-- QR kód — obrázek z images/ složky, s fallbackem -->
    <div id="donate-qr">
      <img id="donate-qr-img"
           src="images/revolut-qr.png"
           alt="QR Revolut – revolut.me/vclavlxjq"
           width="200" height="200"
           onerror="this.hidden=true; document.getElementById('donate-qr-fallback').hidden=false">
      <div id="donate-qr-fallback" hidden>
        <svg viewBox="0 0 120 120" width="120" height="120">
          <!-- Minimalistický QR placeholder -->
          <rect width="120" height="120" fill="#0f172a" rx="8"/>
          <rect x="10" y="10" width="40" height="40" fill="none"
                stroke="#0075eb" stroke-width="3" rx="4"/>
          <rect x="20" y="20" width="20" height="20" fill="#0075eb" rx="2"/>
          <rect x="70" y="10" width="40" height="40" fill="none"
                stroke="#0075eb" stroke-width="3" rx="4"/>
          <rect x="80" y="20" width="20" height="20" fill="#0075eb" rx="2"/>
          <rect x="10" y="70" width="40" height="40" fill="none"
                stroke="#0075eb" stroke-width="3" rx="4"/>
          <rect x="20" y="80" width="20" height="20" fill="#0075eb" rx="2"/>
          <text x="60" y="100" text-anchor="middle"
                fill="#64748b" font-size="8" font-family="monospace">revolut.me/vclavlxjq</text>
        </svg>
      </div>
    </div>

    <a id="donate-link"
       href="https://revolut.me/vclavlxjq"
       target="_blank" rel="noopener noreferrer"
       data-i18n="donate_link_text">
      Otevřít Revolut →
    </a>

    <p id="donate-handle">revolut.me/vclavlxjq</p>

    <p id="donate-note" data-i18n="donate_note">
      <!-- Text vloží renderUI() -->
    </p>

  </div>
</div>
```

### 18.3 CSS donate modalu

```css
#donate-modal {
  position:        fixed; inset: 0;
  background:      rgba(0,0,0,0.80);
  display:         flex;
  align-items:     center;
  justify-content: center;
  z-index:         1000;
  padding:         16px;
}
#donate-modal[hidden] { display: none; }

#donate-content {
  background:    #0f172a;
  border:        1px solid #1e3a5f;
  border-radius: 16px;
  padding:       28px 24px;
  max-width:     400px;
  width:         100%;
  text-align:    center;
  position:      relative;
  color:         #f1f5f9;
  font-family:   var(--font-ui);
}

#donate-close {
  position:   absolute; top: 10px; right: 12px;
  background: none; border: none;
  color:      #4b5563; font-size: 18px; cursor: pointer;
  line-height: 1; padding: 4px;
  transition: color 0.15s;
}
#donate-close:hover { color: #f1f5f9; }

#donate-title {
  font-size:   20px; font-weight: 700;
  color:       #f1f5f9; margin-bottom: 10px;
}

#donate-desc {
  color:       #94a3b8; font-size: 13px;
  line-height: 1.5; margin-bottom: 0;
}

#donate-qr {
  display:         flex;
  justify-content: center;
  margin:          18px auto;
}

#donate-qr-img {
  border-radius: 12px;
  border:        3px solid #0075eb;
  display:       block;
}

#donate-link {
  display:         inline-block;
  background:      #0075eb;
  color:           #fff;
  text-decoration: none;
  padding:         10px 28px;
  border-radius:   24px;
  font-weight:     700;
  font-size:       14px;
  transition:      background 0.2s, transform 0.1s;
}
#donate-link:hover  { background: #005bb5; }
#donate-link:active { transform: scale(0.97); }

#donate-handle {
  color:       #334155;
  font-size:   12px;
  font-family: monospace;
  margin-top:  8px;
  letter-spacing: 0.5px;
}

#donate-note {
  color:       #334155;
  font-size:   11px;
  margin-top:  14px;
  line-height: 1.5;
}
```

### 18.4 JavaScript — otevření, zavření, lokalizace

```javascript
function openDonateModal() {
  // Aktualizovat texty modalu pro aktuální jazyk
  renderUI();
  document.getElementById('donate-modal').hidden = false;
  document.getElementById('donate-close').focus();
}

function closeDonateModal() {
  document.getElementById('donate-modal').hidden = true;
  document.getElementById('btn-donate').focus();
}

// Zavřít kliknutím na overlay
document.getElementById('donate-modal')
  .addEventListener('click', e => {
    if (e.target.id === 'donate-modal') closeDonateModal();
  });

// Zavřít Escape
document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && !document.getElementById('donate-modal').hidden)
    closeDonateModal();
});
```

**Rozšíření `renderUI()` pro donate modal:**
```javascript
function renderUI() {
  // Standardní data-i18n elementy
  document.querySelectorAll('[data-i18n]').forEach(el => {
    el.textContent = t('ui', el.dataset.i18n);
  });
  // Elementy kde text vložíme přímo (p, h2 s data-i18n)
  // — pokrývá donate_desc, donate_note, donate_title atd.

  // Tlačítka s ikonou — zachovat ikonu, přepsat text
  document.querySelectorAll('[data-i18n-text]').forEach(el => {
    el.textContent = '♥ ' + t('ui', el.dataset.i18nText);
  });

  // aria-label
  document.querySelectorAll('[data-i18n-aria]').forEach(el => {
    el.setAttribute('aria-label', t('ui', el.dataset.i18nAria));
  });

  // Scenario selector options — přepsat texty
  const sel = document.getElementById('scenario-selector');
  if (sel) {
    const map = {
      random: 'scenario_random',
      S1: 'scenario_s1', S2: 'scenario_s2', S3: 'scenario_s3',
      S4: 'scenario_s4', S5: 'scenario_s5', S6: 'scenario_s6',
    };
    Array.from(sel.options).forEach(opt => {
      if (map[opt.value]) opt.text = t('ui', map[opt.value]);
    });
  }

  // Btn compress a breaths — hardcoded text v HTML, přepsat
  const btnC = document.getElementById('btn-compress');
  if (btnC) btnC.textContent = t('ui', 'btn_compress');
  const btnB = document.getElementById('btn-breaths');
  if (btnB) btnB.textContent = t('ui', 'btn_breaths');

  // CPR round label
  const rl = document.getElementById('cpr-round-label');
  if (rl) rl.textContent = t('ui', 'cpr_round_label');

  // Site title
  const st = document.querySelector('.site-name');
  if (st) st.textContent = t('ui', 'site_title');
}
```

### 18.5 QR kód — umístění souborů

```
aed-trenazor.html
images/
  revolut-qr.png      ← hlavní QR pro Revolut platbu
                         URL: https://revolut.me/vclavlxjq
                         Doporučená velikost: 400×400 px PNG
                         Barvy: tmavá na světlém (lépe čitelné na tmavém pozadí modalu)
```

Pokud `images/revolut-qr.png` neexistuje → `onerror` zobrazí SVG placeholder.
QR lze také vložit jako base64 přímo do HTML (single-file varianta):
```html
<img src="data:image/png;base64,iVBORw0KGgo..." alt="QR Revolut">
```

---

*Specifikace v2.1 – plně lokalizovaná, připravena pro single-file implementaci*
*Projekt: IDDA Trainer #12392 · 4D Dive Deep Descend Down · 4dive.cz*
