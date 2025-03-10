import subprocess
import sys
import importlib
import time
from datetime import datetime
import platform
import logging
import requests

# Configure logging to output to both console and file
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("network_monitor_v2.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

def install_package(package_name: str) -> bool:
    """
    Install a Python package using pip.
    
    Parameters:
        package_name (str): The name of the package to be installed.
    
    Returns:
        bool: True if installation succeeded; False otherwise.
    """
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to install {package_name}. Error: {e}")
        return False

def ensure_packages(package_requirements: list[tuple[str, str]]) -> None:
    """
    Ensure that the required packages are installed.
    
    Args:
        package_requirements (list[tuple[str, str]]): List of tuples in the form (pip package name, import module name).
    """
    for pip_name, import_name in package_requirements:
        try:
            importlib.import_module(import_name)
            logging.info(f"{pip_name} is already installed.")
        except ImportError:
            logging.info(f"Installing {pip_name}...")
            if install_package(pip_name):
                logging.info(f"Successfully installed {pip_name}.")
            else:
                logging.error(f"Failed to install {pip_name}. Please install it manually.")
                sys.exit(1)

def get_public_ip() -> str:
    """
    Retrieve the public IP address using the ipify API.
    
    Returns:
        str: The public IP address or an error message if retrieval fails.
    """
    try:
        response = requests.get('https://api.ipify.org', timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Error retrieving public IP: {e}")
        return "Unable to get IP"

def ping_google() -> tuple[bool, float]:
    """
    Ping google.com to verify connectivity and measure latency.
    
    Returns:
        tuple: A tuple containing a boolean for connectivity and a float for latency (in ms).
    """
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', 'google.com']
    
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT).decode('utf-8')
        if platform.system().lower() == 'windows':
            if 'TTL=' in output:
                try:
                    # Extract numeric latency value from output (e.g., 时间=xxms)
                    time_part = [s for s in output.split() if '时间=' in s or 'time=' in s]
                    if time_part:
                        latency = float(''.join(filter(lambda ch: ch.isdigit() or ch == '.', time_part[0])))
                        return True, latency
                except Exception as e:
                    logging.error(f"Error parsing ping latency: {e}")
        else:
            if 'time=' in output:
                try:
                    time_str = output.split('time=')[-1].split(' ')[0].strip()
                    return True, float(time_str)
                except Exception as e:
                    logging.error(f"Error parsing ping latency: {e}")
        return True, 0.0
    except subprocess.CalledProcessError as e:
        logging.error(f"Ping failed: {e}")
        return False, 0.0

def get_active_network_service() -> dict:
    """
    Retrieve the active network service information.
    
    Returns:
        dict: A dictionary containing 'network_name' and 'device_name'. In case of error, an 'error' key is added.
    """
    try:
        # Obtain the default route's interface (command may vary with the platform)
        route_output = subprocess.check_output(
            ["route", "-n", "get", "default"], stderr=subprocess.STDOUT
        ).decode("utf-8")
        active_interface = None
        for line in route_output.splitlines():
            if "interface:" in line:
                active_interface = line.split(":")[1].strip()
                break

        if not active_interface:
            return {"network_name": "No Active Network", "device_name": None}

        # Retrieve the hardware port information using networksetup
        networksetup_output = subprocess.check_output(
            ["/usr/sbin/networksetup", "-listallhardwareports"], stderr=subprocess.STDOUT
        ).decode("utf-8")
        current_port = None
        device_name = None

        for line in networksetup_output.splitlines():
            if "Hardware Port" in line:
                current_port = line.split(":")[1].strip()
            elif "Device" in line and active_interface in line:
                device_name = line.split(":")[1].strip()
                return {"network_name": current_port, "device_name": device_name}

        return {"network_name": "Unknown Network", "device_name": None}
    except subprocess.CalledProcessError as e:
        logging.error(f"Error retrieving network service: {e}")
        return {"network_name": "Error", "device_name": None, "error": str(e)}
    except Exception as e:
        logging.error(f"Unexpected error retrieving network service: {e}")
        return {"network_name": "Error", "device_name": None, "error": str(e)}

def get_mac_address(device_name: str) -> str:
    """
    Retrieve the MAC address for the specified network device.
    
    Args:
        device_name (str): The name of the network device.
    
    Returns:
        str: The MAC address if found; otherwise, None.
    """
    try:
        if not device_name:
            return None
        # Use ifconfig to obtain the MAC address
        ifconfig_output = subprocess.check_output(
            ["/sbin/ifconfig", device_name], stderr=subprocess.STDOUT
        ).decode("utf-8")
        
        for line in ifconfig_output.splitlines():
            if "ether" in line:
                return line.split()[1].strip()
        return None
    except subprocess.CalledProcessError as e:
        logging.error(f"Error getting MAC address for {device_name}: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error getting MAC address for {device_name}: {e}")
        return None

def get_active_network_info() -> dict:
    """
    Retrieve active network information including network name, device name, and MAC address.
    
    Returns:
        dict: A dictionary containing the network information.
    """
    network_info = get_active_network_service()
    mac_address = get_mac_address(network_info.get('device_name')) if network_info.get('device_name') else None
    
    return {
        "network_name": network_info.get("network_name"),
        "device_name": network_info.get("device_name"),
        "mac_address": mac_address
    }

def main() -> None:
    """
    Main function that executes network monitoring.
    """
    # Define required packages: (pip package name, import module name)
    required_packages = [('requests', 'requests')]
    # Ensure that the required packages are installed
    ensure_packages(required_packages)
    
    logging.info("Starting network monitoring...")
    
    try:
        while True:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            public_ip = get_public_ip()
            is_connected, latency = ping_google()
            network_info = get_active_network_info()
            network_name = network_info.get("network_name")
            device_name = network_info.get("device_name")
            mac_address = network_info.get("mac_address")
            status = "Connected" if is_connected else "Disconnected"
            
            log_entry = (
                f"{current_time} | Network: {network_name} | Device Name: {device_name} | "
                f"MAC Address: {mac_address} | IP: {public_ip} | Status: {status}"
            )
            if is_connected:
                log_entry += f" | Latency: {latency}ms"
            
            logging.info(log_entry)
            time.sleep(30)
    except KeyboardInterrupt:
        logging.info("Monitoring stopped by user.")

if __name__ == "__main__":
    main()