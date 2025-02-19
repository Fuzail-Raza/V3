import subprocess
import csv

def run_volatility(vol_bin, mem_dump, plugin):

    command = [ "python.exe", vol_bin, "-f", mem_dump, plugin]

    try:

        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error executing Volatility plugin {plugin}: {e}")
        print(f"Command output: {e.output}")


def main():

    vol_bin = "./volatility3-develop/vol.py"

    mem_dump = "./Memory Dumps/Windows 7 Memory Dumps/memdump_win7_0.raw"

    plugins = ["windows.info.Info","windows.dlllist","windows.pstree","windows.malfind.Malfind", "windows.netscan.NetScan","windows.registry.hivelist","windows.pslist.PsList","windows.cmdline","windows.psscan.PsScan","windows.suspicious_threads.SupsiciousThreads"]


    for plugin in plugins:
        print(f"Running plugin: {plugin}")
        run_volatility(vol_bin, mem_dump, plugin)
        print("-" * 50)





if __name__ == "__main__":
    main()
