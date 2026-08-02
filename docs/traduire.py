from bs4 import BeautifulSoup, NavigableString
from pathlib import Path

input_file = Path("bloc_system_add.html")
output_file = Path("bloc_system_add_en.html")
output_file.parent.mkdir(exist_ok=True)

translations = {
    "Le bloc <add> est l’équivalent de l’opérateur « + » en Python, il permet soit :": "The <add> block is equivalent to the Python \"+\" operator. It can be used to:",
    "l’addition de 2 nombres": "add two numbers",
    "La concaténation de 2 éléments (chaînes de caractères, list, tuple)": "concatenate two elements (strings, list, tuple)",
    "Se reporter à la documentation Python pour plus de détails.": "Refer to the Python documentation for more details.",
    "« a » : La valeur par défaut est 0 (type int)": "\"a\": The default value is 0 (int type)",
    "« b » : La valeur par défaut est 0 (type int)": "\"b\": The default value is 0 (int type)",
    "« out » : Son type est fonction du type des entrées": "\"out\": Its type depends on the input types",
    "Si une des entrée est de type : int, float ou complex, l’autre entrée doit aussi faire partie de l’un de ces 3 types.": "If one of the inputs is of type int, float, or complex, the other input must also be one of these three types.",
    "Si une des entrées est de type « chaîne de caractères », l’autre entrée doit être de même type": "If one of the inputs is a string, the other input must be of the same type",
    "Si une des entrées est de type « list », l’autre entrée doit être de même type": "If one of the inputs is a list, the other input must be of the same type",
    "Si une des entrées est de type « tuple », l’autre entrée doit être de même type": "If one of the inputs is a tuple, the other input must be of the same type",
}

def translate_text(text):
    stripped = text.strip()
    if stripped in translations:
        return text.replace(stripped, translations[stripped])
    for fr, en in translations.items():
        if fr in text:
            return text.replace(fr, en)
    return text

html = input_file.read_text(encoding="utf-8")
soup = BeautifulSoup(html, "html.parser")

for node in soup.find_all(string=True):
    if isinstance(node, NavigableString):
        parent = node.parent.name if node.parent else None
        if parent not in ["script", "style"]:
            new_text = translate_text(str(node))
            if new_text != str(node):
                node.replace_with(new_text)

output_file.write_text(str(soup), encoding="utf-8")
print(f"Written to {output_file}")