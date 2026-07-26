from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


def rounded_box(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str, font: ImageFont.ImageFont, fill: str = "#ffffff") -> None:
    draw.rounded_rectangle(box, radius=24, fill=fill, outline="#335c81", width=3)
    text_box = draw.multiline_textbbox((0, 0), text, font=font, spacing=6, align="center")
    text_w = text_box[2] - text_box[0]
    text_h = text_box[3] - text_box[1]
    x0, y0, x1, y1 = box
    draw.multiline_text(
        ((x0 + x1 - text_w) / 2, (y0 + y1 - text_h) / 2 - 2),
        text,
        font=font,
        fill="#17324d",
        spacing=6,
        align="center",
    )


def arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int]) -> None:
    draw.line([start, end], fill="#4f6d8a", width=4)
    ex, ey = end
    sx, sy = start
    dx = ex - sx
    dy = ey - sy
    if abs(dx) > abs(dy):
        left = (ex - 16, ey - 8)
        right = (ex - 16, ey + 8)
        if dx < 0:
            left = (ex + 16, ey - 8)
            right = (ex + 16, ey + 8)
    else:
        left = (ex - 8, ey - 16)
        right = (ex + 8, ey - 16)
        if dy < 0:
            left = (ex - 8, ey + 16)
            right = (ex + 8, ey + 16)
    draw.polygon([end, left, right], fill="#4f6d8a")


def main() -> None:
    output = ROOT / "artifacts" / "figures" / "scalability_architecture.png"
    output.parent.mkdir(parents=True, exist_ok=True)

    width, height = 2400, 1600
    image = Image.new("RGBA", (width, height), "#ffffff")
    draw = ImageDraw.Draw(image)

    title_font = load_font(44)
    box_font = load_font(34)
    caption_font = load_font(26)

    title = "Proposed Entity-Partitioned Production Evolution"
    title_box = draw.textbbox((0, 0), title, font=title_font)
    draw.text(((width - (title_box[2] - title_box[0])) / 2, 40), title, font=title_font, fill="#17324d")

    rounded_box(draw, (700, 130, 1700, 250), "Authentication / Access /\nDevice Events", box_font)
    rounded_box(draw, (760, 340, 1640, 460), "Entity-Keyed Event Stream", box_font, fill="#eef5fb")
    rounded_box(draw, (140, 560, 640, 670), "Partition 1", box_font)
    rounded_box(draw, (950, 560, 1450, 670), "Partition 2", box_font)
    rounded_box(draw, (1760, 560, 2260, 670), "Partition 3", box_font)
    rounded_box(draw, (140, 800, 640, 920), "Scoring Worker", box_font, fill="#f7fbff")
    rounded_box(draw, (950, 800, 1450, 920), "Scoring Worker", box_font, fill="#f7fbff")
    rounded_box(draw, (1760, 800, 2260, 920), "Scoring Worker", box_font, fill="#f7fbff")
    rounded_box(draw, (700, 1050, 1700, 1180), "Shared Profile Store", box_font, fill="#eef5fb")
    rounded_box(draw, (820, 1240, 1580, 1350), "Ranked Alert Store", box_font)
    rounded_box(draw, (900, 1390, 1500, 1500), "Analyst Dashboard", box_font, fill="#f7fbff")

    arrow(draw, (1200, 250), (1200, 340))
    arrow(draw, (1200, 460), (390, 560))
    arrow(draw, (1200, 460), (1200, 560))
    arrow(draw, (1200, 460), (2010, 560))
    arrow(draw, (390, 670), (390, 800))
    arrow(draw, (1200, 670), (1200, 800))
    arrow(draw, (2010, 670), (2010, 800))
    arrow(draw, (390, 920), (900, 1050))
    arrow(draw, (1200, 920), (1200, 1050))
    arrow(draw, (2010, 920), (1500, 1050))
    arrow(draw, (1200, 1180), (1200, 1240))
    arrow(draw, (1200, 1350), (1200, 1390))

    caption = (
        "Proposed entity-partitioned production evolution of AegisUEBA. "
        "Distributed components are architectural extensions and are not implemented in the current prototype."
    )
    caption_width = 2100
    words = caption.split()
    lines: list[str] = []
    current = []
    for word in words:
        trial = " ".join(current + [word])
        trial_box = draw.textbbox((0, 0), trial, font=caption_font)
        if trial_box[2] - trial_box[0] <= caption_width:
            current.append(word)
        else:
            lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))

    draw.multiline_text((150, 1520), "\n".join(lines), font=caption_font, fill="#263b52", spacing=6, align="center")
    image.save(output)


if __name__ == "__main__":
    main()
