from app.models.monster_card import MonsterCard
import logging
from app.models.model_enums import CardType
from app.services.cards_service import get_all_possessions
logger = logging.getLogger("uvicorn.error")
from enum import Enum
from copy import copy

class BattleAction(str, Enum):
    CONTINUE = "continue"
    SKIP = "skip"
    AUTO = "auto"


def edit_card_menu(card: MonsterCard) -> BattleAction:
    action = BattleAction.CONTINUE

    while True:
        print(f"\nEditing {card.name}")
        print("1. Edit HP")
        print("2. Edit attack")
        print("3. Edit defense")
        print("4. Edit speed")
        print("5. Edit primary type")
        print("6. Edit secondary type")
        print("7. Skip turn")
        print("8. Go to auto battle")
        print("0. Exit menu")

        choice = input("Choose option: ")

        if choice == "1":
            old = card.health
            card.health = int(input("New HP: "))
            logger.info(f"{card.name} HP changed from {old} to {card.health}")

        elif choice == "2":
            old = card.attack
            card.attack = int(input("New attack: "))
            logger.info(f"{card.name} attack changed from {old} to {card.attack}")

        elif choice == "3":
            old = card.defense
            card.defense = int(input("New defense: "))
            logger.info(f"{card.name} defense changed from {old} to {card.defense}")

        elif choice == "4":
            old = card.speed
            card.speed = int(input("New speed: "))
            logger.info(f"{card.name} speed changed from {old} to {card.speed}")

        elif choice == "5":
            old = card.primary_type
            card.primary_type = CardType(input("New primary type: "))
            logger.info(f"{card.name} primary type changed from {old} to {card.primary_type}")

        elif choice == "6":
            old = card.secondary_type
            card.secondary_type = CardType(input("New secondary type: "))
            logger.info(f"{card.name} secondary type changed from {old} to {card.secondary_type}")

        elif choice == "7":
            logger.info(f"{card.name} chose to skip this turn")
            return BattleAction.SKIP

        elif choice == "8":
            logger.info(f"{card.name} chose to continue with auto battle")
            return BattleAction.AUTO

        elif choice == "0":
            logger.info(f"{card.name} finished editing")
            return action


def calculate_damage(card1: MonsterCard, card2: MonsterCard) ->  tuple[int, int]:
    base = 1000
    card1_multipler, card2_multiplier = MonsterCard.get_damage_multipliers(card1, card2)
    logger.info(f"Damage multipliers - {card1.name}: {card1_multipler}")
    card1_damage = round(base * (card1.attack / max(card2.defense, 1)) * card1_multipler)
    logger.info(f"Damage multipliers - {card2.name}: {card2_multiplier}")
    card2_damage = round(base * (card2.attack / max(card1.defense, 1)) * card2_multiplier)
    return card1_damage, card2_damage

def battle(card1: MonsterCard, card2: MonsterCard) -> MonsterCard:
    auto_battle_flag = True
    card1_possesions = get_all_possessions(card1.id)
    card2_possessions = get_all_possessions(card2.id)
    if len(card1_possesions) + len(card2_possessions) > 0 or card1.description or card2.description:
        logger.info("We detected that one of the battling cards has important info")
        logger.info(f"please look at http://localhost:8000/monster-cards/display_possesion?monster_card_ids={card1.id},{card2.id} to see the cards possesions and descriptions before you decide to use auto battle")
        answer = ""
        while answer.lower() not in ["y", "n"]:
            answer = input("Would you like to use auto battle? (y/n):")
        auto_battle_flag = answer.lower() == "y"
    if auto_battle_flag:
        winner = auto_battle(card1, card2)
    else:
        winner = custom_battle(card1, card2)
    if winner.id == card1.id:
        MonsterCard.kill_card(card2.id)
    else:
        MonsterCard.kill_card(card1.id)
    return winner
        
def auto_battle(card1: MonsterCard, card2: MonsterCard) -> MonsterCard:
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
        
def custom_battle(card1: MonsterCard, card2: MonsterCard) -> MonsterCard:
    card1_temp = copy(card1)
    card2_temp = copy(card2)

    card1_health = card1.health
    card2_health = card2.health

    logger.info(f"Custom battle starts between {card1.name} and {card2.name}")

    while card1_health > 0 and card2_health > 0:
        card1_temp.health = card1_health
        card2_temp.health = card2_health

        action1 = edit_card_menu(card1_temp)
        action2 = edit_card_menu(card2_temp)

        if action1 == BattleAction.AUTO or action2 == BattleAction.AUTO:
            logger.info("Switching to auto battle with current temporary changes")
            card1_temp.health = card1_health
            card2_temp.health = card2_health
            return auto_battle(card1_temp, card2_temp)

        initiator = 1 if card1_temp.speed >= card2_temp.speed else 0
        logger.info(f"{card1_temp.name if initiator == 1 else card2_temp.name} attacks first this round")

        card1_damage, card2_damage = calculate_damage(card1_temp, card2_temp)

        if initiator == 1:
            if action1 == BattleAction.SKIP:
                logger.info(f"{card1.name} skipped this turn")
            else:
                card2_health -= card1_damage
                logger.info(f"{card1.name} attacks {card2.name} for {card1_damage} damage. {card2.name} health: {max(card2_health, 0)}")

            if card2_health <= 0:
                break

            if action2 == BattleAction.SKIP:
                logger.info(f"{card2.name} skipped this turn")
            else:
                card1_health -= card2_damage
                logger.info(f"{card2.name} attacks {card1.name} for {card2_damage} damage. {card1.name} health: {max(card1_health, 0)}")

        else:
            if action2 == BattleAction.SKIP:
                logger.info(f"{card2.name} skipped this turn")
            else:
                card1_health -= card2_damage
                logger.info(f"{card2.name} attacks {card1.name} for {card2_damage} damage. {card1.name} health: {max(card1_health, 0)}")

            if card1_health <= 0:
                break

            if action1 == BattleAction.SKIP:
                logger.info(f"{card1.name} skipped this turn")
            else:
                card2_health -= card1_damage
                logger.info(f"{card1.name} attacks {card2.name} for {card1_damage} damage. {card2.name} health: {max(card2_health, 0)}")

    if card1_health > 0:
        logger.info(f"{card1.name} wins the custom battle!")
        return card1

    logger.info(f"{card2.name} wins the custom battle!")
    return card2