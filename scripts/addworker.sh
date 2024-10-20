#!/bin/bash

# =================================================================
# Setup Worker Node - Docker Swarm
# =================================================================
# Este script automatiza a configuração de um novo worker node no
# cluster Docker Swarm, incluindo:
# - Instalação do Docker
# - Configuração do NFS
# - Join no Swarm
# - Testes de conectividade
# =================================================================

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
INFO="${BLUE}[INFO]${NC}"
SUCCESS="${GREEN}[SUCCESS]${NC}"
WARNING="${YELLOW}[WARNING]${NC}"
ERROR="${RED}[ERROR]${NC}"

# Função para exibir banner
show_banner() {
    clear
    echo -e "${BLUE}"
    echo "======================================================"
    echo "              Docker Swarm Worker Setup                "
    echo "======================================================"
    echo -e "${NC}"
}

# Função para exibir progresso
show_progress() {
    echo -e "${INFO} $1"
}

# Função para verificar status de serviços
check_service() {
    local service_name="$1"
    if ! systemctl is-active --quiet "$service_name"; then
        echo -e "[WARNING] $service_name não está ativo. Tentando iniciar..."
        systemctl start "$service_name"
        sleep 2 # Espera um pouco para o serviço iniciar
        if ! systemctl is-active --quiet "$service_name"; then
            echo -e "[ERROR] Falha ao iniciar $service_name. Verifique os logs do sistema."
            exit 1
        else
            echo -e "[SUCCESS] $service_name iniciado e habilitado para inicialização."
        fi
    else
        echo -e "[SUCCESS] $service_name está ativo."
    fi
}
        

# Função para verificar se comando foi executado com sucesso
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${SUCCESS} $1"
    else
        echo -e "${ERROR} $2"
        exit 1
    fi
}

# Função para verificar requisitos
check_requirements() {
    show_progress "Verificando requisitos..."
    
    # Verifica se está rodando como root
    if [ "$EUID" -ne 0 ]; then 
        echo -e "[ERROR] Este script precisa ser executado como root (sudo)"
        exit 1
    fi

    if ! command -v tailscale &> /dev/null; then
        echo -e "[ERROR] Tailscale não está instalado. Instalando..."

        curl -fsSL https://tailscale.com/install.sh | sh

        check_status "Tailscale instalado e conectado com sucesso" "Falha na instalação do Tailscale"
    fi

        # Verifica se o serviço tailscaled está ativo
        check_service "tailscaled"

        # Verifica se Tailscale está rodando
        if ! tailscale status &> /dev/null; then
            echo -e "[ERROR] Tailscale não está conectado. Fazendo login..."
            tailscale up
            if ! tailscale status &> /dev/null; then
                echo -e "[ERROR] Falha ao conectar ao Tailscale."
            else
                echo -e "[INFO] Tailscale conectado com sucesso."
            fi
        else
            echo -e "[INFO] Tailscale já está rodando."
        fi

    # Verifica se o Tailscale está instalado e rodando
    if ! command -v tailscale &> /dev/null; then
        show_progress "Tailscale não encontrado. Instalando..."
        install_tailscale
    else
        show_progress "Tailscale já está instalado. Verificando status..."
        if ! tailscale status &> /dev/null; then
            echo -e "[ERROR] Tailscale não está conectado. Faça o login."
            tailscale up
            check_status "Tailscale conectado" "Falha ao conectar ao Tailscale"
        fi
    fi

    # Verificando hostname
    HOSTNAME=$(hostname)
    show_progress "Hostname do novo worker: ${HOSTNAME}"
    
    check_status "Todos os requisitos atendidos" "Falha na verificação de requisitos"
}

# Função para instalar Tailscale

# Função para instalar Docker
install_docker() {
    show_progress "Instalando Docker..."
    
    # Removendo versões antigas
    apt-get remove docker docker-engine docker.io containerd runc &> /dev/null
    
    # Instalando dependências
    apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # Adicionando chave GPG oficial do Docker
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    # Configurando repositório
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Instalando Docker
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    check_status "Docker instalado com sucesso" "Falha na instalação do Docker"
}

# Função para configurar NFS
setup_nfs() {
    show_progress "Configurando o cliente NFS..."
    
    # Verifica se o nfs-common está instalado
    if ! dpkg -l | grep -q nfs-common; then
        show_progress "nfs-common não encontrado. Instalando..."
        sudo apt-get install -y nfs-common
        check_status "nfs-common instalado com sucesso" "Falha na instalação do nfs-common"
    else
        show_progress "nfs-common já está instalado."
    fi

    # Criando diretório de montagem se não existir
    sudo mkdir -p /docker_volumes
    
    # Lendo MANAGER_IP do arquivo .env
    if [ -f "./scripts/.env" ]; then
        source "./scripts/.env"
    else
        echo -e "$[ERROR] Arquivo .env não encontrado. Por favor, defina a variável MANAGER_IP manualmente."
        read -p "Digite o IP/nome do host do servidor NFS: " MANAGER_IP
    fi

    # Montando o compartilhamento NFS
    mount -t nfs "${MANAGER_IP}:/docker_volumes" /docker_volumes
    check_status "Compartilhamento NFS montado com sucesso" "Falha ao montar o compartilhamento NFS"
}

    #
    # Retorno:
    #   Nenhum
    # =================================================================
join_swarm() {
    show_progress "Obtendo token do Swarm..."
    
    
    # Verifica se o TOKEN_WORKER está definido
    if [ -z "${TOKEN_WORKER}" ]; then
        echo -e "[ERROR] Token do worker não fornecido. Defina TOKEN_WORKER no arquivo .env."
        echo -e "[INFO] Obtenha o token no manager usando: docker swarm join-token worker"
        read -p "Digite o token do worker: " TOKEN_WORKER
    fi
    
    # Juntando-se ao Swarm
    docker swarm join --token ${TOKEN_WORKER} ${MANAGER_IP}:2377
    
    check_status "Node adicionado ao Swarm com sucesso" "Falha ao juntar-se ao Swarm"
}

# Função principal
main() {

    apt-get update && apt-get upgrade -y
    
    show_banner
    
    # Carregar variáveis do arquivo .env
    if [ -f "./scripts/.env" ]; then
        source "./scripts/.env"
    else
        echo -e "[ERROR] O arquivo .env não foi encontrado. Certifique-se de que ele existe no diretório atual."
        exit 1
    fi

    # Verifica se o MANAGER_IP está definido
    if [ -z "${MANAGER_IP}" ]; then
        echo -e "[ERROR] Token do worker não fornecido. Defina TOKEN_WORKER no arquivo .env."
        echo -e "[INFO] Obtenha o token no manager usando: docker swarm join-token worker"
        read -p "Digite o token do worker: " MANAGER_IP
    fi

    # Verifica se o TOKEN_WORKER está definido
    if [ -z "${TOKEN_WORKER}" ]; then
        echo -e "[ERROR] Token do worker não fornecido. Defina TOKEN_WORKER no arquivo .env."
        echo -e "[INFO] Obtenha o token no manager usando: docker swarm join-token worker"
        read -p "Digite o token do worker: " TOKEN_WORKER
    fi
    
    check_requirements
    install_docker
    setup_nfs
    join_swarm "$1"
    
    echo -e "\n[SUCCESS] Worker configurado com sucesso!"
    echo -e "[INFO] Verifique o status do node no manager usando: docker node ls"
}


# Execução do script
main "$1"
