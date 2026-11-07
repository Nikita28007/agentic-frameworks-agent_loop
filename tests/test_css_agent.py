from pathlib import Path

import css_agent


def test_strip_fences_removes_language_fence():
    assert css_agent._strip_fences("```css\nbody{}\n```") == "body{}"


def test_strip_fences_leaves_plain_text():
    assert css_agent._strip_fences("  body{}  ") == "body{}"


def test_template_style_is_written(tmp_path):
    site = tmp_path / "site"
    css_agent.write_template_style(site)
    assert ":root" in (site / "common.css").read_text(encoding="utf-8")


def test_template_hub_links_every_game(tmp_path):
    site = tmp_path / "site"
    games = [{"label": "Quiz", "slug": "strands"}, {"label": "Memory", "slug": "agno"}]
    css_agent.write_template_hub("RAG", games, site)
    html = Path(site / "index.html").read_text(encoding="utf-8")
    assert "<title>RAG Arcade</title>" in html
    assert 'href="strands/game.html"' in html and 'href="agno/game.html"' in html