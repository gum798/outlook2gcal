#!/usr/bin/env python3
"""
Create a minimal, properly-sized macOS app icon
"""

from PIL import Image, ImageDraw
import subprocess
from pathlib import Path
import sys

def create_minimal_icon():
    # Standard macOS icon size with proper proportions
    size = 1024
    padding = size // 8  # 12.5% padding (standard for macOS)
    effective_size = size - (padding * 2)
    
    # Create transparent base
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    
    # Create the main icon area
    icon_img = Image.new('RGBA', (effective_size, effective_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon_img)
    
    # Simple blue background with subtle gradient
    for y in range(effective_size):
        # Light blue to darker blue gradient
        progress = y / effective_size
        r = int(0 + (0 - 0) * progress)
        g = int(122 + (100 - 122) * progress)
        b = int(255 + (220 - 255) * progress)
        draw.rectangle([(0, y), (effective_size, y+1)], fill=(r, g, b, 255))
    
    # Round corners
    corner_radius = effective_size // 6  # More subtle rounding
    mask = Image.new('L', (effective_size, effective_size), 0)
    mask_draw = ImageDraw.Draw(mask)
    
    # Create rounded rectangle mask
    mask_draw.rectangle([(corner_radius, 0), (effective_size - corner_radius, effective_size)], fill=255)
    mask_draw.rectangle([(0, corner_radius), (effective_size, effective_size - corner_radius)], fill=255)
    
    # Corner circles
    mask_draw.ellipse([(0, 0), (corner_radius * 2, corner_radius * 2)], fill=255)
    mask_draw.ellipse([(effective_size - corner_radius * 2, 0), (effective_size, corner_radius * 2)], fill=255)
    mask_draw.ellipse([(0, effective_size - corner_radius * 2), (corner_radius * 2, effective_size)], fill=255)
    mask_draw.ellipse([(effective_size - corner_radius * 2, effective_size - corner_radius * 2), (effective_size, effective_size)], fill=255)
    
    # Apply mask
    icon_img.putalpha(mask)
    
    # Add simple calendar symbol
    symbol_size = effective_size // 2
    symbol_x = (effective_size - symbol_size) // 2
    symbol_y = (effective_size - symbol_size) // 2 - effective_size // 20
    
    draw = ImageDraw.Draw(icon_img)
    
    # Calendar body (white rectangle)
    cal_rect = [symbol_x, symbol_y, symbol_x + symbol_size, symbol_y + symbol_size]
    draw.rectangle(cal_rect, fill=(255, 255, 255, 230))
    
    # Calendar header
    header_height = symbol_size // 5
    draw.rectangle([symbol_x, symbol_y, symbol_x + symbol_size, symbol_y + header_height], fill=(255, 255, 255, 255))
    
    # Calendar grid (simple dots for dates)
    dot_size = symbol_size // 20
    for row in range(3):
        for col in range(4):
            dot_x = symbol_x + symbol_size // 8 + col * (symbol_size // 6)
            dot_y = symbol_y + header_height + symbol_size // 8 + row * (symbol_size // 8)
            
            if row == 1 and col == 1:  # Highlight "today"
                color = (0, 122, 255, 200)
            else:
                color = (120, 120, 120, 150)
            
            draw.ellipse([dot_x, dot_y, dot_x + dot_size, dot_y + dot_size], fill=color)
    
    # Add sync indicator (small arrows at bottom)
    arrow_y = symbol_y + symbol_size + effective_size // 20
    arrow_size = effective_size // 15
    center_x = effective_size // 2
    
    # Right arrow
    arrow_points = [
        (center_x + 5, arrow_y),
        (center_x + arrow_size + 5, arrow_y + arrow_size // 2),
        (center_x + 5, arrow_y + arrow_size)
    ]
    draw.polygon(arrow_points, fill=(255, 255, 255, 180))
    
    # Left arrow
    arrow_points = [
        (center_x - 5 - arrow_size, arrow_y),
        (center_x - 5, arrow_y + arrow_size // 2),
        (center_x - 5 - arrow_size, arrow_y + arrow_size)
    ]
    draw.polygon(arrow_points, fill=(255, 255, 255, 180))
    
    # Paste the icon onto the full-size image with padding
    img.paste(icon_img, (padding, padding), icon_img)
    
    return img

def convert_and_install(png_path):
    """Convert to ICNS and install"""
    iconset_dir = png_path.parent / f"{png_path.stem}.iconset"
    icns_path = png_path.parent / f"{png_path.stem}.icns"
    
    # Create iconset
    subprocess.run(['rm', '-rf', str(iconset_dir)], capture_output=True)
    subprocess.run(['mkdir', '-p', str(iconset_dir)])
    
    # Generate all sizes
    sizes = [
        (16, 'icon_16x16.png'),
        (32, 'icon_16x16@2x.png'),
        (32, 'icon_32x32.png'),
        (64, 'icon_32x32@2x.png'),
        (128, 'icon_128x128.png'),
        (256, 'icon_128x128@2x.png'),
        (256, 'icon_256x256.png'),
        (512, 'icon_256x256@2x.png'),
        (512, 'icon_512x512.png'),
        (1024, 'icon_512x512@2x.png')
    ]
    
    for size, filename in sizes:
        subprocess.run(['sips', '-z', str(size), str(size), str(png_path), 
                       '--out', str(iconset_dir / filename)], capture_output=True)
    
    # Convert to icns
    subprocess.run(['iconutil', '-c', 'icns', str(iconset_dir), '-o', str(icns_path)])
    
    # Install
    app_icon_path = "/Applications/Outlook2GCal Sync.app/Contents/Resources/AppIcon.icns"
    subprocess.run(['cp', str(icns_path), app_icon_path])
    
    # Refresh
    subprocess.run(['touch', '/Applications/Outlook2GCal Sync.app'])
    subprocess.run(['killall', 'Finder'], capture_output=True)
    subprocess.run(['killall', 'Dock'], capture_output=True)
    
    return True

def main():
    print("🎨 Creating minimal macOS app icon...")
    
    # Create icon
    icon = create_minimal_icon()
    
    # Save
    png_path = Path(__file__).parent / "minimal_app_icon.png"
    icon.save(png_path, "PNG")
    print(f"✅ Created PNG: {png_path}")
    
    # Convert and install
    if convert_and_install(png_path):
        print("🎉 Minimal icon installed successfully!")
        print("📱 This should now appear the same size as other apps.")
    
    return True

if __name__ == "__main__":
    main()