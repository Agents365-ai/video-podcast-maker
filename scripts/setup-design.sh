#!/bin/bash
# Setup remotion-design-master components for video-podcast-maker

DESIGN_MASTER="$HOME/.claude/skills/remotion-design-master/src"
TARGET_DIR="src/remotion/design"

if [ ! -d "$DESIGN_MASTER" ]; then
  echo "Error: remotion-design-master not found at $DESIGN_MASTER"
  echo "Clone it first: git clone https://github.com/Agents365-ai/remotion-design-master.git ~/.claude/skills/remotion-design-master"
  exit 1
fi

echo "Setting up design system..."

# Remove old design folder if exists
rm -rf "$TARGET_DIR"

# Copy design system
cp -r "$DESIGN_MASTER" "$TARGET_DIR"

echo "✓ Design system installed to $TARGET_DIR"
echo ""
echo "Available imports:"
echo "  import { FullBleed, ContentArea } from './design'"
echo "  import { FadeIn, SpringPop } from './design'"
echo "  import { minimalWhite } from './design'"
