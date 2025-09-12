#!/usr/bin/env python3
"""
Create a better, standard-sized macOS app icon
"""

from PIL import Image, ImageDraw, ImageFont
import subprocess
from pathlib import Path
import sys

def create_app_icon():
    # Create a 1024x1024 base image with proper padding
    size = 1024
    # Add padding to make icon appear smaller (like other macOS apps)
    padding = size // 12  # About 8% padding
    effective_size = size - (padding * 2)
    
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Modern blue gradient background (similar to Apple's style)
    # Create gradient from light blue to darker blue, with padding
    for y in range(effective_size):
        # Gradient from #007AFF (Apple blue) to #0051D0
        r = int(0 + (0 - 0) * y / effective_size)
        g = int(122 + (81 - 122) * y / effective_size) 
        b = int(255 + (208 - 255) * y / effective_size)
        draw.rectangle([(padding, y + padding), (size - padding, y + padding + 1)], fill=(r, g, b, 255))
    
    # Round the corners (macOS Big Sur style) with padding
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    corner_radius = effective_size // 8  # Proportional to effective size
    
    # Apply rounded corners to the padded area
    mask_draw.rectangle([(padding + corner_radius, padding), (size - padding - corner_radius, size - padding)], fill=255)
    mask_draw.rectangle([(padding, padding + corner_radius), (size - padding, size - padding - corner_radius)], fill=255)
    mask_draw.ellipse([(padding, padding), (padding + corner_radius*2, padding + corner_radius*2)], fill=255)
    mask_draw.ellipse([(size - padding - corner_radius*2, padding), (size - padding, padding + corner_radius*2)], fill=255)
    mask_draw.ellipse([(padding, size - padding - corner_radius*2), (padding + corner_radius*2, size - padding)], fill=255)
    mask_draw.ellipse([(size - padding - corner_radius*2, size - padding - corner_radius*2), (size - padding, size - padding)], fill=255)
    
    # Apply mask to make rounded corners
    output = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    output.paste(img, (0, 0))
    output.putalpha(mask)
    
    # Add calendar icon (simplified white calendar) - adjusted for padding
    calendar_size = effective_size // 3
    calendar_x = size // 2 - calendar_size // 2
    calendar_y = size // 2 - calendar_size // 2 - effective_size // 12
    
    # Calendar background
    draw = ImageDraw.Draw(output)
    calendar_rect = [calendar_x, calendar_y, calendar_x + calendar_size, calendar_y + calendar_size]
    draw.rectangle(calendar_rect, fill=(255, 255, 255, 240))
    
    # Calendar header
    header_height = calendar_size // 6
    header_rect = [calendar_x, calendar_y, calendar_x + calendar_size, calendar_y + header_height]
    draw.rectangle(header_rect, fill=(255, 255, 255, 255))
    draw.rectangle([calendar_x, calendar_y + header_height - 10, calendar_x + calendar_size, calendar_y + header_height], 
                  fill=(255, 255, 255, 255))
    
    # Calendar grid
    grid_y_start = calendar_y + header_height + 10
    grid_size = calendar_size - 20
    cell_size = grid_size // 5
    
    for i in range(4):
        for j in range(4):
            if i == 1 and j == 1:  # Highlight today
                cell_color = (0, 122, 255, 180)
            else:
                cell_color = (100, 100, 100, 100)
            
            cell_x = calendar_x + 10 + j * cell_size + j * 5
            cell_y = grid_y_start + i * cell_size + i * 5
            draw.rectangle([cell_x, cell_y, cell_x + cell_size - 5, cell_y + cell_size - 5], 
                         fill=cell_color)
    
    # Add sync arrows - adjusted for padding
    arrow_size = effective_size // 10  # Smaller arrows
    arrow_y = calendar_y + calendar_size + effective_size // 15
    
    # Right arrow (→)
    arrow1_x = size // 2 + size // 20
    arrow_points = [
        (arrow1_x, arrow_y),
        (arrow1_x + arrow_size, arrow_y + arrow_size // 2),
        (arrow1_x, arrow_y + arrow_size)
    ]
    draw.polygon(arrow_points, fill=(255, 255, 255, 200))
    
    # Left arrow (←) 
    arrow2_x = size // 2 - size // 20 - arrow_size
    arrow_points = [
        (arrow2_x + arrow_size, arrow_y),
        (arrow2_x, arrow_y + arrow_size // 2),
        (arrow2_x + arrow_size, arrow_y + arrow_size)
    ]
    draw.polygon(arrow_points, fill=(255, 255, 255, 200))
    
    return output

def convert_to_icns(png_path):
    """Convert PNG to ICNS format"""
    iconset_dir = png_path.parent / f"{png_path.stem}.iconset"
    icns_path = png_path.parent / f"{png_path.stem}.icns"
    
    # Create iconset directory
    subprocess.run(['rm', '-rf', str(iconset_dir)], capture_output=True)
    subprocess.run(['mkdir', '-p', str(iconset_dir)])
    
    # Generate all required sizes
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
                       '--out', str(iconset_dir / filename)], 
                      capture_output=True)
    
    # Convert to icns
    result = subprocess.run(['iconutil', '-c', 'icns', str(iconset_dir), '-o', str(icns_path)], 
                           capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Created ICNS file: {icns_path}")
        return icns_path
    else:
        print(f"❌ Error creating ICNS: {result.stderr}")
        return None

def install_icon(icns_path):
    """Install icon to the app bundle"""
    app_icon_path = "/Applications/Outlook2GCal Sync.app/Contents/Resources/AppIcon.icns"
    
    # Backup original icon
    subprocess.run(['cp', app_icon_path, f"{app_icon_path}.backup"], capture_output=True)
    
    # Install new icon
    result = subprocess.run(['cp', str(icns_path), app_icon_path], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Installed icon to app bundle")
        
        # Refresh Finder and Dock
        subprocess.run(['touch', '/Applications/Outlook2GCal Sync.app'])
        subprocess.run(['killall', 'Finder'], capture_output=True)
        subprocess.run(['killall', 'Dock'], capture_output=True)
        
        print("🔄 Refreshed Finder and Dock")
        return True
    else:
        print(f"❌ Error installing icon: {result.stderr}")
        return False

def main():
    print("🎨 Creating better macOS app icon...")
    
    # Check if PIL is available
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("❌ PIL (Pillow) not found. Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'Pillow'])
        from PIL import Image, ImageDraw
    
    # Create icon
    icon = create_app_icon()
    
    # Save PNG
    png_path = Path(__file__).parent / "new_app_icon.png"
    icon.save(png_path, "PNG")
    print(f"✅ Created PNG icon: {png_path}")
    
    # Convert to ICNS
    icns_path = convert_to_icns(png_path)
    if not icns_path:
        return False
    
    # Install to app
    if install_icon(icns_path):
        print("🎉 New icon installed successfully!")
        print("📱 The app icon should update shortly.")
        return True
    else:
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)