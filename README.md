# Shinobi-RPG1 (AOE-lite)

AOE-lite is a lightweight, browser-based strategy sandbox inspired by Age of Empires and shaped as a first-step foundation for a future Shinobi RPG. This code was originally developed in the [AOE-lite repository](https://github.com/ToadSageDan/AOE-lite) and has been moved here as the canonical home for the project.

## Features

- Four playable clans with balanced bonuses, drawbacks, activated abilities, and terrain affinities
- Multiple unit roles for army-building choices: militia, archers, riders, ninjas (shinobi), and assassins (kunoichi)
- Sandbox progression through gathering, building, training, trading, and expansion
- Succession pressure through heir events and leader weaknesses that can trigger surprise defeats
- Diplomacy, truces, and covert missions for lighter interpersonal play between clans
- Weather and disaster events that reshape each turn's economy
- Multiple win conditions:
  - **Conquest**: destroy every rival capital
  - **Prosperity**: outscale everyone with a score of 220 while securing an heir
  - **Wonder**: build and protect a wonder until the countdown finishes
- Three AI rivals that pressure you with raids, intrigue, expansion, and their own wonder attempts

## How to play

1. Open `index.html` in a modern browser.
2. Choose a clan and start a new campaign.
3. Use the economy, development, and strategy actions to shape your realm, succession, and covert options.
4. End turns to collect passive region income, trigger heir/world events, and let rival clans act.

## Clan overview

- **Peasant Commons**: fertile growth clan with heartland and river-plain affinity, stronger militia, and the **Village Muster** growth ability
- **Ironroot Horde**: mountain raiders with ridge and quarry affinity, stronger riders, and the **War Drums** burst attack ability
- **Sunveil Enclave**: forest mystics with woodland affinity, stronger gathering and archers, and the **Bloom of Ages** economy/wonder ability
- **Tideborn League**: river traders with diplomacy and covert pressure, trade-ruin affinity, and the **Silver Accord** truce ability

## RPG baseline

This prototype establishes a foundation for future Shinobi RPG-style expansion by separating clans into distinct strengths, weaknesses, succession risks, and unit roles that can later evolve into heroes, courts, quests, and progression systems.

## Files

| File | Description |
|------|-------------|
| `index.html` | Game UI — clan setup, dashboard, map, economy, strategy panels |
| `styles.css` | Dark-theme styling for the entire game UI |
| `script.js` | All game logic — clans, units, economy, combat, AI, win conditions | 
