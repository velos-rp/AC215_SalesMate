#!/bin/sh

if [ "$DEV" = "1" ]; then
  # Open a shell
  exec sh
else
  # Default behavior: Run npm commands
  npm install && npm run dev
fi
