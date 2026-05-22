"""Convert SVG to ICO using pure Python (no cairosvg needed)."""
from PIL import Image, ImageDraw
import math, os

def draw_icon(size):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size

    # ── Background rounded rect ──
    radius = int(s * 0.19)
    bg_top    = (31, 58, 138)
    bg_bottom = (15, 23, 42)

    # Simple gradient by drawing rows
    for y in range(s):
        t = y / s
        r = int(bg_top[0] + (bg_bottom[0] - bg_top[0]) * t)
        g = int(bg_top[1] + (bg_bottom[1] - bg_top[1]) * t)
        b = int(bg_top[2] + (bg_bottom[2] - bg_top[2]) * t)
        d.line([(0, y), (s, y)], fill=(r, g, b, 255))

    # Mask corners to make rounded rect
    corner = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    cd = ImageDraw.Draw(corner)
    cd.rounded_rectangle([0, 0, s-1, s-1], radius=radius, fill=(255, 255, 255, 255))
    img.putalpha(corner.split()[0])

    # ── Oil drop ──
    cx = s // 2
    drop_top    = int(s * 0.195)
    drop_bottom = int(s * 0.76)
    drop_mid    = int(s * 0.575)
    drop_w      = int(s * 0.376)

    # Draw the teardrop path as a polygon
    points = []
    # Top tip
    tip = (cx, drop_top)
    # Bottom arc (semicircle)
    r_drop = drop_w // 2
    for angle in range(0, 181, 5):
        rad = math.radians(angle)
        px = cx + r_drop * math.sin(rad)
        py = drop_mid + r_drop * (-math.cos(rad)) * 0.9
        points.append((px, py))
    # Add left slope
    drop_poly = [(cx, drop_top)] + [(cx - r_drop * abs(math.sin(math.radians(a*180//40))),
                  drop_top + (drop_mid - drop_top - r_drop) * a/40)
                 for a in range(1, 41)] + \
               [(cx - r_drop, drop_mid)] + \
               [(cx + r_drop * math.sin(math.radians(a)), drop_mid + r_drop * (1-math.cos(math.radians(a)))) for a in range(0,181,6)] + \
               [(cx + r_drop, drop_mid)] + \
               [(cx + r_drop * abs(math.sin(math.radians(a*180//40))),
                 drop_top + (drop_mid - drop_top - r_drop) * (40-a)/40)
                for a in range(1, 41)]

    # Simpler teardrop
    pts = []
    for i in range(360):
        angle = math.radians(i)
        base_r = r_drop
        # Teardrop: compress top half
        if math.cos(angle) < 0:
            r_eff = base_r * (0.6 + 0.4 * abs(math.sin(angle)))
        else:
            r_eff = base_r
        px = cx + r_eff * math.sin(angle)
        py = drop_mid + r_eff * (-math.cos(angle)) * 0.85
        pts.append((px, py))
    # Extend top to a point
    top_pts = []
    for i in range(30, 151):
        angle = math.radians(i)
        frac = (i - 30) / 120
        # lerp from drop edge to tip
        edge_x = cx + r_drop * math.sin(math.radians(i))
        edge_y = drop_mid - r_drop
        tx, ty = cx, drop_top
        px = edge_x + (tx - edge_x) * frac
        py = edge_y + (ty - edge_y) * frac
        top_pts.append((px, py))

    # Use a clean teardrop polygon
    tear = []
    # Bottom semicircle
    for a in range(0, 181, 4):
        rad = math.radians(a)
        tear.append((cx + r_drop * math.sin(rad), drop_mid + r_drop * (1 - math.cos(rad)) * 0.6))
    # Right side to tip
    for a in range(40):
        frac = a / 40
        x0, y0 = cx + r_drop, drop_mid
        x1, y1 = cx, drop_top
        tear.append((x0 + (x1 - x0) * frac, y0 + (y1 - y0) * frac))
    # Left side from tip
    for a in range(40):
        frac = a / 40
        x0, y0 = cx, drop_top
        x1, y1 = cx - r_drop, drop_mid
        tear.append((x0 + (x1 - x0) * frac, y0 + (y1 - y0) * frac))

    d.polygon(tear, fill=(251, 191, 36, 242))

    # Highlight on drop
    hl_pts = []
    for a in range(20):
        frac = a / 20
        x0, y0 = cx - int(r_drop*0.55), drop_mid - int(r_drop*0.3)
        x1, y1 = cx - int(r_drop*0.25), drop_top + int((drop_mid - drop_top)*0.3)
        hl_pts.append((x0 + (x1-x0)*frac + int(s*0.015*math.sin(frac*math.pi)),
                       y0 + (y1-y0)*frac))
    d.line(hl_pts, fill=(255, 255, 255, 55), width=max(2, s//60))

    # ── Gear ring behind drop ──
    gear_cx, gear_cy = cx, drop_mid
    outer_r = int(s * 0.107)
    inner_r = int(s * 0.068)
    teeth = 8
    gear_color = (147, 197, 253, 140)

    d.ellipse([gear_cx - outer_r, gear_cy - outer_r,
               gear_cx + outer_r, gear_cy + outer_r],
              outline=gear_color, width=max(2, s//80))
    d.ellipse([gear_cx - inner_r, gear_cy - inner_r,
               gear_cx + inner_r, gear_cy + inner_r],
              outline=gear_color, width=max(2, s//80))

    tooth_w = int(s * 0.031)
    tooth_h = int(s * 0.039)
    for i in range(teeth):
        angle = math.radians(i * 360 / teeth)
        tx = gear_cx + int((outer_r + tooth_h//2) * math.cos(angle))
        ty = gear_cy + int((outer_r + tooth_h//2) * math.sin(angle))
        rect_pts = [
            (tx - tooth_w//2, ty - tooth_h//2),
            (tx + tooth_w//2, ty - tooth_h//2),
            (tx + tooth_w//2, ty + tooth_h//2),
            (tx - tooth_w//2, ty + tooth_h//2),
        ]
        # rotate teeth
        def rot(p, a, c):
            cs, sn = math.cos(a), math.sin(a)
            x = cs*(p[0]-c[0]) - sn*(p[1]-c[1]) + c[0]
            y = sn*(p[0]-c[0]) + cs*(p[1]-c[1]) + c[1]
            return (x, y)
        rpts = [rot(p, angle, (tx, ty)) for p in rect_pts]
        d.polygon(rpts, fill=gear_color)

    # ── "OIL" text ──
    text_y = int(s * 0.895)
    from PIL import ImageFont
    font_size = max(8, int(s * 0.115))
    try:
        from PIL import ImageFont
        font = ImageFont.truetype("arialbd.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", font_size)
        except:
            font = ImageFont.load_default()

    text = "OIL"
    bbox = d.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    d.text((cx - tw//2, text_y - font_size), text, font=font, fill=(251, 191, 36, 255))

    return img


# Generate all sizes
sizes = [256, 128, 64, 48, 32, 16]
images = []
output_dir = os.path.dirname(os.path.abspath(__file__))

for sz in sizes:
    img = draw_icon(sz)
    images.append(img)
    img.save(os.path.join(output_dir, f'icon_{sz}.png'))
    print(f'OK Generated {sz}x{sz}')

# Save as ICO (multi-size)
ico_path = os.path.join(output_dir, '..', 'app.ico')
images[0].save(
    ico_path,
    format='ICO',
    sizes=[(s, s) for s in sizes],
    append_images=images[1:]
)
print(f'OK Saved ICO: {ico_path}')

# Also save 256x256 PNG
png_path = os.path.join(output_dir, '..', 'app-icon.png')
images[0].save(png_path, 'PNG')
print(f'OK Saved PNG: {png_path}')
