from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import subprocess
import csv
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)

@csrf_exempt
def home(request):
    return render(request, 'index.html')


# Handle the memory dump upload and processing
def upload_memory_dump(request):
    if request.method == 'POST':
        try:
            memory_dump = request.FILES['memory_dump']
        except KeyError:
            logger.error('No memory dump was uploaded.')
            return JsonResponse({'error': 'No memory dump was uploaded.'}, status=400)

        # Save the uploaded file
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'uploads'))
        filename = fs.save(memory_dump.name, memory_dump)
        memory_dump_path = os.path.join(settings.MEDIA_ROOT, 'uploads', filename)

        # Log the uploaded file path
        logger.info(f'Uploaded file path: {memory_dump_path}')

        # Check if the file exists
        if not os.path.isfile(memory_dump_path):
            logger.error(f'Memory dump file not found after upload: {memory_dump_path}')
            return JsonResponse({'error': f'Memory dump file not found after upload: {memory_dump_path}'}, status=404)

        # Run Volatility
        try:
            run_volatility(memory_dump_path)
        except Exception as e:
            logger.error(f'Volatility failed: {str(e)}')
            return JsonResponse({'error': f'Volatility failed: {str(e)}'}, status=500)

        return JsonResponse({'results': 'Processing completed successfully'}, status=200)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


def run_volatility(mem_dump_path):
    vol_bin = os.path.abspath("./TraceAI/volatility3-develop/vol.py")

    print(f"Volatility path: {vol_bin}")
    print(f"Memory dump path: {os.path.abspath(mem_dump_path)}")  # Use absolute path for memory dump
    memory_dump_name = os.path.splitext(os.path.basename(mem_dump_path))[0]
    # Ensure the memory dump file exists
    if not os.path.isfile(mem_dump_path):
        logger.error(f'Memory dump file not found: {mem_dump_path}')
        raise FileNotFoundError(f'Memory dump file not found: {mem_dump_path}')

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
        command = ["python", vol_bin, "-f", os.path.abspath(mem_dump_path), plugin]  # Use absolute path for memory dump
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            save_output_to_csv(plugin, result.stdout, memory_dump_name)
        except subprocess.CalledProcessError as e:
            logger.error(f'Error running {plugin}: {e.stderr}')  # Log stderr
            logger.error(f'Command: {" ".join(command)}')  # Log the command that was run
            raise e  # Reraise to handle in the view

def save_output_to_csv(plugin, output, memory_dump_name):
    # Create a directory for the output named after the memory dump file
    output_dir = os.path.join(settings.MEDIA_ROOT, 'output', memory_dump_name)
    os.makedirs(output_dir, exist_ok=True)

    output_lines = output.strip().splitlines()
    if len(output_lines) < 2:
        print(f"No data returned for plugin: {plugin}")
        return

    # Extract the header and data
    header = output_lines[0].split()  # Assumes space-separated header
    data = [line.split() for line in output_lines[1:] if line]

    # Create the CSV file for each plugin
    csv_file_path = os.path.join(output_dir, f"{plugin.replace('.', '_')}_output.csv")

    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        writer.writerows(data)

    print(f"Saved output for {plugin} to {csv_file_path}")
