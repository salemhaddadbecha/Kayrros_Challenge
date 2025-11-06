#!/usr/bin/env bash

set -eu

ROOTDIR=$(dirname $0)

install_brew() {
    URL_BREW='https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh'
    echo 'Installing brew...'
    echo | bash -c "$(curl -fsSL $URL_BREW)"
}

install_docker() {
    echo 'Installing Docker...'
    brew install --cask docker
}

install_pyenv() {
    echo 'Installing pyenv...'
    brew install pyenv

    if [[ -n "$ZSH_VERSION" ]]; then
        RCFILE="$HOME/.zshrc"
    elif [[ -n "$BASH_VERSION" ]]; then
        RCFILE="$HOME/.bashrc"
    else
        echo 'Unsupported shell. Please set RCFILE manually.'
    fi

    cat <<- "EOF" >> $RCFILE
        export PYENV_ROOT="$HOME/.pyenv"
        export PATH="$PYENV_ROOT/shims:$PATH"
        if command -v pyenv > /dev/null 2>&1; then
            eval "$(pyenv init -)"
        fi
EOF
}

install_python() {
    PYTHON_VERSION_FILE="$ROOTDIR/../.python-version"
    PYTHON_VERSION=$(cat $PYTHON_VERSION_FILE | xargs)

    if pyenv versions --bare | grep -q "^$PYTHON_VERSION$"; then
        echo "Python $PYTHON_VERSION is already installed."
    else
        echo "Installing Python $PYTHON_VERSION..."
        $SHELL -c "pyenv install -s $PYTHON_VERSION"
    fi
}

install_uv() {
    echo 'Installing UV...'
    brew install uv
}

echo 'Installing prerequisites...'
command -v brew > /dev/null || install_brew
command -v docker > /dev/null || install_docker
command -v pyenv > /dev/null || install_pyenv
install_python
command -v uv > /dev/null || install_uv