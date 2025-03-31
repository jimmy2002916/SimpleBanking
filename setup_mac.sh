#!/bin/bash
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Simple Banking System Setup ===${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Python 3 not found. Please install Python 3.6 or higher.${NC}"
    exit 1
fi

if [ ! -d "venv" ]; then
    echo -e "${GREEN}Creating virtual environment...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}Failed to create virtual environment. Please install venv package.${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Failed to activate virtual environment.${NC}"
    exit 1
fi

echo -e "${GREEN}Installing dependencies...${NC}"
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Failed to install dependencies.${NC}"
    exit 1
fi

if [ ! -d "logs" ]; then
    echo -e "${GREEN}Creating logs directory...${NC}"
    mkdir -p logs
fi

echo -e "${GREEN}Setup complete! Starting Simple Banking System...${NC}"
python3 main.py "$@"
