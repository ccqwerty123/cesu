import subprocess
import json
import os
import datetime
import requests
import time
import base64
import signal
import urllib.parse

def get_xray_speed_and_verify():
    vmess_configs = [
        "vmess://ew0KICAidiI6ICIyIiwNCiAgInBzIjogIlx1ODFFQVx1OTAwOSBoYXgtY2xvbmUiLA0KICAiYWRkIjogImNmLjBzbS5jb20iLA0KICAicG9ydCI6ICI4MCIsDQogICJpZCI6ICIzMzgwOWNkNC0zMDk1LTQ0N2QtZGI2Ny0wZTYwN2RkMjNkNWIiLA0KICAiYWlkIjogIjAiLA0KICAic2N5IjogImF1dG8iLA0KICAibmV0IjogIndzIiwNCiAgInR5cGUiOiAibm9uZSIsDQogICJob3N0IjogInZwcy54aW5jZXMwMDEuZmlsZWdlYXItc2cubWUiLA0KICAicGF0aCI6ICIvIiwNCiAgInRscyI6ICIiLA0KICAic25pIjogIiIsDQogICJhbHBuIjogIiIsDQogICJmcCI6ICIiDQp9",
        "vmess://ew0KICAidiI6ICIyIiwNCiAgInBzIjogIlx1NTcxRlx1ODAzM1x1NTE3NjEiLA0KICAiYWRkIjogImNkbjEuYnBjZG4uY2MiLA0KICAicG9ydCI6ICI4MCIsDQogICJpZCI6ICI2ZjQyY2ZlNS02NGYxLTQ2NmQtODg2MC04NTlkOGUwZjBhOTgiLA0KICAiYWlkIjogIjAiLA0KICAic2N5IjogImF1dG8iLA0KICAibmV0IjogIndzIiwNCiAgInR5cGUiOiAibm9uZSIsDQogICJob3N0IjogInRrMS5iazVqaDR0Nncuamllc2s0cGRxY3FqbzE2ai54eXoiLA0KICAicGF0aCI6ICIvIiwNCiAgInRscyI6ICIiLA0KICAic25pIjogIiIsDQogICJhbHBuIjogIiIsDQogICJmcCI6ICIiDQp9"
    ]
    results = []
    xray_socks_port = 1081  # Hardcoded socks proxy port
    xray_config_file = os.path.join(os.getcwd(), "config.json")  # 设置文件名和路径
    xray_path = os.path.join(os.getcwd(), "xray")  # 获取 xray 的绝对路径
    xray_dir = os.path.dirname(xray_path)  # 获取 xray 所在的目录
   

    # 确保 xray 可执行文件存在
    if not os.path.exists(xray_path):
      print(f"Error: Could not find 'xray' executable at '{xray_path}'.")
      return None
    
     # 打印 xray 文件列表
    print("Xray files:")
    for item in os.listdir(xray_dir):
        print(item)
    
    # 尝试运行 Xray 
    print("Checking Xray executable...")
    try:
        xray_version_output = subprocess.run(
            [xray_path, "-version"],
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"Xray version:\n{xray_version_output.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Error: Xray executable check failed: {e}")
        return None
    except Exception as e:
      print(f"Error: Xray executable check failed: {e}")
      return None

    
    # 启动 Xray
    print("Starting Xray...")
    xray_process = subprocess.Popen(
                [xray_path, "-c", os.path.basename(xray_config_file)], # 使用相对于xray执行文件的路径
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=xray_dir,
                )
    time.sleep(5)


    for vmess_b64 in vmess_configs:
        try:
           # 添加 padding
           missing_padding = len(vmess_b64) % 4
           if missing_padding:
               vmess_b64 += '='* (4 - missing_padding)
           
           # 使用urlsafe_b64decode
           vmess_json_str = base64.urlsafe_b64decode(vmess_b64[8:]).decode("utf-8")
           vmess_config = json.loads(vmess_json_str)
        except Exception as e:
            print(f"Error: Failed to decode or parse Vmess config: {e}")
            continue # 如果解析失败，跳过这个节点

        print(f"Testing Vmess config: {vmess_config.get('ps','')}")

        # 创建 Xray config.json 文件
        print(f"Creating Xray config file at: {xray_config_file}...")
        
        address = vmess_config["add"]
        port = vmess_config["port"]
        id = vmess_config["id"]
        alterId = vmess_config["aid"]
        security = vmess_config["scy"]
        net = vmess_config["net"]
        type = vmess_config["type"]
        host = vmess_config["host"]
        path = vmess_config["path"]
        tls = vmess_config["tls"]
       
        config =  {
             "log": {
                "access": "",
                "error": "",
                "loglevel": "warning"
            },
            "inbounds": [
                {
                "tag": "socks",
                "port": xray_socks_port,
                "listen": "0.0.0.0",
                "protocol": "socks",
                "sniffing": {
                    "enabled": True,
                    "destOverride": [
                    "http",
                    "tls"
                    ],
                    "routeOnly": False
                },
                "settings": {
                    "auth": "noauth",
                    "udp": True,
                    "allowTransparent": False
                }
                }
            ],
            "outbounds": [
                {
                "tag": "proxy",
                "protocol": "vmess",
                "settings": {
                    "vnext": [
                    {
                        "address": address,
                        "port": int(port),
                        "users": [
                        {
                            "id": id,
                            "alterId": int(alterId),
                            "email": "t@t.tt",
                            "security": security
                        }
                        ]
                    }
                    ]
                },
                "streamSettings": {
                    "network": "ws",
                    "wsSettings": {
                    "path": path,
                    "headers": {
                        "Host": host
                    }
                    }
                },
                "mux": {
                    "enabled": False,
                    "concurrency": -1
                }
                },
                {
                "tag": "direct",
                "protocol": "freedom",
                "settings": {}
                },
                {
                "tag": "block",
                "protocol": "blackhole",
                "settings": {
                    "response": {
                    "type": "http"
                    }
                }
                }
            ],
            "dns": {
                "hosts": {
                "dns.google": "8.8.8.8",
                "proxy.example.com": "127.0.0.1"
                },
                "servers": [
                {
                    "address": "180.76.76.76",
                    "domains": [
                    "geosite:cn",
                    "geosite:geolocation-cn"
                    ],
                    "expectIPs": [
                    "geoip:cn"
                    ]
                },
                "1.1.1.1",
                "8.8.8.8",
                "https://dns.google/dns-query",
                {
                    "address": "223.5.5.5",
                    "domains": [
                    "cdn1.bpcdn.cc"
                    ]
                }
                ]
            },
            "routing": {
                "domainStrategy": "AsIs",
                "rules": [
                {
                    "type": "field",
                    "inboundTag": [
                    "api"
                    ],
                    "outboundTag": "api"
                },
                {
                    "type": "field",
                    "port": "443",
                    "network": "udp",
                    "outboundTag": "block"
                },
                {
                    "type": "field",
                    "port": "0-65535",
                    "outboundTag": "proxy"
                }
                ]
            }
        }
       
        with open(xray_config_file, "w") as f:
            json.dump(config, f, indent=4)
        print(f"Xray config file has been created at : {xray_config_file}")
        
        #打印 config.json的内容，确保配置正确
        with open(xray_config_file, "r") as f:
            config_content = f.read()
            print(f"Xray config file content: {config_content}")

        try:
           # 获取本机 IP
            print("Getting direct IP...")
            try:
                direct_ip = requests.get("https://api.ipify.org", timeout=10).text.strip()
                print(f"Direct IP: {direct_ip}")
            except requests.exceptions.RequestException as e:
                print(f"Error getting direct IP: {e}")
                continue


            # 1. 测试代理是否正常运行
            print("Testing Proxy...")
            try:
                proxies = {
                    "http": f"socks5://127.0.0.1:{xray_socks_port}",
                    "https": f"socks5://127.0.0.1:{xray_socks_port}"
                }
                proxy_ip = requests.get("https://api.ipify.org", proxies=proxies, timeout=10).text.strip()
                print(f"Proxy test passed, IP: {proxy_ip}")
                if direct_ip == proxy_ip:
                     print("Proxy test failed: direct IP and proxy IP are the same.")
                     continue
            except requests.exceptions.RequestException as e:
               print(f"Proxy test failed: {e}")
               continue

           # 2. 进行速度测试
            print("Starting speed test...")
            result = subprocess.run(
                [xray_path, "api", "stats.query", "--server=127.0.0.1:10085","outbound.proxy.user.traffic","outbound.direct.user.traffic"],
                capture_output=True,
                text=True,
                check=True,
                env=os.environ.copy(),
            )
            if result.returncode != 0:
                print(f"Error: xctl failed with code {result.returncode}, output: {result.stderr}")
                continue

            initial_stats = json.loads(result.stdout.strip())
            initial_outbound_proxy_traffic = initial_stats["stat"][0]["value"] if len(initial_stats["stat"]) > 0 else 0
            initial_outbound_direct_traffic = initial_stats["stat"][1]["value"] if len(initial_stats["stat"]) > 1 else 0

           # 发起一些流量
            test_speed_result = subprocess.run(
                ["curl","-v","https://www.google.com","--proxy",f"socks5://127.0.0.1:{xray_socks_port}"],
                capture_output=True,
                text=True,
                check=False,
                env=os.environ.copy(),
            )
            if test_speed_result.returncode != 0:
                print(f"Error: speed test failed with code {test_speed_result.returncode}, output: {test_speed_result.stderr}")
                continue

           # 获取结束流量
            result_after = subprocess.run(
               [xray_path, "api", "stats.query", "--server=127.0.0.1:10085","outbound.proxy.user.traffic","outbound.direct.user.traffic"],
                capture_output=True,
                text=True,
                check=True,
                env=os.environ.copy(),
            )
            if result_after.returncode != 0:
                print(f"Error: xctl failed with code {result_after.returncode}, output: {result_after.stderr}")
                continue

            after_stats = json.loads(result_after.stdout.strip())
            after_outbound_proxy_traffic = after_stats["stat"][0]["value"] if len(after_stats["stat"]) > 0 else 0
            after_outbound_direct_traffic = after_stats["stat"][1]["value"] if len(after_stats["stat"]) > 1 else 0

            outbound_proxy_diff = after_outbound_proxy_traffic - initial_outbound_proxy_traffic
            outbound_direct_diff = after_outbound_direct_traffic - initial_outbound_direct_traffic
            results.append(
                {
                    "vmess_config": vmess_config.get('ps',''),
                    "outbound_proxy_bytes": outbound_proxy_diff,
                    "outbound_direct_bytes": outbound_direct_diff,
                 }
            )
        except Exception as e:
           print(f"Error:  failed: {e}")
        finally:
            # 使用信号量重载配置
            print("Reloading Xray config...")
            os.kill(xray_process.pid, signal.SIGHUP)
            time.sleep(1) # 等待信号量处理完成
            if os.path.exists(xray_config_file):
                os.remove(xray_config_file)

    # 停止 Xray
    print("Stopping Xray...")
    xray_process.terminate()
    xray_process.wait()
    return results


if __name__ == "__main__":
   
    speed_data_list = get_xray_speed_and_verify()
    if speed_data_list:
             current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
             print(f"Speed Test Result {current_time}:")
             for data in speed_data_list:
                print(f"  Node: {data['vmess_config']}")
                print(f"  Outbound proxy traffic: {data['outbound_proxy_bytes']} bytes")
                print(f"  Outbound direct traffic: {data['outbound_direct_bytes']} bytes")
