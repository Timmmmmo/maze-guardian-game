// 引导系统 - 新手引导状态机
// 迷宫守护者 V2.0

class GuideSystem {
  constructor(game) {
    this.game = game;
    this.enabled = true;
    this.currentStep = 0;
    this.steps = [];
    this.highlightedCells = [];
    this.locked = false; // 是否锁定交互
  }
  
  // 设置引导步骤
  setSteps(steps) {
    this.steps = steps;
    this.currentStep = 0;
    if (this.steps.length > 0) {
      this.executeStep(0);
    }
  }
  
  // 执行指定步骤
  executeStep(index) {
    if (index >= this.steps.length) {
      this.complete();
      return;
    }
    
    const step = this.steps[index];
    this.clearHighlights();
    
    switch (step.type) {
      case 'highlight':
        this.showHighlight(step.target, step.text);
        if (step.forceTower) {
          this.game.ui.selectTower(step.forceTower);
        }
        break;
        
      case 'waitWave':
        this.showTip(step.text);
        this.waitForWave(step.wave);
        break;
        
      case 'complete':
        this.showComplete(step.text);
        break;
        
      case 'placeTower':
        this.showHighlight(step.target, step.text);
        this.game.ui.selectTower(step.tower);
        break;
        
      case 'highlightTower':
        this.showTowerHighlight(step.target, step.text);
        this.locked = true;
        this.waitForTowerClick(step.target, () => {
          this.nextStep();
        });
        break;
        
      case 'forceUpgrade':
        this.showUpgradePrompt(step.target, step.text);
        break;
        
      case 'introEnemy':
        this.showEnemyIntro(step.enemy, step.text);
        break;
        
      case 'introBoss':
        this.showBossIntro(step.text);
        break;
        
      case 'tip':
        this.showTip(step.text);
        setTimeout(() => this.nextStep(), 2000);
        break;
        
      case 'warn':
        this.showWarning(step.text);
        setTimeout(() => this.nextStep(), 3000);
        break;
        
      case 'suggestCombo':
        this.showComboSuggestion(step.combo, step.text);
        break;
    }
  }
  
  // 显示高亮提示
  showHighlight(target, text) {
    this.highlightedCells.push({ x: target.x, y: target.y });
    this.showBubble(target, text, 'highlight');
  }
  
  // 显示塔高亮
  showTowerHighlight(target, text) {
    this.highlightedCells.push({ x: target.x, y: target.y });
    this.showBubble(target, text, 'tower');
  }
  
  // 显示气泡提示
  showBubble(target, text, style) {
    const ui = this.game.ui;
    const cellSize = this.game.cellSize;
    
    // 创建提示气泡
    let bubble = document.getElementById('guide-bubble');
    if (!bubble) {
      bubble = document.createElement('div');
      bubble.id = 'guide-bubble';
      bubble.className = 'guide-bubble';
      document.body.appendChild(bubble);
    }
    
    bubble.textContent = text;
    bubble.className = `guide-bubble style-${style}`;
    
    // 定位气泡
    const x = (target.x + 0.5) * cellSize;
    const y = target.y * cellSize - 30;
    bubble.style.left = `${x}px`;
    bubble.style.top = `${y}px`;
    bubble.style.transform = 'translateX(-50%)';
    bubble.style.display = 'block';
    
    // 箭头指向
    if (style === 'highlight') {
      bubble.innerHTML = `<div class="arrow-down"></div>${text}`;
    }
  }
  
  // 显示文字提示
  showTip(text) {
    this.showBanner(text, 'tip');
  }
  
  // 显示警告
  showWarning(text) {
    this.showBanner(text, 'warn');
  }
  
  // 显示完成
  showComplete(text) {
    this.showBanner(text, 'success');
    setTimeout(() => this.complete(), 2000);
  }
  
  // 显示横幅
  showBanner(text, type) {
    let banner = document.getElementById('guide-banner');
    if (!banner) {
      banner = document.createElement('div');
      banner.id = 'guide-banner';
      document.body.appendChild(banner);
    }
    
    banner.textContent = text;
    banner.className = `guide-banner ${type}`;
    banner.style.display = 'block';
    
    setTimeout(() => {
      banner.style.display = 'none';
    }, 2500);
  }
  
  // 显示敌人介绍
  showEnemyIntro(enemyType, text) {
    const config = require('../data/enemies').ENEMY_CONFIG[enemyType];
    const emoji = config ? config.emoji : '👾';
    
    this.showBanner(`${emoji} ${text}`, 'info');
    setTimeout(() => this.nextStep(), 3000);
  }
  
  // 显示BOSS介绍
  showBossIntro(text) {
    this.showBanner(`👹 ${text}`, 'boss');
    setTimeout(() => this.nextStep(), 4000);
  }
  
  // 显示升级提示
  showUpgradePrompt(target, text) {
    this.showTowerHighlight(target, text);
    this.locked = true;
    
    // 监听升级按钮点击
    const checkUpgrade = () => {
      if (this.game.selectedTower && 
          this.game.selectedTower.x === target.x && 
          this.game.selectedTower.y === target.y) {
        // 显示升级按钮高亮
        const upgradeBtn = document.getElementById('btn-upgrade');
        if (upgradeBtn) {
          upgradeBtn.classList.add('highlight-pulse');
          upgradeBtn.onclick = () => {
            upgradeBtn.classList.remove('highlight-pulse');
            this.nextStep();
          };
        }
      } else {
        setTimeout(checkUpgrade, 100);
      }
    };
    checkUpgrade();
  }
  
  // 显示组合建议
  showComboSuggestion(combo, text) {
    const towerEmojis = combo.map(t => {
      const configs = require('../data/towers').TOWER_CONFIG;
      return configs[t] ? configs[t].emoji : '';
    }).join(' + ');
    
    this.showBanner(`${towerEmojis} ${text}`, 'combo');
    setTimeout(() => this.nextStep(), 4000);
  }
  
  // 等待指定波次
  waitForWave(waveNumber) {
    const check = () => {
      if (this.game.wave >= waveNumber) {
        this.nextStep();
      } else {
        setTimeout(check, 200);
      }
    };
    check();
  }
  
  // 等待点击塔
  waitForTowerClick(target, callback) {
    const check = () => {
      if (this.game.selectedTower &&
          this.game.selectedTower.x === target.x &&
          this.game.selectedTower.y === target.y) {
        callback();
      } else {
        setTimeout(check, 100);
      }
    };
    check();
  }
  
  // 下一步
  nextStep() {
    this.currentStep++;
    this.executeStep(this.currentStep);
  }
  
  // 完成引导
  complete() {
    this.clearHighlights();
    this.hideAllUI();
    this.enabled = false;
    
    // 触发完成回调
    if (this.onComplete) {
      this.onComplete();
    }
  }
  
  // 清除高亮
  clearHighlights() {
    this.highlightedCells = [];
  }
  
  // 隐藏所有引导UI
  hideAllUI() {
    const bubble = document.getElementById('guide-bubble');
    if (bubble) bubble.style.display = 'none';
    
    const banner = document.getElementById('guide-banner');
    if (banner) banner.style.display = 'none';
  }
  
  // 检查是否点击了高亮区域
  isValidClick(x, y) {
    if (!this.locked) return true;
    
    return this.highlightedCells.some(cell => cell.x === x && cell.y === y);
  }
  
  // 跳过引导
  skip() {
    this.complete();
  }
  
  // 保存引导进度
  saveProgress() {
    return {
      enabled: this.enabled,
      currentStep: this.currentStep,
      completed: !this.enabled
    };
  }
  
  // 加载引导进度
  loadProgress(data) {
    if (data && data.completed) {
      this.enabled = false;
    }
  }
}

module.exports = GuideSystem;