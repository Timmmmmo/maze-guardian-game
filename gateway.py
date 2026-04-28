#!/usr/bin/env python3
"""
OpenClaw 统一网关启动器
启动所有 /proxy 服务
"""
import subprocess
import sys
import time
import signal
from pathlib import Path

# 服务配置
SERVICES = {
    "finance": {
        "script": "stock_api/layer2_service_api.py",
        "port": 8765,
        "description": "金融数据API"
    },
    # "game": {
    #     "script": "MazeTD/config/api.py",
    #     "port": 8766,
    #     "description": "游戏配置API"
    # }
}

processes = []

def start_service(name: str, config: dict) -> subprocess.Popen:
    """启动单个服务"""
    script_path = Path(__file__).parent / config["script"]
    
    cmd = [
        sys.executable,
        str(script_path),
        "--port", str(config["port"])
    ]
    
    print(f"🚀 启动 {name}: {config['description']} (port {config['port']})")
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8'
    )
    
    return process

def start_all():
    """启动所有服务"""
    print("=" * 50)
    print("OpenClaw 统一网关启动")
    print("=" * 50)
    
    for name, config in SERVICES.items():
        try:
            proc = start_service(name, config)
            processes.append((name, proc))
            time.sleep(1)  # 等待服务启动
        except Exception as e:
            print(f"❌ 启动 {name} 失败: {e}")
    
    print("=" * 50)
    print("所有服务已启动")
    print("按 Ctrl+C 停止")
    print("=" * 50)
    
    # 保持运行
    try:
        while True:
            time.sleep(1)
            # 检查进程状态
            for name, proc in processes:
                if proc.poll() is not None:
                    print(f"⚠️ {name} 已退出，退出码: {proc.returncode}")
    except KeyboardInterrupt:
        shutdown()

def shutdown():
    """关闭所有服务"""
    print("\n🛑 正在关闭服务...")
    for name, proc in processes:
        proc.terminate()
        try:
            proc.wait(timeout=5)
            print(f"  ✅ {name} 已停止")
        except subprocess.TimeoutExpired:
            proc.kill()
            print(f"  ⚠️ {name} 强制停止")
    print("所有服务已关闭")

if __name__ == "__main__":
    start_all()
