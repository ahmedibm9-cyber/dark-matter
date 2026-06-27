from dm.audit.detectors.regex import (
    hardcoded_secrets,
    sql_injection,
    empty_catch,
    console_log,
    eval_usage,
    todo_without_ticket,
    insecure_compare,
)
from dm.audit.detectors.structural import todo_density

# evidence shape: {"kind": "file", "payload": {"content_preview": ..., "relative_path": ..., "extension": ..., "line_count": N}}


def _ev(content: str, ext: str = ".py") -> dict:
    return {
        "kind": "file",
        "payload": {
            "content_preview": content[:500],
            "relative_path": f"src/test{ext}",
            "extension": ext,
            "line_count": len(content.splitlines()),
        },
    }


class TestEvalUsage:
    def test_detects_eval(self):
        results = eval_usage(None, [_ev("eval('print(1)')")])
        assert len(results) == 1
        assert results[0].rule_id == "DM-REGEX-005"

    def test_skips_re_compile(self):
        results = eval_usage(None, [_ev("re.compile(r'pattern')")])
        assert len(results) == 0


class TestTodoWithoutTicket:
    def test_detects_comment_todo(self):
        results = todo_without_ticket(None, [_ev("# TODO: fix this")])
        assert len(results) == 1

    def test_skips_todo_in_string(self):
        results = todo_without_ticket(None, [_ev('name = "TODO Density"')])
        assert len(results) == 0

    def test_detects_js_comment_todo(self):
        results = todo_without_ticket(None, [_ev("// TODO: fix this", ".js")])
        assert len(results) == 1


class TestHardcodedSecrets:
    def test_detects_password(self):
        results = hardcoded_secrets(None, [_ev("password = 'supersecret'")])
        assert len(results) == 1
        assert results[0].severity == "high"

    def test_skips_example(self):
        results = hardcoded_secrets(None, [_ev("password = 'your_password_here'")])
        assert len(results) == 0


class TestSQLInjection:
    def test_detects_fstring_query(self):
        results = sql_injection(None, [_ev("cursor.execute(f'SELECT * FROM {table}')")])
        assert len(results) == 1
        assert results[0].severity == "high"

    def test_skips_safe_query(self):
        results = sql_injection(None, [_ev("cursor.execute('SELECT * FROM users')")])
        assert len(results) == 0


class TestEmptyCatch:
    def test_detects_except_pass(self):
        results = empty_catch(None, [_ev("try:\n    pass\nexcept:\n    pass")])
        assert len(results) == 1

    def test_detects_catch_empty(self):
        results = empty_catch(None, [_ev("try {\n  foo()\n} catch (e) {}", ".js")])
        assert len(results) >= 1


class TestConsoleLog:
    def test_detects_console_log(self):
        results = console_log(None, [_ev("console.log('hello')", ".js")])
        assert len(results) == 1
        assert results[0].rule_id == "DM-REGEX-004"

    def test_detects_print(self):
        results = console_log(None, [_ev("print('hello')")])
        assert len(results) == 1

    def test_fix_strategy_present(self):
        results = console_log(None, [_ev("console.log('x')", ".js")])
        assert results[0].fix_strategy is not None
        assert results[0].fix_strategy["action"] == "comment_out"


class TestInsecureCompare:
    def test_detects_password_eq(self):
        results = insecure_compare(None, [_ev("if password == 'secret':")])
        assert len(results) == 1

    def test_skips_normal_compare(self):
        results = insecure_compare(None, [_ev("if x == y:")])
        assert len(results) == 0


class TestTodoDensity:
    def test_high_density(self):
        content = "# TODO: fix\n" * 50
        results = todo_density(None, [_ev(content)])
        assert len(results) >= 1

    def test_no_todos(self):
        results = todo_density(None, [_ev("print('hello')\nprint('world')")])
        assert len(results) == 0
