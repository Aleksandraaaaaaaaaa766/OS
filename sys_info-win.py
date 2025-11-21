import psutil
import platform
import os
import ctypes

#1. Версия ОС 
class OSVERSIONINFOEXW(ctypes.Structure):
    _fields_ = [
        ('dwOSVersionInfoSize', ctypes.c_ulong),
        ('dwMajorVersion', ctypes.c_ulong),
        ('dwMinorVersion', ctypes.c_ulong),
        ('dwBuildNumber', ctypes.c_ulong),
        ('dwPlatformId', ctypes.c_ulong),
        ('szCSDVersion', ctypes.c_wchar * 128),
        ('wServicePackMajor', ctypes.c_ushort),
        ('wServicePackMinor', ctypes.c_ushort),
        ('wSuiteMask', ctypes.c_ushort),
        ('wProductType', ctypes.c_byte),
        ('wReserved', ctypes.c_byte),
    ]

def get_windows_version():
    RtlGetVersion = ctypes.windll.ntdll.RtlGetVersion
    info = OSVERSIONINFOEXW()
    info.dwOSVersionInfoSize = ctypes.sizeof(info)
    RtlGetVersion(ctypes.byref(info))
    return f"Windows {info.dwMajorVersion}.{info.dwMinorVersion}"

#2. Информация о памяти
class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ('dwLength', ctypes.c_ulong),
        ('dwMemoryLoad', ctypes.c_ulong),
        ('ullTotalPhys', ctypes.c_ulonglong),
        ('ullAvailPhys', ctypes.c_ulonglong),
        ('ullTotalPageFile', ctypes.c_ulonglong),
        ('ullAvailPageFile', ctypes.c_ulonglong),
        ('ullTotalVirtual', ctypes.c_ulonglong),
        ('ullAvailVirtual', ctypes.c_ulonglong),
        ('ullAvailExtendedVirtual', ctypes.c_ulonglong),
    ]


def get_memory_info():
    memory_status = MEMORYSTATUSEX()
    memory_status.dwLength = ctypes.sizeof(memory_status)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory_status))
    return memory_status

#4. Имя компьютера и пользователя 
def get_system_names():
    computer = os.getenv("COMPUTERNAME")
    user = os.getenv("USERNAME")
    return computer, user

#5. Архитектура 
def get_architecture():
    arch = platform.machine().lower()
    if "amd64" in arch or "x86_64" in arch:
        return "x64 (AMD64)"
    elif "x86" in arch:
        return "x86"
    elif "arm" in arch:
        return "ARM"
    return arch

#6. Размер файла подкачки
class PERFORMANCE_INFORMATION(ctypes.Structure):
    _fields_ = [
        ('cb', ctypes.c_ulong),
        ('CommitTotal', ctypes.c_size_t),
        ('CommitLimit', ctypes.c_size_t),
        ('CommitPeak', ctypes.c_size_t),
        ('PhysicalTotal', ctypes.c_size_t),
        ('PhysicalAvailable', ctypes.c_size_t),
        ('SystemCache', ctypes.c_size_t),
        ('KernelTotal', ctypes.c_size_t),
        ('KernelPaged', ctypes.c_size_t),
        ('KernelNonpaged', ctypes.c_size_t),
        ('PageSize', ctypes.c_size_t),
        ('HandleCount', ctypes.c_ulong),
        ('ProcessCount', ctypes.c_ulong),
        ('ThreadCount', ctypes.c_ulong),
    ]

def get_pagefile_info():
    perf_info = PERFORMANCE_INFORMATION()
    perf_info.cb = ctypes.sizeof(perf_info)
    if ctypes.windll.psapi.GetPerformanceInfo(ctypes.byref(perf_info), perf_info.cb):
        total = perf_info.CommitLimit * perf_info.PageSize / (1024 ** 2)
        used = perf_info.CommitTotal * perf_info.PageSize / (1024 ** 2)
        return used, total
    else:
        return None, None

#7. Диски 
def get_drives_info():
    drives = psutil.disk_partitions()
    info = []
    for d in drives:
        try:
            usage = psutil.disk_usage(d.device)
            info.append({
                "device": d.device,
                "fstype": d.fstype,
                "free": usage.free // (1024**3),
                "total": usage.total // (1024**3)
            })
        except PermissionError:
            continue
    return info

if __name__ == "__main__":
    print(f"OS: {get_windows_version()}")

    comp, user = get_system_names()
    print(f"Computer Name: {comp}")
    print(f"User: {user}")
    print(f"Architecture: {get_architecture()}")

    mem = get_memory_info()
    print(f"RAM: {mem.ullAvailPhys // (1024**2)}MB / {mem.ullTotalPhys // (1024**2)}MB")
    print(f"Virtual Memory: {mem.ullTotalVirtual // (1024**2)}MB")
    print(f"Memory Load: {mem.dwMemoryLoad}%")

    used_pf, total_pf = get_pagefile_info()
    if used_pf:
        print(f"Pagefile: {int(used_pf)}MB / {int(total_pf)}MB")

    print(f"Processors: {os.cpu_count()}")

    print("Drives:")
    for d in get_drives_info():
        print(f"  - {d['device']} ({d['fstype']}): {d['free']} GB free / {d['total']} GB total")
