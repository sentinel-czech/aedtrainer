# tips.md — Časté chyby a jak se jim vyhnout

> Tento soubor shrnuje problémy které se při implementaci AED trenažéru
> typicky vyskytnou. Přečti před psaním kódu, ne až když něco nefunguje.

---

## Web Speech API

### Hlas se nenačte při startu
**Problém:** `speechSynthesis.getVoices()` vrátí prázdné pole.  
**Proč:** Hlasy se načítají asynchronně — při `DOMContentLoaded` ještě nejsou dostupné.  
**Řešení:**
```javascript
function loadVoice() {
  const voices = speechSynthesis.getVoices();
  if (!voices.length) return;           // ještě nejsou — počkej na event
  SpeechEngine.voice = voices.find(v => v.lang === 'cs-CZ')
    ?? voices.find(v => v.lang.startsWith('cs'))
    ?? voices.find(v => v.lang.startsWith('en'))
    ?? voices[0];
  const hasNative = voices.some(v => v.lang === 'cs-CZ');
  document.getElementById('voice-warning').hidden = hasNative;
}
speechSynthesis.onvoiceschanged = loadVoice;
loadVoice(); // zkus i hned — Chrome Desktop má hlasy okamžitě
```

### Synthesis se zastaví po 15 sekundách (Chrome)
**Problém:** Dlouhá KPR fáze = synthesis přestane mluvit bez chyby.  
**Řešení:** Workaround pause/resume každých 10 sekund:
```javascript
setInterval(() => {
  if (speechSynthesis.speaking) {
    speechSynthesis.pause();
    speechSynthesis.resume();
  }
}, 10000);
```
Toto volat jednou v `SpeechEngine.init()`.

### Hlas mluví japonsky / arabsky
**Problém:** Fallback `voices[0]` je na některých systémech jiný jazyk než angličtina.  
**Řešení:** Fallback řetězec viz výše — `cs` → `en` → první dostupný.  
Zobrazit `#voice-warning` pokud přesná `cs-CZ` shoda není dostupná.

### iOS Safari — synthesis nefunguje vůbec
**Problém:** Na iPhone/iPad Web Speech API vyžaduje user gesture pro **každou** promluvu.  
**Chování:** Funguje první hláška po kliku, pak se zastaví.  
**Řešení:** Nezkoušet to opravit. Zobrazit persistent banner:
```html
<div id="ios-warning">
  Pro hlasové navádění použijte Chrome nebo Edge na počítači / Androidu.
</div>
```
Detekce: `navigator.userAgent.includes('iPhone') || navigator.userAgent.includes('iPad')`

---

## AudioContext

### "AudioContext was not allowed to start"
**Problém:** Vytvoření `AudioContext` v `DOMContentLoaded` nebo globálně.  
**Proč:** Chrome blokuje AudioContext bez předchozí user interaction.  
**Řešení:** Viz `CLAUDE.md` — vytvářet **výhradně** v handleru prvního kliku:
```javascript
document.addEventListener('click', () => {
  if (!AudioEngine.ctx) AudioEngine.init();
}, { once: true });
```

### Metronom driftuje po minutách
**Problém:** `setInterval(beep, 60000/bpm)` — každý tick je o pár ms pozdě,
chyba se kumuluje.  
**Řešení:** Lookahead scheduling přes `AudioContext.currentTime` — viz §6.2 v spec.
Správná implementace plánuje beaty 200 ms dopředu a každých 50 ms kontroluje frontu.

### Zvuk při výboji je příliš tichý / hlasitý
Doporučené hlasitosti:
```
startup sweep:    volume 0.20
analýza pípání:   volume 0.25
nabíjení sweep:   volume 0.22
výboj burst:      volume 0.55  ← záměrně hlasitější = dramatický efekt
metronom klik:    volume 0.20
varování baterie: volume 0.18
```

---

## Canvas / EKG

### Canvas je rozmazaný na Retina / HiDPI displejích
**Problém:** Canvas rozlišení neodpovídá fyzickým pixelům.  
**Řešení:**
```javascript
function initCanvas(canvas) {
  const dpr = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  canvas.width  = rect.width  * dpr;
  canvas.height = rect.height * dpr;
  const ctx = canvas.getContext('2d');
  ctx.scale(dpr, dpr);          // všechny souřadnice v CSS px
  return ctx;
}
```
Volat v `EcgEngine.init()` a znovu při `window.resize`.

### EKG způsobuje memory leak
**Problém:** Alokace nových objektů (`new Float32Array`, `{}`) v každém animFrame.  
**Řešení:**
- Buffer = předdimenzovaný `Float32Array(canvasWidth)`, plnit cyklicky
- `precomputedWaveform` = statické pole, generovat jednou při init
- Žádné `new` uvnitř `requestAnimationFrame` callbacku

### AnimFrame se nekumuluje při skryté záložce
**Chování:** Když uživatel přepne záložku, `requestAnimationFrame` se pozastaví.
Timer, metronom a state machine pokračují. Při návratu = EKG „doskočí".  
**Řešení:** Uložit `lastTimestamp`, při resumu neignorovat velké `dt`:
```javascript
function animLoop(timestamp) {
  const dt = Math.min(timestamp - lastTimestamp, 100); // max 100ms skok
  lastTimestamp = timestamp;
  // ... použij dt pro smooth update
  requestAnimationFrame(animLoop);
}
```

---

## State Machine

### UI se aktualizuje, ale state.phase zaostává (nebo naopak)
**Příčina:** Přímá manipulace s DOM z event listeneru místo přes `transitionTo()`.  
**Pravidlo:** Event listener smí volat **pouze** `transitionTo(newPhase)`.
Veškerá DOM manipulace (třídy, texty, viditelnost) se děje **výhradně** uvnitř
`transitionTo()` nebo v `renderState()` který volá.

### SHOCK tlačítko zůstane aktivní po resetu
**Příčina:** Reset nevolá `transitionTo('IDLE')`, ale manuálně nastavuje `state.*`.  
**Řešení:** Reset = vždy `transitionTo('IDLE')` — state machine sama uvede UI do čistého stavu.

### i-button bliká i po přechodu mimo SHOCK_READY
**Příčina:** `iButtonFlashEnd` timestamp se nekontroluje při každém přechodu.  
**Řešení:** V každém `transitionTo()` volat:
```javascript
if (newPhase !== 'SHOCK_READY') {
  clearInterval(state.iButtonFlashInterval);
  document.getElementById('btn-info').classList.remove('blink');
  state.iButtonFlashEnd = null;
}
```

---

## Layout / CSS

### Na tabletu se simulátor vertikálně nevejde
**Příčina:** Jednotlivé komponenty v `#frx-body` mají pevnou výšku
místo `flex: 1` s `overflow: hidden`.  
**Kontrola:** `#frx-body` musí být `display: flex; flex-direction: column`.
Prvky které se mají roztahovat mají `flex: 1`, pevné prvky mají `flex: none`.
Celková výška `#frx-body` = `calc(100vh - 56px - 24px)` (odečíst oba headery + padding).

### EKG canvas má šířku 0 při inicializaci
**Příčina:** `canvas.offsetWidth` je 0 pokud je parent `display: none`
nebo ještě není v DOMu.  
**Řešení:** Inicializovat canvas až po `DOMContentLoaded`, nikoli v `<script>` v `<head>`.

### Touch na elektrodách spustí událost dvakrát (ghost click)
**Příčina:** `touchend` → po 300 ms přijde i syntetický `click`.  
**Řešení:**
```javascript
ontouchend="connectPad(1); event.preventDefault()"
// event.preventDefault() zabrání ghost click
```

### Přepínač jazyka rozbije layout site-baru
**Příčina:** Přidání dalšího jazyka rozšíří `.site-controls` a vytlačí `.site-name`.  
**Řešení:** `.site-controls` má `flex-shrink: 0`, `.site-name` má `overflow: hidden; text-overflow: ellipsis`.

---

## i18n / Lokalizace

### `t()` vrátí `[klic]` místo textu
**Příčiny (v pořadí pravděpodobnosti):**
1. Překlep v klíči — klíče jsou case-sensitive
2. `currentLang` je nastaveno na jazyk který v `LANG` objektu neexistuje
3. `renderUI()` volána před inicializací `LANG` objektu (pořadí scriptů)

**Debug:**
```javascript
console.log(Object.keys(LANG));              // dostupné jazyky
console.log(Object.keys(LANG.cs.voice));     // dostupné hlasové klíče
```

### Přepnutí jazyka přeruší probíhající hláška
**Příčina:** `setLang()` volá `SpeechEngine.reloadVoice()` ale neruší synthesis.  
**Řešení:** Pokud právě mluví, nechat domluvit — nový jazyk se projeví od příští hlášky:
```javascript
function setLang(lang) {
  if (!LANG[lang]) return;
  currentLang = lang;
  SpeechEngine.reloadVoice();   // načte hlas, neruší synthesis
  renderUI();
  // Aktualizovat aktivní lang-btn
  document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('lang-' + lang).classList.add('active');
}
```

---

## Donate modal

### Modal je za AED přístrojem (z-index)
`#donate-modal` musí mít `z-index: 1000` — AED layout má max `z-index: 200` (site-bar).

### QR kód se negeneruje (Varianta C — qrcode.js z CDN)
**Příčina:** `generateQR()` voláno před načtením skriptu z CDN.  
**Řešení:** Volat `generateQR()` uvnitř `openDonateModal()`, ne při init.
Zkontrolovat zda CDN URL odpovídá: `cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js`

---

## Výkonnostní tipy

- **EKG buffer:** `Float32Array` místo běžného JS pole — ~4× méně paměti
- **Gradient cache:** Pokud `createRadialGradient` na canvasu, cachovat objekt mimo animFrame
- **LED blikání:** CSS animace (`@keyframes`) jsou výkonnější než JS `setInterval` pro toggle tříd
- **SVG elektrody:** `classList.add/remove` místo `setAttribute('class', ...)` — méně repaint

---

*Poslední aktualizace: v2.0 · Projekt 4dive.cz · IDDA Trainer #12392*
