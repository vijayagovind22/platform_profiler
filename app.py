import json

from flask import Flask, jsonify, request
import requests
import subprocess
import paramiko

app = Flask(__name__)

BMC_IP = '127.0.0.1'  # Replace with your BMC IP
OS_IP = '127.0.0.1'  # Replace with your OS IP

# Function to interact with BMC via Redfish API
def get_bmc_data(endpoint):
    url = f"https://{BMC_IP}/redfish/v1/{endpoint}"
    response = requests.get(url, verify=False)  # In production, handle SSL certs properly
    return response.json() if response.status_code == 200 else {}

# Function to run a command on the OS using subprocess
def run_os_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout, result.stderr
    except Exception as e:
        return str(e), None

# Function to run a command on a remote OS using paramiko
def run_remote_command(command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(OS_IP, username='vijayalaxmi', password='Maha0617@')  # Replace with your credentials
    stdin, stdout, stderr = client.exec_command(command)
    return stdout.read().decode(), stderr.read().decode()

# API endpoint to get BMC data
@app.route('/bmc/<endpoint>', methods=['GET'])
def bmc_endpoint(endpoint):
    data = get_bmc_data(endpoint)
    return jsonify(data)

# API endpoint to run an OS command
@app.route('/os/command', methods=['POST'])
def os_command():
    command = request.json.get('command')
    output, error = run_os_command(command)
    # Split the raw string into lines
    lines = output.strip().split('\n')

    # Initialize an empty dictionary
    data_dict = {}

    # Parse each line
    for line in lines:
        # Split the line at the first colon
        key_value = line.split(':', 1)  # Split into at most 2 parts
        if len(key_value) == 2:
            key = key_value[0].strip()  # Remove whitespace from the key
            value = key_value[1].strip()  # Remove whitespace from the value
            data_dict[key] = value
    return jsonify({'output': data_dict, 'error': error})

# API endpoint to run a remote OS command
@app.route('/remote/command', methods=['POST'])
def remote_command():
    command = request.json.get('command')
    output, error = run_remote_command(command)
    return jsonify({'output': output, 'error': error})

if __name__ == '__main__':
    app.run(debug=True)
