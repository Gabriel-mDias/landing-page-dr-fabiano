"""Build conservative, publication-ready image derivatives from approved originals."""

from pathlib import Path

from PIL import Image, ImageFilter, ImageOps


ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "media"
OUTPUT = ROOT / "public" / "assets"


def prepare(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Resize without generative reconstruction and add restrained output sharpening."""
    image = ImageOps.exif_transpose(image)
    resized = image.resize(size, Image.Resampling.LANCZOS)
    return resized.filter(ImageFilter.UnsharpMask(radius=0.8, percent=52, threshold=4))


def save_responsive(source: Path, name: str, widths: tuple[int, ...]) -> None:
    with Image.open(source) as original:
        original.load()
        ratio = original.height / original.width
        for width in widths:
            size = (width, round(width * ratio))
            image = prepare(original, size)
            image.save(
                OUTPUT / "images" / f"{name}-{width}.avif",
                quality=67,
                speed=5,
            )
            image.save(
                OUTPUT / "images" / f"{name}-{width}.webp",
                quality=88,
                method=6,
            )


def clean_alpha(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A").point(lambda value: 0 if value < 8 else value)
    rgba.putalpha(alpha)
    return rgba


def save_logos() -> None:
    with Image.open(MEDIA / "Logo" / "logo.png") as supplied:
        logo = clean_alpha(supplied)
        content = logo.getchannel("A").point(lambda value: 255 if value >= 8 else 0).getbbox()
        if content is None:
            raise ValueError("The supplied logo has no visible pixels")
        full = logo.crop(content)
        full.thumbnail((1200, 840), Image.Resampling.LANCZOS)
        full.save(OUTPUT / "logo" / "logo-full.png", optimize=True)

        # The monogram occupies the upper portion of the supplied composition.
        icon = logo.crop((300, 190, 1090, 850))
        icon_bbox = icon.getchannel("A").point(lambda value: 255 if value >= 8 else 0).getbbox()
        if icon_bbox is None:
            raise ValueError("The supplied logo has no visible monogram")
        icon = icon.crop(icon_bbox)
        canvas = Image.new("RGBA", (640, 640), (0, 0, 0, 0))
        icon.thumbnail((570, 570), Image.Resampling.LANCZOS)
        canvas.alpha_composite(icon, ((640 - icon.width) // 2, (640 - icon.height) // 2))
        canvas.save(OUTPUT / "logo" / "logo-icon.png", optimize=True)


def main() -> None:
    (OUTPUT / "images").mkdir(parents=True, exist_ok=True)
    (OUTPUT / "logo").mkdir(parents=True, exist_ok=True)

    sources = (
        (MEDIA / "Profissional" / "fabiano_1.png", "fabiano-retrato", (640, 960, 1280)),
        (MEDIA / "Profissional" / "fabiano_2.png", "fabiano-cirurgia", (640, 960, 1280)),
        (MEDIA / "Profissional" / "fabiano_3.png", "fabiano-perfil", (640, 960, 1280)),
        (MEDIA / "Espaço" / "espaco_1.png", "adriele-recepcao", (640, 960, 1280)),
        (MEDIA / "Espaço" / "espaco_2.png", "consultorio-recepcao", (640, 960, 1280)),
        (MEDIA / "Espaço" / "espaco_3.png", "adriele-consultorio", (640, 960, 1280)),
        (
            MEDIA / "Instagram" / "ia_generated_1" / "tratamento_fisioterapeutico_1.jpg",
            "fisioterapia-conceitual",
            (640, 960, 1280, 1600),
        ),
    )
    for source, name, widths in sources:
        save_responsive(source, name, widths)

    # The approved poster is an extracted frame; retain framing and apply only
    # conservative resampling/sharpening for high-density displays.
    with Image.open(OUTPUT / "images" / "hero-poster.webp") as poster:
        poster = prepare(poster.convert("RGB"), (1200, 2133))
        poster.save(OUTPUT / "images" / "hero-poster-1200.avif", quality=68, speed=5)
        poster.save(OUTPUT / "images" / "hero-poster-1200.webp", quality=89, method=6)

    save_logos()


if __name__ == "__main__":
    main()
