// 关卡管理器 - 关卡加载与进度追踪
// 迷宫守护者 V2.0

const { LEVEL_CONFIG, LEVEL_ORDER, isLevelUnlocked } = require('../data/levels');

class LevelManager {
  constructor(game) {
    this.game = game;
    this.currentLevel = null;
    this.playerProgress = {
      completedLevels: [],
      highScores: {},
      unlockedTowers: ['archer'],
      totalPlayTime: 0,
      totalKills: 0
    };
    
    // 加载存档
    this.loadProgress();
  }
  
  // 获取关卡配置
  getLevelConfig(levelId) {
    return LEVEL_CONFIG[levelId] || null;
  }
  
  // 加载关卡
  loadLevel(levelId) {
    const config = this.getLevelConfig(levelId);
    if (!config) {
      console.error(`Level not found: ${levelId}`);
      return false;
    }
    
    // 检查是否解锁
    if (!isLevelUnlocked(levelId, this.playerProgress)) {
      console.warn(`Level locked: ${levelId}`);
      return false;
    }
    
    this.currentLevel = {
      ...config,
      currentWave: 0,
      totalWaves: config.waves ? config.waves.length : 0,
      enemiesRemaining: 0
    };
    
    // 应用关卡限制
    this.game.gold = config.restrictions?.startGold || 100;
    this.game.hp = config.restrictions?.startHp || 20;
    this.game.maxHp = config.restrictions?.startHp || 20;
    
    // 设置允许的塔类型
    if (config.restrictions?.allowedTowers === 'all') {
      this.game.allowedTowers = null; // 全部允许
    } else {
      this.game.allowedTowers = config.restrictions?.allowedTowers || null;
    }
    
    return true;
  }
  
  // 开始关卡
  startLevel() {
    if (!this.currentLevel) return false;
    
    const level = this.currentLevel;
    
    // 生成迷宫
    this.game.generateMaze();
    
    // 清空战场
    this.game.towers = [];
    this.game.enemies = [];
    this.game.bullets = [];
    this.game.particles = [];
    
    // 重置游戏状态
    this.game.wave = 0;
    this.game.kills = 0;
    this.game.selectedTower = null;
    this.game.isPlaying = true;
    
    // 启动引导系统
    if (level.tutorial) {
      this.game.guideSystem = new (require('./GuideSystem'))(this.game);
      this.game.guideSystem.setSteps(level.tutorial.steps);
      this.game.guideSystem.onComplete = () => {
        this.onTutorialComplete();
      };
    }
    
    // 启动关卡
    this.startNextWave();
    
    return true;
  }
  
  // 下一波
  startNextWave() {
    if (!this.currentLevel) return;
    
    const level = this.currentLevel;
    level.currentWave++;
    
    // 无尽模式波次生成
    if (level.difficulty === 'endless') {
      this.spawnEndlessWave(level.currentWave);
      return;
    }
    
    // 固定波次
    if (level.waves && level.currentWave <= level.waves.length) {
      const waveConfig = level.waves[level.currentWave - 1];
      this.spawnWaveConfig(waveConfig);
    } else {
      // 关卡完成
      this.completeLevel();
    }
  }
  
  // 生成无尽波次
  spawnEndlessWave(waveNum) {
    const rules = this.currentLevel.endlessRules;
    
    // 每10波BOSS
    if (waveNum % rules.bossInterval === 0) {
      const bossHp = 5000 * (1 + waveNum * 0.3);
      this.game.spawnEnemy('boss', bossHp);
    } else {
      // 普通波次
      const baseCount = 5 + Math.floor(waveNum / 3) * 2;
      const hpMultiplier = 1 + waveNum * 0.15;
      
      // 根据波次引入更难的敌人
      const availableEnemies = ['mushroom'];
      if (waveNum >= 3) availableEnemies.push('pumpkin');
      if (waveNum >= 6) availableEnemies.push('ghost');
      if (waveNum >= 10) availableEnemies.push('statue');
      
      // 生成敌人
      for (let i = 0; i < baseCount; i++) {
        const type = availableEnemies[Math.floor(Math.random() * availableEnemies.length)];
        const hp = this.game.enemyConfigs[type].baseHp * hpMultiplier;
        const delay = Math.max(300, 800 - waveNum * 20); // 越后期越快
        
        setTimeout(() => {
          if (this.game.isPlaying) {
            this.game.spawnEnemy(type, hp);
          }
        }, i * delay);
      }
    }
    
    this.currentLevel.enemiesRemaining = this.countWaveEnemies();
  }
  
  // 生成波次配置中的敌人
  spawnWaveConfig(waveConfig) {
    let delay = 0;
    
    waveConfig.enemies.forEach(group => {
      for (let i = 0; i < group.count; i++) {
        setTimeout(() => {
          if (this.game.isPlaying) {
            const hp = this.game.enemyConfigs[group.type].baseHp;
            this.game.spawnEnemy(group.type, hp);
          }
        }, delay);
        delay += group.interval;
      }
    });
    
    this.currentLevel.enemiesRemaining = this.countWaveEnemies();
  }
  
  // 统计波次敌人数量
  countWaveEnemies() {
    if (this.currentLevel.waves) {
      const waveConfig = this.currentLevel.waves[this.currentLevel.currentWave - 1];
      if (waveConfig) {
        return waveConfig.enemies.reduce((sum, g) => sum + g.count, 0);
      }
    }
    return 10; // 默认
  }
  
  // 敌人在终点
  onEnemyReachEnd(enemy) {
    this.game.hp--;
    this.game.shaking = 10;
    
    if (this.game.hp <= 0) {
      this.gameOver();
    }
  }
  
  // 敌人死亡
  onEnemyKilled(enemy) {
    this.game.kills++;
    this.game.gold += enemy.gold;
    
    if (this.currentLevel) {
      this.currentLevel.enemiesRemaining--;
      
      // 检查波次是否完成
      if (this.currentLevel.enemiesRemaining <= 0 && this.game.enemies.length === 0) {
        setTimeout(() => this.startNextWave(), 1000);
      }
    }
  }
  
  // 关卡完成
  completeLevel() {
    if (!this.currentLevel) return;
    
    const level = this.currentLevel;
    this.game.isPlaying = false;
    
    // 保存进度
    if (!this.playerProgress.completedLevels.includes(level.id)) {
      this.playerProgress.completedLevels.push(level.id);
    }
    
    // 记录成绩
    this.playerProgress.highScores[level.id] = Math.max(
      this.playerProgress.highScores[level.id] || 0,
      this.game.wave
    );
    
    // 发放奖励
    if (level.rewards) {
      if (level.rewards.gold) {
        this.game.gold += level.rewards.gold;
      }
      if (level.rewards.unlock) {
        // 解锁新关卡/塔等
        this.unlock(level.rewards.unlock);
      }
    }
    
    this.saveProgress();
    
    // 显示结算界面
    this.game.ui.showResult(true, {
      level: level.name,
      wave: this.game.wave,
      kills: this.game.kills,
      gold: level.rewards?.gold || 0
    });
  }
  
  // 游戏结束
  gameOver() {
    this.game.isPlaying = false;
    
    // 保存记录
    if (this.currentLevel?.difficulty === 'endless') {
      this.playerProgress.highScores['endless'] = Math.max(
        this.playerProgress.highScores['endless'] || 0,
        this.game.wave
      );
    }
    
    this.playerProgress.totalKills += this.game.kills;
    this.saveProgress();
    
    // 显示结算界面
    this.game.ui.showResult(false, {
      level: this.currentLevel?.name || '无尽挑战',
      wave: this.game.wave,
      kills: this.game.kills
    });
  }
  
  // 解锁内容
  unlock(type) {
    if (type.startsWith('tutorial_')) {
      // 解锁新关卡
      console.log(`Unlocked: ${type}`);
    } else if (['archer', 'cannon', 'freeze', 'flame', 'lightning', 'dragon'].includes(type)) {
      // 解锁新塔
      if (!this.playerProgress.unlockedTowers.includes(type)) {
        this.playerProgress.unlockedTowers.push(type);
      }
    }
  }
  
  // 教程完成回调
  onTutorialComplete() {
    console.log('Tutorial completed!');
  }
  
  // 保存进度到localStorage
  saveProgress() {
    try {
      localStorage.setItem('mazeGuardian_progress', JSON.stringify(this.playerProgress));
    } catch (e) {
      console.error('Failed to save progress:', e);
    }
  }
  
  // 加载进度
  loadProgress() {
    try {
      const saved = localStorage.getItem('mazeGuardian_progress');
      if (saved) {
        this.playerProgress = { ...this.playerProgress, ...JSON.parse(saved) };
      }
    } catch (e) {
      console.error('Failed to load progress:', e);
    }
  }
  
  // 获取最高记录
  getHighScore(levelId) {
    return this.playerProgress.highScores[levelId] || 0;
  }
  
  // 获取可玩关卡列表
  getAvailableLevels() {
    return LEVEL_ORDER.map(id => ({
      id,
      config: this.getLevelConfig(id),
      unlocked: isLevelUnlocked(id, this.playerProgress),
      highScore: this.getHighScore(id)
    }));
  }
}

module.exports = LevelManager;