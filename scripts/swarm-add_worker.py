#!/usr/bin/env python3

import os
import subprocess

from .utils.loadenv import load_env


def add_worker(manager_ip: str, token: str, new_worker_ip: str) -> None:
    """
    Join a new worker to the Docker Swarm.

    :param manager_ip: The IP address of the manager node
    :param token: The token for adding a worker node
    :param new_worker_ip: The IP address of the new worker node
    """
    if not manager_ip:
        raise ValueError("Manager IP is required")
    if not token:
        raise ValueError("Token is required")
    if not new_worker_ip:
        raise ValueError("New worker IP is required")

    print(f"Attempting to add worker {new_worker_ip} to the swarm...")
    command = ["docker", "swarm", "join", f"--token={token}", f"{manager_ip}:2377"]
    print(f"Running command: {' '.join(command)}")
    try:
        subprocess.run(command, check=True)
        print(f"Worker {new_worker_ip} successfully added to the swarm!")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to add worker: {e}")


def main() -> None:
    """
    Main function to add a new worker.
    """
    # Load environment variables
    env_file = './stacks/.env'
    if not os.path.exists(env_file):
        raise FileNotFoundError(f"Environment file '{env_file}' does not exist")
    load_env(env_file)

    # Get the required variables
    manager_ip = os.getenv('MANAGER_IP')
    token = os.getenv('TOKEN_WORKER')

    if not manager_ip:
        raise ValueError("MANAGER_IP is not set in the environment")
    if not token:
        raise ValueError("TOKEN_WORKER is not set in the environment")

    print(f"Using manager IP: {manager_ip}")
    print(f"Using token: {token}")

    new_worker_ip = input("Enter the IP address of the new worker: ")
    print(f"Using new worker IP: {new_worker_ip}")

    # Add the new worker
    add_worker(manager_ip, token, new_worker_ip)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        raise ValueError(f"Error: {e}")
