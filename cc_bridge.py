#!/usr/bin/env python3
import subprocess, sys, json
from pathlib import Path
from datetime import datetime

class CCBridge:
    def __init__(self, root="/home/sevenstars/CLionProjects/Oasis"):
        self.root = Path(root)
        (self.root / "cc_prompt").mkdir(exist_ok=True)
        (self.root / "cc_results").mkdir(exist_ok=True)
    
    def execute(self, task_id, title, content):
        prompt = f"# Task: {title}\n\nProject: /home/sevenstars/CLionProjects/Oasis\n\n{content}"
        
        # 保存任务
        (self.root / "cc_prompt" / f"{task_id}.md").write_text(prompt)
        
        print(f"\n{'='*60}\n📤 任务: {task_id} - {title}\n{'='*60}\n")
        
        # 调用 claude CLI (使用 --print 获取非交互输出)
        result = subprocess.run(["claude", "--print"], input=prompt.encode(), 
                              capture_output=True, timeout=300)
        
        output = result.stdout.decode('utf-8', errors='ignore') if result.returncode == 0 else result.stderr.decode('utf-8', errors='ignore')
        
        # 保存结果
        (self.root / "cc_results" / f"{task_id}_result.md").write_text(f"# 执行结果\n\n{output}")
        
        print(output)
        print(f"\n✅ 完成！结果已保存\n{'='*60}\n")

if __name__ == "__main__":
    bridge = CCBridge()
    if len(sys.argv) >= 4:
        bridge.execute(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "")
    else:
        print("用法: python cc_bridge.py execute <task_id> <title> <content>")
