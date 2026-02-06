import hashlib
import os
import zipfile

ROOT = os.getcwd()
ZIPS_DIR = os.path.join(ROOT, "zips")

def strip_decl(s: str) -> str:
    s = s.strip()
    if s.startswith("<?xml"):
        s = s.split("?>", 1)[1].lstrip()
    return s

def find_addon_xml_in_zip(z: zipfile.ZipFile) -> str | None:
    cands = [n for n in z.namelist() if n.endswith("/addon.xml") or n == "addon.xml"]
    if not cands:
        cands = [n for n in z.namelist() if n.lower().endswith("/addon.xml") or n.lower() == "addon.xml"]
    if not cands:
        return None
    cands.sort(key=lambda x: (x.count("/"), len(x)))
    return cands[0]

def read_text(z: zipfile.ZipFile, name: str) -> str:
    data = z.read(name)
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            pass
    return data.decode("utf-8", errors="replace")

def main():
    if not os.path.isdir(ZIPS_DIR):
        raise SystemExit("Missing zips/ folder")

    entries: list[str] = []

    for base, _, files in os.walk(ZIPS_DIR):
        for fn in sorted(files):
            if not fn.lower().endswith(".zip"):
                continue
            zp = os.path.join(base, fn)
            with zipfile.ZipFile(zp) as z:
                ax = find_addon_xml_in_zip(z)
                if not ax:
                    continue
                xml = strip_decl(read_text(z, ax))
                entries.append(xml)

    addons_xml = "<addons>\n" + "\n".join(entries) + "\n</addons>\n"
    with open(os.path.join(ROOT, "addons.xml"), "w", encoding="utf-8", newline="\n") as f:
        f.write(addons_xml)

    md5 = hashlib.md5(addons_xml.encode("utf-8")).hexdigest()
    with open(os.path.join(ROOT, "addons.xml.md5"), "w", encoding="utf-8", newline="\n") as f:
        f.write(md5)

if __name__ == "__main__":
    main()
