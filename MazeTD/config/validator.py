#!/usr/bin/env python3
"""
MazeTD 配置验证器 - Cloud Code 化
职责：验证游戏配置完整性、数值平衡性
原则：配置错误必须修复后才能运行，不自动修正
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

@dataclass
class ConfigValidationResult:
    valid: bool
    errors: List[str]
    warnings: List[str]
    stats: Dict[str, Any]

class GameConfigValidator:
    """游戏配置校验器"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent / "game_config.json"
        self.config_path = config_path
        self.config = None
    
    def load_config(self) -> bool:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            return True
        except Exception as e:
            return False
    
    def validate(self) -> ConfigValidationResult:
        """执行完整校验"""
        if not self.config:
            if not self.load_config():
                return ConfigValidationResult(
                    valid=False,
                    errors=["无法加载配置文件"],
                    warnings=[],
                    stats={}
                )
        
        errors = []
        warnings = []
        stats = {}
        
        # 校验塔配置
        tower_result = self._validate_towers()
        errors.extend(tower_result['errors'])
        warnings.extend(tower_result['warnings'])
        stats['towers'] = tower_result['stats']
        
        # 校验敌人配置
        enemy_result = self._validate_enemies()
        errors.extend(enemy_result['errors'])
        warnings.extend(enemy_result['warnings'])
        stats['enemies'] = enemy_result['stats']
        
        # 校验关卡配置
        level_result = self._validate_levels()
        errors.extend(level_result['errors'])
        warnings.extend(level_result['warnings'])
        stats['levels'] = level_result['stats']
        
        # 校验数值平衡
        balance_result = self._validate_balance()
        errors.extend(balance_result['errors'])
        warnings.extend(balance_result['warnings'])
        
        return ConfigValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            stats=stats
        )
    
    def _validate_towers(self) -> Dict:
        """校验塔配置"""
        errors = []
        warnings = []
        stats = {"count": 0, "total_upgrade_levels": 0}
        
        towers = self.config.get("towers", {})
        if not towers:
            errors.append("塔配置为空")
            return {"errors": errors, "warnings": warnings, "stats": stats}
        
        stats["count"] = len(towers)
        
        for tower_id, tower in towers.items():
            # 检查必填字段
            required = ["id", "name", "base_cost", "base_dps", "range", "upgrade_path"]
            for field in required:
                if field not in tower:
                    errors.append(f"塔[{tower_id}] 缺少字段: {field}")
            
            # 校验升级路径
            upgrade_path = tower.get("upgrade_path", [])
            if len(upgrade_path) != 5:
                errors.append(f"塔[{tower_id}] 升级路径必须有5级，当前{len(upgrade_path)}级")
            
            stats["total_upgrade_levels"] += len(upgrade_path)
            
            # 校验数值递增
            for i in range(1, len(upgrade_path)):
                prev = upgrade_path[i-1]
                curr = upgrade_path[i]
                if curr.get("cost", 0) <= prev.get("cost", 0):
                    warnings.append(f"塔[{tower_id}] L{i+1}成本应大于L{i}")
                if curr.get("dps", 0) <= prev.get("dps", 0):
                    errors.append(f"塔[{tower_id}] L{i+1}DPS应大于L{i}")
            
            # 校验性价比
            base_cost = tower.get("base_cost", 0)
            base_dps = tower.get("base_dps", 0)
            if base_cost > 0 and base_dps > 0:
                efficiency = base_dps / base_cost
                if efficiency < 0.1 or efficiency > 1.0:
                    warnings.append(f"塔[{tower_id}] 性价比异常: {efficiency:.3f} (建议0.2-0.5)")
        
        return {"errors": errors, "warnings": warnings, "stats": stats}
    
    def _validate_enemies(self) -> Dict:
        """校验敌人配置"""
        errors = []
        warnings = []
        stats = {"count": 0, "total_hp": 0, "avg_speed": 0}
        
        enemies = self.config.get("enemies", {})
        if not enemies:
            errors.append("敌人配置为空")
            return {"errors": errors, "warnings": warnings, "stats": stats}
        
        stats["count"] = len(enemies)
        total_speed = 0
        
        for enemy_id, enemy in enemies.items():
            required = ["id", "name", "hp", "speed", "reward", "damage"]
            for field in required:
                if field not in enemy:
                    errors.append(f"敌人[{enemy_id}] 缺少字段: {field}")
            
            hp = enemy.get("hp", 0)
            speed = enemy.get("speed", 0)
            reward = enemy.get("reward", 0)
            
            stats["total_hp"] += hp
            total_speed += speed
            
            # 校验数值范围
            if hp <= 0:
                errors.append(f"敌人[{enemy_id}] HP必须大于0")
            if speed <= 0 or speed > 5:
                errors.append(f"敌人[{enemy_id}] 速度异常: {speed}")
            if reward <= 0:
                errors.append(f"敌人[{enemy_id}] 奖励必须大于0")
            
            # 校验HP与奖励比例
            if hp > 0 and reward > 0:
                ratio = reward / hp
                if ratio < 0.01 or ratio > 0.5:
                    warnings.append(f"敌人[{enemy_id}] HP/奖励比例异常: {ratio:.3f}")
        
        stats["avg_speed"] = total_speed / len(enemies) if enemies else 0
        return {"errors": errors, "warnings": warnings, "stats": stats}
    
    def _validate_levels(self) -> Dict:
        """校验关卡配置"""
        errors = []
        warnings = []
        stats = {"count": 0, "total_waves": 0, "total_enemies": 0}
        
        levels = self.config.get("levels", [])
        if not levels:
            errors.append("关卡配置为空")
            return {"errors": errors, "warnings": warnings, "stats": stats}
        
        stats["count"] = len(levels)
        enemies_config = self.config.get("enemies", {})
        
        for i, level in enumerate(levels):
            level_id = level.get("id", i+1)
            
            # 检查必填字段
            required = ["id", "name", "start_gold", "start_lives", "waves"]
            for field in required:
                if field not in level:
                    errors.append(f"关卡[{level_id}] 缺少字段: {field}")
            
            waves = level.get("waves", [])
            stats["total_waves"] += len(waves)
            
            # 校验波次
            for wave_idx, wave in enumerate(waves):
                enemy_type = wave.get("enemy")
                count = wave.get("count", 0)
                
                if enemy_type not in enemies_config:
                    errors.append(f"关卡[{level_id}] 波次{wave_idx+1} 未知敌人类型: {enemy_type}")
                
                if count <= 0:
                    errors.append(f"关卡[{level_id}] 波次{wave_idx+1} 敌人数量必须大于0")
                
                stats["total_enemies"] += count
            
            # 校验星级阈值
            thresholds = level.get("star_thresholds", [])
            if len(thresholds) != 3:
                warnings.append(f"关卡[{level_id}] 星级阈值应为3个")
            else:
                if not (thresholds[0] < thresholds[1] < thresholds[2]):
                    warnings.append(f"关卡[{level_id}] 星级阈值应递增")
        
        return {"errors": errors, "warnings": warnings, "stats": stats}
    
    def _validate_balance(self) -> Dict:
        """校验数值平衡"""
        errors = []
        warnings = []
        
        towers = self.config.get("towers", {})
        enemies = self.config.get("enemies", {})
        levels = self.config.get("levels", [])
        
        # 计算理论DPS
        for level in levels:
            level_id = level.get("id")
            start_gold = level.get("start_gold", 0)
            waves = level.get("waves", [])
            
            # 计算敌人总HP
            total_enemy_hp = 0
            for wave in waves:
                enemy_type = wave.get("enemy")
                count = wave.get("count", 0)
                if enemy_type in enemies:
                    total_enemy_hp += enemies[enemy_type].get("hp", 0) * count
            
            # 计算可用塔的最大DPS
            max_tower_dps = 0
            for tower_id, tower in towers.items():
                base_cost = tower.get("base_cost", 9999)
                base_dps = tower.get("base_dps", 0)
                if base_cost <= start_gold:
                    max_tower_dps = max(max_tower_dps, base_dps)
            
            # 校验是否能通关
            if max_tower_dps > 0 and total_enemy_hp > 0:
                time_needed = total_enemy_hp / max_tower_dps
                if time_needed > 300:  # 超过5分钟可能太难
                    warnings.append(f"关卡[{level_id}] 理论通关时间过长: {time_needed:.0f}秒")
        
        return {"errors": errors, "warnings": warnings}
    
    def generate_report(self) -> str:
        """生成校验报告"""
        result = self.validate()
        
        lines = []
        lines.append("=" * 50)
        lines.append("MazeTD 配置校验报告")
        lines.append("=" * 50)
        lines.append(f"状态: {'✅ 通过' if result.valid else '❌ 失败'}")
        lines.append(f"")
        
        if result.errors:
            lines.append("【错误】必须修复:")
            for i, error in enumerate(result.errors, 1):
                lines.append(f"  {i}. {error}")
            lines.append("")
        
        if result.warnings:
            lines.append("【警告】建议优化:")
            for i, warning in enumerate(result.warnings, 1):
                lines.append(f"  {i}. {warning}")
            lines.append("")
        
        lines.append("【统计】")
        for category, stats in result.stats.items():
            lines.append(f"  {category}: {stats}")
        
        lines.append("=" * 50)
        
        return "\n".join(lines)

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    validator = GameConfigValidator()
    print(validator.generate_report())
