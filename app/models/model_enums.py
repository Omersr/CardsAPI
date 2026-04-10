from enum import Enum

class CardType(str, Enum):
    arms = "arms"
    void = "void"
    earth = "earth"
    fire = "fire"
    frost = "frost"
    light = "light"
    lightning = "lightning"
    magic = "magic"
    ore = "ore"
    poison = "poison"
    water = "water"
    wind = "wind"
    plant = "plant"
    cosmic = "cosmic"



class DisplayType(str, Enum):
    normal = "normal_card.html"
    sunlight = "sunlight_card.html"
    moonlight = "moonlight_card.html"
    twilight = "twilight_card.html"
    @classmethod
    def _missing_(cls, value):
        return cls.normal


class RarityType(str, Enum):
    normal = "normal"
    sunlight = "sunlight"
    moonlight = "moonlight"
    twilight = "twilight"
    @classmethod
    def _missing_(cls, value):
        return cls.normal


class TeamType(str, Enum):
    bull = "bull"
    owl = "owl"
    swordfish = "swordfish"
    neutral = "neutral"

    @classmethod
    def _missing_(cls, value):
        return cls.neutral

class DownloadType(str, Enum):
    monster_card = "monster-cards"
    action_card = "action-cards"
    item_card = "item-cards" 