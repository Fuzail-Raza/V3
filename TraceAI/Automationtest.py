import subprocess
import csv
import os

def run_volatility(vol_bin, mem_dump, plugin):
    command = ["python.exe", vol_bin, "-f", mem_dump, plugin]

    try:
        # Run the command and capture output
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        # Print the output (optional)
        print(result.stdout)

        save_output_to_csv(plugin, result.stdout)

    except subprocess.CalledProcessError as e:
        print(f"Error executing Volatility plugin {plugin}: {e}")
        print(f"Command output: {e.output}")

def save_output_to_csv(plugin, output):
    # Define the output directory and ensure it exists
    output_dir = './output'
    os.makedirs(output_dir, exist_ok=True)

    # Process the output into lines
    output_lines = output.strip().splitlines()

    # Extract header and data lines
    if len(output_lines) < 2:
        print(f"No data returned for plugin: {plugin}")
        return

    header = output_lines[0].split()  # Assumes space-separated header
    data = [line.split() for line in output_lines[1:] if line]  # Process each line into a list

    # Define the CSV file path
    csv_file_path = os.path.join(output_dir, f"{plugin.replace('.', '_')}_output.csv")

    # Save data to CSV
    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)  # Write the header
        writer.writerows(data)  # Write the data rows

    print(f"Saved output for {plugin} to {csv_file_path}")

def main():
    vol_bin = "./volatility3-develop/vol.py"
    mem_dump = "./Memory Dumps/Windows 7 Memory Dumps/memdump_win7_2_31.raw"



    plugins = [
        "windows.info.Info",
        "windows.dlllist",
        "windows.pstree",
        "windows.malfind.Malfind",
        "windows.netscan.NetScan",
        "windows.registry.hivelist",
        "windows.pslist.PsList",
        "windows.cmdline",
        "windows.psscan.PsScan",
        "windows.suspicious_threads.SupsiciousThreads"
    ]
    for plugin in plugins:
        print(f"Running plugin: {plugin}")
        run_volatility(vol_bin, mem_dump, plugin)
        print("-" * 50)

if __name__ == "__main__":
    main()
