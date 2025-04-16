import json
import socket
import subprocess
import sys
import os

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return False
        except socket.error:
            return True

def load_config():
    try:
        with open('mcp_config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("配置文件未找到：mcp_config.json")
        sys.exit(1)

def start_mcp_server(config):
    if not is_port_in_use(config['mcp_server']['port']):
        print(f"正在启动MCP服务器，端口：{config['mcp_server']['port']}")
        try:
            # 使用npx启动服务器
            subprocess.Popen(
                f"npx {config['mcp_server']['package']}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print("MCP服务器启动成功！")
        except Exception as e:
            print(f"启动MCP服务器时出错：{str(e)}")
            sys.exit(1)
    else:
        print(f"MCP服务器已经在运行，端口：{config['mcp_server']['port']}")

if __name__ == "__main__":
    config = load_config()
    if config['mcp_server']['auto_start']:
        start_mcp_server(config) 