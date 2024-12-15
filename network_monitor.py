import subprocess
import sys
import importlib
import time
from datetime import datetime
import platform

def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Check and install required packages
def install_package(package_name):
    """
    Install a Python package using pip
    """
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {package_name}. Error: {e}")
        return False

def ensure_packages(package_requirements):
    """
    Check and install required packages if they're not already installed
    Args:
        package_requirements: List of tuples (pip_name, import_name)
    """
    for pip_name, import_name in package_requirements:
        try:
            importlib.import_module(import_name)
            print(f"{pip_name} is already installed.")
        except ImportError:
            print(f"Installing {pip_name}...")
            if install_package(pip_name):
                print(f"Successfully installed {pip_name}")
            else:
                print(f"Failed to install {pip_name}. Please install it manually.")
                sys.exit(1)

def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org')
        return response.text
    except:
        return "Unable to get IP"

def ping_google():
    # Determine the ping command based on the operating system
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', 'google.com']
    
    try:
        output = subprocess.check_output(command).decode('utf-8')
        if platform.system().lower() == 'windows':
            if 'TTL=' in output:
                # Extract time from Windows ping output
                time_str = output.split('时间=')[-1].split('ms')[0].strip()
                return True, float(time_str)
        else:
            if 'time=' in output:
                # Extract time from Unix ping output
                time_str = output.split('time=')[-1].split(' ')[0].strip()
                return True, float(time_str)
        return True, 0
    except:
        return False, 0

def get_active_network_service():
    try:
        # 获取默认路由对应的网络接口
        route_output = subprocess.check_output(["route", "-n", "get", "default"]).decode("utf-8")
        active_interface = None
        for line in route_output.splitlines():
            if "interface:" in line:
                active_interface = line.split(":")[1].strip()
                break

        if not active_interface:
            return "No Active Network", None

        # 获取该接口的具体名称
        networksetup_output = subprocess.check_output(
            ["/usr/sbin/networksetup", "-listallhardwareports"]
        ).decode("utf-8")
        current_port = None
        device_name = None

        for line in networksetup_output.splitlines():
            if "Hardware Port" in line:
                current_port = line.split(":")[1].strip()
            elif "Device" in line and active_interface in line:
                device_name = line.split(":")[1].strip()
                return current_port, device_name

        return "Unknown Network"
    except Exception as e:
        return f"Error: {str(e)}"

def get_mac_address(device_name):
    try:
        if not device_name:
            return None
            
        # 使用 ifconfig 命令获取指定接口的 MAC 地址
        ifconfig_output = subprocess.check_output(
            ["/sbin/ifconfig", device_name]
        ).decode("utf-8")
        
        for line in ifconfig_output.splitlines():
            if "ether" in line:
                return line.split()[1].strip()
        return None
    except Exception as e:
        print(f"Error getting MAC address: {str(e)}")
        return None

def get_active_network_info():
    network_name, device_name = get_active_network_service()
    mac_address = get_mac_address(device_name) if device_name else None
    
    return {
        "network_name": network_name,
        "device_name": device_name,
        "mac_address": mac_address
    }

def main():
    # 1. 定义需要的包：(pip安装名称, import名称)
    # required_packages = [
    #     ('requests', 'requests'),              # 名称相同的包
    #     ('beautifulsoup4', 'bs4'),            # 名称不同的包
    #     ('python-dateutil', 'dateutil'),       # 名称不同的包
    # ]
    required_packages = [('requests', 'requests')]
    # 2. 确保包已安装
    ensure_packages(required_packages)
    
    # 3. 导入所需的包
    import requests # type: ignore

    print("Starting network monitoring...")

    while True:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        public_ip = get_public_ip()
        is_connected, latency = ping_google()
        # network_name = get_network_name()
        info = get_active_network_info()
        network_name = info['network_name']
        MAC_Address = info['mac_address']
        device_name = info['device_name']
        status = "Connected" if is_connected else "Disconnected"
        log_entry = f"{current_time} | Network: {network_name} | Device Name: {device_name} | MAC Address: {MAC_Address} | IP: {public_ip} | Status: {status}"
        if is_connected:
            log_entry += f" | Latency: {latency}ms"
        
        # Write to log file
        with open('network_monitor_v2.log', 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')
        
        print(log_entry)  # Also print to console
        time.sleep(30)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
