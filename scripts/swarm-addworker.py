#!/usr/bin/env -S poetry run python

"""
Script to add a worker node to a Docker Swarm cluster.
Reads configuration from config.toml file and executes the necessary Docker commands.
"""

import subprocess
import tomli
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from pathlib import Path

# Initialize Rich console for better output
console = Console()

def load_config() -> dict:
    """
    Load configuration from the 'config.toml' file in the current directory.
    
    Returns:
        dict: Configuration dictionary containing swarm settings
    """
    try:
        # Define the path to the config file
        config_file_path = Path("config.toml")
        
        # Check if the config file exists
        if not config_file_path.exists():
            raise FileNotFoundError(f"'config.toml' file not found in {config_file_path.parent}")
        
        # Load the config file
        with open(config_file_path, "rb") as file:
            # Parse the TOML file
            config_data = tomli.load(file)
            
            # Get the swarm config from the file
            # The swarm config is in the 'swarm-config' table
            swarm_config = config_data.get("swarm-config", {})
            
            # Return the swarm config
            return swarm_config
    
    except Exception as error:
        console.print(f"[red]Error loading 'config.toml': {str(error)}[/red]")
        raise

def add_worker(manager_ip: str, token: str) -> None:
    """
    Join the current node to the Docker Swarm as a worker.

    Args:
        manager_ip (str): The IP address of the manager node
        token (str): The worker token for joining the swarm

    Raises:
        ValueError: If manager_ip or token is empty
        RuntimeError: If failed to join the swarm
    """
    if not manager_ip or not token:
        raise ValueError("Manager IP and token are required")

    # Create styled header for the operation
    header = Text("🔄 Adding Worker to Docker Swarm", style="bold blue")
    console.print(Panel(header, border_style="blue"))

    # Display connection information
    console.print(f"\n[yellow]Manager IP:[/yellow] {manager_ip}")
    console.print(f"[yellow]Token:[/yellow] {token[:10]}...{token[-10:]}\n")

    # Construct and execute the join command
    command = ["docker", "swarm", "join", f"--token={token}", f"{manager_ip}:2377"]
    
    with console.status("[bold green]Joining swarm...") as status:
        try:
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True
            )
            console.print("[green]✓ Successfully joined the swarm![/green]")
            console.print(result.stdout)
        except subprocess.CalledProcessError as e:
            console.print(f"[red]✗ Failed to join swarm:[/red] {e.stderr}")
            raise RuntimeError(f"Failed to add worker: {e.stderr}")

def main() -> None:
    """
    Main function to execute the worker addition process.
    
    Loads configuration from `config.toml` and initiates the join operation.
    """
    try:
        # Load configuration from config.toml
        config = load_config()
        
        # Extract required values
        manager_ip = config.get("manager_ip")
        worker_token = config.get("worker")
        
        # Check if manager_ip and worker_token are set
        if not manager_ip or not worker_token:
            raise ValueError("Manager IP and worker token must be set in config.toml")
        
        # Add worker to swarm
        add_worker(manager_ip, worker_token)
        
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {str(e)}")
        raise SystemExit(1)

if __name__ == "__main__":
    main()