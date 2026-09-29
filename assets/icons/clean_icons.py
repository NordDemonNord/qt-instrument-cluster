#!/usr/bin/env python3
# Убирает фоновые подложки-прямоугольники из SVG-иконок приборки.
# Такой <rect> (во всю ширину/высоту иконки, без осмысленного fill или
# чёрный) при ColorOverlay красится в сплошной квадрат. Удаляем его.
#
# Запуск из папки, где лежат иконки (assets/icons):
#     python clean_icons.py
# Скрипт правит файлы на месте, делая резервные копии *.svg.bak

import re
import glob
import os

# Иконки, у которых точно есть фоновая подложка (потрейс-конверсия).
# Остальные не трогаем.
TARGET_HINT = re.compile(r'<rect\b[^>]*\bwidth="(\d+(?:\.\d+)?)"[^>]*\bheight="(\d+(?:\.\d+)?)"[^>]*/?>')

def is_background_rect(tag, svg_w, svg_h):
    # Прямоугольник считается подложкой, если:
    #  - занимает почти всю площадь иконки (>= 90% по обеим сторонам)
    #  - и у него нет явного видимого fill (чёрный/отсутствует)
    m = re.search(r'width="(\d+(?:\.\d+)?)"', tag)
    n = re.search(r'height="(\d+(?:\.\d+)?)"', tag)
    if not (m and n):
        return False
    w = float(m.group(1)); h = float(n.group(1))
    covers = (svg_w and svg_h and w >= 0.9*svg_w and h >= 0.9*svg_h)
    # fill отсутствует (чёрный по умолчанию) или явно чёрный/none-подложка
    fill = re.search(r'fill="([^"]*)"', tag)
    fill_val = fill.group(1).strip().lower() if fill else ""
    no_visible_fill = fill_val in ("", "#000", "#000000", "black")
    return covers and no_visible_fill

def get_svg_size(text):
    vb = re.search(r'viewBox="[\d.\s]*?\s([\d.]+)\s+([\d.]+)"', text)
    if vb:
        return float(vb.group(1)), float(vb.group(2))
    w = re.search(r'<svg[^>]*\bwidth="([\d.]+)"', text)
    h = re.search(r'<svg[^>]*\bheight="([\d.]+)"', text)
    if w and h:
        return float(w.group(1)), float(h.group(1))
    return None, None

def clean_file(path):
    text = open(path, encoding="utf-8").read()
    svg_w, svg_h = get_svg_size(text)

    # Находим все <rect .../> (самозакрывающиеся)
    rects = list(re.finditer(r'<rect\b[^>]*/>', text))
    removed = 0
    for r in reversed(rects):  # с конца, чтобы не сбить индексы
        tag = r.group(0)
        if is_background_rect(tag, svg_w, svg_h):
            text = text[:r.start()] + text[r.end():]
            removed += 1

    if removed:
        # бэкап оригинала (если ещё нет) + запись очищенной версии
        bak = path + ".bak"
        if not os.path.exists(bak):
            original = open(path, encoding="utf-8").read()
            open(bak, "w", encoding="utf-8").write(original)
        open(path, "w", encoding="utf-8").write(text)
        print(f"  {os.path.basename(path)}: удалено подложек {removed}")
    return removed

def main():
    files = glob.glob("*.svg")
    if not files:
        print("SVG-файлы не найдены. Запусти скрипт из папки assets/icons.")
        return
    total = 0
    print("Очистка иконок от фоновых подложек:")
    for f in sorted(files):
        total += clean_file(f)
    print(f"\nГотово. Всего убрано подложек: {total}")
    print("Оригиналы сохранены как *.svg.bak")

if __name__ == "__main__":
    main()
