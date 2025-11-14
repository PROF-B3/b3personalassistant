#!/usr/bin/env python3
"""
Create application icons for B3PersonalAssistant
Generates icons in multiple formats and sizes for all platforms
"""

import os
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Error: Pillow is required")
    print("Install with: pip install Pillow")
    sys.exit(1)


def create_gradient_icon(size, output_path):
    """Create a gradient icon with B3 text."""
    # Create image with gradient background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw gradient circle background
    for i in range(size):
        # Gradient from cyan to purple
        r = int(50 + (150 * i / size))
        g = int(200 - (100 * i / size))
        b = int(250 - (50 * i / size))

        circle_size = size - (i * 2)
        if circle_size > 0:
            draw.ellipse(
                [i, i, size - i, size - i],
                fill=(r, g, b, 255)
            )

    # Add B3 text
    try:
        # Try to use a bold font
        font_size = size // 2
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
            except:
                font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()

    # Draw text
    text = "B3"

    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Center text
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - (font_size // 10)

    # Draw text with shadow
    shadow_offset = size // 40
    draw.text((x + shadow_offset, y + shadow_offset), text, fill=(0, 0, 0, 128), font=font)
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)

    # Save
    img.save(output_path)
    print(f"Created: {output_path}")


def create_icon_set():
    """Create complete icon set for all platforms."""

    print("Creating B3PersonalAssistant icon set...")
    print()

    # Create icons directory
    icons_dir = Path("resources/icons")
    icons_dir.mkdir(parents=True, exist_ok=True)

    # Sizes needed for different platforms
    sizes = {
        'windows': [16, 32, 48, 64, 128, 256],
        'macos': [16, 32, 64, 128, 256, 512, 1024],
        'linux': [16, 24, 32, 48, 64, 128, 256, 512],
    }

    all_sizes = sorted(set(sum(sizes.values(), [])))

    # Generate PNG icons at all sizes
    print("Generating PNG icons...")
    png_files = []
    for size in all_sizes:
        png_path = icons_dir / f"icon_{size}x{size}.png"
        create_gradient_icon(size, png_path)
        png_files.append(png_path)

    print()

    # Create Windows ICO file (multi-resolution)
    try:
        print("Creating Windows .ico file...")
        ico_sizes = [(s, s) for s in sizes['windows']]
        images = [Image.open(icons_dir / f"icon_{s}x{s}.png").resize((s, s)) for s in sizes['windows']]
        ico_path = Path("icon.ico")
        images[0].save(ico_path, format='ICO', sizes=ico_sizes, append_images=images[1:])
        print(f"Created: {ico_path}")
    except Exception as e:
        print(f"Warning: Could not create .ico file: {e}")

    print()

    # Create macOS ICNS file
    try:
        print("Creating macOS .icns file...")
        print("Note: Use iconutil on macOS to create .icns from iconset")

        # Create iconset directory
        iconset_dir = Path("icon.iconset")
        iconset_dir.mkdir(exist_ok=True)

        # Copy icons with proper naming for macOS
        macos_mapping = {
            16: 'icon_16x16.png',
            32: 'icon_16x16@2x.png',
            32: 'icon_32x32.png',
            64: 'icon_32x32@2x.png',
            128: 'icon_128x128.png',
            256: 'icon_128x128@2x.png',
            256: 'icon_256x256.png',
            512: 'icon_256x256@2x.png',
            512: 'icon_512x512.png',
            1024: 'icon_512x512@2x.png',
        }

        for size in sizes['macos']:
            src = icons_dir / f"icon_{size}x{size}.png"
            if size == 16:
                dst = iconset_dir / 'icon_16x16.png'
            elif size == 32:
                dst = iconset_dir / 'icon_32x32.png'
            elif size == 64:
                dst = iconset_dir / 'icon_32x32@2x.png'
            elif size == 128:
                dst = iconset_dir / 'icon_128x128.png'
            elif size == 256:
                dst = iconset_dir / 'icon_256x256.png'
            elif size == 512:
                dst = iconset_dir / 'icon_512x512.png'
            elif size == 1024:
                dst = iconset_dir / 'icon_512x512@2x.png'
            else:
                continue

            img = Image.open(src)
            img.save(dst)

        print(f"Created: {iconset_dir}")
        print("To create .icns on macOS, run:")
        print(f"  iconutil -c icns {iconset_dir}")

    except Exception as e:
        print(f"Warning: Could not create iconset: {e}")

    print()

    # Create Linux desktop icon
    print("Creating Linux desktop icon...")
    linux_icon = icons_dir / "b3personalassistant.png"
    Image.open(icons_dir / "icon_256x256.png").save(linux_icon)
    print(f"Created: {linux_icon}")

    print()
    print("=" * 50)
    print("Icon creation complete!")
    print()
    print("Next steps:")
    print("  1. Windows: icon.ico is ready to use")
    print("  2. macOS: Run 'iconutil -c icns icon.iconset' to create icon.icns")
    print("  3. Linux: Icons are in resources/icons/")
    print()
    print("To use icons in PyInstaller:")
    print("  - Edit B3PersonalAssistant.spec")
    print("  - Set icon='icon.ico' (Windows)")
    print("  - Set icon='icon.icns' (macOS)")


if __name__ == "__main__":
    create_icon_set()
