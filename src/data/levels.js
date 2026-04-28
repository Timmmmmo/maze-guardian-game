// 关卡配置数据 - 新手引导关卡
// 迷宫守护者 V2.0

const LEVEL_CONFIG = {
  // ===== 新手引导关卡 =====
  
  // 1-1: 学会放塔
  tutorial_1: {
    id: 'tutorial_1',
    name: '第1关：初识守护',
    description: '学会放置第一个塔',
    difficulty: 'tutorial',
    mapSize: { cols: 9, rows: 7 },
    mazeSeed: 1, // 固定迷宫布局
    
    // 教学步骤
    tutorial: {
      steps: [
        { 
          type: 'highlight', 
          target: { x: 3, y: 2 }, 
          text: '点击这里放置象牙弓手',
          forceTower: 'archer'
        },
        {
          type: 'waitWave',
          wave: 1,
          text: '看！蘑菇来了，弓手会自动攻击'
        },
        {
          type: 'complete',
          text: '太棒了！你学会了放塔！'
        }
      ]
    },
    
    // 波次配置
    waves: [
      { enemies: [{ type: 'mushroom', count: 3, interval: 1500 }] }
    ],
    
    // 限制条件
    restrictions: {
      allowedTowers: ['archer'],
      maxTowers: 1,
      startGold: 100,
      startHp: 20
    },
    
    // 奖励
    rewards: {
      gold: 50,
      unlock: 'tutorial_2'
    }
  },
  
  // 1-2: 学会升级
  tutorial_2: {
    id: 'tutorial_2',
    name: '第2关：塔的力量',
    description: '学会升级塔',
    difficulty: 'tutorial',
    mapSize: { cols: 9, rows: 7 },
    mazeSeed: 2,
    
    tutorial: {
      steps: [
        {
          type: 'placeTower',
          target: { x: 2, y: 2 },
          tower: 'archer',
          text: '先放一个弓手'
        },
        {
          type: 'highlightTower',
          target: { x: 2, y: 2 },
          text: '点击塔查看信息'
        },
        {
          type: 'forceUpgrade',
          target: { x: 2, y: 2 },
          text: '点击升级按钮！'
        },
        {
          type: 'complete',
          text: '升级成功！塔变强了！'
        }
      ]
    },
    
    waves: [
      { enemies: [{ type: 'mushroom', count: 5, interval: 1200 }] }
    ],
    
    restrictions: {
      allowedTowers: ['archer'],
      maxTowers: 2,
      startGold: 200,
      startHp: 20,
      forceUpgrade: true
    },
    
    rewards: {
      gold: 80,
      unlock: 'tutorial_3'
    }
  },
  
  // 1-3: 认识敌人
  tutorial_3: {
    id: 'tutorial_3',
    name: '第3关：敌人入侵',
    description: '认识蘑菇和南瓜',
    difficulty: 'easy',
    mapSize: { cols: 9, rows: 8 },
    mazeSeed: 3,
    
    tutorial: {
      steps: [
        {
          type: 'introEnemy',
          enemy: 'mushroom',
          text: '蘑菇小兵：普通敌人，金币+5'
        },
        {
          type: 'introEnemy',
          enemy: 'pumpkin',
          text: '南瓜战士：有护盾，首次受伤减半！'
        },
        {
          type: 'tip',
          text: '建议：弓手对付南瓜需要更多火力'
        }
      ]
    },
    
    waves: [
      { enemies: [{ type: 'mushroom', count: 4, interval: 1000 }] },
      { enemies: [{ type: 'mushroom', count: 3, interval: 800 }, { type: 'pumpkin', count: 2, interval: 1200 }] }
    ],
    
    restrictions: {
      allowedTowers: ['archer', 'cannon'],
      startGold: 150,
      startHp: 15
    },
    
    rewards: {
      gold: 100,
      unlock: 'tutorial_4'
    }
  },
  
  // 1-4: 多塔配合
  tutorial_4: {
    id: 'tutorial_4',
    name: '第4关：策略搭配',
    description: '减速+输出的配合',
    difficulty: 'medium',
    mapSize: { cols: 9, rows: 9 },
    mazeSeed: 4,
    
    tutorial: {
      steps: [
        {
          type: 'tip',
          text: '兔兔冰冻可以减速敌人'
        },
        {
          type: 'tip',
          text: '减速后，其他塔更容易击杀'
        },
        {
          type: 'suggestCombo',
          combo: ['freeze', 'archer'],
          text: '试试：先放冰冻塔，再放弓手'
        }
      ]
    },
    
    waves: [
      { enemies: [{ type: 'mushroom', count: 5, interval: 600 }] },
      { enemies: [{ type: 'pumpkin', count: 4, interval: 800 }] },
      { enemies: [{ type: 'mushroom', count: 6, interval: 400 }, { type: 'pumpkin', count: 3, interval: 600 }] }
    ],
    
    restrictions: {
      allowedTowers: ['archer', 'cannon', 'freeze'],
      startGold: 200,
      startHp: 12
    },
    
    rewards: {
      gold: 150,
      unlock: 'tutorial_5'
    }
  },
  
  // 1-5: BOSS初遇
  tutorial_5: {
    id: 'tutorial_5',
    name: '第5关：魔王降临',
    description: '首次面对BOSS',
    difficulty: 'medium',
    mapSize: { cols: 9, rows: 10 },
    mazeSeed: 5,
    
    tutorial: {
      steps: [
        {
          type: 'introBoss',
          text: '暗影魔王：三阶段BOSS！'
        },
        {
          type: 'tip',
          text: '龙神终结塔对BOSS有额外伤害'
        },
        {
          type: 'warn',
          text: 'BOSS会变身：正常→狂暴→濒死'
        }
      ]
    },
    
    waves: [
      { enemies: [{ type: 'mushroom', count: 8, interval: 400 }] },
      { enemies: [{ type: 'pumpkin', count: 5, interval: 500 }] },
      { enemies: [{ type: 'boss', count: 1, interval: 0 }] } // BOSS波
    ],
    
    restrictions: {
      allowedTowers: ['archer', 'cannon', 'freeze', 'dragon'],
      startGold: 400,
      startHp: 10
    },
    
    rewards: {
      gold: 300,
      unlock: 'endless' // 解锁无尽模式
    }
  },
  
  // ===== 无尽模式 =====
  endless: {
    id: 'endless',
    name: '无尽挑战',
    description: '无限波次，挑战极限',
    difficulty: 'endless',
    mapSize: { cols: 9, rows: 12 },
    mazeSeed: 'random', // 每次随机迷宫
    
    // 无尽模式特殊规则
    endlessRules: {
      hpGrowth: 0.15,       // 每波HP增长
      countGrowth: 2,       // 每波敌人增加
      bossInterval: 10,     // 每10波BOSS
      skillInterval: 5      // 每5波选技能
    },
    
    restrictions: {
      allowedTowers: 'all',
      startGold: 100,
      startHp: 20
    },
    
    rewards: {
      type: 'score',
      record: 'highWave'
    }
  }
};

// 关卡解锁顺序
const LEVEL_ORDER = ['tutorial_1', 'tutorial_2', 'tutorial_3', 'tutorial_4', 'tutorial_5', 'endless'];

// 检查关卡是否解锁
function isLevelUnlocked(levelId, playerProgress) {
  const index = LEVEL_ORDER.indexOf(levelId);
  if (index === 0) return true; // 第一关默认解锁
  const prevLevel = LEVEL_ORDER[index - 1];
  return playerProgress.completedLevels.includes(prevLevel);
}

module.exports = { LEVEL_CONFIG, LEVEL_ORDER, isLevelUnlocked };