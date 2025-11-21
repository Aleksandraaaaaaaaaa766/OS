import os
import platform
import subprocess
import getpass
import socket
import pwd

# Получение версии дистрибутива: lsb_release или /etc/os-release
def get_distro():
    try:
        # Если есть lsb_release
        return subprocess.check_output(["lsb_release", "-ds"], text=True).strip().strip('"')
    except Exception:
        # Fallback через /etc/os-release
        if os.path.exists("/etc/os-release"):
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        return line.split("=", 1)[1].strip().strip('"')
        return "Unknown Linux"


# Чтение /proc/meminfo (RAM, swap, virtual memory)
def get_memory_info():
    meminfo = {}
    with open("/proc/meminfo") as f:
        for line in f:
            key, value = line.split(":", 1)
            meminfo[key] = value.strip()

    to_mb = lambda kb: int(kb.split()[0]) // 1024

    total = to_mb(meminfo.get("MemTotal", "0 kB"))
    free = to_mb(meminfo.get("MemAvailable", "0 kB"))
    swap_total = to_mb(meminfo.get("SwapTotal", "0 kB"))
    swap_free = to_mb(meminfo.get("SwapFree", "0 kB"))
    vm_total = meminfo.get("VmallocTotal", "0 kB")

    return total, free, swap_total, swap_free, vm_total


# Загрузка CPU
def get_loadavg():
    with open("/proc/loadavg") as f:
        parts = f.read().split()
        return parts[0], parts[1], parts[2]


# Список дисков: чтение /proc/mounts + statvfs()
def get_drives():
    drives = []
    with open("/proc/mounts") as f:
        for line in f:
            dev, mount, fstype, *_ = line.split()

            # Только реальные пути
            if not mount.startswith("/"):
                continue

            try:
                stat = os.statvfs(mount)
                free = stat.f_bavail * stat.f_frsize
                total = stat.f_blocks * stat.f_frsize
                drives.append((mount, fstype, free, total))
            except:
                pass

    return drives


# Информация о пользователе и хосте
def get_user_host():
    user = getpass.getuser()
    hostname = socket.gethostname()
    return user, hostname


# MAIN
def main():
    print(f"OS: {get_distro()}")

    uname = os.uname()  # Системный вызов uname()
    print(f"Kernel: {uname.sysname} {uname.release}")
    print(f"Architecture: {uname.machine}")

    user, hostname = get_user_host()
    print(f"Hostname: {hostname}")
    print(f"User: {user}")

    total, free, swap_total, swap_free, vm_total = get_memory_info()
    print(f"RAM: {free}MB free / {total}MB total")
    print(f"Swap: {swap_free}MB free / {swap_total}MB total")
    print(f"Virtual memory: {vm_total}")

    print(f"Processors: {os.cpu_count()}")

    la1, la5, la15 = get_loadavg()
    print(f"Load average: {la1}, {la5}, {la15}")

    print("Drives:")
    for mount, fstype, free, total in get_drives():
        free_gb = free / (1024**3)
        total_gb = total / (1024**3)
        print(f"  {mount:<15} {fstype:<8} {free_gb:.1f}GB free / {total_gb:.1f}GB total")


if __name__ == "__main__":
    main()
