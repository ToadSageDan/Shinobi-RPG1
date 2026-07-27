// ── Leader name pools (Japanese-inspired) ────────────────────────────────────
const leaderFirstNames = [
  'Takeda', 'Shimazu', 'Oda', 'Date', 'Uesugi', 'Sanada', 'Hojo', 'Mori',
  'Chosokabe', 'Imagawa', 'Nene', 'Tsuruhime', 'Matsu', 'Kaihime', 'Nohime',
  'Ryoma', 'Shingen', 'Kenshin', 'Hideyoshi', 'Ieyasu', 'Yukimura', 'Masamune',
  'Yodo', 'Gracia', 'Ginchiyo', 'Chacha', 'Tora', 'Kiku', 'Hanzo', 'Fuma',
];

const leaderWeaknessPool = ['shinobi', 'kunoichi'];
// 'shinobi' maps to ninja missions; 'kunoichi' maps to assassin missions

// ── Covert specialty pools ────────────────────────────────────────────────────
const ninjaSpecialties = [
  { key: 'phantom',      label: 'Phantom',      hint: 'Excels against large, spread-out clans.',         bonus: 'large_targets' },
  { key: 'viper',        label: 'Viper',         hint: 'Effective once a rival secures an heir.',         bonus: 'heir_targets' },
  { key: 'wind',         label: 'Wind',          hint: 'Best deployed against wonder-building lords.',    bonus: 'wonder_targets' },
];

const assassinSpecialties = [
  { key: 'shadow-step',  label: 'Shadow Step',   hint: 'Slips past guards; thrives in heirless courts.', bonus: 'heirless_targets' },
  { key: 'poisoncraft',  label: 'Poisoncraft',   hint: 'Best used against wealthy lords.',               bonus: 'rich_targets' },
  { key: 'bladework',    label: 'Bladework',     hint: 'Reliable against most leaders.',                 bonus: 'base_success' },
  { key: 'infiltrator',  label: 'Infiltrator',   hint: 'Effective against well-defended courts.',        bonus: 'defended_targets' },
];

// ── Difficulty settings ───────────────────────────────────────────────────────
const difficultySettings = {
  easy:   { label: 'Easy',   resourceMult: 1.4, enemyAggression: 0.15, aiAbilityChance: 0.1, desc: 'More starting resources, slow enemy response.' },
  normal: { label: 'Normal', resourceMult: 1.0, enemyAggression: 0.30, aiAbilityChance: 0.25, desc: 'Balanced campaign.' },
  hard:   { label: 'Hard',   resourceMult: 0.7, enemyAggression: 0.50, aiAbilityChance: 0.45, desc: 'Less resources, aggressive rivals from the start.' },
};

function pickRandom(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function pickDistinct(pool, exclude) {
  const options = pool.filter((v) => v !== exclude);
  return pickRandom(options);
}

// ── Clan definitions ──────────────────────────────────────────────────────────
const races = {
  peasants: {
    name: 'Heimin Clan',
    summary: 'Wide-food growers with cheap growth, steady ashigaru, and fertile plain affinity.',
    traits: '+35 food, +1 villager, expansion costs less, ashigaru deal +1 damage, cavalry deal -1 damage.',
    bonuses: { food: 35, villagers: 1, expandDiscount: 4 },
    unitPower: { militia: 1, archer: 0, rider: -1, ninja: 0, assassin: 0 },
    leaderTitle: 'Chamberlain',
    affinity: { terrains: ['heartland', 'river'], resource: 'food', amount: 2, label: 'Heartlands & river plains' },
    specialistFocus: 'Kunoichi excel against courts without an heir; shinobi are steadier in richer provinces.',
    abilityName: 'Village Muster',
    abilityDescription: 'Gain 2 ashigaru, 1 villager, and 10 food.',
    useAbility(faction) {
      faction.units.militia += 2;
      faction.villagers += 1;
      faction.resources.food += 10;
      return `The ${races.peasants.name} rally the countryside — 2 ashigaru, 1 villager, and 10 food gained.`;
    },
  },
  horde: {
    name: 'Ironroot Raiders',
    summary: 'Hard-hitting raiders with mountain affinity, brutal cavalry, and shakier defenses.',
    traits: '+20 gold, +2 global attack, -10 town health, cavalry deal +2 damage, archers deal -1 damage.',
    bonuses: { gold: 20, militia: 1, attack: 2, townHealth: -10 },
    unitPower: { militia: 0, archer: -1, rider: 2, ninja: 1, assassin: -1 },
    leaderTitle: 'Warlord',
    affinity: { terrains: ['ridge', 'quarry'], resource: 'stone', amount: 2, label: 'Ridges & quarries' },
    specialistFocus: 'Shinobi thrive infiltrating strongholds; kunoichi hit weakened family lines.',
    abilityName: 'War Drums',
    abilityDescription: 'Deal a fierce strike for bonus damage and gain 20 food.',
    useAbility(faction, target) {
      if (!target) {
        return 'War Drums needs a target.';
      }
      const damage = 18 + faction.attackBonus;
      clearTruce(faction, target);
      applyDamage(target, damage);
      faction.resources.food += 20;
      return `The ${races.horde.name} smash ${target.name} for ${damage} damage and feast on the spoils.`;
    },
  },
  enclave: {
    name: 'Sunveil Order',
    summary: 'Flexible gatherers with forest affinity, elite archers, and fragile front lines.',
    traits: '+20 wood, +20 stone, +3 gather power, -5 town health, archers deal +2 damage, ashigaru deal -1 damage.',
    bonuses: { wood: 20, stone: 20, gather: 3, townHealth: -5 },
    unitPower: { militia: -1, archer: 2, rider: -1, ninja: 1, assassin: 0 },
    leaderTitle: 'Seer',
    affinity: { terrains: ['forest', 'grove'], resource: 'wood', amount: 2, label: 'Forests & groves' },
    specialistFocus: 'Shinobi are better once rivals grow large; kunoichi punish heirless dynasties.',
    abilityName: 'Bloom of Ages',
    abilityDescription: 'Gain 25 wood, 20 food, and reduce wonder countdown by 1 if built.',
    useAbility(faction) {
      faction.resources.wood += 25;
      faction.resources.food += 20;
      if (faction.buildings.wonder > 0 && faction.wonderCountdown !== null) {
        faction.wonderCountdown = Math.max(1, faction.wonderCountdown - 1);
      }
      return `The ${races.enclave.name} summons a golden bloom — extra resources flow in.`;
    },
  },
  tideborn: {
    name: 'Tideborn Harbor',
    summary: 'River traders with diplomatic leverage, nimble covert play, and softer ashigaru.',
    traits: '+25 gold, +15 wood, market-ready economy, ashigaru deal -1 damage, kunoichi deal +1 damage.',
    bonuses: { gold: 25, wood: 15 },
    unitPower: { militia: -1, archer: 0, rider: 1, ninja: 0, assassin: 1 },
    leaderTitle: 'Harbor Master',
    affinity: { terrains: ['river', 'ruins'], resource: 'gold', amount: 2, label: 'Rivers & trade ruins' },
    specialistFocus: 'Kunoichi are best against heirless courts; shinobi are best against wealthy frontiers.',
    abilityName: 'Silver Accord',
    abilityDescription: 'Gain 20 gold, set a short truce with a rival, and steady your stores with 10 food.',
    useAbility(faction, target) {
      faction.resources.gold += 20;
      faction.resources.food += 10;
      if (target) {
        faction.truceUntilTurn = Math.max(faction.truceUntilTurn, state.turn + 1);
        target.truceUntilTurn = Math.max(target.truceUntilTurn, state.turn + 1);
      }
      return target
        ? `The ${races.tideborn.name} buys breathing room with ${target.name} and gathers 20 gold.`
        : `The ${races.tideborn.name} gather 20 gold and stabilize their stores.`;
    },
  },
};

const unitTypes = {
  militia: {
    label: 'Ashigaru',
    cost: { food: 20, gold: 10 },
    power: 6,
    requires: () => true,
    blockedText: 'Ashigaru are always available.',
  },
  archer: {
    label: 'Yumi Archer',
    cost: { food: 18, wood: 12, gold: 12 },
    power: 7,
    requires: (faction) => faction.buildings.barracks > 0,
    blockedText: 'Build a barracks to train yumi archers.',
  },
  rider: {
    label: 'Cavalry',
    cost: { food: 28, gold: 24 },
    power: 10,
    requires: (faction) => faction.buildings.market > 0 || countOwnedRegions(faction) >= 3,
    blockedText: 'Build a market or control 3 regions to field cavalry.',
  },
  ninja: {
    label: 'Shinobi',
    cost: { food: 16, wood: 12, gold: 28 },
    power: 5,
    requires: (faction) => faction.buildings.barracks > 0 && countOwnedRegions(faction) >= 2,
    blockedText: 'Build a barracks and control 2 provinces to train shinobi.',
  },
  assassin: {
    label: 'Kunoichi',
    cost: { food: 12, gold: 32 },
    power: 4,
    requires: (faction) => faction.buildings.market > 0 && countOwnedRegions(faction) >= 2,
    blockedText: 'Build a market and control 2 provinces to train kunoichi.',
  },
};

const regionDeck = [
  { name: 'Home Province',    terrain: 'heartland', yield: { food: 2, wood: 2 },          score: 12 },
  { name: 'Whispering Forest',terrain: 'forest',    yield: { wood: 4, food: 1 },           score: 18 },
  { name: 'Golden Pass',      terrain: 'ridge',     yield: { gold: 4, stone: 1 },          score: 18 },
  { name: 'Fertile Delta',    terrain: 'river',     yield: { food: 4, wood: 1 },           score: 18 },
  { name: 'Stone Quarry',     terrain: 'quarry',    yield: { stone: 4, gold: 1 },          score: 18 },
  { name: 'Bamboo Grove',     terrain: 'grove',     yield: { food: 2, wood: 2, gold: 1 },  score: 20 },
  { name: 'Crumbling Temple', terrain: 'ruins',     yield: { gold: 2, stone: 2 },          score: 20 },
];

const buildingCosts = {
  house:       { wood: 30, stone: 10 },
  barracks:    { wood: 25, stone: 25 },
  market:      { wood: 30, gold: 20 },
  shinobi_den: { wood: 35, gold: 30 },
  wonder:      { wood: 120, stone: 120, gold: 80 },
};

const state = {
  turn: 1,
  gameOver: false,
  winner: null,
  player: null,
  enemies: [],
  regions: [],
  log: [],
  currentEvent: 'The age is calm.',
  difficulty: 'normal',
};

const raceSelect = document.getElementById('race-select');
const difficultySelect = document.getElementById('difficulty-select');
const startButton = document.getElementById('start-game');
const enemySelect = document.getElementById('enemy-select');
const abilityButton = document.getElementById('ability-button');
const overviewEl = document.getElementById('overview');
const enemiesEl = document.getElementById('enemies');
const regionsEl = document.getElementById('regions');
const logEl = document.getElementById('log');
const winConditionsEl = document.getElementById('win-conditions');
const traitsEl = document.getElementById('race-traits');

Object.entries(races).forEach(([key, race]) => {
  const option = document.createElement('option');
  option.value = key;
  option.textContent = `${race.name} — ${race.summary}`;
  raceSelect.append(option);
});

Object.entries(difficultySettings).forEach(([key, diff]) => {
  const option = document.createElement('option');
  option.value = key;
  option.textContent = `${diff.label} — ${diff.desc}`;
  if (key === 'normal') option.selected = true;
  difficultySelect.append(option);
});

startButton.addEventListener('click', () => startGame(raceSelect.value, difficultySelect.value));
abilityButton.addEventListener('click', () => handleAction('ability'));

document.querySelectorAll('[data-action]').forEach((button) => {
  button.addEventListener('click', () => handleAction(button.dataset.action, button.dataset));
});

function makeFaction(id, raceKey, isPlayer = false) {
  const race = races[raceKey];
  const diff = difficultySettings[state.difficulty] || difficultySettings.normal;

  const leaderWeakness = pickRandom(leaderWeaknessPool);
  const leaderStrength = pickDistinct(leaderWeaknessPool, leaderWeakness);
  const leaderName = pickRandom(leaderFirstNames);
  const ninjaSpec = pickRandom(ninjaSpecialties);
  const assassinSpec = pickRandom(assassinSpecialties);

  const baseResources = { food: 90, wood: 80, gold: 50, stone: 40 };
  const scaledResources = Object.fromEntries(
    Object.entries(baseResources).map(([k, v]) => [k, Math.floor(v * diff.resourceMult)])
  );

  const faction = {
    id,
    name: isPlayer ? 'Your Clan' : race.name,
    raceKey,
    resources: scaledResources,
    villagers: 5,
    units: { militia: 2, archer: 0, rider: 0, ninja: 0, assassin: 0 },
    townHealth: 100,
    popCap: 10,
    attackBonus: race.bonuses.attack || 0,
    gatherBonus: race.bonuses.gather || 0,
    expandDiscount: race.bonuses.expandDiscount || 0,
    unitPower: race.unitPower,
    buildings: { house: 0, barracks: 0, market: 0, shinobi_den: 0, wonder: 0 },
    abilityReadyTurn: 1,
    wonderCountdown: null,
    truceUntilTurn: 0,
    leader: {
      name: leaderName,
      title: race.leaderTitle,
      weakness: leaderWeakness,
      strength: leaderStrength,
      hasHeir: false,
    },
    // Covert specialties (good at one, bad at one)
    ninjaSpec,
    assassinSpec,
    // Intel — what THIS faction knows about rivals (keyed by target id)
    knownIntel: {},
  };

  for (const [resource, amount] of Object.entries(race.bonuses)) {
    if (faction.resources[resource] !== undefined) {
      faction.resources[resource] += amount;
    }
  }

  faction.villagers += race.bonuses.villagers || 0;
  faction.units.militia += race.bonuses.militia || 0;
  faction.townHealth = Math.min(100, faction.townHealth + (race.bonuses.townHealth || 0));

  return faction;
}

function startGame(selectedRace, selectedDifficulty = 'normal') {
  state.turn = 1;
  state.gameOver = false;
  state.winner = null;
  state.log = [];
  state.currentEvent = 'The age is calm.';
  state.difficulty = selectedDifficulty;
  state.regions = regionDeck.map((region, index) => ({
    ...region,
    id: index,
    ownerId: index === 0 ? 'player' : null,
  }));
  state.player = makeFaction('player', selectedRace, true);

  const enemyRaces = Object.keys(races).filter((key) => key !== selectedRace);
  state.enemies = enemyRaces.map((raceKey, index) => makeFaction(`enemy-${index}`, raceKey));

  state.enemies.forEach((enemy, index) => {
    const startRegion = state.regions[index + 1];
    if (startRegion) {
      startRegion.ownerId = enemy.id;
    }
  });

  const race = races[selectedRace];
  logMessage(`A new campaign begins. Difficulty: ${difficultySettings[selectedDifficulty].label}.`);
  logMessage(`${formatAffinity(race.affinity)} grants bonus ${race.affinity.resource} from matching lands.`);
  logMessage(`Your leader ${state.player.leader.name} leads the ${race.name}. Run espionage to learn rival weaknesses.`);
  logMessage(race.abilityDescription);
  render();
}

function handleAction(action, data = {}) {
  if (!state.player || state.gameOver) {
    return;
  }

  let result = '';

  switch (action) {
    case 'gather':
      result = gatherResource(state.player, data.resource);
      break;
    case 'expand':
      result = claimRegion(state.player);
      break;
    case 'build':
      result = buildStructure(state.player, data.building);
      break;
    case 'train':
      result = trainUnit(state.player, data.unit);
      break;
    case 'trade':
      result = tradeAtMarket(state.player);
      break;
    case 'attack':
      result = launchAttack(state.player, enemySelect.value);
      break;
    case 'diplomacy':
      result = conductDiplomacy(state.player, enemySelect.value);
      break;
    case 'covert':
      result = attemptAssassination(state.player, enemySelect.value, data.unit);
      break;
    case 'espionage':
      result = runEspionage(state.player, enemySelect.value);
      break;
    case 'ability':
      result = useAbility(state.player, enemySelect.value);
      break;
    case 'end-turn':
      endTurn();
      return;
    default:
      result = 'Nothing happens.';
  }

  if (result) {
    logMessage(result);
  }

  evaluateWinConditions();
  render();
}

function gatherResource(faction, resource) {
  if (faction.villagers < 1) {
    return `${faction.name} has no villagers free to gather. Train more villagers first.`;
  }
  const amount = 12 + faction.villagers * 2 + faction.gatherBonus + territoryYield(faction, resource);
  faction.resources[resource] += amount;
  return `${faction.name} gathers ${amount} ${resource}.`;
}

function claimRegion(faction) {
  const neutral = state.regions.find((region) => !region.ownerId);
  if (!neutral) {
    return 'No neutral regions remain to claim.';
  }

  const cost = {
    food: Math.max(8, 18 - faction.expandDiscount),
    wood: Math.max(8, 18 - faction.expandDiscount),
  };
  if (!canAfford(faction, cost)) {
    return 'You need more food and wood to expand.';
  }

  payCost(faction, cost);
  neutral.ownerId = faction.id;
  return `${faction.name} claims ${neutral.name} and unlocks new yields.`;
}

function buildStructure(faction, building) {
  const cost = buildingCosts[building];
  if (!cost) {
    return 'Unknown building.';
  }

  if (faction.villagers < 1) {
    return `${faction.name} has no villagers free to build. Train more villagers first.`;
  }

  if (building === 'wonder' && faction.buildings.wonder > 0) {
    return 'Your empire already has a wonder.';
  }

  if (building === 'shinobi_den' && faction.buildings.shinobi_den > 0) {
    return 'Your clan already has a shinobi den.';
  }

  if (!canAfford(faction, cost)) {
    return `Not enough resources to build a ${building.replace('_', ' ')}.`;
  }

  payCost(faction, cost);
  faction.buildings[building] += 1;

  if (building === 'house') {
    faction.popCap += 4;
  }

  if (building === 'wonder') {
    faction.wonderCountdown = 3;
  }

  if (building === 'shinobi_den') {
    return `${faction.name} establishes a shinobi den — your shadow network is open.`;
  }

  return `${faction.name} builds a ${building.replace('_', ' ')}.`;
}

function trainUnit(faction, unit) {
  if (faction.villagers + totalMilitary(faction) >= faction.popCap) {
    return 'Your population is capped. Build houses first.';
  }

  if (unit === 'villager') {
    const cost = { food: 20 };
    if (!canAfford(faction, cost)) {
      return 'Not enough food to train a villager.';
    }
    payCost(faction, cost);
    faction.villagers += 1;
    return `${faction.name} trains a villager.`;
  }

  const unitConfig = unitTypes[unit];
  if (!unitConfig) {
    return 'Unknown unit.';
  }

  if (!unitConfig.requires(faction)) {
    return unitConfig.blockedText;
  }

  if (!canAfford(faction, unitConfig.cost)) {
    return `Not enough resources to train a ${unitConfig.label.toLowerCase()}.`;
  }

  payCost(faction, unitConfig.cost);
  faction.units[unit] += 1;
  return `${faction.name} trains a ${unitConfig.label.toLowerCase()}.`;
}

function tradeAtMarket(faction) {
  if (faction.buildings.market < 1) {
    return 'Build a market first.';
  }
  if (faction.villagers < 1) {
    return `${faction.name} has no villagers free to trade. Train more villagers first.`;
  }
  if (faction.resources.wood < 20) {
    return 'You need 20 wood to trade.';
  }

  faction.resources.wood -= 20;
  faction.resources.gold += 15;
  faction.resources.food += 10;
  return `${faction.name} trades 20 wood for 15 gold and 10 food.`;
}

function conductDiplomacy(faction, targetId) {
  const target = findFactionById(targetId);
  if (!target || target.id === faction.id || target.townHealth <= 0) {
    return 'Choose a living rival for diplomacy.';
  }
  if (faction.truceUntilTurn >= state.turn && target.truceUntilTurn >= state.turn) {
    return `${target.name} is already under truce until turn ${target.truceUntilTurn}.`;
  }

  const leverage = countOwnedRegions(faction) - countOwnedRegions(target) + (faction.buildings.market > 0 ? 1 : 0);
  const result = Math.random() + leverage * 0.08;

  if (result >= 0.7) {
    faction.truceUntilTurn = state.turn + 2;
    target.truceUntilTurn = state.turn + 2;
    faction.resources.gold += 10;
    faction.resources.food += 8;
    return `${faction.name} win a truce and tribute from ${target.name} through careful diplomacy.`;
  }

  if (faction.resources.gold >= 10) {
    faction.resources.gold -= 10;
    faction.truceUntilTurn = state.turn + 1;
    target.truceUntilTurn = state.turn + 1;
    return `${faction.name} spend 10 gold to calm tensions with ${target.name} for a turn.`;
  }

  target.resources.food += 8;
  return `${target.name} snub the envoys and turn the meeting into their own advantage.`;
}

function launchAttack(attacker, targetId) {
  const target = state.enemies.find((enemy) => enemy.id === targetId && enemy.townHealth > 0);
  if (!target) {
    return 'Choose a living rival to attack.';
  }
  if (totalMilitary(attacker) < 1) {
    return 'You need military units before you can attack.';
  }

  clearTruce(attacker, target);
  const damage = armyPower(attacker) + Math.floor(countOwnedRegions(attacker) / 2);
  applyDamage(target, damage);
  attacker.resources.gold += 10;
  return `${attacker.name} attacks ${target.name} for ${damage} damage and plunders 10 gold.`;
}

function useAbility(faction, targetId) {
  if (state.turn < faction.abilityReadyTurn) {
    return `${races[faction.raceKey].abilityName} will be ready on turn ${faction.abilityReadyTurn}.`;
  }

  const target = findFactionById(targetId);
  const message = races[faction.raceKey].useAbility(faction, target && target.id !== faction.id && target.townHealth > 0 ? target : null);
  if (message.includes('needs a target')) {
    return message;
  }
  faction.abilityReadyTurn = state.turn + 3;
  return message;
}

function runEspionage(faction, targetId) {
  const target = findFactionById(targetId);
  if (!target || target.id === faction.id || target.townHealth <= 0) {
    return 'Choose a living rival to spy on.';
  }

  const hasDen = faction.buildings.shinobi_den > 0;
  const cost = hasDen ? { gold: 10 } : { gold: 20 };
  if (!canAfford(faction, cost)) {
    return `Espionage costs ${cost.gold} gold${hasDen ? ' (discounted by your shinobi den)' : ''}. Gather more.`;
  }

  payCost(faction, cost);

  if (!faction.knownIntel[target.id]) {
    faction.knownIntel[target.id] = {};
  }

  const intel = faction.knownIntel[target.id];
  const baseChance = hasDen ? 0.75 : 0.55;
  const alreadyKnowsWeakness = intel.weaknessKnown;
  const alreadyKnowsStrength = intel.strengthKnown;
  const alreadyKnowsSpec = intel.specKnown;

  if (!alreadyKnowsWeakness && Math.random() < baseChance) {
    intel.weaknessKnown = true;
    return `Your spy reports: ${target.leader.name} of ${target.name} is vulnerable to ${target.leader.weakness} techniques.`;
  }

  if (!alreadyKnowsStrength && Math.random() < baseChance) {
    intel.strengthKnown = true;
    return `Your spy reports: ${target.leader.name} is hardened against ${target.leader.strength} attacks — avoid that approach.`;
  }

  if (!alreadyKnowsSpec && Math.random() < baseChance) {
    intel.specKnown = true;
    const ninjaHint = target.ninjaSpec.hint;
    const assassinHint = target.assassinSpec.hint;
    return `Field report on ${target.name}: shinobi are best as "${ninjaHint}" while kunoichi work best as "${assassinHint}".`;
  }

  return `Your agents return with nothing new from ${target.name}. The ${cost.gold} gold was spent regardless.`;
}

function endTurn() {
  applyPassiveIncome(state.player);
  resolveHeirEvent(state.player);
  advanceWonder(state.player);
  applyPassiveIntel(state.player);

  state.enemies.forEach((enemy) => {
    if (enemy.townHealth <= 0) {
      return;
    }

    applyPassiveIncome(enemy);
    resolveHeirEvent(enemy);
    runEnemyTurn(enemy);
    advanceWonder(enemy);
  });

  resolveWorldEvent();
  state.turn += 1;
  evaluateWinConditions();
  render();
}

function applyPassiveIntel(faction) {
  if (faction.buildings.shinobi_den < 1) {
    return;
  }
  state.enemies.forEach((enemy) => {
    if (enemy.townHealth <= 0) {
      return;
    }
    if (!faction.knownIntel[enemy.id]) {
      faction.knownIntel[enemy.id] = {};
    }
    const intel = faction.knownIntel[enemy.id];
    if (!intel.weaknessKnown && Math.random() < 0.25) {
      intel.weaknessKnown = true;
      logMessage(`Shinobi den report: ${enemy.leader.name} of ${enemy.name} is vulnerable to ${enemy.leader.weakness} techniques.`);
    } else if (!intel.strengthKnown && Math.random() < 0.2) {
      intel.strengthKnown = true;
      logMessage(`Shinobi den report: ${enemy.leader.name} resists ${enemy.leader.strength} attacks.`);
    }
  });
}

function applyPassiveIncome(faction) {
  ['food', 'wood', 'gold', 'stone'].forEach((resource) => {
    faction.resources[resource] += territoryYield(faction, resource);
  });
}

function runEnemyTurn(enemy) {
  const diff = difficultySettings[state.difficulty] || difficultySettings.normal;
  const aggression = diff.enemyAggression;

  const playerNoHeir = !state.player.leader.hasHeir;
  if (playerNoHeir && enemy.units.assassin > 0 && enemy.buildings.market > 0 && state.turn > 5 && Math.random() < aggression) {
    logMessage(attemptAssassination(enemy, 'player', 'assassin'));
    return;
  }

  if (enemy.units.ninja > 0 && countOwnedRegions(state.player) >= 3 && state.turn > 6 && Math.random() < aggression * 0.7) {
    logMessage(attemptAssassination(enemy, 'player', 'ninja'));
    return;
  }

  if (enemy.resources.food < 45) {
    logMessage(gatherResource(enemy, 'food'));
    return;
  }

  if (enemy.buildings.barracks < 1 && canAfford(enemy, buildingCosts.barracks)) {
    logMessage(buildStructure(enemy, 'barracks'));
    return;
  }

  if (enemy.units.archer < 2 && enemy.buildings.barracks > 0) {
    logMessage(trainUnit(enemy, 'archer'));
    return;
  }

  if (enemy.buildings.market < 1 && canAfford(enemy, buildingCosts.market)) {
    logMessage(buildStructure(enemy, 'market'));
    return;
  }

  if (enemy.buildings.shinobi_den < 1 && canAfford(enemy, buildingCosts.shinobi_den) && state.turn > 6) {
    logMessage(buildStructure(enemy, 'shinobi_den'));
    return;
  }

  if (enemy.units.assassin < 1 && unitTypes.assassin.requires(enemy) && state.turn > 4) {
    logMessage(trainUnit(enemy, 'assassin'));
    return;
  }

  if (enemy.units.ninja < 1 && unitTypes.ninja.requires(enemy) && state.turn > 4) {
    logMessage(trainUnit(enemy, 'ninja'));
    return;
  }

  if (enemy.units.rider < 2 && unitTypes.rider.requires(enemy)) {
    logMessage(trainUnit(enemy, 'rider'));
    return;
  }

  if (enemy.buildings.wonder < 1 && canAfford(enemy, buildingCosts.wonder) && state.turn > 4) {
    logMessage(buildStructure(enemy, 'wonder'));
    return;
  }

  const neutralExists = state.regions.some((region) => !region.ownerId);
  if (neutralExists) {
    logMessage(claimRegion(enemy));
    return;
  }

  if (totalMilitary(enemy) >= 4 && enemy.truceUntilTurn < state.turn) {
    const retaliation = Math.max(8, armyPower(enemy) - 2);
    applyDamage(state.player, retaliation);
    logMessage(`${enemy.name} raids your frontier for ${retaliation} damage.`);
    return;
  }

  if (enemy.truceUntilTurn >= state.turn && enemy.buildings.market > 0 && enemy.resources.wood >= 20) {
    logMessage(tradeAtMarket(enemy));
    return;
  }

  logMessage(trainUnit(enemy, 'militia'));
}

function resolveHeirEvent(faction) {
  if (faction.townHealth <= 0 || faction.leader.hasHeir) {
    return;
  }

  if (Math.random() < 0.22) {
    faction.leader.hasHeir = true;
    logMessage(`${faction.name} celebrate the birth of an heir — the lord's line is secured.`);
  }
}

function resolveWorldEvent() {
  const livingFactions = [state.player, ...state.enemies].filter((faction) => faction && faction.townHealth > 0);
  const roll = Math.random();

  if (roll < 0.2) {
    state.currentEvent = 'The provinces are still. No wind disturbs the banners.';
    logMessage(state.currentEvent);
    return;
  }

  if (roll < 0.42) {
    livingFactions.forEach((faction) => {
      const fertileRegions = countTerrainMatches(faction, ['heartland', 'river', 'plains']);
      faction.resources.food += 6 + fertileRegions * 3;
    });
    state.currentEvent = 'The monsoon season brings a plentiful harvest across all provinces.';
    logMessage(state.currentEvent);
    return;
  }

  if (roll < 0.6) {
    livingFactions.forEach((faction) => {
      faction.resources.wood = Math.max(0, faction.resources.wood - 8);
    });
    state.currentEvent = 'A fierce typhoon strips 8 wood from every clan.';
    logMessage(state.currentEvent);
    return;
  }

  if (roll < 0.77) {
    livingFactions.forEach((faction) => {
      const floodZones = countTerrainMatches(faction, ['river']);
      if (floodZones > 0) {
        faction.resources.food = Math.max(0, faction.resources.food - floodZones * 7);
        faction.townHealth = Math.max(0, faction.townHealth - floodZones * 3);
      }
    });
    state.currentEvent = 'River floods sweep through delta holdings.';
    logMessage(state.currentEvent);
    return;
  }

  if (roll < 0.9) {
    livingFactions.forEach((faction) => {
      const groves = countTerrainMatches(faction, ['forest', 'grove']);
      if (groves > 0) {
        faction.resources.wood = Math.max(0, faction.resources.wood - groves * 10);
        faction.townHealth = Math.max(0, faction.townHealth - groves * 2);
      }
    });
    state.currentEvent = 'Wildfire devours bamboo groves and forested provinces.';
    logMessage(state.currentEvent);
    return;
  }

  livingFactions.forEach((faction) => {
    const faultLines = countTerrainMatches(faction, ['ridge', 'quarry', 'ruins']);
    if (faultLines > 0) {
      faction.resources.stone = Math.max(0, faction.resources.stone - faultLines * 10);
      faction.townHealth = Math.max(0, faction.townHealth - faultLines * 4);
    }
  });
  state.currentEvent = 'A great tremor shatters mountain passes and old stone fortifications.';
  logMessage(state.currentEvent);
}

function advanceWonder(faction) {
  if (faction.buildings.wonder > 0 && faction.wonderCountdown !== null) {
    faction.wonderCountdown -= 1;
    if (faction.wonderCountdown > 0) {
      logMessage(`${faction.name}'s wonder needs ${faction.wonderCountdown} more turn(s) to secure victory.`);
    }
  }
}

function attemptAssassination(attacker, targetId, killerType) {
  const killer = unitTypes[killerType];
  if (!killer || !['ninja', 'assassin'].includes(killerType)) {
    return 'Only shinobi or kunoichi can run covert missions.';
  }

  const target = findFactionById(targetId);
  if (!target || target.id === attacker.id || target.townHealth <= 0) {
    return 'Choose a living rival for a covert mission.';
  }

  if ((attacker.units[killerType] || 0) < 1) {
    return `Train a ${killer.label.toLowerCase()} first.`;
  }

  clearTruce(attacker, target);
  attacker.units[killerType] -= 1;
  const successChance = assassinationChance(attacker, target, killerType);

  if (Math.random() <= successChance) {
    if (!target.leader.hasHeir) {
      eliminateFaction(target, `${attacker.name}'s ${killer.label.toLowerCase()} cuts down ${target.leader.name}, ending ${target.name}'s line.`);
      return `${attacker.name}'s ${killer.label.toLowerCase()} kills ${target.leader.name}. ${target.name} collapse with no heir.`;
    }

    target.leader.hasHeir = false;
    target.leader.name = `Heir of ${target.leader.title}`;
    target.townHealth = Math.max(0, target.townHealth - 12);
    return `${attacker.name}'s ${killer.label.toLowerCase()} cuts down ${target.name}'s lord, but an heir steps forward to command.`;
  }

  target.resources.gold += 6;
  return `${attacker.name}'s ${killer.label.toLowerCase()} is exposed in ${target.name} and the plot fails.`;
}

// Map leader weakness/strength strings to killer type keys
function weaknessToKillerType(weaknessKey) {
  return weaknessKey === 'kunoichi' ? 'assassin' : 'ninja';
}

function assassinationChance(attacker, target, killerType) {
  let chance = killerType === 'assassin' ? 0.38 : 0.3;

  // ── Specialty bonuses ────────────────────────────────────────────────────────
  if (killerType === 'assassin') {
    const spec = attacker.assassinSpec;
    if (spec) {
      if (spec.bonus === 'heirless_targets' && !target.leader.hasHeir)          chance += 0.18;
      if (spec.bonus === 'rich_targets' && target.resources.gold >= 80)          chance += 0.15;
      if (spec.bonus === 'base_success')                                          chance += 0.10;
      if (spec.bonus === 'defended_targets' && target.buildings.barracks > 0)    chance += 0.15;
    }
  }

  if (killerType === 'ninja') {
    const spec = attacker.ninjaSpec;
    if (spec) {
      if (spec.bonus === 'large_targets' && countOwnedRegions(target) >= 3)      chance += 0.17;
      if (spec.bonus === 'heir_targets' && target.leader.hasHeir)                 chance += 0.15;
      if (spec.bonus === 'wonder_targets' && target.buildings.wonder > 0)         chance += 0.17;
    }
  }

  // ── Legacy chance bump for no-heir targets (assassin) and wealthy/big (ninja)
  if (killerType === 'ninja' && (countOwnedRegions(target) >= 3 || target.buildings.wonder > 0 || target.resources.gold >= 80)) {
    chance += 0.07; // smaller now since specialties already cover parts of this
  }

  // ── Leader weakness (bonus if attacker's killer type matches) ────────────────
  if (weaknessToKillerType(target.leader.weakness) === killerType) {
    chance += 0.20;
  }

  // ── Leader strength (penalty if attacker's killer type is resisted) ──────────
  if (weaknessToKillerType(target.leader.strength) === killerType) {
    chance -= 0.15;
  }

  if (countOwnedRegions(attacker) > countOwnedRegions(target)) {
    chance += 0.05;
  }

  return Math.min(0.82, Math.max(0.05, chance));
}

function evaluateWinConditions() {
  if (!state.player) {
    return;
  }

  if (state.player.townHealth <= 0) {
    state.gameOver = true;
    state.winner = state.player.leader.hasHeir
      ? 'Your clan survives, but the capital falls to rival powers.'
      : 'Your ruler is gone, no heir remains, and the clan is lost.';
    logMessage(state.winner);
    return;
  }

  const livingEnemies = state.enemies.filter((enemy) => enemy.townHealth > 0);
  if (livingEnemies.length === 0) {
    state.gameOver = true;
    state.winner = 'Conquest victory! Every rival capital has fallen.';
    logMessage(state.winner);
    return;
  }

  if (state.player.buildings.wonder > 0 && state.player.wonderCountdown !== null && state.player.wonderCountdown <= 0) {
    state.gameOver = true;
    state.winner = 'Wonder victory! Your monument defines the age.';
    logMessage(state.winner);
    return;
  }

  if (calculateScore(state.player) >= 220 && state.player.leader.hasHeir) {
    state.gameOver = true;
    state.winner = 'Dynastic prosperity victory! Your clan outgrows the competition and secures succession.';
    logMessage(state.winner);
    return;
  }

  const enemyWonderWinner = state.enemies.find(
    (enemy) => enemy.buildings.wonder > 0 && enemy.wonderCountdown !== null && enemy.wonderCountdown <= 0,
  );
  if (enemyWonderWinner) {
    state.gameOver = true;
    state.winner = `${enemyWonderWinner.name} wins by wonder dominance.`;
    logMessage(state.winner);
  }
}

function render() {
  if (!state.player) {
    overviewEl.innerHTML = '<p class="muted">Choose a clan and start a campaign.</p>';
    enemiesEl.innerHTML = '<p class="muted">Rival clans will appear here.</p>';
    regionsEl.innerHTML = '<p class="muted">The frontier map will appear here.</p>';
    logEl.innerHTML = '<li>Awaiting your first campaign.</li>';
    winConditionsEl.innerHTML = '<li class="objective-item">Multiple victory paths will appear here.</li>';
    enemySelect.innerHTML = '';
    abilityButton.textContent = 'Use clan ability';
    traitsEl.textContent = '';
    return;
  }

  const player = state.player;
  const score = calculateScore(player);
  const totalPopulation = player.villagers + totalMilitary(player);
  const ownedTerritories = countOwnedRegions(player);
  traitsEl.textContent = `${races[player.raceKey].summary} ${races[player.raceKey].traits} Affinity: ${formatAffinity(races[player.raceKey].affinity)}. ${races[player.raceKey].specialistFocus}`;

  overviewEl.innerHTML = [
    stat('Turn', state.turn),
    stat('Difficulty', difficultySettings[state.difficulty]?.label || 'Normal'),
    stat('Clan', races[player.raceKey].name),
    stat('Leader', `${player.leader.name} (${player.leader.title})`),
    stat('Weakness', player.leader.weakness),
    stat('Resists', player.leader.strength),
    stat('Heir', player.leader.hasHeir ? 'Secured' : 'None'),
    stat('Food', player.resources.food),
    stat('Wood', player.resources.wood),
    stat('Gold', player.resources.gold),
    stat('Stone', player.resources.stone),
    stat('Population', `${totalPopulation}/${player.popCap}`),
    stat('Villagers', player.villagers),
    stat('Army', formatArmy(player)),
    stat('Shinobi spec', `${player.ninjaSpec.label} — ${player.ninjaSpec.hint}`),
    stat('Kunoichi spec', `${player.assassinSpec.label} — ${player.assassinSpec.hint}`),
    stat('Spy den', player.buildings.shinobi_den > 0 ? 'Active' : 'None'),
    stat('Town health', player.townHealth),
    stat('Territories', ownedTerritories),
    stat('Score', score),
    stat('Affinity', formatAffinity(races[player.raceKey].affinity)),
    stat('World event', state.currentEvent),
  ].join('');

  winConditionsEl.innerHTML = [
    objective('Conquest', `${state.enemies.filter((enemy) => enemy.townHealth > 0).length} rival capitals remain.`, state.enemies.every((enemy) => enemy.townHealth <= 0)),
    objective('Prosperity', player.leader.hasHeir ? `${score}/220 score with a secure heir` : 'Secure an heir before claiming prosperity.', score >= 220 && player.leader.hasHeir),
    objective('Wonder', player.buildings.wonder > 0 ? `${Math.max(player.wonderCountdown, 0)} turn(s) left` : 'Build a wonder to begin the countdown.', player.buildings.wonder > 0 && player.wonderCountdown <= 0),
    objective('Succession', player.leader.hasHeir ? 'Your line is secure against sudden murder.' : 'An heir event is needed to prevent a succession loss.', player.leader.hasHeir),
  ].join('');

  regionsEl.innerHTML = state.regions
    .map((region) => {
      const owner = ownerLabel(region.ownerId);
      const classes = region.ownerId === player.id ? 'region-card owned' : region.ownerId ? 'region-card enemy-owned' : 'region-card neutral';
      return `<div class="${classes}"><strong>${region.name}</strong><span>${owner}</span><small>${capitalize(region.terrain)} · ${formatYield(region.yield)}</small></div>`;
    })
    .join('');

  enemiesEl.innerHTML = state.enemies
    .map((enemy) => {
      const alive = enemy.townHealth > 0;
      const wonderText = enemy.buildings.wonder > 0 ? `Wonder: ${Math.max(enemy.wonderCountdown, 0)} turn(s)` : 'No wonder';
      const heirText = enemy.leader.hasHeir ? 'Heir secured' : 'No heir';
      const truceText = enemy.truceUntilTurn >= state.turn ? `Truce until turn ${enemy.truceUntilTurn}` : 'No truce';
      const intel = player.knownIntel[enemy.id] || {};
      const weaknessText = intel.weaknessKnown ? `Vulnerable: ${enemy.leader.weakness}` : 'Weakness: ???';
      const strengthText = intel.strengthKnown ? `Resists: ${enemy.leader.strength}` : 'Resistance: ???';
      const spyDenText = enemy.buildings.shinobi_den > 0 ? ' · Spy den' : '';
      return `<div class="enemy-card"><strong>${enemy.name}</strong><span>${alive ? 'Alive' : 'Defeated'}</span><small>Lord ${enemy.leader.name} (${enemy.leader.title}) · ${heirText}</small><small>${weaknessText} · ${strengthText} · Run espionage to reveal</small><small>Health ${enemy.townHealth} · Army ${formatArmy(enemy)} · Provinces ${countOwnedRegions(enemy)} · ${wonderText}${spyDenText}</small><small>${truceText}</small></div>`;
    })
    .join('');

  enemySelect.innerHTML = state.enemies
    .filter((enemy) => enemy.townHealth > 0)
    .map((enemy) => `<option value="${enemy.id}">${enemy.name}</option>`)
    .join('');

  abilityButton.textContent = `${races[player.raceKey].abilityName}${state.turn < player.abilityReadyTurn ? ` (ready turn ${player.abilityReadyTurn})` : ''}`;
  logEl.innerHTML = state.log.map((entry) => `<li>${entry}</li>`).join('');

  document.querySelectorAll('button[data-action], #ability-button').forEach((button) => {
    button.disabled = state.gameOver;
  });
}

function stat(label, value) {
  return `<div class="stat-card"><small>${label}</small><strong>${value}</strong></div>`;
}

function objective(title, detail, complete) {
  return `<li class="objective-item ${complete ? 'complete' : ''}"><strong>${title}</strong><small>${detail}</small></li>`;
}

function logMessage(message) {
  state.log = [message, ...state.log].slice(0, 12);
}

function calculateScore(faction) {
  const resourceScore = Object.values(faction.resources).reduce((sum, value) => sum + Math.floor(value / 10), 0);
  const buildingScore = faction.buildings.house * 6 + faction.buildings.barracks * 10 + faction.buildings.market * 12 + faction.buildings.shinobi_den * 8 + faction.buildings.wonder * 40;
  const populationScore = faction.villagers * 4 + totalMilitary(faction) * 6 + faction.units.archer + faction.units.rider * 2 + faction.units.ninja + faction.units.assassin;
  const territoryScore = ownedRegions(faction)
    .map((region) => region.score)
    .reduce((sum, value) => sum + value, 0);
  const heirScore = faction.leader.hasHeir ? 12 : 0;
  return resourceScore + buildingScore + populationScore + territoryScore + heirScore;
}

function canAfford(faction, cost) {
  return Object.entries(cost).every(([resource, amount]) => faction.resources[resource] >= amount);
}

function payCost(faction, cost) {
  Object.entries(cost).forEach(([resource, amount]) => {
    faction.resources[resource] -= amount;
  });
}

function territoryYield(faction, resource) {
  return ownedRegions(faction).reduce((sum, region) => {
    let total = sum + (region.yield[resource] || 0);
    const affinity = races[faction.raceKey].affinity;
    if (resource === affinity.resource && affinity.terrains.includes(region.terrain)) {
      total += affinity.amount;
    }
    return total;
  }, 0);
}

function ownedRegions(faction) {
  return state.regions.filter((region) => region.ownerId === faction.id);
}

function countOwnedRegions(faction) {
  return ownedRegions(faction).length;
}

function countTerrainMatches(faction, terrains) {
  return ownedRegions(faction).filter((region) => terrains.includes(region.terrain)).length;
}

function totalMilitary(faction) {
  return Object.values(faction.units).reduce((sum, value) => sum + value, 0);
}

function armyPower(faction) {
  return Object.entries(faction.units).reduce((sum, [unit, count]) => {
    const modifier = faction.unitPower[unit] || 0;
    return sum + count * (unitTypes[unit].power + modifier);
  }, faction.attackBonus);
}

function applyDamage(target, damage) {
  target.townHealth = Math.max(0, target.townHealth - damage);
  if (target.townHealth === 0) {
    eliminateFaction(target);
  }
}

function eliminateFaction(target, extraLog = '') {
  target.townHealth = 0;
  Object.keys(target.units).forEach((unit) => {
    target.units[unit] = 0;
  });
  target.villagers = 0;
  releaseTerritories(target.id);
  if (extraLog) {
    logMessage(extraLog);
  }
}

function releaseTerritories(ownerId) {
  state.regions.forEach((region) => {
    if (region.ownerId === ownerId) {
      region.ownerId = null;
    }
  });
}

function ownerLabel(ownerId) {
  if (!ownerId) {
    return 'Neutral frontier';
  }
  if (ownerId === state.player.id) {
    return 'Your clan';
  }
  return state.enemies.find((enemy) => enemy.id === ownerId)?.name || 'Rival clan';
}

function findFactionById(id) {
  if (!id) {
    return null;
  }
  if (id === 'player') {
    return state.player;
  }
  return state.enemies.find((enemy) => enemy.id === id) || null;
}

function clearTruce(attacker, target) {
  if (attacker.truceUntilTurn >= state.turn || target.truceUntilTurn >= state.turn) {
    attacker.truceUntilTurn = 0;
    target.truceUntilTurn = 0;
  }
}

function formatYield(yieldMap) {
  return Object.entries(yieldMap)
    .map(([resource, amount]) => `+${amount} ${resource}`)
    .join(' · ');
}

function formatArmy(faction) {
  return `${totalMilitary(faction)} (${faction.units.militia} ashigaru / ${faction.units.archer} archers / ${faction.units.rider} cavalry / ${faction.units.ninja} shinobi / ${faction.units.assassin} kunoichi)`;
}

function formatAffinity(affinity) {
  return `${affinity.label} affinity (+${affinity.amount} ${affinity.resource} per matching region)`;
}

function capitalize(value) {
  return value.charAt(0).toUpperCase() + value.slice(1);
}

render();
