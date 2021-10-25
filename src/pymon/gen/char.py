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


class Lookup:
    """For searching through data files for certain key-value pairs."""

    # TODO: only open files when needed to reduce memory usage
    # load all data to global dictionary
    paths = {
        "download/ExcelBinOutput/AvatarExcelConfigData.json",
        "download/ExcelBinOutput/FetterInfoExcelConfigData.json",
        "download/ExcelBinOutput/ManualTextMapConfigData.json",
        "download/TextMap/TextMapEN.json",
    }
    content = {f"{pymon.io.file_name(path)}": pymon.io.read(path) for path in paths}

    @classmethod
    @cache
    def avatar(cls, avatar_id: str) -> dict:
        """Returns the dictionary corresponding to avatar ID."""

        for avatar in cls.content["AvatarExcelConfigData"]:
            if Lookup.is_playable(avatar) and str(avatar["Id"]) == avatar_id:
                logger.debug("ID %s matches avatar %s", avatar_id, avatar)
                return avatar

        logger.critical("Unable to find avatar with id %s", avatar_id)
        raise RuntimeError(f"Unable to find avatar with id {avatar_id}")

    @classmethod
    @cache
    def manual_text_map(cls, text_map_id: str) -> str:
        """Given `TextMapId` return `TextMapContentTextMapHash`."""

        for element in cls.content["ManualTextMapConfigData"]:
            if element["TextMapId"] == text_map_id:
                return str(element["TextMapContentTextMapHash"])

        logger.critical("Unable to find %s in manual text map", text_map_id)
        raise RuntimeError(f"Unable to find {text_map_id} in manual text map")

    @classmethod
    @cache
    def text_map(cls, hash_id: str) -> str:
        """Given key `hash_` get corresponding value in text map."""

        try:
            value = str(cls.content["TextMapEN"][hash_id])
            logger.debug("%s returns %s", hash_id, value)
            return value
        except KeyError:
            logger.critical("Invalid hash %s", hash_id)
            raise

    @staticmethod
    def is_playable(avatar: dict) -> bool:
        """Returns whether a character is playable."""

        try:
            return avatar["UseType"] == "AVATAR_FORMAL"
        except KeyError:
            return False


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

    for element in Lookup.content["AvatarExcelConfigData"]:
        if Lookup.is_playable(element):
            character_id = str(element.get("Id"))
            character_name_hash = str(element.get("NameTextMapHash"))

            character_name = Lookup.text_map(character_name_hash)

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

    for avatar_id, avatar_data in characters.items():
        description_hash = str(Lookup.avatar(avatar_id).get("DescTextMapHash"))
        description = Lookup.text_map(description_hash)
        logger.debug("Name: %s, Description: %s", avatar_data["name"], description)
        avatar_data["description"] = description


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

    rarity_conversion = {
        "QUALITY_PURPLE": "4",
        "QUALITY_ORANGE": "5",
        "QUALITY_ORANGE_SP": "5",
    }

    for avatar_id, avatar_data in characters.items():
        character_rarity = rarity_conversion.get(
            Lookup.avatar(avatar_id).get("QualityType")
        )
        logger.debug("Name: %s, Rarity: %s", avatar_data["name"], character_rarity)
        avatar_data["rarity"] = character_rarity


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

    for element in Lookup.content["FetterInfoExcelConfigData"]:
        character_id = str(element.get("AvatarId"))
        vision_before_hash = str(element.get("AvatarVisionBeforTextMapHash"))
        vision_after_hash = str(element.get("AvatarVisionAfterTextMapHash"))

        # for archons: vision_before == vision_after
        vision_before = Lookup.text_map(vision_before_hash)
        vision_after = Lookup.text_map(vision_after_hash)

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

    for avatar_id, avatar_data in characters.items():
        character_weapon = Lookup.avatar(avatar_id)["WeaponType"]
        weapon_hash = Lookup.manual_text_map(character_weapon)
        avatar_data["weapon"] = Lookup.text_map(weapon_hash)


def main():
    """Extracts character data from Dimbreath/GenshinData."""

    characters = {}

    functions = [_setup, _add_description, _add_rarity, _add_element, _add_weapon]

    for function in functions:
        function(characters)

    pymon.io.write("doc/avatar_sample.json", characters)
