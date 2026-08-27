"""Image effects for wallpapers."""

from PIL import Image, ImageFilter, ImageEnhance
from pathlib import Path

def apply_effect(image_path: str, effect: str) -> Path:
    """Apply visual effects to wallpaper.
    
    Args:
        image_path: Path to source image
        effect: Effect name (blur, darken, grayscale, vignette)
        
    Returns:
        Path to processed image
    """
    img_path = Path(image_path)
    output_path = img_path.parent / f"{img_path.stem}_effect{img_path.suffix}"
    
    try:
        with Image.open(img_path) as opened:
            img: Image.Image = opened
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Apply requested effect
            if effect == 'blur':
                img = img.filter(ImageFilter.GaussianBlur(radius=5))
            elif effect == 'darken':
                brightness = ImageEnhance.Brightness(img)
                img = brightness.enhance(0.6)
            elif effect == 'grayscale':
                img = img.convert('L').convert('RGB')
            elif effect == 'vignette':
                # Create vignette effect
                img = _apply_vignette(img)
            elif effect == 'vibrant':
                color = ImageEnhance.Color(img)
                img = color.enhance(1.3)
                contrast = ImageEnhance.Contrast(img)
                img = contrast.enhance(1.1)
            
            # Save processed image
            img.save(output_path, quality=90)
            return output_path
            
    except Exception as e:
        print(f"Error applying effect: {e}")
        return img_path

def _apply_vignette(img: Image.Image, strength: float = 0.5) -> Image.Image:
    """Apply vignette effect to image."""
    from PIL import ImageDraw, ImageFilter
    
    # Create mask
    mask = Image.new('L', img.size, 255)
    draw = ImageDraw.Draw(mask)
    
    # Draw fading circle
    width, height = img.size
    radius = min(width, height) * (0.7 - strength * 0.2)
    draw.ellipse(
        [(width/2 - radius, height/2 - radius), 
         (width/2 + radius, height/2 + radius)],
        fill=255
    )
    
    # Apply blur to mask
    mask = mask.filter(ImageFilter.GaussianBlur(radius=width*0.05))
    
    # Apply mask
    img.putalpha(mask)
    
    # Blend with black background
    black_bg = Image.new('RGB', img.size, (0, 0, 0))
    black_bg.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
    
    return black_bg
