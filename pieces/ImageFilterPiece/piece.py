from domino.base_piece import BasePiece
from .models import InputModel, OutputModel
from pathlib import Path
from PIL import Image
from io import BytesIO
from typing import List
import numpy as np
import base64
import os


filter_masks = {
    'sepia': ((0.393, 0.769, 0.189), (0.349, 0.686, 0.168), (0.272, 0.534, 0.131)),
    'black_and_white': ((0.333, 0.333, 0.333), (0.333, 0.333, 0.333), (0.333, 0.333, 0.333)),
    'brightness': ((1.4, 0, 0), (0, 1.4, 0), (0, 0, 1.4)),
    'darkness': ((0.6, 0, 0), (0, 0.6, 0), (0, 0, 0.6)),
    'contrast': ((1.2, 0.6, 0.6), (0.6, 1.2, 0.6), (0.6, 0.6, 1.2)),
    'red': ((1.6, 0, 0), (0, 1, 0), (0, 0, 1)),
    'green': ((1, 0, 0), (0, 1.6, 0), (0, 0, 1)),
    'blue': ((1, 0, 0), (0, 1, 0), (0, 0, 1.6)),
    'cool': ((0.9, 0, 0), (0, 1.1, 0), (0, 0, 1.3)),
    'warm': ((1.2, 0, 0), (0, 0.9, 0), (0, 0, 0.8)),
}

FILTER_FIELDS = [
    'sepia', 'black_and_white', 'brightness', 'darkness', 'contrast',
    'red', 'green', 'blue', 'cool', 'warm',
]


class ImageFilterPiece(BasePiece):

    def _load_image(self, input_image: str) -> Image.Image:
        max_path_size = int(os.pathconf('/', 'PC_PATH_MAX'))
        if len(input_image) < max_path_size and Path(input_image).exists() and Path(input_image).is_file():
            return Image.open(input_image)

        self.logger.info("Input is not a file path, decoding as base64 string")
        try:
            decoded_data = base64.b64decode(input_image)
        except Exception:
            raise ValueError("Input image is not a file path or a base64 encoded string")

        image_stream = BytesIO(decoded_data)
        # Verify, then rewind: Image.verify() consumes the stream.
        Image.open(image_stream).verify()
        image_stream.seek(0)
        return Image.open(image_stream)

    def _apply_filters(self, image: Image.Image, filter_names: List[str]) -> Image.Image:
        np_image = np.array(image, dtype=float)
        for filter_name in filter_names:
            np_mask = np.array(filter_masks[filter_name], dtype=float)
            for y in range(np_image.shape[0]):
                for x in range(np_image.shape[1]):
                    rgb = np_image[y, x, :3]
                    np_image[y, x, :3] = np.dot(np_mask, rgb)
            np_image = np.clip(np_image, 0, 255)

        return Image.fromarray(np_image.astype(np.uint8))

    def _build_composite_preview(self, images: List[Image.Image]) -> Image.Image:
        """Stack filtered images vertically into one preview, so the GUI shows the full batch."""
        if len(images) == 1:
            return images[0]
        max_width = max(img.width for img in images)
        total_height = sum(img.height for img in images)
        composite = Image.new("RGB", (max_width, total_height), color=(0, 0, 0))
        y_offset = 0
        for img in images:
            composite.paste(img.convert("RGB"), (0, y_offset))
            y_offset += img.height
        return composite

    def piece_function(self, input_data: InputModel):

        active_filters = [name for name in FILTER_FIELDS if getattr(input_data, name)]
        n = len(input_data.input_images)
        self.logger.info(f"Applying {active_filters} to {n} image(s)")

        modified_images: List[Image.Image] = []
        image_file_paths: List[str] = []
        image_base64_strings: List[str] = []

        for index, input_image in enumerate(input_data.input_images):
            self.logger.info(f"Processing image {index + 1}/{n}")
            image = self._load_image(input_image)
            modified_image = self._apply_filters(image, active_filters)
            modified_images.append(modified_image)

            if input_data.output_type in ("file", "both"):
                image_file_path = f"{self.results_path}/modified_image_{index}.png"
                modified_image.save(image_file_path)
                image_file_paths.append(image_file_path)

            if input_data.output_type in ("base64_string", "both"):
                buffered = BytesIO()
                modified_image.save(buffered, format="PNG")
                image_base64_strings.append(
                    base64.b64encode(buffered.getvalue()).decode('utf-8')
                )

        # display_result is a single dict (matches every other piece in this repo).
        # When N>1, render a vertical composite so the GUI shows the whole batch.
        composite_path = ""
        composite_b64 = ""
        if modified_images:
            composite = self._build_composite_preview(modified_images)
            composite_path = f"{self.results_path}/display_preview.png"
            composite.save(composite_path)
            buffered = BytesIO()
            composite.save(buffered, format="PNG")
            composite_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        self.display_result = {
            "file_type": "png",
            "base64_content": composite_b64,
            "file_path": composite_path,
        }

        return OutputModel(
            image_base64_strings=image_base64_strings,
            image_file_paths=image_file_paths,
        )
