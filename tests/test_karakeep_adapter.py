from __future__ import annotations

import json

from ipos.etl.karakeep import KarakeepClient


class CurrentKarakeepClient(KarakeepClient):
    def __init__(self) -> None:
        super().__init__(base_url="http://127.0.0.1:3000", api_key="test-key")

    def list_bookmarks(self, **kwargs):
        return (
            [
                {
                    "id": "bookmark-1",
                    "title": "Grounded source",
                    "note": json.dumps({"claims": []}),
                    "tags": [{"name": "macro"}],
                    "content": {
                        "type": "link",
                        "url": "https://example.com/research",
                    },
                    "assets": [],
                }
            ],
            None,
        )


def test_current_karakeep_link_url_is_preserved_in_drop(tmp_path):
    [drop_path] = CurrentKarakeepClient().fetch_tagged_evidence(
        destination_dir=tmp_path
    )

    drop = json.loads(drop_path.read_text(encoding="utf-8"))

    assert drop["url"] == "https://example.com/research"
    assert drop["custody_url"] == (
        "http://127.0.0.1:3000/dashboard/preview/bookmark-1"
    )
