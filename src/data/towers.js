// 塔配置数据 - 腾讯级品质标准
// 迷宫守护者 V2.0

const TOWER_CONFIG = {
  // 象牙弓手 - 远程单体
  archer: {
    id: 'archer',
    name: '象牙弓手',
    emoji: '🐘',
    description: '远程单体攻击，稳定输出',
    cost: 50,
    levels: [
      { damage: 15, range: 3, fireRate: 1.0, sprite: 'level1' },
      { damage: 30, range: 3.5, fireRate: 1.2, cost: 40, sprite: 'level2' },
      { damage: 60, range: 4, fireRate: 1.5, cost: 80, sprite: 'level3' }
    ],
    super: { damage: 120, range: 5, fireRate: 2.0, sprite: 'super' },
    color: '#FFB347',
    attackType: 'arrow',
    sound: 'arrow_shot'
  },
  
  // 熊熊炮塔 - AOE范围
  cannon: {
    id: 'cannon',
    name: '熊熊炮塔',
    emoji: '🐻',
    description: 'AOE范围攻击，炸一片',
    cost: 100,
    levels: [
      { damage: 25, range: 2.5, fireRate: 0.8, aoeRadius: 1.2, sprite: 'level1' },
      { damage: 50, range: 3, fireRate: 0.8, aoeRadius: 1.5, cost: 80, sprite: 'level2' },
      { damage: 100, range: 3.5, fireRate: 0.8, aoeRadius: 2, cost: 160, sprite: 'level3' }
    ],
    super: { damage: 200, range: 4, fireRate: 1.0, aoeRadius: 2.5, sprite: 'super' },
    color: '#8B4513',
    attackType: 'explosion',
    sound: 'cannon_fire'
  },
  
  // 兔兔冰冻 - 减速控制
  freeze: {
    id: 'freeze',
    name: '兔兔冰冻',
    emoji: '🐰',
    description: '减速敌人，辅助控制',
    cost: 80,
    levels: [
      { damage: 8, range: 2.5, fireRate: 0.7, slowRate: 0.3, slowDuration: 120, sprite: 'level1' },
      { damage: 15, range: 3, fireRate: 0.7, slowRate: 0.5, slowDuration: 150, cost: 60, sprite: 'level2' },
      { damage: 30, range: 3.5, fireRate: 0.7, slowRate: 0.7, slowDuration: 180, cost: 120, sprite: 'level3' }
    ],
    super: { damage: 50, range: 4, fireRate: 0.8, slowRate: 0.85, slowDuration: 240, sprite: 'super' },
    color: '#E0FFFF',
    attackType: 'ice',
    sound: 'freeze_blast'
  },
  
  // 狮王烈焰 - 高伤穿透
  flame: {
    id: 'flame',
    name: '狮王烈焰',
    emoji: '🦁',
    description: '火焰穿透，直线多目标',
    cost: 200,
    levels: [
      { damage: 40, range: 2.5, fireRate: 0.5, pierce: 1, sprite: 'level1' },
      { damage: 80, range: 3, fireRate: 0.5, pierce: 2, cost: 150, sprite: 'level2' },
      { damage: 160, range: 3.5, fireRate: 0.5, pierce: 3, cost: 300, sprite: 'level3' }
    ],
    super: { damage: 320, range: 4, fireRate: 0.6, pierce: 5, sprite: 'super' },
    color: '#FF4500',
    attackType: 'flame',
    sound: 'flame_burst'
  },
  
  // 猴王闪电 - 连锁闪电
  lightning: {
    id: 'lightning',
    name: '猴王闪电',
    emoji: '🐒',
    description: '闪电连锁，跳多个敌人',
    cost: 150,
    levels: [
      { damage: 20, range: 2.5, fireRate: 0.6, chain: 2, sprite: 'level1' },
      { damage: 40, range: 3, fireRate: 0.6, chain: 3, cost: 120, sprite: 'level2' },
      { damage: 80, range: 3.5, fireRate: 0.6, chain: 4, cost: 240, sprite: 'level3' }
    ],
    super: { damage: 160, range: 4, fireRate: 0.7, chain: 6, sprite: 'super' },
    color: '#FFD700',
    attackType: 'lightning',
    sound: 'lightning_strike'
  },
  
  // 龙神终结 - BOSS杀手
  dragon: {
    id: 'dragon',
    name: '龙神终结',
    emoji: '🐉',
    description: '对BOSS额外伤害，斩杀神器',
    cost: 300,
    levels: [
      { damage: 50, range: 3, fireRate: 0.4, bossBonus: 0.5, sprite: 'level1' },
      { damage: 100, range: 3.5, fireRate: 0.4, bossBonus: 1.0, cost: 250, sprite: 'level2' },
      { damage: 200, range: 4, fireRate: 0.4, bossBonus: 2.0, cost: 500, sprite: 'level3' }
    ],
    super: { damage: 400, range: 5, fireRate: 0.5, bossBonus: 5.0, executeThreshold: 0.2, sprite: 'super' },
    color: '#4B0082',
    attackType: 'laser',
    sound: 'dragon_roar'
  }
};

// 塔类型列表（用于选择面板）
const TOWER_TYPES = ['archer', 'cannon', 'freeze', 'flame', 'lightning', 'dragon'];

module.exports = { TOWER_CONFIG, TOWER_TYPES };