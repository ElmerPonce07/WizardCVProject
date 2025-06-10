SPELL_COUNTERS = {
    "Fire" : "Water",
    "Water": "Earth",
    "Earth": "Fire"
}

DIFFICULTY_LEVELS = {
    "easy" : 2.5,
    "medium" : 1.5,
    "hard" : 0.75
 }

def is_counter (playerSpell, mageSpell):
    return SPELL_COUNTERS.get(mageSpell) == playerSpell

def evaluate_spell(playerSpell , mageSpell , playerHp, mageHp ):
    if is_counter(playerSpell,mageSpell):
        mageHp -= 10
        result = f"You cast {playerSpell} and countered the mage! Mage -10 HP."
    elif playerSpell: # Player cast something, but it wasn't a counter
        playerHp -= 10
        result = f"You cast {playerSpell}... It was not effective! You take -10 HP."
    else: # Player failed to cast anything
        playerHp -= 10
        result = f"You failed to cast a spell... You take -10 HP."
    return playerHp,mageHp,result

def get_reaction_time (difficulty):
    return DIFFICULTY_LEVELS.get(difficulty, 1.5) # Default to medium if not found

def is_game_over (playerHp,mageHp ):
    if playerHp <= 0:
        return "player"
    elif mageHp <= 0:
        return "mage"
    return None

def get_random_spell():
    import random
    return random.choice(list(SPELL_COUNTERS.keys()))
