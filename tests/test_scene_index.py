import copy
import csv
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest

from tools.build_scene_index import (
    film_stream, import_chapter_sweep, resource_id, scene_candidates, write_csv, write_json,
)


def film(sample=b"test"):
    header = struct.pack(">4sI4sI", b"FILM", 80, b"1.08", 0)
    descriptor = struct.pack(">4sI4sII12x", b"FDSC", 32, b"cvid", 224, 320)
    table = struct.pack(">4sIIIIIII", b"STAB", 32, 600, 1, 0, len(sample), 0, 1)
    return header + descriptor + table + sample


class SceneIndexTests(unittest.TestCase):
    def test_film_span_requires_descriptor_table_and_in_bounds_samples(self):
        stream = film()
        data = bytes(2048) + stream + bytes(2048)
        metadata = film_stream(data, 2048, 2048 + len(stream))
        self.assertEqual((metadata["byte_length"], metadata["width"], metadata["height"]),
                         (84, 320, 224))
        self.assertIsNone(film_stream(data, 2048, 2048 + len(stream) - 1))
        self.assertIsNone(film_stream(stream[:48] + b"FAIL" + stream[52:], 0, len(stream)))
        self.assertIsNone(film_stream(b"FILM" + bytes(80), 0, 84))

    def test_scene_candidates_keep_video_text_unknown_and_exact_table_association(self):
        path = "/S/0100TBL.BIN"
        sha = hashlib.sha256(b"test").hexdigest()
        first = {"disc": 1, "iso_path": path, "sha256": sha}
        second = {"disc": 2, "iso_path": "/S/0100.CPK", "sha256": sha}
        first["resource_id"] = resource_id(1, path, sha)
        second["resource_id"] = resource_id(2, second["iso_path"], sha)
        first["video_streams"] = []
        second["video_streams"] = [{"offset": 0, "sha256": sha}]
        key = f"1:{path}:9:0"
        scenes = scene_candidates([first, second], {(1, path): [{"record_key": key}]})
        dialogue, video = scenes
        self.assertEqual(dialogue["associated_record_keys"], [key])
        self.assertEqual(dialogue["tag"], "dialogo")
        self.assertEqual(dialogue["text_presence"], "unknown")
        self.assertEqual(video["tag"], "video")
        self.assertEqual(video["associated_record_keys"], [])
        self.assertIsNone(video["dialogue_table"])
        self.assertIsNone(video["wait_for_text"])
        self.assertEqual(video["zoom_eligibility"], "unknown")
        self.assertNotEqual(first["resource_id"], second["resource_id"])

    def sweep_fixture(self):
        sha = "a" * 64
        path = "/S/0100TBL.BIN"
        resource = {"disc": 2, "iso_path": path, "sha256": sha, "byte_length": 123, "lba": 10,
                    "format": "english_dialogue_table", "resource_id": resource_id(2, path, sha)}
        row = {
            "case": "bank-10-battle-1", "disc_on_continue": 2, "slot": 1,
            "episode_on_continue": "Finale", "bank_declared_episode": 10,
            "selection": {"tag": "menu", "evidence": {"frame": 2, "path": "case/menu.png", "sha256": sha}},
            "observed_scene": {"tag": "dialogo", "text_presence": "present",
                               "evidence": {"frame": 3, "path": "case/story.png", "sha256": sha}},
            "exact_resident_resources": [{"iso_path": path, "sha256": sha, "whole_file_equal": True,
                                          "bytes": 123, "equal_bytes": 123, "lba": 10}],
        }
        records = {(2, path): [{"record_key": f"2:{path}:9:0"}]}
        return row, resource, records

    def test_sweep_keeps_observed_menu_separate_and_uses_verified_table(self):
        row, resource, records = self.sweep_fixture()
        menu, dialogue = import_chapter_sweep([row], [resource], records)
        self.assertEqual(menu["scene_id"], "2:observation:chapter-sweep:bank-10-battle-1:selection")
        self.assertEqual(dialogue["scene_id"], "2:observation:chapter-sweep:bank-10-battle-1:dialogue")
        self.assertEqual(menu["tag"], "menu")
        self.assertIsNone(menu["dialogue_table"])
        self.assertEqual(dialogue["observed_episode"], "Finale")
        self.assertEqual(dialogue["dialogue_table"], resource["resource_id"])
        self.assertEqual(dialogue["text_presence"], "present")
        self.assertEqual(dialogue["associated_record_keys"],
                         [records[2, resource["iso_path"]][0]["record_key"]])
        self.assertEqual(dialogue["zoom_eligibility"], "unknown")

        with tempfile.TemporaryDirectory() as new:
            out = Path(new)
            write_json(out / "scene-index.json", [menu, dialogue])
            write_csv(out / "scene-index.csv", [menu, dialogue])
            json_rows = json.loads((out / "scene-index.json").read_text(encoding="utf-8"))
            with (out / "scene-index.csv").open(encoding="utf-8", newline="") as stream:
                csv_rows = list(csv.DictReader(stream))
            self.assertEqual(len(json_rows), len(csv_rows))
            for j, c in zip(json_rows, csv_rows):
                self.assertEqual(c["scene_id"], j["scene_id"])
                self.assertEqual(json.loads(c["associated_record_keys"]), j["associated_record_keys"])

    def test_sweep_rejects_unsupported_tags_or_unverified_evidence(self):
        original, resource, records = self.sweep_fixture()
        changes = [
            (("selection", "tag"), "transition"),
            (("selection", "evidence", "sha256"), "wrong"),
            (("selection", "evidence", "path"), "../foreign.png"),
            (("disc_on_continue",), 1),
            (("exact_resident_resources", 0, "iso_path"), "/S/0101TBL.BIN"),
            (("exact_resident_resources", 0, "sha256"), "b" * 64),
            (("exact_resident_resources", 0, "whole_file_equal"), False),
            (("exact_resident_resources", 0, "equal_bytes"), 122),
            (("observed_scene", "text_presence"), "unknown"),
        ]
        for keys, value in changes:
            row = copy.deepcopy(original)
            field = row
            for key in keys[:-1]:
                field = field[key]
            field[keys[-1]] = value
            with self.subTest(keys=keys), self.assertRaises(ValueError):
                import_chapter_sweep([row], [resource], records)

        with self.assertRaises(ValueError):
            import_chapter_sweep([original, original], [resource], records)

    def test_sweep_preserves_dialogue_without_guessing_from_table_or_episode(self):
        row, resource, records = self.sweep_fixture()
        row["exact_resident_resources"] = []
        menu, dialogue = import_chapter_sweep([row], [resource], records)
        self.assertEqual(dialogue["text_presence"], "present")
        self.assertEqual(dialogue["record_association"], "unknown")
        self.assertEqual(dialogue["associated_record_keys"], [])
        del row["observed_scene"]
        self.assertEqual(import_chapter_sweep([row], [resource], records), [menu])


if __name__ == "__main__":
    unittest.main()
