from dm.audit.models import Finding


class TestFinding:
    def test_required_fields(self):
        f = Finding(
            rule_id="DM-TEST-001",
            severity="high",
            file="src/main.py",
            line=42,
            description="Something bad",
            confidence=0.95,
        )
        assert f.rule_id == "DM-TEST-001"
        assert f.severity == "high"
        assert f.file == "src/main.py"
        assert f.line == 42
        assert f.confidence == 0.95
        assert f.suggested_fix is None
        assert f.evidence_ref is None
        assert f.fix_strategy is None

    def test_optional_fields(self):
        f = Finding(
            rule_id="DM-TEST-002",
            severity="low",
            file="test.py",
            line=1,
            description="test",
            confidence=0.5,
            suggested_fix="Remove it",
            evidence_ref="ev-001",
            fix_strategy={"action": "remove_line", "line": 1},
        )
        assert f.suggested_fix == "Remove it"
        assert f.evidence_ref == "ev-001"
        assert f.fix_strategy["action"] == "remove_line"

    def test_severity_values(self):
        for sev in ("critical", "high", "medium", "low", "info"):
            f = Finding(
                rule_id="DM-TEST", severity=sev, file="x.py", line=1,
                description="test", confidence=0.5,
            )
            assert f.severity == sev
