#!/usr/bin/env python3
"""Rotates the daily block in README.md. Deterministic per UTC day, stdlib only."""
import datetime, pathlib, re, sys

README = pathlib.Path(__file__).resolve().parents[2] / "README.md"
START, END = "<!-- DAILY:START -->", "<!-- DAILY:END -->"
U = "https://github.com/Amithkrishna29z"

# (repo, display name, one-line pitch, badge slugs)
ROULETTE = [
    ("SLangJava", "SLangJava", "A compiler, ported. 174 tests say it agrees with the original everywhere.", "Java · ANTLR"),
    ("mini-rate-limiter", "mini-rate-limiter", "Token bucket, thread-safe, small enough to read in one sitting.", "Java · JUnit 5"),
    ("jython-plugin-engine", "jython-plugin-engine", "A Python runtime living inside a JVM app, hot-loading plugins.", "Java · Jython"),
    ("java-byteCode-engineering", "java-byteCode-engineering", "Rewriting classes after javac has already had its say.", "Java · ASM"),
    ("java-jni", "java-jni", "Crossing the JVM/native boundary, on purpose.", "Java · C"),
    ("dotnet-seat-wave", "dotnet-seat-wave", "A seat engine that refuses to double-book under load.", ".NET 8 · SignalR"),
    ("documind-multi-agent-document-intelligence", "documind", "RAG that grades its own retrieval and backs out when context is weak.", "LangGraph · FastAPI"),
    ("springcli", "springcli", "Scaffolds Spring Boot projects without opening a browser.", "Java 21 · Picocli"),
    ("linux-internals", "linux-internals", "Notes from reading the parts of the OS you normally just trust.", "C · Linux"),
    ("rust-todo-api", "rust-todo-api", "The smallest possible excuse to fight the borrow checker.", "Rust · Axum"),
    ("python-google-search-mcp-server", "google-search-mcp", "An MCP server, so a model can go look things up itself.", "Python · MCP"),
    ("java-CompletableFuture", "java-CompletableFuture", "Async composition in Java, without the callback pyramid.", "Java · Concurrency"),
    ("connect-c-to-sqlite", "connect-c-to-sqlite", "Talking to SQLite from C — and the repo that ruins my language stats.", "C · SQLite"),
    ("tiny-c-plus-plus", "tiny-c-plus-plus", "C++ kept deliberately small.", "C++"),
    ("design-patterns", "design-patterns", "The classics, written out until they stopped being vocabulary.", "Java"),
]

# Things I actually believe, rotated one per day.
LESSONS = [
    "A test that has never failed has never told you anything.",
    "If two components disagree about who owns a piece of state, you have a bug — you just haven't reproduced it yet.",
    "`SERIALIZABLE` is not slow. Retrying a doomed transaction forty times is slow.",
    "The hardest part of porting a compiler is discovering which parts of the spec were never really decided.",
    "Every cache is a correctness bug waiting for enough traffic.",
    "Logs you only read during an incident are logs you designed during an incident.",
    "An abstraction with exactly one implementation is a rename with extra steps.",
    "If the retry has no jitter, you did not build a retry — you built a thundering herd.",
    "Reading someone else's stack trace properly is faster than writing your own print statement. It never feels that way.",
    "A RAG system that can't say \"I don't know\" is a confident liar with citations.",
    "Concurrency bugs are just race conditions you were lucky about in testing.",
    "`git bisect` has found more of my bugs than my intuition has.",
    "The bug is in the code you didn't think was involved. It is always in that code.",
    "A build that only works on your machine is a personality trait, not a deliverable.",
    "If it needs a comment explaining *what*, rename it. If it needs one explaining *why*, keep it forever.",
]


def render(day: datetime.date) -> str:
    n = day.toordinal()
    slug, name, pitch, stack = ROULETTE[n % len(ROULETTE)]
    lesson = LESSONS[(n * 7) % len(LESSONS)]
    return "\n".join([
        START,
        "",
        "<table><tr><td width=\"55%\" valign=\"top\">",
        "",
        f"**🎲 Repo roulette — {day.isoformat()}**",
        "",
        f"### [{name}]({U}/{slug})",
        "",
        f"{pitch}",
        "",
        f"`{stack}`",
        "",
        "</td><td width=\"45%\" valign=\"top\">",
        "",
        "**💡 Something I believe today**",
        "",
        f"> {lesson}",
        "",
        f"<sub>Rotated by <a href=\"{U}/Amithkrishna29z/blob/main/.github/workflows/daily.yml\">a cron job</a>, not by hand. Come back tomorrow.</sub>",
        "",
        "</td></tr></table>",
        "",
        END,
    ])


def main() -> int:
    text = README.read_text(encoding="utf-8")
    if START not in text or END not in text:
        print("markers not found in README.md", file=sys.stderr)
        return 1
    block = render(datetime.datetime.now(datetime.timezone.utc).date())
    updated = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block,
                     text, flags=re.DOTALL)
    if updated == text:
        print("no change")
        return 0
    README.write_text(updated, encoding="utf-8")
    print("daily block updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
