#!/bin/bash
# Setup remotion-design-master components for video-podcast-maker

REPO_URL="https://github.com/Agents365-ai/remotion-design-master.git"
LOCAL_PATH="$HOME/.claude/skills/remotion-design-master"
TARGET_DIR="src/remotion/design"

echo "Setting up design system..."

# Clone from GitHub if not exists locally
if [ ! -d "$LOCAL_PATH/src" ]; then
  echo "Cloning remotion-design-master from GitHub..."
  TEMP_DIR=$(mktemp -d)
  git clone --depth 1 "$REPO_URL" "$TEMP_DIR/rdm"

  if [ $? -ne 0 ]; then
    echo "Error: Failed to clone from $REPO_URL"
    rm -rf "$TEMP_DIR"
    exit 1
  fi

  # Remove old design folder and copy new
  rm -rf "$TARGET_DIR"
  cp -r "$TEMP_DIR/rdm/src" "$TARGET_DIR"
  rm -rf "$TEMP_DIR"
else
  echo "Using local remotion-design-master..."
  rm -rf "$TARGET_DIR"
  cp -r "$LOCAL_PATH/src" "$TARGET_DIR"
fi

echo ""
echo "✓ Design system installed to $TARGET_DIR"
echo ""
echo "Available imports:"
echo "  import { FullBleed, ContentArea } from './design'"
echo "  import { FadeIn, SpringPop } from './design'"
echo "  import { minimalWhite } from './design/themes'"
