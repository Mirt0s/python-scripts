"""
PoB Parser - Prueba de concepto
Sin dependencias externas, solo librería estándar de Python 3.x

Uso:
    python3 poe_pob_parser.py
    python3 poe_pob_parser.py <pob_code>
"""

import base64
import zlib
import xml.etree.ElementTree as ET
import sys
import json


# ── Decode ─────────────────────────────────────────────────────────────────────

def decode_pob(code: str) -> ET.Element:
    # PoB usa base64 con variante URL-safe, hay que normalizar padding
    code = code.strip().replace("\n", "").replace(" ", "")
    # Añadir padding si falta
    missing = len(code) % 4
    if missing:
        code += "=" * (4 - missing)

    raw = base64.urlsafe_b64decode(code)
    xml_bytes = zlib.decompress(raw)
    return ET.fromstring(xml_bytes.decode("utf-8"))


# ── Extracción ─────────────────────────────────────────────────────────────────

def extract_build_info(root: ET.Element) -> dict:
    build = root.find("Build")
    if build is None:
        return {}

    return {
        "class":       build.get("className", "?"),
        "ascendancy":  build.get("ascendClassName", "?"),
        "level":       build.get("level", "?"),
        "main_skill":  build.get("mainSocketGroup", "?"),
    }


def extract_skills(root: ET.Element) -> list:
    skills = []
    skills_section = root.find("Skills")
    if skills_section is None:
        return skills
    for skill in skills_section.findall(".//Skill"):
        gems = []
        for gem in skill.findall("Gem"):
            gems.append({
                "name":    gem.get("nameSpec", "?"),
                "level":   gem.get("level", "?"),
                "quality": gem.get("quality", "0"),
                "enabled": gem.get("enabled", "true"),
            })
        slot = skill.get("slot")
        if gems and slot:
            skills.append({
                "slot":    slot,
                "enabled": skill.get("enabled", "true"),
                "gems":    gems,
            })
    return skills


def extract_items(root: ET.Element) -> list:
    items = []
    items_section = root.find("Items")
    if items_section is None:
        return items

    for item in items_section.findall("Item"):
        raw_text = item.text or ""
        lines    = [l.strip() for l in raw_text.strip().splitlines() if l.strip()]

        # La primera línea de rarity y la segunda el nombre
        rarity = ""
        name   = ""
        for line in lines:
            if line.startswith("Rarity:"):
                rarity = line.replace("Rarity:", "").strip()
            elif rarity and not name:
                name = line
                break

        items.append({
            "id":     item.get("id", "?"),
            "rarity": rarity,
            "name":   name or lines[0] if lines else "?",
        })

    # Slots equipados
    slots = {}
    for slot in items_section.findall(".//Slot"):
        slot_name = slot.get("name", "?")
        item_id   = slot.get("itemId", "0")
        if item_id != "0":
            slots[slot_name] = item_id

    # Enriquecer ítems con su slot
    id_to_item = {it["id"]: it for it in items}
    equipped   = []
    for slot_name, item_id in slots.items():
        if item_id in id_to_item:
            entry = dict(id_to_item[item_id])
            entry["slot"] = slot_name
            equipped.append(entry)

    return equipped


def extract_stats(root: ET.Element) -> list:
    build = root.find("Build")
    if build is None:
        return []

    stats = []
    for stat in build.findall("PlayerStat"):
        stats.append({
            "stat":  stat.get("stat"),
            "value": stat.get("value"),
        })
    return stats


# ── Presentación ───────────────────────────────────────────────────────────────

def print_report(data: dict) -> None:
    sep = "─" * 55

    info = data["build_info"]
    print(f"\n{'═' * 55}")
    print(f"  Personaje: {info.get('class')} / {info.get('ascendancy')}")
    print(f"  Nivel    : {info.get('level')}")
    print(f"{'═' * 55}\n")

    print(f"{sep}")
    print(f"  Ítems equipados ({len(data['equipped_items'])})")
    print(sep)
    for item in data["equipped_items"]:
        rarity = f"[{item['rarity']}]" if item["rarity"] else ""
        print(f"  {item['slot']:<22} {rarity:<10} {item['name']}")

    print(f"\n{sep}")
    print(f"  Skills")
    print(sep)
    for skill in data["skills"]:
        enabled = "" if skill["enabled"] == "true" else " (desactivado)"
        print(f"  Slot: {skill['slot']}{enabled}")
        for gem in skill["gems"]:
            active = "" if gem["enabled"] == "true" else " ✗"
            print(f"    · {gem['name']:<30} lv{gem['level']:>2}  q{gem['quality']:>2}{active}")

    print(f"\n{sep}")
    print(f"  Stats principales")
    print(sep)
    relevant = {"Life", "EnergyShield", "Mana", "TotalDPS", "CritChance", "SpellDPS"}
    for stat in data["stats"]:
        if stat["stat"] in relevant:
            try:
                val = float(stat["value"])
                print(f"  {stat['stat']:<25} {val:>12,.1f}")
            except (ValueError, TypeError):
                print(f"  {stat['stat']:<25} {stat['value']:>12}")
    print()


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) > 1:
        code = sys.argv[1]
    else:
        print("Pega tu código PoB (Enter dos veces para confirmar):")
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        code = "".join(lines)

    if not code:
        print("Error: no se proporcionó ningún código.")
        sys.exit(1)

    try:
        root = decode_pob(code)
    except Exception as e:
        print(f"Error al decodificar el código PoB: {e}")
        sys.exit(1)

    ET.indent(root, space="  ")
    with open("pob_raw.xml", "w", encoding="utf-8") as f:
        f.write(ET.tostring(root, encoding="unicode"))

    data = {
        "build_info":     extract_build_info(root),
        "equipped_items": extract_items(root),
        "skills":         extract_skills(root),
        "stats":          extract_stats(root),
    }

    print_report(data)

    # También vuelca el JSON completo por si quieres inspeccionarlo
    with open("pob_parsed.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("  JSON completo guardado en pob_parsed.json")
    print("  XML completo guardado en pob_raw.xml\n")


if __name__ == "__main__":
    main()