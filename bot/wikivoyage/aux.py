import re

def is_section_empty(section_text):
    # Remove comments
    text_without_comments = re.sub(r'<!--.*?-->', '', section_text, flags=re.DOTALL)
    # Remove spacing templates
    text_without_spacing = re.sub(r'\{\{-\}\}', '', text_without_comments)

    # Remove newlines
    text_without_spacing = text_without_spacing.replace('\n', '')
    # Check if there's any content left
    return not text_without_spacing.strip()
