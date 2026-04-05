#!/usr/bin/env python3
"""Generate MP3 voice files for AED Trainer using edge-tts (Microsoft Edge Neural TTS)."""

import asyncio
import edge_tts
import os

VOICE_CS = "cs-CZ-AntoninNeural"   # Czech male - calm, authoritative
VOICE_EN = "en-US-GuyNeural"       # English male - clear, professional

AUDIO_DIR = os.path.join(os.path.dirname(__file__), "..", "audio")

# Czech voice lines
CS = {
    "start":           "Přístroj zapnut. Přiložte elektrody na holou kůži pacienta.",
    "pad1_prompt":     "Přiložte elektrodu číslo jedna pod pravou klíční kost.",
    "pad1_ok":         "Elektroda jedna přiložena.",
    "pad2_prompt":     "Přiložte elektrodu číslo dvě na levý bok pacienta, pod podpaží.",
    "pad2_ok":         "Elektroda dvě přiložena.",
    "analyzing":       "Nedotýkejte se pacienta. Analyzuji srdeční rytmus.",
    "analyze_wait":    "Nedotýkejte se pacienta.",
    "shock_advised":   "Výboj doporučen. Nabíjím. Všichni pryč od pacienta!",
    "shock_ready":     "Přístroj nabit. Stiskněte oranžové tlačítko výboje.",
    "shock_clear":     "Všichni pryč!",
    "shock_delivered": "Výboj podán. Okamžitě zahajte KPR.",
    "no_shock":        "Výboj nedoporučen. Okamžitě zahajte KPR – třicet stlačení, dva vdechy.",
    "no_shock_child":  "Výboj nedoporučen. Proveďte pět úvodních vdechů, poté patnáct stlačení a dva vdechy.",
    "cpr_start":       "Zahajte KPR. Stlačujte hrudník do hloubky pět až šest centimetrů.",
    "cpr_start_child": "Proveďte pět úvodních záchranných vdechů. Poté stlačujte hrudník do hloubky asi pět centimetrů, třetinu hloubky hrudníku.",
    "initial_breaths": "Proveďte pět úvodních záchranných vdechů.",
    "cpr_depth":       "Stlačujte pevněji – minimálně pět centimetrů.",
    "cpr_depth_child": "Stlačujte pevněji – třetina hloubky hrudníku.",
    "cpr_rate":        "Udržujte frekvenci sto až sto dvacet stlačení za minutu.",
    "cpr_15":          "Patnáct stlačení – pokračujte!",
    "cpr_15_done":     "Patnáct stlačení. Proveďte dva záchranné vdechy.",
    "cpr_30":          "Třicet stlačení. Proveďte dva záchranné vdechy.",
    "breaths_done":    "Pokračujte v KPR.",
    "reanalyze":       "Analyzuji srdeční rytmus. Nedotýkejte se pacienta.",
    "rosc":            "Spontánní oběh obnoven. Zkontrolujte dýchání. Uložte do stabilizované polohy.",
    "continue_cpr":    "Pokračujte v KPR. Záchranná služba byla přivolána.",
    "shock2":          "Druhý výboj doporučen. Všichni pryč od pacienta!",
    "shock3":          "Třetí výboj doporučen. Všichni pryč od pacienta!",
    "off":             "Přístroj vypnut.",
    "end_session":     "Trénink ukončen. Prohlédněte si výsledky.",
    "low_battery":     "Baterie je slabá.",
    "pediatric_on":    "Dětský klíč vložen. Energie snížena na padesát džaulů.",
}

# English voice lines
EN = {
    "start":           "Unit on. Attach pads to the patient's bare skin.",
    "pad1_prompt":     "Place pad one below the right collarbone.",
    "pad1_ok":         "Pad one attached.",
    "pad2_prompt":     "Place pad two on the left side of the chest, below the armpit.",
    "pad2_ok":         "Pad two attached.",
    "analyzing":       "Do not touch the patient. Analyzing heart rhythm.",
    "analyze_wait":    "Do not touch the patient.",
    "shock_advised":   "Shock advised. Charging. Stand clear of the patient!",
    "shock_ready":     "Unit charged. Press the orange shock button.",
    "shock_clear":     "Stand clear!",
    "shock_delivered": "Shock delivered. Start CPR immediately.",
    "no_shock":        "No shock advised. Start CPR immediately – thirty compressions, two breaths.",
    "no_shock_child":  "No shock advised. Give five initial breaths, then fifteen compressions and two breaths.",
    "cpr_start":       "Begin CPR. Push down five to six centimetres on the chest.",
    "cpr_start_child": "Give five initial rescue breaths. Then push down about five centimetres, one third of the chest depth.",
    "initial_breaths": "Give five initial rescue breaths.",
    "cpr_depth":       "Push harder – at least five centimetres.",
    "cpr_depth_child": "Push harder – one third of chest depth.",
    "cpr_rate":        "Maintain a rate of one hundred to one hundred and twenty per minute.",
    "cpr_15":          "Fifteen compressions – keep going!",
    "cpr_15_done":     "Fifteen compressions. Give two rescue breaths.",
    "cpr_30":          "Thirty compressions. Give two rescue breaths.",
    "breaths_done":    "Continue CPR.",
    "reanalyze":       "Analyzing heart rhythm. Do not touch the patient.",
    "rosc":            "Return of spontaneous circulation. Check breathing. Place in recovery position.",
    "continue_cpr":    "Continue CPR. Emergency services have been called.",
    "shock2":          "Second shock advised. Stand clear of the patient!",
    "shock3":          "Third shock advised. Stand clear of the patient!",
    "off":             "Unit off.",
    "end_session":     "Training complete. Review your results.",
    "low_battery":     "Battery is low.",
    "pediatric_on":    "Child key inserted. Energy reduced to fifty joules.",
}


async def generate(voice, lang_code, texts):
    outdir = os.path.join(AUDIO_DIR, lang_code)
    os.makedirs(outdir, exist_ok=True)
    for key, text in texts.items():
        outpath = os.path.join(outdir, f"{key}.mp3")
        if os.path.exists(outpath):
            print(f"  SKIP {lang_code}/{key}.mp3 (exists)")
            continue
        print(f"  GEN  {lang_code}/{key}.mp3 ...")
        comm = edge_tts.Communicate(text, voice, rate="-10%", pitch="-5Hz")
        await comm.save(outpath)


async def main():
    print(f"Generating Czech voice files ({VOICE_CS})...")
    await generate(VOICE_CS, "cs", CS)
    print(f"\nGenerating English voice files ({VOICE_EN})...")
    await generate(VOICE_EN, "en", EN)
    print("\nDone!")

    # Count files and generate durations.json
    durations = {}
    for lang in ("cs", "en"):
        d = os.path.join(AUDIO_DIR, lang)
        durations[lang] = {}
        files = [f for f in os.listdir(d) if f.endswith(".mp3")]
        for f in sorted(files):
            key = f[:-4]
            try:
                import subprocess
                result = subprocess.run(
                    ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                     "-of", "csv=p=0", os.path.join(d, f)],
                    capture_output=True, text=True
                )
                durations[lang][key] = round(float(result.stdout.strip()), 2)
            except Exception:
                pass
        print(f"  {lang}: {len(files)} MP3 files")

    # Write durations.json for runtime timing
    dur_path = os.path.join(AUDIO_DIR, "durations.json")
    import json
    with open(dur_path, "w", encoding="utf-8") as f:
        json.dump(durations, f, indent=2)
    print(f"\n  durations.json written ({dur_path})")


if __name__ == "__main__":
    asyncio.run(main())
