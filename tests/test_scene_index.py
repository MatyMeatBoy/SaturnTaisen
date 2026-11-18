import hashlib
import struct
import unittest

from tools.build_scene_index import film_stream, resource_id, scene_candidates


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


if __name__ == "__main__":
    unittest.main()
