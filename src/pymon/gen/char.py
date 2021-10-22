#!/usr/bin/env python


"""
Summary
-------
To create a database for playable characters.

Rational
--------
For each character, we want to extract the same information (sets of key-value pairs).
I think the best way to approach this problem is to create a (extract) function for each pair we want.
The drawback of this approach is that we will have to open and close the same (large) files repeatedly which affects performance.
But since the code is not performance critical, I believe this is the better approach.
Furthermore, this allows the code to be much more modular and extensible.

Output
------
```
{
    <Character ID>: {
        name:        <Character Name>,
        description: <Character Description>,
        rarity:      <Character Rarity>,
        element:     <Character Element Type>,
        weapon:      <Character Weapon Type>,
    },
    ...
}
```
"""


from functools import cache
import pymon.io
import pymon.log


logger = pymon.log.get_logger()


def _is_playable(character: dict) -> bool:
    """Returns whether a character is playable."""

    return character.get("UseType") == "AVATAR_FORMAL"


@cache
def _lookup_hash_of_id(text_map_id: str) -> str:
    """Given `TextMapId` return `TextMapContentTextMapHash`."""

    manual_text_map = pymon.io.read(
        "download/ExcelBinOutput/ManualTextMapConfigData.json"
    )

    for element in manual_text_map:
        if element.get("TextMapId") == text_map_id:
            return str(element.get("TextMapContentTextMapHash"))

    logger.critical("Unable to find %s in manual text map", text_map_id)
    raise RuntimeError(f"Unable to find {text_map_id} in manual text map")


@cache
def _lookup_text_map(hash_: str) -> str:
    """Given key `hash_` get corresponding value in text map."""

    text_map = pymon.io.read("download/TextMap/TextMapEN.json")

    try:
        value = text_map[hash_]
        logger.debug("%s returns %s", hash_, value)
        return value
    except KeyError:
        logger.critical("Invalid hash %s", hash_)
        raise


def _setup(characters: dict) -> None:
    """Generate a template dictionary for characters.

    ```
    {
        <Character ID>: {
            name: <Character Name>
        },
        ...
    }
    ```
    """

    character_data = pymon.io.read("download/ExcelBinOutput/AvatarExcelConfigData.json")

    for element in character_data:
        if _is_playable(element):
            character_id = str(element.get("Id"))
            character_name_hash = str(element.get("NameTextMapHash"))

            character_name = _lookup_text_map(character_name_hash)

            # special case for traveler
            if character_name.lower() == "traveler":
                # FIXME: black doesn't support 3.10 pattern matching
                # match element.get("BodyType"):
                #     case "BODY_BOY":
                #         character_name = "Aether"
                #     case "BODY_GIRL":
                #         character_name = "Lumine"
                if element.get("BodyType") == "BODY_BOY":
                    character_name = "Aether"
                elif element.get("BodyType") == "BODY_GIRL":
                    character_name = "Lumine"
                else:
                    raise NotImplementedError

            logger.debug("Name: %s, Id: %s", character_name, character_id)

            characters[character_id] = {"name": character_name}


def _add_description(characters: dict) -> None:
    """Add description to each character.

    ```
    {
        <Character ID>: {
            description: <Character Description>
        },
        ...
    }
    """

    character_data = pymon.io.read("download/ExcelBinOutput/AvatarExcelConfigData.json")
    text_hash_map = pymon.io.read("download/TextMap/TextMapEN.json")

    for element in character_data:
        if _is_playable(element):
            character_id = str(element.get("Id"))
            description_hash = str(element.get("DescTextMapHash"))

            description = text_hash_map.get(description_hash)

            logger.debug(
                "Name: %s, Description: %s",
                characters[character_id]["name"],
                description,
            )

            characters[character_id]["description"] = description


def _add_rarity(characters: dict) -> None:
    """Add rarity to each character.

    ```
    {
        <Character ID>: {
            rarity: <Character Rarity>
        },
        ...
    }
    """

    character_data = pymon.io.read("download/ExcelBinOutput/AvatarExcelConfigData.json")
    rarity_conversion = {
        "QUALITY_PURPLE": "4",
        "QUALITY_ORANGE": "5",
        "QUALITY_ORANGE_SP": "5",
    }

    for element in character_data:
        if _is_playable(element):
            character_id = str(element.get("Id"))
            character_rarity = rarity_conversion.get(element.get("QualityType"))

            logger.debug(
                "Name: %s, Rarity: %s",
                characters[character_id]["name"],
                character_rarity,
            )

            characters[character_id]["rarity"] = character_rarity


def _add_element(characters: dict) -> None:
    """Add element type to each character.

    ```
    {
        <Character ID>: {
            element: <Character Element Type>
        },
        ...
    }
    """

    fetter = pymon.io.read("download/ExcelBinOutput/FetterInfoExcelConfigData.json")
    text_hash_map = pymon.io.read("download/TextMap/TextMapEN.json")

    for element in fetter:
        character_id = str(element.get("AvatarId"))
        vision_before_hash = str(element.get("AvatarVisionBeforTextMapHash"))
        vision_after_hash = str(element.get("AvatarVisionAfterTextMapHash"))

        # for archons: vision_before == vision_after
        vision_before = text_hash_map.get(vision_before_hash)
        vision_after = text_hash_map.get(vision_after_hash)

        logger.debug(
            "Name: %s, Vision Before: %s, Vision After: %s",
            characters[character_id]["name"],
            vision_before,
            vision_after,
        )

        characters[character_id]["element"] = vision_before


def _add_weapon(characters: dict) -> None:
    """Add weapon type to each character.

    ```
    {
        <Character ID>: {
            weapon: <Character Weapon Type>
        },
        ...
    }
    """

    character_data = pymon.io.read("download/ExcelBinOutput/AvatarExcelConfigData.json")

    for element in character_data:
        if _is_playable(element):
            character_id = str(element.get("Id"))
            character_weapon = element.get("WeaponType")
            weapon_hash = _lookup_hash_of_id(character_weapon)

            characters[character_id]["weapon"] = _lookup_text_map(weapon_hash)


def main():
    """Extracts character data from Dimbreath/GenshinData."""

    characters = {}

    functions = [_setup, _add_description, _add_rarity, _add_element, _add_weapon]

    for function in functions:
        function(characters)

    pymon.io.write("characters.json", characters)
