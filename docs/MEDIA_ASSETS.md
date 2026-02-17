# Media Assets Reference

Recommended sources for free video/image assets.

## Access Markers

- **Global** - No restrictions, API-friendly
- **Protected** - Bot protection, use browser to download

---

## Video Assets (Recommended Order)

| Site | Access | Features | License | Best For |
|------|--------|----------|---------|----------|
| **[Mixkit](https://mixkit.co)** | Global | Envato, professional quality, video+music+SFX | Free commercial | **Top pick**, professional footage |
| **[Coverr](https://coverr.co)** | Global | Film-maker style, artistic, HD/4K | Free commercial | **Top pick**, backgrounds, transitions |
| **[Pexels Videos](https://pexels.com/videos)** | Protected | Comprehensive, Chinese search | Free commercial | General footage, lifestyle |
| **[Pixabay Videos](https://pixabay.com/videos)** | Protected | 160M+ assets, CC0 | Free commercial | Largest library |
| **[Videvo](https://videvo.net)** | Protected | Large free selection | Some require attribution | Tech, nature, city |

---

## Image Assets

### General Photography

| Site | Access | Features | License | Best For |
|------|--------|----------|---------|----------|
| **[Unsplash](https://unsplash.com)** | Protected | High-quality photos, modern style | Free commercial | Backgrounds, atmosphere |
| **[Pexels](https://pexels.com)** | Protected | Photos+videos, Chinese search | Free commercial | General, lifestyle |
| **[Pixabay](https://pixabay.com)** | Protected | 3.8M+ images, vectors | CC0 | Illustrations, icons |
| **[Burst](https://burst.shopify.com)** | Global | Shopify, business style | Free commercial | Business, e-commerce |

### Tech/Product

| Source | Features | Best For |
|--------|----------|----------|
| **Official Press Kit** | Official media packages | Product intros, news |
| **GitHub Repos** | Screenshots, architecture diagrams | Tech tutorials, open source |
| **Product Hunt** | Homepage screenshots, intro videos | New product intros |
| **Playwright Screenshots** | Real-time capture | Latest UI, demos |

### Illustrations/Icons

| Site | Features | License | Best For |
|------|----------|---------|----------|
| **[unDraw](https://undraw.co)** | Customizable SVG color | Free commercial | Concept explanations |
| **[Storyset](https://storyset.com)** | Animated illustrations, GIF/video export | Free commercial | Scene animations |
| **[Flaticon](https://flaticon.com)** | Massive icon library | Attribution required | UI icons |
| **[Icons8](https://icons8.com)** | Icons+illustrations+photos | Attribution required | Unified icon sets |
| **[Noun Project](https://thenounproject.com)** | Minimal line icons | Attribution required | Minimalist infographics |

### Special Purpose

| Source | Features | Best For |
|--------|----------|----------|
| **[NASA Images](https://images.nasa.gov)** | NASA official library | Space, science, exploration |
| **[Wikimedia Commons](https://commons.wikimedia.org)** | Wikipedia assets | Historical, scientific diagrams |
| **[Flickr CC](https://flickr.com/creativecommons)** | CC licensed photos | Various, check specific license |
| **[Internet Archive](https://archive.org)** | Historical footage, public domain | Retro style, historical |

---

## Download Tips

1. **Prefer Global sites** - Mixkit, Coverr most reliable
2. **Official assets first** - Use Press Kit for product videos
3. **Consistent style** - Use same source within a video
4. **Check attribution** - Note requirements in video description
5. **Pre-download Protected** - Use browser for bot-protected sites

---

## AI Image Generation

### imagen (Google Gemini)

```bash
source ~/.zshrc && python3 ~/.claude/skills/imagen/scripts/generate_image.py \
  --size 2K \
  "Prompt description here" \
  output.png
```

- **Requires**: `GEMINI_API_KEY`
- **Best for**: International use, English content

### imagenty (Alibaba Cloud)

```bash
source ~/.zshrc && python3 ~/.claude/skills/imagenty/scripts/generate_image.py \
  --size 16:9 \
  "Prompt description here" \
  output.png
```

- **Requires**: `DASHSCOPE_API_KEY`
- **Best for**: Chinese text rendering, domestic users

---

## Media Naming Convention

```
public/media/{video-name}/
├── {section}_{index}.{ext}           # General: hero_1.png
├── {section}_screenshot.png          # Screenshot: demo_screenshot.png
├── {section}_screenshot_cropped.png  # Cropped: demo_screenshot_cropped.png
├── {section}_logo.png                # Logo: overview_logo.png
├── {section}_web_{index}.{ext}       # Web search: comparison_web_1.jpg
└── {section}_ai.png                  # AI generated: summary_ai.png
```
