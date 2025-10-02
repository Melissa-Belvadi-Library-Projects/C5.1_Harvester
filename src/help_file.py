""" Help documentation URLs for the application."""

# Help documentation URLs
HELP_URLS = {
    'main': 'https://github.com/Melissa-Belvadi-Library-Projects/C5.1_Harvester',
    'settings': 'https://github.com/Melissa-Belvadi-Library-Projects/C5.1_Harvester',
    'providers': 'https://github.com/Melissa-Belvadi-Library-Projects/C5.1_Harvester',
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
