"""Génère assets/camera.ico (logo caméra pour l'application)."""
from pathlib import Path

from PIL import Image, ImageDraw

ASSETS = Path(__file__).resolve().parent / "assets"
ASSETS.mkdir(exist_ok=True)


def draw_camera(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    m = size / 256
    bg = (38, 42, 48, 255)
    body = (66, 133, 244, 255)
    lens_outer = (28, 30, 34, 255)
    lens_inner = (120, 190, 255, 255)

    draw.ellipse(
        (int(16 * m), int(16 * m), int(240 * m), int(240 * m)),
        fill=bg,
    )
    draw.rounded_rectangle(
        (int(52 * m), int(88 * m), int(204 * m), int(178 * m)),
        radius=int(14 * m),
        fill=body,
    )
    draw.rounded_rectangle(
        (int(118 * m), int(62 * m), int(168 * m), int(92 * m)),
        radius=int(8 * m),
        fill=body,
    )
    draw.ellipse(
        (int(100 * m), int(108 * m), int(156 * m), int(164 * m)),
        fill=lens_outer,
    )
    draw.ellipse(
        (int(112 * m), int(120 * m), int(144 * m), int(152 * m)),
        fill=lens_inner,
    )
    draw.ellipse(
        (int(168 * m), int(98 * m), int(188 * m), int(118 * m)),
        fill=(220, 230, 245, 255),
    )
    return img


def main():
    base = draw_camera(256)
    ico_path = ASSETS / "camera.ico"
    base.save(
        ico_path,
        format="ICO",
        sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)],
    )
    base.save(ASSETS / "camera.png", format="PNG")
    print(f"Icône créée : {ico_path}")


if __name__ == "__main__":
    main()
