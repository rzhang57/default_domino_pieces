from domino.testing import piece_dry_run
from pathlib import Path
from PIL import Image
from io import BytesIO
import base64


img_path = str(Path(__file__).parent / "test_image.png")
img = Image.open(img_path)
buffered = BytesIO()
img.save(buffered, format="PNG")
image_bytes = buffered.getvalue()
base64_image = base64.b64encode(image_bytes).decode("utf-8")


def test_imagefilterpiece():
    input_data = dict(
        input_images=[base64_image, base64_image],
        sepia=True,
        blue=True,
        output_type="both"
    )
    piece_output = piece_dry_run(
        piece_name="ImageFilterPiece",
        input_data=input_data
    )
    assert piece_output is not None
    file_paths = piece_output.get('image_file_paths')
    base64_strings = piece_output.get('image_base64_strings')
    assert isinstance(file_paths, list)
    assert isinstance(base64_strings, list)
    assert len(file_paths) == 2
    assert len(base64_strings) == 2
    for path in file_paths:
        assert path.endswith('.png')
