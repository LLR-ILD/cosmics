#!/bin/bash
CODE_DIR=$(dirname $(realpath $0))

activate_environment () {
    VENV=$CODE_DIR/.venv
    venv_activate=$VENV/bin/activate
    if ! [ -f $venv_activate ]; then
        echo "No python venv found: at " $venv_activate
        echo "It will be built now."
        python3 -m venv $VENV --prompt $(basename $(pwd))
        source $VENV/bin/activate
        pip install --upgrade pip wheel
        pip install -r $CODE_DIR/requirements-dev.txt
        pre-commit install
        # If you are developping a local package
        python -m pip install -e .
        # Expose the kernel to notebook.
        python -m ipykernel install --user --name $(basename $CODE_DIR)
    else
        source $venv_activate
    fi
}

activate_environment
