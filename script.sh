#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

# Check color support
if [ -z "$TERM" ] || [ "$TERM" = "dumb" ]; then
    RED='' GREEN='' YELLOW='' BLUE='' CYAN='' BOLD='' DIM='' NC=''
fi

# Spinner variables
SPINNERChars=('⠋' '⠙' '⠹' '⠸' '⠼' '⠴' '⠦' '⠧' '⠇' '⠏')
SPINNER_PID=""

# Spinner functions
start_spinner() {
    local message="${1:-Loading...}"
    printf "${CYAN}%s${NC}" "$message"
    SPINNER_PID=$!
    (
        while true; do
            for char in "${SPINNERChars[@]}"; do
                printf "\r${CYAN}%s %s${NC}" "$char" "$message"
                sleep 0.1
            done
        done
    ) &
    SPINNER_PID=$!
}

stop_spinner() {
    if [ -n "$SPINNER_PID" ]; then
        kill $SPINNER_PID 2>/dev/null
        wait $SPINNER_PID 2>/dev/null
        SPINNER_PID=""
    fi
    printf "\r\033[K"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check for fzf
has_fzf() {
    command -v fzf &>/dev/null
}

# Menu with fzf
menu_fzf() {
    local height=${1:-15}
    echo "$MENU_OPTIONS_JSON" | fzf --height=$height --border --layout=reverse --prompt="Chọn tác vụ: " --color=fg:#e5e9f0,bg:#1e1e2e,preview-bg:#181825,hl:#cba6f7,fg+:#cdd6f4,bg+:#313244,border:#585b70,spinner:#f5c2e7,header:#f5c2e7
}

# Native menu (fallback)
menu_native() {
    clear
    echo -e "${BOLD}${CYAN}╔══════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${CYAN}║${NC}     ${BOLD}AI HelpDesk - Backend Manager${NC}     ${CYAN}║${NC}"
    echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════╝${NC}"
    echo ""
    
    for i in "${!MENU_LABELS[@]}"; do
        if [ "$i" -eq "$SELECTED" ]; then
            echo -e "  ${GREEN}▶${NC} ${BOLD}$((i+1))) ${MENU_LABELS[$i]}${NC}"
        else
            echo -e "    ${DIM}$((i+1))) ${MENU_LABELS[$i]}${NC}"
        fi
    done
    
    echo ""
    echo -e "${DIM}↑↓ di chuyển | Enter chọn | q thoát${NC}"
}

# Functions from original script.sh
TARGET_FILE="src/Domain/base_entities.py"

convert_uuid() {
    print_info "Đang tiến hành convert ID sang UUID7..."
    python -m sqlacodegen mysql://root:@localhost:3306/AI_HelpDesk --generator sqlmodels --outfile $TARGET_FILE 2>/dev/null
    
    if [ ! -f "$TARGET_FILE" ]; then
        print_error "Không tìm thấy file $TARGET_FILE"
        return 1
    fi

    if ! grep -q "import uuid6" "$TARGET_FILE"; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' '1i\'$'\n''import uuid6' "$TARGET_FILE"
        else
            sed -i '1iimport uuid6' "$TARGET_FILE"
        fi
        print_success "Đã thêm 'import uuid6'"
    fi

    SEARCH="sa_column=Column('id', CHAR(36), primary_key=True, server_default=text('(uuid())'))"
    REPLACE="default_factory=lambda: str(uuid6.uuid7()), sa_column=Column(CHAR(36), primary_key=True)"

    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s|$SEARCH|$REPLACE|g" "$TARGET_FILE"
    else
        sed -i "s|$SEARCH|$REPLACE|g" "$TARGET_FILE"
    fi
    
    print_success "Convert hoàn tất!"
}

run_server() {
    print_info "Khởi chạy server..."
    dev
}

dev() {
    npx nodemon --watch . --ext .yaml ^ --exec "taskkill /IM python.exe /F >nul 2>&1 & set PYTHONPATH=%cd%\src && granian --interface asgi --port 8080 src.main:app"
}

run_streamlit() {
    print_info "Khởi chạy Streamlit..."
    set PYTHONPATH=%cd%\src && streamlit run ui/app.py --server.port 1337 --server.runOnSave true --server.headless true
}

run_ollama() {
    print_info "Khởi chạy Ollama..."
    ollama serve
}

run_wsl() {
    print_info "Khởi chạy WSL..."
    wsl
}

clear_uploads() {
    print_info "Đang xóa UUID folders..."
    find static/ -type d -name "*-*-*-*-*" -exec rm -rf {} + 2>/dev/null
    print_success "Done"
}

list_packages() {
    echo -e "\n${BOLD}Các package không cần thiết:${NC}"
    pip list --not-required 2>/dev/null | grep -v "^pip "
}

install_packages() {
    print_info "Đang cài đặt packages..."
    pip install -r packages.sh 2>/dev/null
    print_success "Hoàn tất"
}

uninstall_package() {
    print_warning "Đang gỡ cài đặt tất cả packages..."
    pip freeze > to_delete.txt 2>/dev/null
    pip uninstall -r to_delete.txt -y 2>/dev/null
    print_success "Hoàn tất"
}

create_venv() {
    if [ -d "venv" ]; then
        print_warning "Venv đã tồn tại"
    else
        python -m venv venv 2>/dev/null
        print_success "Venv created"
    fi
}

activate_venv() {
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate && print_success "Activated venv (Linux/WSL)"
    elif [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate && print_success "Activated .venv (Linux/WSL)"
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate && print_success "Activated venv (Windows)"
    elif [ -f ".venv/Scripts/activate" ]; then
        source .venv/Scripts/activate && print_success "Activated .venv (Windows)"
    else
        print_error "Venv not found"
    fi
}

deactivate_venv() {
    deactivate 2>/dev/null && print_success "Deactivated"
}

# Menu options
MENU_OPTIONS=(
    "run_server"
    "run_streamlit"
    "run_ollama"
    "run_wsl"
    "convert_uuid"
    "clear_uploads"
    "list_packages"
    "install_packages"
    "uninstall_package"
    "create_venv"
    "activate_venv"
    "deactivate_venv"
)

MENU_LABELS=(
    "Server (Granian)"
    "Streamlit"
    "Ollama Serve"
    "WSL"
    "Convert Model (UUID7)"
    "Clear uploads"
    "List packages"
    "Install packages"
    "Uninstall packages"
    "Create venv"
    "Activate venv"
    "Deactivate venv"
)

SELECTED=0

# Main menu loop
main_menu() {
    if has_fzf; then
        echo -e "${BOLD}${CYAN}Đang khởi động với fzf...${NC}"
        sleep 0.5
        selected=$(printf '%s\n' "${MENU_LABELS[@]}" | fzf --height=20 --border --layout=reverse --prompt="AI HelpDesk > " --color=bg:#1e1e2e,fg:#cdd6f4,hl:#cba6f7,pointer:#f5c2e7,header:#89b4fa --preview="echo 'Chọn tác vụ để thực thi'")
        
        for i in "${!MENU_LABELS[@]}"; do
            if [ "${MENU_LABELS[$i]}" = "$selected" ]; then
                clear
                ${MENU_OPTIONS[$i]}
                return
            fi
        done
    else
        while true; do
            menu_native
            
            read -n 1 key
            if [ "$key" = $'\e' ]; then
                read -n 1 -t 0.1 seq
                if [ "$seq" = "[" ]; then
                    read -n 1 -t 0.1 dir
                    case $dir in
                        A)
                            ((SELECTED--))
                            if [ "$SELECTED" -lt 0 ]; then SELECTED=$((${#MENU_LABELS[@]}-1)); fi
                            ;;
                        B)
                            ((SELECTED++))
                            if [ "$SELECTED" -ge ${#MENU_LABELS[@]} ]; then SELECTED=0; fi
                            ;;
                    esac
                fi
            elif [ "$key" = "" ]; then
                clear
                ${MENU_OPTIONS[$SELECTED]}
                return
            elif [ "$key" = "q" ] || [ "$key" = "Q" ]; then
                clear
                echo -e "${CYAN}Tạm biệt!${NC}"
                exit 0
            elif [[ "$key" =~ [1-9] ]]; then
                idx=$((key-1))
                if [ "$idx" -lt ${#MENU_LABELS[@]} ]; then
                    clear
                    ${MENU_OPTIONS[$idx]}
                    return
                fi
            fi
        done
    fi
}

main_menu
