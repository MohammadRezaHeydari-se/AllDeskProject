from __future__ import annotations

import enum
from dataclasses import dataclass


class VoiceGender(enum.Enum):
    MALE = "male"
    FEMALE = "female"


@dataclass(frozen=True)
class VoiceProfile:
    id: str
    name: str
    gender: VoiceGender
    age: int
    tone: str
    language: str
    edge_voice: str
    edge_pitch: str = "+0Hz"
    edge_rate: str = "+0%"
    description: str = ""


def _v(id: str, name: str, gender: VoiceGender, age: int, tone: str,
       lang: str, edge_voice: str, pitch: str = "+0Hz", rate: str = "+0%") -> VoiceProfile:
    tone_en = tone.split("|")[0]
    return VoiceProfile(id, name, gender, age, tone, lang, edge_voice, pitch, rate, tone_en)


VOICE_CATALOG: list[VoiceProfile] = [
    # ── English (10 distinct voices, natural speed) ──
    _v("en_10_boy",    "Leo",         VoiceGender.MALE,   10, "Energetic young storyteller",                      "en", "en-US-EricNeural",           "+30Hz", "+0%"),
    _v("en_12_girl",   "Luna",        VoiceGender.FEMALE, 12, "Bright cheerful narrator",                         "en", "en-US-AnaNeural",            "+25Hz", "+0%"),
    _v("en_16_boy",    "Noah",        VoiceGender.MALE,   16, "Casual friendly teen voice",                        "en", "en-US-BrianNeural",          "+12Hz", "+0%"),
    _v("en_18_girl",   "Emma",        VoiceGender.FEMALE, 18, "Expressive warm narrator",                          "en", "en-US-EmmaNeural",           "+6Hz",  "+0%"),
    _v("en_25_man",    "Liam",        VoiceGender.MALE,   25, "Confident engaging storyteller",                    "en", "en-US-AndrewNeural",         "+0Hz",  "+0%"),
    _v("en_28_woman",  "Ava",         VoiceGender.FEMALE, 28, "Caring pleasant voice",                             "en", "en-US-AvaNeural",             "+0Hz",  "+0%"),
    _v("en_40_man",    "Christopher", VoiceGender.MALE,   40, "Authoritative deep narrator",                       "en", "en-US-ChristopherNeural",     "-5Hz",  "+0%"),
    _v("en_45_woman",  "Michelle",    VoiceGender.FEMALE, 45, "Friendly warm storyteller",                         "en", "en-US-MichelleNeural",       "-5Hz",  "+0%"),
    _v("en_60_man",    "Arthur",      VoiceGender.MALE,   60, "Wise experienced voice",                            "en", "en-GB-RyanNeural",           "-15Hz", "+0%"),
    _v("en_65_woman",  "Eleanor",     VoiceGender.FEMALE, 65, "Soothing calm narrator",                            "en", "en-GB-LibbyNeural",          "-15Hz", "+0%"),

    # ── Swedish (10 voices, 2 base + pitch variations, natural speed) ──
    _v("sv_10_boy",    "Erik",        VoiceGender.MALE,   10, "Ung livlig berättare|Lively young storyteller",     "sv", "sv-SE-MattiasNeural", "+30Hz", "+0%"),
    _v("sv_12_girl",   "Maja",        VoiceGender.FEMALE, 12, "Glad glad röst|Happy cheerful voice",                "sv", "sv-SE-SofieNeural",   "+25Hz", "+0%"),
    _v("sv_16_boy",    "Oskar",       VoiceGender.MALE,   16, "Avslappnad tonåring|Casual teen",                     "sv", "sv-SE-MattiasNeural", "+12Hz", "+0%"),
    _v("sv_17_girl",   "Elin",        VoiceGender.FEMALE, 17, "Varm berättarröst|Warm narrator",                     "sv", "sv-SE-SofieNeural",   "+10Hz", "+0%"),
    _v("sv_25_man",    "William",     VoiceGender.MALE,   25, "Självsäker berättare|Confident storyteller",          "sv", "sv-SE-MattiasNeural", "+0Hz",  "+0%"),
    _v("sv_28_woman",  "Alice",       VoiceGender.FEMALE, 28, "Vänlig tydlig röst|Friendly clear voice",            "sv", "sv-SE-SofieNeural",   "+0Hz",  "+0%"),
    _v("sv_40_man",    "Henrik",      VoiceGender.MALE,   40, "Djup auktoritativ|Deep authoritative",               "sv", "sv-SE-MattiasNeural", "-5Hz",  "+0%"),
    _v("sv_42_woman",  "Sofia",       VoiceGender.FEMALE, 42, "Lugn tydlig röst|Calm clear voice",                  "sv", "sv-SE-SofieNeural",   "-5Hz",  "+0%"),
    _v("sv_60_man",    "Gustav",      VoiceGender.MALE,   60, "Erfaren vis berättare|Experienced wise narrator",    "sv", "sv-SE-MattiasNeural", "-15Hz", "+0%"),
    _v("sv_65_woman",  "Ingrid",      VoiceGender.FEMALE, 65, "Mjuk lugnande röst|Soft soothing voice",             "sv", "sv-SE-SofieNeural",   "-15Hz", "+0%"),

    # ── Persian (10 voices, 2 base + pitch variations, natural speed) ──
    _v("fa_10_boy",    "Parsa",       VoiceGender.MALE,   10, "پر انرژی و جوان|Energetic young",          "fa", "fa-IR-FaridNeural",   "+30Hz", "+0%"),
    _v("fa_12_girl",   "Nila",        VoiceGender.FEMALE, 12, "شاد و سرزنده|Happy lively",                "fa", "fa-IR-DilaraNeural",  "+25Hz", "+0%"),
    _v("fa_16_boy",    "Kian",        VoiceGender.MALE,   16, "خودمانی و جوان|Casual young",              "fa", "fa-IR-FaridNeural",   "+12Hz", "+0%"),
    _v("fa_17_girl",   "Sara",        VoiceGender.FEMALE, 17, "راوی گرم|Warm narrator",                    "fa", "fa-IR-DilaraNeural",  "+10Hz", "+0%"),
    _v("fa_25_man",    "Mehdi",       VoiceGender.MALE,   25, "راوی با اعتماد به نفس|Confident narrator",  "fa", "fa-IR-FaridNeural",   "+0Hz",  "+0%"),
    _v("fa_28_woman",  "Leila",       VoiceGender.FEMALE, 28, "صدای زن حرفه‌ای|Professional female",      "fa", "fa-IR-DilaraNeural",  "+0Hz",  "+0%"),
    _v("fa_40_man",    "Reza",        VoiceGender.MALE,   40, "عمیق و معتبر|Deep authoritative",           "fa", "fa-IR-FaridNeural",   "-5Hz",  "+0%"),
    _v("fa_42_woman",  "Mahnaz",      VoiceGender.FEMALE, 42, "آرام و شفاف|Calm clear",                    "fa", "fa-IR-DilaraNeural",  "-5Hz",  "+0%"),
    _v("fa_60_man",    "Pedar",       VoiceGender.MALE,   60, "راوی باتجربه|Experienced narrator",         "fa", "fa-IR-FaridNeural",   "-15Hz", "+0%"),
    _v("fa_65_woman",  "Maman",       VoiceGender.FEMALE, 65, "صدای گرم مادرانه|Warm motherly voice",      "fa", "fa-IR-DilaraNeural",  "-15Hz", "+0%"),
]

VOICE_MAP: dict[str, VoiceProfile] = {v.id: v for v in VOICE_CATALOG}

DEFAULT_VOICE = "en_28_woman"


def get_voices_by_language(language: str) -> list[VoiceProfile]:
    return [v for v in VOICE_CATALOG if v.language == language]


def get_languages() -> list[str]:
    langs: list[str] = []
    seen: set[str] = set()
    for v in VOICE_CATALOG:
        if v.language not in seen:
            langs.append(v.language)
            seen.add(v.language)
    return langs
