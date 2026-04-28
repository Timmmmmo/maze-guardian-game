// 敌人配置数据 - 腾讯级品质标准
// 迷宫守护者 V2.0

const ENEMY_CONFIG = {
  // 蘑菇小兵 - 普通怪
  mushroom: {
    id: 'mushroom',
    name: '蘑菇小兵',
    emoji: '🍄',
    description: '可爱的小蘑菇，蹦跳前进',
    baseHp: 50,
    speed: 1.0,
    gold: 5,
    size: 0.6,
    color: '#8FBC8F',
    abilities: [],
    sprite: 'mushroom',
    deathSound: 'mushroom_pop'
  },
  
  // 南瓜战士 - 中等怪
  pumpkin: {
    id: 'pumpkin',
    name: '南瓜战士',
    emoji: '🎃',
    description: '持盾南瓜，首次受伤减半',
    baseHp: 150,
    speed: 0.7,
    gold: 15,
    size: 0.75,
    color: '#FFA500',
    abilities: ['shield'], // 护盾：首次伤害减半
    sprite: 'pumpkin',
    deathSound: 'pumpkin_smash'
  },
  
  // 幽灵法师 - 高伤怪
  ghost: {
    id: 'ghost',
    name: '幽灵法师',
    emoji: '👻',
    description: '漂浮幽灵，会闪避攻击',
    baseHp: 300,
    speed: 0.9,
    gold: 30,
    size: 0.9,
    color: '#9370DB',
    abilities: ['dodge'], // 闪避：每5秒闪避一次
    sprite: 'ghost',
    deathSound: 'ghost_wooo'
  },
  
  // 石像巨人 - 超高防
  statue: {
    id: 'statue',
    name: '石像巨人',
    emoji: '🗿',
    description: '沉重石像，护甲减伤30%',
    baseHp: 800,
    speed: 0.4,
    gold: 80,
    size: 1.2,
    color: '#708090',
    abilities: ['armor'], // 护甲：减伤30%
    sprite: 'statue',
    deathSound: 'statue_crack'
  },
  
  // 暗影魔王 - BOSS
  boss: {
    id: 'boss',
    name: '暗影魔王',
    emoji: '👹',
    description: '三阶段BOSS，越来越疯狂',
    baseHp: 5000,
    speed: 0.3,
    gold: 500,
    size: 1.5,
    color: '#4B0082',
    abilities: ['phases'], // 三阶段变身
    phases: [
      { name: '正常', hpThreshold: 1.0, damageMultiplier: 1.0, speedMultiplier: 1.0 },
      { name: '狂暴', hpThreshold: 0.5, damageMultiplier: 1.5, speedMultiplier: 1.2 },
      { name: '濒死', hpThreshold: 0.2, damageMultiplier: 2.0, speedMultiplier: 0.8 }
    ],
    sprite: 'boss',
    deathSound: 'boss_fall'
  }
};

// 敌人类型列表
const ENEMY_TYPES = ['mushroom', 'pumpkin', 'ghost', 'statue', 'boss'];

// 波次生成规则
const WAVE_RULES = {
  // 普通波次
  normal: {
    baseCount: 5,      // 基础敌人数量
    countGrowth: 2,    // 每波增加数量
    hpGrowth: 0.15,    // HP增长率（每波）
    enemyTypes: ['mushroom'] // 初始只有蘑菇
  },
  
  // BOSS波次（每10波）
  boss: {
    interval: 10,      // 每10波出BOSS
    hpGrowth: 0.3      // BOSS HP增长率更高
  },
  
  // 敌人解锁波次
  unlockWave: {
    pumpkin: 3,        // 波3解锁南瓜
    ghost: 6,          // 波6解锁幽灵
    statue: 10         // 波10解锁石像
  }
};

module.exports = { ENEMY_CONFIG, ENEMY_TYPES, WAVE_RULES };