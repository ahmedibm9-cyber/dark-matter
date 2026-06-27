import tempfile
from pathlib import Path
from dm.audit.models import Finding
from dm.audit.fixer import apply_fix, apply_all


class TestApplyFix:
    def test_comment_out_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "test.py"
            f.write_text("print('hello')\nconsole.log('x')\nprint('bye')\n")
            finding = Finding(
                rule_id="DM-REGEX-004",
                severity="low",
                file="test.py",
                line=2,
                description="debug",
                confidence=0.6,
                fix_strategy={"action": "comment_out", "line": 2},
            )
            ok = apply_fix(finding, tmp)
            assert ok
            content = f.read_text()
            assert "# console.log('x')" in content

    def test_remove_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "test.py"
            f.write_text("line1\nbadline\nline3\n")
            finding = Finding(
                rule_id="DM-TEST",
                severity="high",
                file="test.py",
                line=2,
                description="bad",
                confidence=1.0,
                fix_strategy={"action": "remove_line", "line": 2},
            )
            ok = apply_fix(finding, tmp)
            assert ok
            assert f.read_text() == "line1\nline3\n"

    def test_replace_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "test.py"
            f.write_text("password = 'secret'\n")
            finding = Finding(
                rule_id="DM-TEST",
                severity="high",
                file="test.py",
                line=1,
                description="secret",
                confidence=1.0,
                fix_strategy={"action": "replace_text", "old": "'secret'", "new": "os.getenv('PASSWORD')"},
            )
            ok = apply_fix(finding, tmp)
            assert ok
            assert "os.getenv('PASSWORD')" in f.read_text()

    def test_no_fix_strategy(self):
        finding = Finding(
            rule_id="DM-TEST", severity="info", file="x.py", line=1,
            description="test", confidence=0.5,
        )
        assert not apply_fix(finding, ".")


class TestApplyAll:
    def test_fixed_and_failed_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "test.py"
            f.write_text("print('a')\nprint('b')\n")
            findings = [
                Finding(
                    rule_id="DM-REGEX-004", severity="low", file="test.py",
                    line=1, description="x", confidence=0.6,
                    fix_strategy={"action": "comment_out", "line": 1},
                ),
                Finding(
                    rule_id="DM-REGEX-004", severity="low", file="test.py",
                    line=2, description="x", confidence=0.6,
                    fix_strategy={"action": "comment_out", "line": 2},
                ),
            ]
            fixed, failed = apply_all(findings, tmp)
            assert fixed == 2
            assert failed == 0
