import re


def transform_wikimedia_list(file_path):
    # Read the input text from a file
    with open(file_path, "r", encoding="utf-8") as file:
        input_text = file.read()

    # Regular expression to match island names and descriptions
    regex = r"\*\s*'?'?'?(?:\[?\[?([^|\]]+)\|)?([^\]]+)\]?\]?'?'?'?(?:\s*-\s*(.*?))?(?:\s*\n|$)"

    # Find all matches
    matches = re.findall(regex, input_text)

    # Template for the formatted output
    template = "{{Citylist\n"
    for i, (alt_name, name, description) in enumerate(matches, start=1):
        # Use alternative name if available
        dest_name = alt_name if alt_name else name
        if check_if_already_wikilink(dest_name):
            dest_name = dest_name[2:-2]
        template += f"| {i}={{{{Città| nome={dest_name} | alt= | lat= | long= | wikidata= | descrizione={description}}}}}\n"
    template += "}}"

    return template


def check_if_already_wikilink(text):
    """
    Check if the specified text is already a wikilink.

    :param text: The text to check.
    :type text: str
    :return: True if the text is already a wikilink, False otherwise.
    :rtype: bool
    """
    return text.startswith("[[") and text.endswith("]]")


# File paths
input_file_path = "output/raw.txt"  # Replace with your input file path
output_file_path = (
    "output/citylist_transformed.txt"  # Replace with your desired output file path
)

# Transform the input text
formatted_output = transform_wikimedia_list(input_file_path)

# Write the output to a file
with open(output_file_path, "w", encoding="utf-8") as file:
    file.write(formatted_output)

print(f"Transformation complete. Output written to {output_file_path}")
exit(0)
