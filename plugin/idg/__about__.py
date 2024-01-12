#! python3  # noqa: E265

"""
    Metadata about the package to easily retrieve informations about it.
    See: https://packaging.python.org/guides/single-sourcing-package-version/
"""

# ############################################################################
# ########## Libraries #############
# ##################################

# standard library
from configparser import ConfigParser
from datetime import date
from pathlib import Path

# ############################################################################
# ########## Globals ###############
# ##################################
__all__: list = [
    "__author__",
    "__copyright__",
    "__email__",
    "__license__",
    "__summary__",
    "__title__",
    "__uri__",
    "__version__",
]


DIR_PLUGIN_ROOT: Path = Path(__file__).parent
PLG_METADATA_FILE: Path = DIR_PLUGIN_ROOT.resolve() / "metadata.txt"


# ############################################################################
# ########## Functions #############
# ##################################
def plugin_metadata_as_dict() -> dict:
    """Read plugin metadata.txt and returns it as a Python dict.

    Raises:
        IOError: if metadata.txt is not found

    Returns:
        dict: dict of dicts.
    """
    config = ConfigParser()
    if PLG_METADATA_FILE.is_file():
        config.read(PLG_METADATA_FILE.resolve(), encoding="UTF-8")
        return {s: dict(config.items(s)) for s in config.sections()}
    else:
        raise IOError("Plugin metadata.txt not found at: %s" % PLG_METADATA_FILE)


# ############################################################################
# ########## Variables #############
# ##################################

# store full metadata.txt as dict into a var
__plugin_md__: dict = plugin_metadata_as_dict()

__author__: str = __plugin_md__.get("general").get("author")
__copyright__: str = "2022 - {0}, {1}".format(date.today().year, __author__)
__email__: str = __plugin_md__.get("general").get("email")
__icon_path__: Path = DIR_PLUGIN_ROOT.resolve() / __plugin_md__.get("general").get(
    "icon"
)
__keywords__: list = [
    t.strip() for t in __plugin_md__.get("general").get("repository").split("tags")
]
__license__: str = "GNU Public License (GPL) Version 2"
__summary__: str = "{}\n{}".format(
    __plugin_md__.get("general").get("description"),
    __plugin_md__.get("general").get("about"),
)

__title__: str = __plugin_md__.get("general").get("name")
__title_clean__: str = "".join(e for e in __title__ if e.isalnum())

__uri_homepage__: str = __plugin_md__.get("general").get("homepage")
__uri_repository__: str = __plugin_md__.get("general").get("repository")
__uri_tracker__: str = __plugin_md__.get("general").get("tracker")
__uri__: str = __uri_repository__

__version__: str = __plugin_md__.get("general").get("version")
__version_info__: tuple = tuple(
    [
        int(num) if num.isdigit() else num
        for num in __version__.replace("-", ".", 1).split(".")
    ]
)

# #############################################################################
# ##### Main #######################
# ##################################
if __name__ == "__main__":
    plugin_md = plugin_metadata_as_dict()
    assert isinstance(plugin_md, dict)
    assert plugin_md.get("general").get("name") == __title__
    print(f"Plugin: {__title__}")
    print(f"By: {__author__}")
    print(f"Version: {__version__}")
    print(f"Description: {__summary__}")
    print(f"Icon: {__icon_path__}")
    print(
        "For: %s > QGIS > %s"
        % (
            plugin_md.get("general").get("qgisminimumversion"),
            plugin_md.get("general").get("qgismaximumversion"),
        )
    )
    print(__title_clean__)
