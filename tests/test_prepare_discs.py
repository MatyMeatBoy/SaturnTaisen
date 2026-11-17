import hashlib
from pathlib import Path
import tempfile
import unittest

from tools.prepare_discs import extract_mode1, parse_two_track_cue, write_audio_wav


def sector(value, mode=1):
    return bytes.fromhex('00ffffffffffffffffffff00') + b'\x00\x02\x00' + bytes([mode]) + bytes([value]) * 2048 + bytes(288)


class PrepareTests(unittest.TestCase):
    def test_preserves_user_bytes_and_source_with_spaces(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source = base / 'original [J] Track 1.bin'
            source.write_bytes(sector(31) + sector(42))
            before = hashlib.sha256(source.read_bytes()).digest()
            output = base / 'copy.iso'
            self.assertEqual(extract_mode1(source, output), 2)
            self.assertEqual(output.read_bytes(), bytes([31]) * 2048 + bytes([42]) * 2048)
            self.assertEqual(hashlib.sha256(source.read_bytes()).digest(), before)

    def test_rejects_truncated_sector(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory)
            (p / 'a.bin').write_bytes(sector(1)[:-1])
            with self.assertRaisesRegex(ValueError, '2352'):
                extract_mode1(p / 'a.bin', p / 'out.iso')
            self.assertFalse((p / 'out.iso').exists())

    def test_rejects_wrong_mode_and_removes_partial(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory)
            (p / 'a.bin').write_bytes(sector(1) + sector(2, mode=2))
            with self.assertRaisesRegex(ValueError, 'MODE1'):
                extract_mode1(p / 'a.bin', p / 'out.iso')
            self.assertFalse((p / 'out.iso').exists())

    def test_never_overwrites_existing_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory)
            (p / 'a.bin').write_bytes(sector(1))
            (p / 'out.iso').write_bytes(b'keep')
            with self.assertRaises(FileExistsError):
                extract_mode1(p / 'a.bin', p / 'out.iso')
            self.assertEqual((p / 'out.iso').read_bytes(), b'keep')

    def test_parse_cue_preserves_embedded_audio_pregap(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory)
            (p / 'data [1].bin').write_bytes(sector(1))
            (p / 'audio track.bin').write_bytes(bytes(151 * 2352))
            cue = p / 'disc.cue'
            cue.write_text('FILE "data [1].bin" BINARY\n TRACK 01 MODE1/2352\n INDEX 01 00:00:00\nFILE "audio track.bin" BINARY\n TRACK 02 AUDIO\n INDEX 00 00:00:00\n INDEX 01 00:02:00\n')
            data, audio, pregap = parse_two_track_cue(cue)
            self.assertEqual((data.name, audio.name, pregap), ('data [1].bin', 'audio track.bin', 150))

    def test_wav_does_not_include_embedded_pregap(self):
        import wave
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory)
            (p / 'audio.bin').write_bytes(bytes(150 * 2352) + b'\x01\x02\x03\x04' * 588)
            write_audio_wav(p / 'audio.bin', p / 'audio.wav', 150)
            with wave.open(str(p / 'audio.wav'), 'rb') as wav:
                self.assertEqual((wav.getnchannels(), wav.getsampwidth(), wav.getframerate(), wav.getnframes()), (2, 2, 44100, 588))
                self.assertEqual(wav.readframes(588), b'\x01\x02\x03\x04' * 588)


if __name__ == '__main__':
    unittest.main()
