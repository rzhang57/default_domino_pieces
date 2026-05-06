from domino.testing import piece_dry_run


def test_pagescrapper():
    input_data = dict(
        url="https://example.com",
        search_items=[
            dict(tag="h1", class_name=""),
            dict(tag="p", class_name=""),
        ]
    )
    piece_output = piece_dry_run(
        piece_name="PageScrapperPiece",
        input_data=input_data
    )
    text = piece_output["scrapped_text"].lower()
    assert "example domain" in text, "PageScrapperPiece failed to scrap the h1"
    assert "documentation examples" in text, "PageScrapperPiece failed to scrap the p tags"
