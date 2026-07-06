"""赛博判官应用图标生成器 - 运行此脚本生成图标"""
import os
from PIL import Image, ImageDraw, ImageFont

def generate_icon(output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), "..", "resources")
    os.makedirs(output_dir, exist_ok=True)
    size = 512
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    gold = (212, 175, 55); lw = 6

    draw.ellipse([20, 20, size-20, size-20], fill=(26, 42, 74))
    beam_y = cy - 30; cl, cr = cx-100, cx+100; pan_y = cy + 20; pw = 60
    draw.line([cl, beam_y, cr, beam_y], fill=gold, width=lw)
    draw.line([cx, cy-90, cx-15, beam_y], fill=gold, width=lw)
    draw.line([cx, cy-90, cx+15, beam_y], fill=gold, width=lw)
    draw.ellipse([cx-10, cy-100, cx+10, cy-80], fill=gold)
    draw.line([cl, beam_y, cl, pan_y], fill=gold, width=lw-1)
    draw.line([cr, beam_y, cr, pan_y], fill=gold, width=lw-1)
    draw.line([cl-pw//2, pan_y, cl+pw//2, pan_y], fill=gold, width=lw)
    draw.line([cr-pw//2, pan_y, cr+pw//2, pan_y], fill=gold, width=lw)

    png = os.path.join(output_dir, "icon.png"); img.save(png, "PNG"); print(f"PNG: {png}")
    ico = os.path.join(output_dir, "icon.ico")
    ss = [(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)]
    imgs = [img.resize(s, Image.LANCZOS) for s in ss]
    imgs[0].save(ico, format="ICO", sizes=ss); print(f"ICO: {ico}")

if __name__ == "__main__":
    generate_icon()