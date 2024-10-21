#!/usr/bin/env -S poetry run python


"""
The script deploys Docker networks based on the configuration in the config.toml file by creating
new networks and displaying the deployment results in a table format.
:return: The script returns the results of deploying Docker networks based on the configuration
specified in the `config.toml` file. It displays the status of each network deployment (whether it
was created successfully or already existed) along with details such as the network name, driver,
and attachable status in a table format. Finally, it prints a message indicating that the network
deployment has been completed.
"""


import tomli
import subprocess
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from typing import List, Dict

console = Console()

def load_config() -> Dict:
    """
    Load configuration from config.toml file.

    The configuration is stored in a TOML file named config.toml. If the file does not exist,
    the function prints an error message and exits with a non-zero status code. If the file
    exists but contains invalid TOML, the function prints an error message and exits with a
    non-zero status code.

    Returns: Dictionary containing the configuration
    """
    try:
        return tomli.load(open("config.toml", "rb"))
    except FileNotFoundError:
        print("[red]Error: config.toml file not found[/red]", file=sys.stderr)
        sys.exit(1)
    except tomli.TOMLDecodeError as error:
        print(f"[red]Error parsing config.toml: {error}[/red]", file=sys.stderr)
        sys.exit(1)
    

def get_existing_networks() -> List[str]:
    """
    Retrieve a list of existing Docker networks.

    Executes the command `docker network ls --format "{{.Name}}"` to capture the output.
    If the command fails, an error message is displayed and an empty list is returned.

    Returns:
        List[str]: A list of network names.
    """
    try:
        # Run the Docker command to get the list of existing networks
        return subprocess.check_output(
            ["docker", "network", "ls", "--format", "{{.Name}}"],
            text=True,
        ).strip().splitlines()
    except subprocess.CalledProcessError as error:
        # If the command fails, print an error message and return an empty list
        console.print(f"[red]Error retrieving existing networks: {error}[/red]")
        return []

def create_docker_network(
    network_name: str,
    driver: str,
    attachable: bool,
    ) -> bool:
    """
    Creates a Docker network with specified parameters.

    Args:
        network_name: Name of the network to create
        driver: Network driver (default: bridge)
        attachable: Whether the network is attachable (default: False)

    Returns:
        Boolean indicating success
    """
    # Construct the command to create the network
    command = ["docker", "network", "create", "--scope", "swarm", network_name]

    # Add the driver argument if specified
    if driver:
        command.extend(["--driver", driver])

    # Add the attachable argument if specified
    if attachable:
        command.append("--attachable")

    try:
        # Run the command to create the network
        subprocess.run(command, check=True, capture_output=True)
        # Return True if the command executes successfully
        return True
    except subprocess.CalledProcessError as error:
        # Print an error message if the command fails
        console.print(
            f"[red]Error creating network {network_name}: {error.stderr.decode()}[/red]"
        )
        # Return False if the command fails
        return False

def remove_docker_network(
    network_name: str) -> bool:
    
    command = ["docker", "network", "rm", network_name]
    
    console.print(
        f"[yellow]Deleting existing network {network_name}[/yellow]"
    )
    
    try:
        subprocess.run(command,
            check=True,
            capture_output=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        console.print(
            f"[red]Error deleting network {name}: {e.stderr.decode()}[/red]"
        )
        return False
    

def main() -> None:
    """
    The main function of the script. It loads the configuration from the config.toml file,
    gets the list of existing networks, creates a table to store the deployment results,
    processes each network in the configuration, and displays the deployment results in
    a table format.
    """
    # Create a header panel
    console.print(Panel.fit(
        "[bold blue]Docker Swarm Network Deployment[/bold blue]",
        border_style="blue"
    ))
    # Load configuration
    config = load_config()
    
    if "networks" not in config:
        console.print("[red]No networks defined in config.toml[/red]", err=True, style="bold red")
        sys.exit(1)

    # Get existing networks
    existing_networks = get_existing_networks()

    # Create table for results
    table = Table(
        title="Network Deployment Results",
        show_header=True,
        header_style="bold magenta",
        title_justify="left",
        title_style="bold blue",
    )
    table.add_column("Network Name", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Driver", style="yellow")
    table.add_column("Attachable", style="blue")

    # Process each network
    for network in config["networks"]:
        name = network.get("name")
        driver = network.get("driver", "overlay")
        attachable = network.get("attachable", True)
        
        # Delete existing networks defined on the config file
        if name in existing_networks:
            console.print(
                f"[yellow]Deleting existing network {name}[/yellow]"
            )
            try:
                subprocess.run(
                    ["docker", "network", "rm", name],
                    check=True,
                    capture_output=True,
                )
            except subprocess.CalledProcessError as e:
                console.print(
                    f"[red]Error deleting network {name}: {e.stderr.decode()}[/red]"
                )

        # Create the network
        success = create_docker_network(name, driver, attachable)
        status = "Created" if success else "Failed"

        table.add_row(
            name,
            status,
            driver,
            "Yes" if attachable else "No",
        )

    # Display results
    console.print(table)
    console.print("\n[bold green]Network deployment completed![/bold green]")

if __name__ == "__main__":
    main()