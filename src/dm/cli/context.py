import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional


def build(repo_path: str) -> dict:
    repo = Path(repo_path).resolve()
    dm_dir = repo / ".darkmatter"
    ctx = {
        "project": {"name": repo.name, "root": str(repo)},
        "language": [],
        "frameworks": [],
        "entry_points": [],
        "dependencies": {},
        "dev_dependencies": {},
        "scripts": {},
        "env_vars": [],
        "test_config": {},
        "ci_config": {},
        "docker": {},
        "architecture": [],
        "file_counts": {"total": 0, "by_ext": {}},
        "conventions": [],
        "summary": "",
    }

    evidence_dir = dm_dir / "evidence"
    if not evidence_dir.exists():
        return ctx

    files = []
    for f in evidence_dir.glob("*.json"):
        try:
            rec = json.loads(f.read_text())
            files.append(rec)
        except (json.JSONDecodeError, OSError):
            continue

    content_map = {}
    for ev in files:
        p = ev.get("payload", {})
        rp = p.get("relative_path", "")
        content_map[rp] = {
            "content": p.get("content_preview", ""),
            "ext": p.get("extension", ""),
        }

    ctx["file_counts"]["total"] = len(files)

    for rp, info in content_map.items():
        ext = info["ext"]
        ctx["file_counts"]["by_ext"][ext] = ctx["file_counts"]["by_ext"].get(ext, 0) + 1
        content = info["content"]

        # detect language
        lang_map = {
            ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
            ".rs": "Rust", ".go": "Go", ".java": "Java", ".kt": "Kotlin",
            ".rb": "Ruby", ".php": "PHP", ".swift": "Swift",
            ".cs": "C#", ".c": "C", ".cpp": "C++", ".h": "C/C++ Header",
        }
        lang = lang_map.get(ext)
        if lang and lang not in ctx["language"]:
            ctx["language"].append(lang)

        # package.json
        if rp == "package.json":
            try:
                pkg = json.loads(content)
                ctx["project"]["name"] = pkg.get("name", ctx["project"]["name"])
                ctx["project"]["version"] = pkg.get("version", "")
                ctx["dependencies"].update(pkg.get("dependencies", {}))
                ctx["dev_dependencies"].update(pkg.get("devDependencies", {}))
                ctx["scripts"].update(pkg.get("scripts", {}))
                for dep in list(pkg.get("dependencies", {})) + list(pkg.get("devDependencies", {})):
                    fw = _detect_framework(dep)
                    if fw and fw not in ctx["frameworks"]:
                        ctx["frameworks"].append(fw)
            except json.JSONDecodeError:
                pass

        # pyproject.toml
        elif rp == "pyproject.toml":
            m = re.search(r'name\s*=\s*"([^"]+)"', content)
            if m:
                ctx["project"]["name"] = m.group(1)
            m = re.search(r'requires-python\s*=\s*"([^"]+)"', content)
            if m:
                ctx["project"]["python_version"] = m.group(1)
            for dep in re.finditer(r'([\w-]+)\s*[>=<]+\s*([^"\']+)', content):
                name = dep.group(1).strip()
                if name not in ("python", "setuptools"):
                    ctx["dependencies"][name] = dep.group(2).strip()
                    fw = _detect_framework(name)
                    if fw and fw not in ctx["frameworks"]:
                        ctx["frameworks"].append(fw)

        # requirements.txt
        elif rp == "requirements.txt":
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = re.split(r'[>=<~!]', line)
                    name = parts[0].strip()
                    if name:
                        ctx["dependencies"][name] = line
                        fw = _detect_framework(name)
                        if fw and fw not in ctx["frameworks"]:
                            ctx["frameworks"].append(fw)

        # Dockerfile
        elif rp == "Dockerfile" or "dockerfile" in rp.lower():
            ctx["docker"]["dockerfile"] = rp
            for m in re.finditer(r'FROM\s+(\S+)', content):
                ctx["docker"]["base_image"] = m.group(1)

        # docker-compose
        elif "docker-compose" in rp.lower():
            ctx["docker"]["compose"] = rp

        # .env.example
        elif rp.endswith(".env.example") or rp.endswith(".env.sample"):
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    var = line.split("=")[0].strip()
                    if var:
                        ctx["env_vars"].append(var)

        # Makefile
        elif rp == "Makefile" or rp == "makefile":
            for m in re.finditer(r'^(\w+):', content, re.MULTILINE):
                ctx["scripts"][m.group(1)] = f"make {m.group(1)}"

        # CI configs
        elif ".github/workflows/" in rp or ".gitlab-ci" in rp:
            ctx["ci_config"]["file"] = rp

        # entry points
        _check_entry_point(rp, ext, ctx)

        # test configs
        _check_test_config(rp, ext, content, ctx)

    # architecture from README
    readme = content_map.get("README.md", {}).get("content", "")
    if readme:
        ctx["summary"] = readme.strip()[:300]
        for arch in ["microservice", "monolith", "layered", "event-driven", "serverless", "mvc", "rest"]:
            if arch.lower() in readme.lower():
                ctx["architecture"].append(arch.capitalize())

    # build run command from scripts
    for cmd_name in ["start", "dev", "run", "serve"]:
        if cmd_name in ctx["scripts"]:
            ctx["project"]["run_command"] = ctx["scripts"][cmd_name]
            break

    # test command
    if ctx["test_config"].get("command"):
        ctx["project"]["test_command"] = ctx["test_config"]["command"]
    elif "test" in ctx["scripts"]:
        ctx["project"]["test_command"] = ctx["scripts"]["test"]

    return ctx


def _detect_framework(dep: str) -> Optional[str]:
    dep = dep.lower()
    fw_map = {
        "express": "Express.js", "react": "React", "next": "Next.js",
        "django": "Django", "flask": "Flask", "fastapi": "FastAPI",
        "spring": "Spring", "rails": "Ruby on Rails", "laravel": "Laravel",
        "vue": "Vue.js", "angular": "Angular", "svelte": "Svelte",
        "jwt": "JWT", "redis": "Redis", "jest": "Jest",
        "pytest": "pytest", "sqlalchemy": "SQLAlchemy", "tensorflow": "TensorFlow",
        "torch": "PyTorch", "ruff": "Ruff", "black": "Black",
        "mypy": "mypy", "typer": "Typer", "click": "Click",
        "httpx": "HTTPX", "requests": "Requests", "aiohttp": "aiohttp",
    }
    for key, name in fw_map.items():
        if key in dep:
            return name
    return None


def _check_entry_point(rp: str, ext: str, ctx: dict):
    name = Path(rp).stem.lower()
    entry_names = {"main", "app", "index", "cli", "server", "api", "bot", "run", "start"}
    if name in entry_names and ext in (".py", ".js", ".ts", ".go", ".rs", ".rb"):
        ctx["entry_points"].append(rp)


def _check_test_config(rp: str, ext: str, content: str, ctx: dict):
    if rp == "pyproject.toml":
        m = re.search(r'test\s*=\s*"([^"]+)"', content)
        if m:
            ctx["test_config"]["command"] = m.group(1)
    elif rp == "package.json":
        if "test" in json.loads(content).get("scripts", {}):
            ctx["test_config"]["command"] = "npm test"
            ctx["test_config"]["framework"] = "jest" if "jest" in content else "node"
    elif rp == "Makefile" or rp == "makefile":
        if re.search(r'^test:', content, re.MULTILINE):
            ctx["test_config"]["command"] = "make test"
    elif rp.endswith("conftest.py"):
        ctx["test_config"]["framework"] = "pytest"
    elif rp == "jest.config.js" or rp == "jest.config.ts":
        ctx["test_config"]["framework"] = "jest"


def format_prompt(ctx: dict) -> str:
    lines = []
    lines.append("# Project Context — autogenerated by Dark Matter")
    lines.append("")
    lines.append(f"Project: {ctx['project'].get('name', 'unknown')}")
    if ctx.get("summary"):
        lines.append(f"Summary: {ctx['summary'][:200]}")
    lines.append("")

    if ctx.get("language"):
        lines.append(f"Languages: {', '.join(ctx['language'])}")
    if ctx.get("frameworks"):
        lines.append(f"Frameworks: {', '.join(ctx['frameworks'])}")
    lines.append("")

    if ctx.get("entry_points"):
        lines.append("Key entry points:")
        for ep in ctx["entry_points"]:
            lines.append(f"  {ep}")
        lines.append("")

    run_cmd = ctx.get("project", {}).get("run_command")
    test_cmd = ctx.get("project", {}).get("test_command")
    if run_cmd:
        lines.append(f"Run: {run_cmd}")
    if test_cmd:
        lines.append(f"Test: {test_cmd}")
    lines.append("")

    if ctx.get("dependencies"):
        lines.append(f"Top dependencies ({min(15, len(ctx['dependencies']))} shown):")
        for i, (name, ver) in enumerate(sorted(ctx["dependencies"].items())):
            if i >= 15:
                break
            lines.append(f"  {name}: {ver}")
        lines.append("")

    if ctx.get("env_vars"):
        lines.append(f"Environment variables ({len(ctx['env_vars'])}):")
        for var in sorted(ctx["env_vars"])[:10]:
            lines.append(f"  {var}")
        if len(ctx["env_vars"]) > 10:
            lines.append(f"  ... and {len(ctx['env_vars']) - 10} more")
        lines.append("")

    if ctx.get("architecture"):
        lines.append(f"Architecture: {', '.join(ctx['architecture'])}")
        lines.append("")

    fc = ctx.get("file_counts", {})
    if fc.get("by_ext"):
        lines.append("File breakdown:")
        for ext, count in sorted(fc["by_ext"].items(), key=lambda x: -x[1])[:8]:
            lines.append(f"  {ext or '(no ext)'}: {count}")
        lines.append("")

    lines.append("---")
    lines.append("Read this context before making changes. Follow existing")
    lines.append("patterns. Run `dm audit -p --severity high` before shipping.")
    return "\n".join(lines)


def format_json(ctx: dict) -> str:
    return json.dumps(ctx, indent=2, default=str)
