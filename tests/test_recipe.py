import hashlib
import tempfile
import unittest
from pathlib import Path
import recipe


class RecipeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.a = self.root / 'mount_a'
        self.b = self.root / 'mount_b'
        self.a.mkdir()
        self.b.mkdir()
        self.manifest = {'total_bytes': 6, 'files': [
            {'path': 'Q2_K/one.gguf', 'size': 3, 'sha256': hashlib.sha256(b'abc').hexdigest()},
            {'path': 'Q2_K/two.gguf', 'size': 3, 'sha256': hashlib.sha256(b'def').hexdigest()}]}

    def test_missing_and_cross_mount(self):
        (self.a / 'one.gguf').write_bytes(b'abc')
        report, found = recipe.inspect(self.manifest, [self.a, self.b], False)
        self.assertFalse(report['ok'])
        (self.b / 'two.gguf').write_bytes(b'def')
        report, found = recipe.inspect(self.manifest, [self.a, self.b], True)
        self.assertTrue(report['ok'])
        self.assertEqual(len(found), 2)

    def test_size_and_hash_mismatch(self):
        (self.a / 'one.gguf').write_bytes(b'abc')
        (self.b / 'two.gguf').write_bytes(b'bad')
        self.assertFalse(recipe.inspect(self.manifest, [self.a, self.b], True)[0]['ok'])
        (self.b / 'two.gguf').write_bytes(b'bad length')
        self.assertFalse(recipe.inspect(self.manifest, [self.a, self.b], False)[0]['ok'])

    def test_duplicate_is_ambiguous(self):
        (self.a / 'one.gguf').write_bytes(b'abc')
        (self.b / 'one.gguf').write_bytes(b'abc')
        self.assertIn('ambiguous', recipe.inspect(self.manifest, [self.a, self.b], False)[0]['files'][0]['status'])

    def test_view_is_symlink_only_and_no_overwrite(self):
        (self.a / 'one.gguf').write_bytes(b'abc')
        (self.b / 'two.gguf').write_bytes(b'def')
        report, found = recipe.inspect(self.manifest, [self.a, self.b], True)
        out = self.root / 'view'
        recipe.make_view(found, out)
        self.assertTrue((out / 'one.gguf').is_symlink())
        self.assertEqual((out / 'two.gguf').read_bytes(), b'def')
        with self.assertRaises(FileExistsError):
            recipe.make_view(found, out)

    def test_no_partial_view_on_missing(self):
        out = self.root / 'view'
        with self.assertRaises(ValueError):
            recipe.make_view({}, out)
        self.assertFalse(out.exists())

    def test_launch_is_loopback_and_small_context(self):
        cmd = recipe.server_command('/bin/llama-server', '/models/one.gguf', 2048, 2, 8080)
        self.assertIn('127.0.0.1', cmd)
        self.assertEqual(cmd[cmd.index('--ctx-size') + 1], '2048')
        self.assertNotIn('--no-mmap', cmd)

    def test_model_manifest(self):
        m = recipe.load_manifest()
        self.assertEqual(len(m['files']), 10)
        self.assertEqual(m['total_bytes'], 264515416800)
        self.assertEqual(sum(f['size'] for f in m['files']), m['total_bytes'])
        self.assertEqual(len(m['revision']), 40)


if __name__ == '__main__':
    unittest.main()
