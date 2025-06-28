import re


def translate_template(input_file, output_file):
    # Mapping of English parameter names to Italian
    translation_map = {
        "name": "nome",
        "url": "sito",
        "address": "indirizzo",
        "phone": "tel",
        "tollfree": "numero verde",
        "hours": "orari",
        "price": "prezzo",
        "content": "descrizione",
    }

    inside_template = False

    try:
        with open(input_file, "r", encoding="utf-8") as infile, open(
            output_file, "w", encoding="utf-8"
        ) as outfile:
            for line in infile:
                # Check if the line is the start or end of a template
                if "{{see" in line:
                    inside_template = True
                elif inside_template and "}}" in line:
                    inside_template = False

                # Process lines inside the template
                if inside_template and "|" in line:
                    for eng, ita in translation_map.items():
                        pattern = r"\|\s*" + eng + r"\s*="
                        replacement = f"| {ita}="
                        line = re.sub(pattern, replacement, line)

                outfile.write(line)

    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Example usage
translate_template("output/raw.txt", "output/output.txt")
