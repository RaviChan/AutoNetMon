# AutoNetMon

[English](#english) | [中文](#chinese)

<a name="english"></a>
## Network Monitor with Auto-dependency Management

AutoNetMon (Automatic Network Monitor) is a robust network monitoring tool that features an innovative automatic package dependency management architecture. It continuously monitors your network status, including public IP, connection quality, and network interface details, while handling its own dependency installation automatically.

### Key Features

- **Automatic Dependency Management**
  - Self-installing required packages
  - Handles pip/import name differences
  - Zero manual package installation needed

- **Comprehensive Network Monitoring**
  - Public IP tracking
  - Network latency measurement
  - Active network interface detection
  - MAC address identification
  - Connection status monitoring

- **Cross-platform Support**
  - Windows compatibility
  - macOS compatibility
  - Adaptive ping command handling

- **Detailed Logging**
  - Timestamp-based logging
  - Console output
  - File-based logging
  - Comprehensive network metrics

### Architecture Highlights

The project introduces a novel approach to Python package management with:
```python
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
            # Auto installation logic
```

### Installation

1. Clone the repository:
```bash
git clone https://github.com/RaviChan/AutoNetMon.git
```

2. Run the script:
```bash
python network_monitor.py
```

The script will automatically handle all dependency installations!

### Requirements
- Python 3.6+
- Internet connection for dependency installation
- Appropriate system permissions for network monitoring

### Output Example
```
2024-12-15 10:30:00 | Network: Wi-Fi | Device Name: en0 | MAC Address: xx:xx:xx:xx:xx | IP: 203.0.113.1 | Status: Connected | Latency: 25ms
```

---

<a name="chinese"></a>
## 具有自动依赖管理的网络监控工具

AutoNetMon (Automatic Network Monitor) 是一个功能强大的网络监控工具，其特色在于创新的自动包依赖管理架构。它能够持续监控您的网络状态，包括公网IP、连接质量和网络接口详情，同时自动处理其所需的依赖包安装。

### 主要特性

- **自动依赖管理**
  - 自动安装所需包
  - 处理pip安装名称与导入名称的差异
  - 无需手动安装任何依赖

- **全面的网络监控**
  - 公网IP追踪
  - 网络延迟测量
  - 活动网络接口检测
  - MAC地址识别
  - 连接状态监控

- **跨平台支持**
  - 支持Windows系统
  - 支持macOS系统
  - 自适应ping命令处理

- **详细的日志记录**
  - 基于时间戳的日志
  - 控制台输出
  - 文件日志记录
  - 完整的网络指标

### 架构亮点

本项目提出了一种创新的Python包管理方式：
```python
def ensure_packages(package_requirements):
    """
    检查并安装所需的包（如果尚未安装）
    参数：
        package_requirements: 包含元组(pip安装名称, 导入名称)的列表
    """
    for pip_name, import_name in package_requirements:
        try:
            importlib.import_module(import_name)
            print(f"{pip_name} 已经安装。")
        except ImportError:
            print(f"正在安装 {pip_name}...")
            # 自动安装逻辑
```

### 安装方法

1. 克隆仓库：
```bash
git clone https://github.com/RaviChan/AutoNetMon.git
```

2. 运行脚本：
```bash
python network_monitor.py
```

脚本将自动处理所有依赖安装！

### 系统要求
- Python 3.6+
- 用于安装依赖的网络连接
- 适当的系统权限用于网络监控

### 输出示例
```
2024-12-15 10:30:00 | 网络: Wi-Fi | 设备名称: en0 | MAC地址: xx:xx:xx:xx:xx | IP: 203.0.113.1 | 状态: 已连接 | 延迟: 25ms
```
