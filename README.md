# A little bit of history

A while ago I found an old unused laptop and started playing around on using it as a homelab and as a device connected to my TV to stream games from my main desktop (using [Sunshine](https://github.com/LizardByte/Sunshine)/[Moonlight](https://github.com/moonlight-stream)).
As I started to deploy some containers on this new homelab, I started to face an issue: limited server resources.

# Docker Swarm Cluster Deployment with Tailscale

This repository provides scripts and configuration files to facilitate the deployment of a customized Docker Swarm cluster in a Mesh VPN environment using Tailscale. The primary goal is to streamline the setup and management of Docker services across multiple nodes, ensuring secure and efficient communication through the Mesh VPN.

## 🌟 Features

- Automated Docker Swarm cluster deployment
- Python-based management scripts
- Environment-based configuration
- Network segmentation for enhanced security

## Overview

The setup includes one manager node (`homeserver`) and multiple worker nodes (`desk-wsl` and `desk-main`) connected via Tailscale. The manager node remains active at all times, while workers can be started or stopped as needed.

## 📋 Prerequisites

1. **System Requirements**
   - Linux-based operating system
   - Python 3.x (with [Poetry](https://github.com/python-poetry/install.python-poetry.org))
   - [Docker](https://github.com/docker/docker-install)
   - [Tailscale](https://tailscale.com/) VPN (optional)

2. **Storage Requirements**
   - A mounted volume to share persistent data between containers

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/phbregnomo/tailswarm.git
   cd tailswarm
   ```

2. Ensure the `.env` file in the `stacks` directory is configured with the necessary variables for each service.

3. Make sure to modify/add the service configurations in the `stacks` directory to meet your needs.

## Directory Structure

```
bash
.
├── LICENSE
├── README.md
├── scripts           # Contains Python scripts for deployment and management
└── stacks            # Contains Docker Compose stack configurations
```

## Scripts

All scripts are written in Python and are designed to facilitate the deployment and management of Docker Swarm services.

Scripts are located in the `scripts` directory and are must be executed from the current working directory.

Python poetry is used to manage the scripts packages. [How to install.](https://github.com/python-poetry/install.python-poetry.org)

The description of each script can be seen [here](./scripts/scripts.md).

### How to execute the scripts

1. Install the `poetry` environment
```bash
poetry install
```

2. Execute the script
```bash
poetry run python ./scripts/<script name>.py
```

## Usage

- Setup the docker-compose files of each stack
- run `docker-compose up` on the stack directory individually
- Or run de `deploy-all.py` script to deploy the full stack

To deploy a stack, use the following command in the directory containing your Docker Compose files:
```bash
docker-compose up -d
```

For more detailed usage instructions for each script, refer to the comments within the respective script files.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
