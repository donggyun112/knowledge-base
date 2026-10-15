import hashlib
import tempfile
import unittest
from pathlib import Path
from scripts.export_notes import sanitize_note, export_notes


class ExportTests(unittest.TestCase):
    def test_private_section_preserves_source(self):
        text = '# Note\n## 8. 우리 맥락(인포뱅크) 활용 아이디어\nprivate\n### Detail\nsecret\n## 출처\nhttps://example.org\n'
        actual = sanitize_note(text)
        self.assertNotIn('private', actual)
        self.assertNotIn('secret', actual)
        self.assertIn('## 출처', actual)

    def test_fenced_heading_and_code_links_preserved(self):
        text = '# Note\n```md\n## 우리 맥락\n[[example]]\n```\n## 출처\nsource\n'
        self.assertEqual(sanitize_note(text), text)

    def test_tilde_fence_and_general_company_reference(self):
        text = '# Note\n~~~md\n## 우리 맥락\nexample\n~~~\n## 배경\nCerebras 사내 검색\n'
        self.assertEqual(sanitize_note(text), text)

    def test_generic_personal_application_section_removed(self):
        text = '# Note\n## 활용 아이디어\nportfolio strategy\n## 출처\nsource\n'
        self.assertNotIn('portfolio strategy', sanitize_note(text))

    def test_export_exclusion_deletion_and_source_unchanged(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); src = root/'source'; dst = root/'content'; src.mkdir(); dst.mkdir()
            (src/'note.md').write_text('---\ntitle: 테스트\nresearched: 2026-10-01\n---\n# Note\n## 우리 맥락\nsecret\n## 출처\nsource\n')
            (src/'non-research-links.md').write_text('private shopping')
            (src/'INDEX.md').write_text('# Index\n- [[note|Note]]\n- [[non-research-links|private]]\n')
            (dst/'stale.md').write_text('obsolete')
            before = hashlib.sha256((src/'note.md').read_bytes()).hexdigest()
            report = export_notes(src, dst)
            self.assertFalse((dst/'stale.md').exists())
            self.assertFalse((dst/'non-research-links.md').exists())
            self.assertNotIn('secret', (dst/'note.md').read_text())
            self.assertNotIn('non-research-links', (dst/'research-index.md').read_text())
            self.assertIn('[[note|Note]]', (dst/'research-index.md').read_text())
            self.assertIn('research-index', (dst/'index.md').read_text())
            self.assertIn('researched: 2026-10-01', (dst/'note.md').read_text())
            self.assertEqual(before, hashlib.sha256((src/'note.md').read_bytes()).hexdigest())
            self.assertIn('note.md', report['exported'])

    def test_unsafe_paths_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            src = Path(temp)/'source'; src.mkdir()
            for dst in [src, src/'nested', src.parent]:
                with self.assertRaises(ValueError): export_notes(src, dst)

    def test_symlink_refused_without_touching_destination(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); src=root/'source'; src.mkdir(); dst=root/'content'; dst.mkdir()
            (root/'secret.md').write_text('secret'); (src/'linked.md').symlink_to(root/'secret.md')
            (dst/'keep.md').write_text('keep')
            with self.assertRaises(ValueError): export_notes(src, dst)
            self.assertEqual((dst/'keep.md').read_text(), 'keep')


if __name__ == '__main__': unittest.main()
