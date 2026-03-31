# resources.md — Reference, manuály a doporučené zdroje

> Zdroje pro implementaci AED trenažéru a pro obsah záložky „Zdroje" v aplikaci.
> Sekce označená ★ = zobrazit uživatelům přímo v aplikaci (záložka Resources).

---

## Philips HeartStart FRx — dokumentace přístroje

### Manuály a technické specifikace
| Dokument | URL | Použití |
|---|---|---|
| Owner's Manual (EN, ed. 13) | `https://www.documents.philips.com/doclib/enc/fetch/577817/577818/FRx_Defibrillator_Owner_s_Manual_(ENGLISH)_Edition_13.pdf` | Přesné hlášky, pořadí kroků, blikání i-tlačítka |
| Quick Reference Guide | Součástí manuálu, Appendix | Shrnutí 3 kroků pro záchrance |
| Technické spec. | `https://www.usa.philips.com/healthcare/product/HC861304/heartstart-frx` | Rozměry, energie výboje, IP rating |

### Klíčové parametry FRx pro simulátor
```
Model:              Philips HeartStart FRx (M3861A)
Energie výboje:     150 J (dospělý) / 50 J (dítě s klíčem)
Nabíjecí čas:       typicky < 8 s po KPR (Quick Shock)
Analýza rytmu:      ~8–13 s
Blikání i-tlačítka: 30 s po každé analýze
Hlasový jazyk:      cs-CZ (v ČR standardně)
IP rating:          IP55 (prach + voda)
Hmotnost:           1.5 kg (s baterií a elektrodami)
```

### Umístění elektrod (pro SVG diagram)
```
Elektroda 1 (STERNUM):
  Pozice:  pravý horní hrudník, pod pravou klíční kostí,
           vedle hrudní kosti, medioklavikulární čára
  SVG:     rect x=140 y=44 (viz spec §2.4)

Elektroda 2 (APEX):
  Pozice:  levý laterální hrudník, přední axilární čára,
           5. mezižeberní prostor (přibližně)
  SVG:     rect x=222 y=82 (viz spec §2.4)

Pediatrický režim (< 8 let nebo < 25 kg):
  Předozadní rozmístění — el.1 přední hrudník střed,
  el.2 levá lopatka (nebo levé záda střed)
```

---

## ★ Resuscitační guidelines (zobrazit v aplikaci)

### ERC Guidelines 2025 — klíčové parametry pro KPR
**Zdroj:** European Resuscitation Council
**Publikováno:** 22. října 2025, Rotterdam (nahrazují guidelines 2021)
**Implementace v kurzech:** od ledna 2026
**URL:** `https://www.erc.edu/science-research/guidelines/guidelines-2025/guidelines-2025-english`
**Interaktivní přehled:** `https://cprguidelines.eu/guidelines-2025`
**BLS guidelines fulltext:** `https://www.resuscitationjournal.com/article/S0300-9572(25)00283-7/fulltext`

```
Frekvence kompresí:  100–120 / min  (beze změny oproti 2021)
Hloubka kompresí:   5–6 cm (dospělý), 1/3 průměru hrudníku (dítě)  (beze změny)
Poměr kompresí:     30 : 2 (1 zachránce), 15 : 2 (2 zachránci + dítě)  (beze změny)
Vdechy:             každý ~1 s, viditelné zdvihání hrudníku  (beze změny)
Přerušení KPR:      maximálně < 10 s (pro analýzu nebo výboj)  (beze změny)
Energie výboje:     150–200 J bifázický (1. výboj), escalating nebo stejná  (beze změny)
Frekvence analýzy:  každé 2 minuty KPR  (beze změny)
```

### Klíčové změny v ERC 2025 oproti 2021
```
1. Volat 155/112 IHNED po zjištění bezvědomí — nemusíte nejprve ověřovat dýchání
2. Změna vektoru elektrod po 3 neúspěšných výbojích (antero-lat → antero-post)
3. Řetězec přežití rozšířen o prevenci zástavy a dlouhodobý recovery
4. První pomoc jako nová samostatná kapitola guidelines
5. AED: doporučení PROTI zamykaným skříňkám pro veřejné defibrilátory
```

### Česká resuscitační rada (ČRR)
**URL:** `https://www.resuscitace.cz/`
**Doporučení:** `https://www.resuscitace.cz/guidelines/`
**ERC 2025 algoritmy v češtině:** `https://zachrannasluzba.cz/aktualita-erc-guidelines-2025-publikovany/`
**Školení PP / Guidelines 2025:** `https://skoleniprvnipomoci.cz/vyukovy-portal/guidelines-erc-kpr-2025/`
Obsahuje česky psané postupy odpovídající ERC 2025.

### Resuscitation Council UK (RCUK)
**URL:** `https://www.resus.org.uk/`
**Guidelines 2025:** `https://www.resus.org.uk/professional-library/2025-resuscitation-guidelines`
**Adult BLS 2025:** `https://www.resus.org.uk/professional-library/2025-resuscitation-guidelines/adult-basic-life-support-guidelines`
**Změny oproti 2021:** `https://www.resus.org.uk/professional-library/2025-resuscitation-guidelines/executive-summary-main-changes-2021-guidelines`
Referenční zdroj pro BLS algoritmy — přehledné flowcharty, volně dostupné PDF postery.

### International Liaison Committee on Resuscitation (ILCOR)
**URL:** `https://www.ilcor.org/`
**Consensus on Science (CoSTR):** `https://costr.ilcor.org/`
Mezinárodní koordinační orgán — vydává vědecké konsenzy, na kterých staví ERC, AHA i další.

### American Heart Association (AHA)
**CPR & ECC Guidelines:** `https://cpr.heart.org/`
**Chain of Survival:** `https://www.heart.org/en/health-topics/cardiac-arrest/about-cardiac-arrest/chain-of-survival`
Americké guidelines — obsahově shodné s ERC, ale s drobnými odlišnostmi v dávkování a postupech.

### European Resuscitation Council — kurzy a materiály
**Hlavní web ERC:** `https://www.erc.edu/`
**BLS Provider Course:** `https://www.erc.edu/courses/bls`
**Guidelines 2025 pro laiky (PDF):** `https://www.erc.edu/media/p5ymaeej/gl2025_layperson_book_ipdf-v11-e.pdf`
**ERC Download Centre:** `https://www.erc.edu/download-centre/`
Standardizované kurzy s mezinárodní certifikací — BLS, ALS, EPALS, NLS.

### ★ Řetězec přežití (Chain of Survival) — zobrazit v záložce Resources
```
1. Časné rozpoznání + přivolání pomoci (155 / 112)
2. Časná KPR (30:2, tvrdě a rychle)
3. Časná defibrilace (AED < 3–5 min od kolapsu)
4. Rozšířená resuscitace (záchranná služba)
5. Komplexní péče po resuscitaci (nemocnice)
```

---

## Web Speech API — reference

### MDN dokumentace
| API | URL |
|---|---|
| `SpeechSynthesis` | `https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis` |
| `SpeechSynthesisUtterance` | `https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesisUtterance` |
| `getVoices()` | `https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis/getVoices` |

### Dostupnost cs-CZ hlasu v prohlížečích
| Prohlížeč | cs-CZ hlas | Poznámka |
|---|---|---|
| Chrome (Windows) | ✅ Microsoft Zuzana / Google (offline) | Nejlepší kvalita |
| Chrome (macOS) | ✅ Zuzana (pokud nainstalována) | Nainstalovat v Nastavení → Accessibility |
| Edge (Windows) | ✅ Microsoft Zuzana Online | Výborná kvalita, TTS online |
| Firefox | ⚠️ závisí na OS | Používá systémový TTS |
| Safari (macOS) | ⚠️ závisí na nainstalovaných hlasech | |
| Chrome (Android) | ✅ Google česky | Funguje spolehlivě |
| Safari (iOS) | ❌ nespolehlivé | Doporučit Chrome |

### Instalace českého hlasu (Windows 11)
```
Nastavení → Čas a jazyk → Mluvené slovo → Přidat hlasy
→ vybrat "Čeština (Česká republika)" → Stáhnout
```

### Instalace českého hlasu (macOS)
```
Předvolby systému → Usnadnění → Obsah řečeného → Spravovat hlasy
→ vyhledat "Czech" → stáhnout Zuzana
```

---

## Web Audio API — reference

| Třída | MDN URL | Použití v projektu |
|---|---|---|
| `AudioContext` | `https://developer.mozilla.org/en-US/docs/Web/API/AudioContext` | Hlavní kontext |
| `OscillatorNode` | `https://developer.mozilla.org/en-US/docs/Web/API/OscillatorNode` | Generátor tónů |
| `GainNode` | `https://developer.mozilla.org/en-US/docs/Web/API/GainNode` | Hlasitost + fade |
| `AudioContext.currentTime` | součást AudioContext | Přesný timing metronomu |

### Frekvence zvuků (ladění pro realismus)
```
Startup sweep:      440 Hz → 880 Hz (oktáva nahoru = „probuzení")
Analýza pípání:     1000 Hz, square wave (ostré, alarmující)
Nabíjecí sweep:     200 Hz → 2000 Hz, sawtooth (naléhavé stoupání)
Výboj:              150 Hz, square, 0.3 s, volume 0.55 (tupý úder)
Metronom:           880 Hz, sine, 0.08 s (jemný, nedráždí)
Varování baterie:   800 Hz, triangle, 3× (méně agresivní)
```

---

## Canvas 2D API — reference

| Metoda | Použití |
|---|---|
| `ctx.beginPath()` | Začátek nové křivky EKG |
| `ctx.lineTo(x, y)` | Bod EKG křivky |
| `ctx.stroke()` | Vykreslení křivky |
| `ctx.fillRect(0, 0, w, h)` | Mazání předchozího framu |
| `ctx.fillText()` | ANALÝZA overlay text |
| `window.devicePixelRatio` | HiDPI korekce |

---

## ★ AED v České republice — pro záložku Resources v aplikaci

### Mapa AED (aplikace Záchranka)
- **Web:** `https://www.zachrankaapp.cz/aed`
- **Aplikace:** Záchranka (iOS / Android) — zobrazí nejbližší AED v okolí
- Databáze obsahuje všechny veřejně dostupné AED v ČR, propojená se ZZS

### Nejčastější AED přístroje v ČR
| Přístroj | Výrobce | Poznámka |
|---|---|---|
| HeartStart FRx | Philips | **Modelový přístroj tohoto trenažéru** |
| HeartStart OnSite (HS1) | Philips | Plně automatický, pro laiky |
| LIFEPAK CR2 | Stryker (Physio-Control) | Běžný ve firmách |
| ZOLL AED Plus | ZOLL | Unikátní elektrody s CPR feedbackem |
| HeartSine Samaritan PAD | HeartSine | Kompaktní, lehký |
| CardioAid-1 | INNOMED / Spencer | Nejprodávanější 2024 v ČR |

### Právní rámec — AED v ČR
```
Zákon č. 374/2011 Sb. o zdravotnické záchranné službě:
  § 19 — povinnost poskytnout první pomoc
  
AED není zdravotnický prostředek „vyžadující odbornou způsobilost"
→ smí ho použít kdokoliv, bez certifikace

Trestní zákoník § 150 — neposkytnutí pomoci:
  Kdo osobě v ohrožení neposkytne pomoc, může být trestně odpovědný.
```

### ★ Doporučené kurzy první pomoci
| Organizace | URL | Typ kurzu |
|---|---|---|
| Český červený kříž | `https://www.cervenykriz.eu` | Základní + rozšířené KPR |
| Záchranný kruh | `https://www.zachrannykruh.cz` | Online + prezenční, vzdělávání |
| IDDA (4dive.cz) | `https://4dive.cz` | Diving + first aid |
| Resuscitace.cz | `https://www.resuscitace.cz` | Odborné kurzy, ERC certifikace |

### ★ Další české a právní zdroje
| Zdroj | URL | Popis |
|---|---|---|
| Zákon č. 374/2011 Sb. | `https://www.zakonyprolidi.cz/cs/2011-374` | Zákon o ZZS, §19 povinnost poskytnout PP |
| Aplikace Záchranka | `https://www.zachrankaapp.cz` | Mapa AED, tísňové volání, propojení se ZZS |
| Trestní zákoník §150 | `https://www.zakonyprolidi.cz/cs/2009-40` | Neposkytnutí pomoci |

### Dokumentace výrobců AED (pro skin reference)
| Výrobce | URL | Model |
|---|---|---|
| Philips HeartStart FRx | viz sekce nahoře | M3861A |
| ZOLL AED Plus | `https://www.zoll.com/medical-products/aed-plus` | CPR-D padz, real-time CPR feedback |
| HeartSine Samaritan PAD | `https://www.heartsine.com/` | PAD 360P — plně automatický |

---

## ★ Záložka „O projektu" — text pro aplikaci

```
AED Trenažér · HeartStart FRx Simulator

Tento trenažér byl vytvořen jako open-source výcvikový nástroj
pro nácvik obsluhy automatického externího defibrilátoru.

Modelovým přístrojem je Philips HeartStart FRx — jeden z nejrozšířenějších
AED v České republice.

Hlasové instrukce odpovídají guidelines ERC 2025.
Simulace není náhradou za certifikovaný kurz první pomoci.

Autor: IDDA Trainer #12392
Web:   4dive.cz
```

---

## Nasazení — doporučené platformy

| Platforma | URL | Plán | Vhodné pro |
|---|---|---|---|
| **Netlify Drop** | `app.netlify.com/drop` | Zdarma | Rychlé sdílení, okamžitá URL |
| **GitHub Pages** | `pages.github.com` | Zdarma | Verzování, vlastní doména |
| **Vercel** | `vercel.com` | Zdarma (hobby) | CI/CD z GitHubu |
| **Cloudflare Pages** | `pages.cloudflare.com` | Zdarma | Nejrychlejší CDN, vlastní doména |

### Doporučená URL struktura pro GitHub Pages
```
github.com/[username]/aed-trenazor
→ pages:  https://[username].github.io/aed-trenazor
→ custom: https://aed.4dive.cz  (CNAME do GitHub Pages)
```

---

## CDN knihovny (použitelné bez buildu)

Všechny z `cdnjs.cloudflare.com` — spolehlivé, rychlé, bez tracking:

```html
<!-- QR kód (varianta C v donate modalu) -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>

<!-- Google Fonts (Rajdhani + IBM Plex Sans) -->
<link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@700;900&family=IBM+Plex+Sans:wght@400;700&display=swap" rel="stylesheet">
```

---

*Poslední aktualizace: v3.0 (ERC 2025) · Projekt 4dive.cz · IDDA Trainer #12392*
