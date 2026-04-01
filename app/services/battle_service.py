from app.models.monster_card import MonsterCard
import logging
logger = logging.getLogger("uvicorn.error")
def calculate_damage(card1: MonsterCard, card2: MonsterCard) ->  tuple[int, int]:
    base = 1000
    card1_multipler, card2_multiplier = MonsterCard.get_damage_multipliers(card1, card2)
    logger.info(f"Damage multipliers - {card1.name}: {card1_multipler}")
    card1_damage = round(base * (card1.attack / max(card2.defense, 1)) * card1_multipler)
    logger.info(f"Damage multipliers - {card2.name}: {card2_multiplier}")
    card2_damage = round(base * (card2.attack / max(card1.defense, 1)) * card2_multiplier)
    return card1_damage, card2_damage

def battle(card1: MonsterCard, card2: MonsterCard) -> MonsterCard:
    card1_damage, card2_damage = calculate_damage(card1, card2)
    card1_health = card1.health
    card2_health = card2.health
    initiator = 1 if card1.speed >= card2.speed else 0
    logger.info(f"Battle starts between {card1.name} and {card2.name}")
    while card1_health > 0 and card2_health > 0:
        if initiator == 1:
            card2_health -= card1_damage
            logger.info(f"{card1.name} attacks {card2.name} for {card1_damage:.2f} damage. {card2.name} health: {max(card2_health, 0):.2f}")
        else:
            card1_health -= card2_damage
            logger.info(f"{card2.name} attacks {card1.name} for {card2_damage:.2f} damage. {card1.name} health: {max(card1_health, 0):.2f}")
        initiator = 1 - initiator  # switch turns
    if card1_health > 0:
        logger.info(f"{card1.name} wins the battle!")
        return card1
    elif card2_health > 0:
        logger.info(f"{card2.name} wins the battle!")
        return card2
        

    
