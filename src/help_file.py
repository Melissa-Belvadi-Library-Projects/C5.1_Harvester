""" Help documentation URLs for the application."""

# Help documentation URLs
HELP_URLS = {
    'main': 'https://github.com/Melissa-Belvadi-Library-Projects/C5.1_Harvester/blob/main/docs/contents.md',
    'settings': 'https://github.com/Melissa-Belvadi-Library-Projects/C5.1_Harvester/blob/main/docs/config-options.md',
    'providers': 'https://github.com/Melissa-Belvadi-Library-Projects/C5.1_Harvester/blob/main/docs/template_providers.md',
}


def get_help_url(section: str):
    """
    Get the help URL for a specific section.

    Args:
        section: Section name ('main', 'settings', 'providers')

    Returns:
        URL string for the help documentation
    """

    return HELP_URLS.get(section, HELP_URLS['main'])
