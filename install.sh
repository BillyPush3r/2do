#!/usr/bin/env bash
set -e

# ── colors ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
info()    { echo -e "${CYAN}[2do]${NC} $*"; }
success() { echo -e "${GREEN}[2do]${NC} $*"; }
warn()    { echo -e "${YELLOW}[2do]${NC} $*"; }
die()     { echo -e "${RED}[2do] ERROR:${NC} $*" >&2; exit 1; }

# ── check / install uv ──────────────────────────────────────────────────────
if ! command -v uv &>/dev/null; then
  info "uv not found — installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # Add uv to PATH for the rest of this script
  export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
  command -v uv &>/dev/null || die "uv installation failed. Please install manually: https://docs.astral.sh/uv/"
  success "uv installed."
else
  info "uv found: $(uv --version)"
fi

# ── resolve project root ─────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${SCRIPT_DIR}"

[ -f "$PROJECT_DIR/pyproject.toml" ] || die "pyproject.toml not found in $PROJECT_DIR"
[ -f "$PROJECT_DIR/main.py" ]        || die "main.py not found in $PROJECT_DIR"

info "Project root: $PROJECT_DIR"

# ── sync dependencies ────────────────────────────────────────────────────────
info "Syncing dependencies..."
cd "$PROJECT_DIR"
uv sync
success "Dependencies ready."

# ── write the wrapper script ─────────────────────────────────────────────────
INSTALL_DIR="$HOME/.local/bin"
mkdir -p "$INSTALL_DIR"

WRAPPER="$INSTALL_DIR/2do"
cat > "$WRAPPER" <<EOF
#!/usr/bin/env bash
exec uv run --project "$PROJECT_DIR" "$PROJECT_DIR/main.py" "\$@"
EOF
chmod +x "$WRAPPER"

# ── ensure ~/.local/bin is on PATH ───────────────────────────────────────────
add_to_path() {
  local cfg="$1"
  if [ -f "$cfg" ] && ! grep -q '\.local/bin' "$cfg"; then
    echo '' >> "$cfg"
    echo '# added by 2do installer' >> "$cfg"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$cfg"
    warn "Added ~/.local/bin to PATH in $cfg — restart your shell or run: source $cfg"
  fi
}

if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
  add_to_path "$HOME/.bashrc"
  add_to_path "$HOME/.zshrc"
  export PATH="$HOME/.local/bin:$PATH"
fi

# ── done ─────────────────────────────────────────────────────────────────────
success "Installed! You can now run: 2do"
echo ""
echo -e "  ${CYAN}2do${NC}         → run the CLI"
echo -e "  ${CYAN}2do --help${NC}  → show help (if implemented)"
echo ""
warn "If '2do' isn't found yet, restart your terminal or run:"
echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
