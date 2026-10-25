import os
import re
import json
import time
from deep_translator import GoogleTranslator

# Языки, доступные для перевода. Ключ — код для GoogleTranslator,
# значение — (название на русском, ключ локализации HOI4, например "l_english")
LANGUAGES = {
    "en": ("Английский", "l_english"),
    "ru": ("Русский", "l_russian"),
    "de": ("Немецкий", "l_german"),
    "fr": ("Французский", "l_french"),
    "es": ("Испанский", "l_spanish"),
    "pl": ("Польский", "l_polish"),
    "pt": ("Португальский (бразильский)", "l_braz_por"),
    "ja": ("Японский", "l_japanese"),
    "zh-CN": ("Китайский (упрощённый)", "l_simp_chinese"),
    "ko": ("Корейский", "l_korean"),
    "tr": ("Турецкий", "l_turkish"),
}


def choose_language(prompt):
    codes = list(LANGUAGES.keys())
    print(f"\n{prompt}")
    for i, code in enumerate(codes, 1):
        name, locale_key = LANGUAGES[code]
        print(f"  {i}. {name} ({locale_key})")

    while True:
        choice = input("Введите номер: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(codes):
            return codes[int(choice) - 1]
        print("Некорректный ввод, попробуйте ещё раз.")


def choose_languages():
    src_code = choose_language("С какого языка переводим мод?")
    while True:
        tgt_code = choose_language("На какой язык переводим мод?")
        if tgt_code != src_code:
            break
        print("Язык перевода не может совпадать с исходным языком.")

    src_name, src_locale = LANGUAGES[src_code]
    tgt_name, tgt_locale = LANGUAGES[tgt_code]
    print(f"\n➡️  Перевод: {src_name} ({src_locale}) → {tgt_name} ({tgt_locale})\n")
    return src_code, tgt_code, src_locale, tgt_locale


SRC_LANG, TGT_LANG, SRC_LOCALE, TGT_LOCALE = choose_languages()

translator = GoogleTranslator(source=SRC_LANG, target=TGT_LANG)
translation_cache_file = f"translation_cache_{SRC_LANG}_{TGT_LANG}.json"

if os.path.exists(translation_cache_file):
    with open(translation_cache_file, "r", encoding="utf-8") as f:
        translation_cache = json.load(f)
else:
    translation_cache = {}

# Глоссарий названий стран Paradox-игр (сейчас заполнен только для EN → RU).
# Для других языковых пар просто не применяется.
COUNTRIES_EN_RU = {
    "germany": "Германия", "german": "Германский", "germans": "Немцы",
    "soviet union": "Советский Союз", "soviets": "Советский Союз", "soviet": "Советский",
    "ussr": "СССР",
    "united states": "США", "usa": "США", "american": "Американский", "americans": "Американцы",
    "united kingdom": "Великобритания", "britain": "Великобритания", "british": "Британский",
    "france": "Франция", "french": "Французский",
    "italy": "Италия", "italian": "Итальянский", "italians": "Итальянцы",
    "japan": "Япония", "japanese": "Японский",
    "china": "Китай", "chinese": "Китайский",
    "afghanistan": "Афганистан", "afghan": "Афганский",
    "albania": "Албания", "albanian": "Албанский",
    "austria": "Австрия", "austrian": "Австрийский",
    "belgium": "Бельгия", "belgian": "Бельгийский",
    "bulgaria": "Болгария", "bulgarian": "Болгарский",
    "czechoslovakia": "Чехословакия", "czechoslovak": "Чехословацкий",
    "denmark": "Дания", "danish": "Датский",
    "estonia": "Эстония", "estonian": "Эстонский",
    "finland": "Финляндия", "finnish": "Финский", "finns": "Финны",
    "greece": "Греция", "greek": "Греческий",
    "hungary": "Венгрия", "hungarian": "Венгерский",
    "ireland": "Ирландия", "irish": "Ирландский",
    "latvia": "Латвия", "latvian": "Латвийский",
    "lithuania": "Литва", "lithuanian": "Литовский",
    "luxembourg": "Люксембург",
    "netherlands": "Нидерланды", "dutch": "Голландский",
    "norway": "Норвегия", "norwegian": "Норвежский",
    "poland": "Польша", "polish": "Польский",
    "portugal": "Португалия", "portuguese": "Португальский",
    "romania": "Румыния", "romanian": "Румынский",
    "slovakia": "Словакия", "slovak": "Словацкий",
    "spain": "Испания", "spanish": "Испанский",
    "sweden": "Швеция", "swedish": "Шведский",
    "switzerland": "Швейцария", "swiss": "Швейцарский",
    "turkey": "Турция", "turkish": "Турецкий",
    "yugoslavia": "Югославия", "yugoslav": "Югославский",
    "croatia": "Хорватия", "croatian": "Хорватский",
    "serbia": "Сербия", "serbian": "Сербский",
    "ukraine": "Украина", "ukrainian": "Украинский",
    "belarus": "Беларусь", "belarusian": "Белорусский",
    "iceland": "Исландия", "icelandic": "Исландский",
    "manchukuo": "Маньчжоу-го",
    "mongolia": "Монголия", "mongolian": "Монгольский",
    "tibet": "Тибет", "tibetan": "Тибетский",
    "india": "Индия", "indian": "Индийский",
    "iran": "Иран", "iranian": "Иранский", "persia": "Персия", "persian": "Персидский",
    "iraq": "Ирак", "iraqi": "Иракский",
    "syria": "Сирия", "syrian": "Сирийский",
    "saudi arabia": "Саудовская Аравия", "saudi": "Саудовский",
    "thailand": "Таиланд", "thai": "Таиландский",
    "siam": "Сиам", "siamese": "Сиамский",
    "vietnam": "Вьетнам", "vietnamese": "Вьетнамский",
    "korea": "Корея", "korean": "Корейский",
    "philippines": "Филиппины", "filipino": "Филиппинский",
    "indonesia": "Индонезия", "indonesian": "Индонезийский",
    "burma": "Бирма", "burmese": "Бирманский",
    "ethiopia": "Эфиопия", "ethiopian": "Эфиопский",
    "egypt": "Египет", "egyptian": "Египетский",
    "libya": "Ливия", "libyan": "Ливийский",
    "morocco": "Марокко", "moroccan": "Марокканский",
    "algeria": "Алжир", "algerian": "Алжирский",
    "south africa": "Южная Африка", "south african": "Южноафриканский",
    "canada": "Канада", "canadian": "Канадский",
    "mexico": "Мексика", "mexican": "Мексиканский",
    "brazil": "Бразилия", "brazilian": "Бразильский",
    "argentina": "Аргентина", "argentinian": "Аргентинский",
    "chile": "Чили", "chilean": "Чилийский",
    "colombia": "Колумбия", "colombian": "Колумбийский",
    "venezuela": "Венесуэла", "venezuelan": "Венесуэльский",
    "peru": "Перу", "peruvian": "Перуанский",
    "australia": "Австралия", "australian": "Австралийский",
    "new zealand": "Новая Зеландия",
    "nationalist china": "Националистический Китай",
    "communist china": "Коммунистический Китай",
    "vichy france": "Режим Виши", "vichy": "Виши",
    "free france": "Свободная Франция",
    "british raj": "Британская Индия",
    "axis": "Ось", "allies": "Союзники", "comintern": "Коминтерн",
    "reich": "Рейх", "reichskommissariat": "Рейхскомиссариат",
}

# Глоссарий применяется, только если выбранная пара языков — EN → RU.
COUNTRIES = COUNTRIES_EN_RU if (SRC_LANG, TGT_LANG) == ("en", "ru") else {}

var_pattern = r'(\$.*?\$|\[.*?\]|§.)'

def protect_variables(text):
    vars_found = re.findall(var_pattern, text)
    protected = text
    for i, v in enumerate(vars_found):
        protected = protected.replace(v, f"__VAR{i}__")
    return protected, vars_found

def restore_variables(text, vars_found):
    for i, v in enumerate(vars_found):
        text = text.replace(f"__VAR{i}__", v)
    return text

def apply_countries(text):
    if not COUNTRIES:
        return text
    result = text
    for eng, rus in sorted(COUNTRIES.items(), key=lambda x: -len(x[0])):
        pattern = re.compile(r'\b' + re.escape(eng) + r'\b', re.IGNORECASE)
        result = pattern.sub(rus, result)
    return result

def translate_one(text):
    if text in translation_cache:
        return translation_cache[text]

    protected, vars_found = protect_variables(text)
    try:
        translated = translator.translate(protected)
        if not translated:
            translated = protected
    except Exception:
        translated = protected

    translated = restore_variables(translated, vars_found)
    translated = apply_countries(translated)
    translation_cache[text] = translated
    return translated

def format_time(seconds):
    if seconds < 60:
        return f"{int(seconds)}с"
    elif seconds < 3600:
        return f"{int(seconds//60)}м {int(seconds%60)}с"
    else:
        return f"{int(seconds//3600)}ч {int((seconds%3600)//60)}м"

def process_file(file, file_num, total_files):
    print(f"\n{'='*50}")
    print(f"📄 Файл {file_num}/{total_files}: {file}")

    with open(file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    total_lines = len(lines)
    new_lines = []
    start_time = time.time()
    translated_count = 0

    for i, line in enumerate(lines):
        if f"{SRC_LOCALE}:" in line:
            new_lines.append(line.replace(f"{SRC_LOCALE}:", f"{TGT_LOCALE}:"))
            continue

        match = re.search(r'"([^"]+)"', line)
        if match:
            text = match.group(1)
            if text.strip():
                translated = translate_one(text)
                line = line[:match.start(1)] + translated + line[match.end(1):]
                translated_count += 1

                # Сохраняем кэш каждые 100 строк
                if translated_count % 100 == 0:
                    with open(translation_cache_file, "w", encoding="utf-8") as f:
                        json.dump(translation_cache, f, ensure_ascii=False, indent=2)

        new_lines.append(line)

        # Прогресс каждые 50 строк
        if (i + 1) % 50 == 0 or i == total_lines - 1:
            elapsed = time.time() - start_time
            percent = (i + 1) / total_lines * 100
            if elapsed > 0 and i > 0:
                speed = (i + 1) / elapsed
                remaining = (total_lines - i - 1) / speed
                eta = format_time(remaining)
            else:
                eta = "?"
            print(f"\r  Прогресс: {percent:.1f}% ({i+1}/{total_lines} строк) | Осталось: {eta}    ", end="")

    # Финальное сохранение кэша
    with open(translation_cache_file, "w", encoding="utf-8") as f:
        json.dump(translation_cache, f, ensure_ascii=False, indent=2)

    print(f"\r  Прогресс: 100.0% ({total_lines}/{total_lines} строк)                    ")

    new_file = file.replace(f"_{SRC_LOCALE}.yml", f"_{TGT_LOCALE}.yml")
    if new_file == file:
        new_file = file.replace(".yml", f"_{TGT_LOCALE}.yml")

    with open(new_file, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    elapsed = time.time() - start_time
    print(f"   Переведено {translated_count} строк за {format_time(elapsed)} → {new_file}")

def main():
    # В первую очередь ищем файлы, относящиеся к исходному языку.
    files = [
        f for f in os.listdir()
        if f.endswith(".yml") and SRC_LOCALE in f and TGT_LOCALE not in f
    ]

    # Если по локализационному ключу ничего не нашлось — берём все .yml,
    # кроме тех, что уже переведены на целевой язык.
    if not files:
        files = [
            f for f in os.listdir()
            if f.endswith(".yml") and TGT_LOCALE not in f
        ]

    if not files:
        print(" YML файлы не найдены")
        return

    total_files = len(files)
    print(f"🚀 Найдено файлов: {total_files}")
    total_start = time.time()

    for i, file in enumerate(files, 1):
        process_file(file, i, total_files)

        total_elapsed = time.time() - total_start
        total_percent = i / total_files * 100
        avg_time = total_elapsed / i
        remaining_files = total_files - i
        total_eta = format_time(remaining_files * avg_time)
        print(f" Общий прогресс: {total_percent:.1f}% ({i}/{total_files} файлов) | До конца: {total_eta}")

    print(f"\n Всё готово за {format_time(time.time() - total_start)}!")

if __name__ == "__main__":
    main()
