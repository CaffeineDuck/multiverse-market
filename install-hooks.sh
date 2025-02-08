#!/bin/sh
for hook in .githooks/*; do
    if [ -f "$hook" ]; then
        ln -sf "../../$hook" ".git/hooks/$(basename "$hook")"
    fi
done
echo "Git hooks installed successfully!"
