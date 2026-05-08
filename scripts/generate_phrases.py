"""
Generate LINE stamp phrase ideas using the Anthropic API.

Bug fix: "text content blocks must be non-empty"
The Anthropic API rejects requests where a text content block has an empty
string.  This happens when `theme` is blank (e.g. empty user input).
The fix validates every text block before it is sent to the API.
"""

import anthropic


def build_prompt(theme: str, count: int) -> str:
    theme = theme.strip()
    if not theme:
        raise ValueError(
            "テーマが空です。スタンプのテーマを指定してください。"
            " (theme must not be empty)"
        )
    return (
        f"LINEスタンプ用の短い日本語フレーズを{count}個考えてください。\n"
        f"テーマ: {theme}\n\n"
        "条件:\n"
        "- 各フレーズは10文字以内\n"
        "- 日常会話で使いやすい表現\n"
        "- 1行に1フレーズ、番号なし"
    )


def generate_stamp_phrases(theme: str = "", count: int = 16) -> list[str]:
    """Return ``count`` stamp phrases for the given theme.

    Raises ``ValueError`` when *theme* is empty to prevent the
    ``"text content blocks must be non-empty"`` error from the Anthropic API.
    """
    prompt = build_prompt(theme, count)  # raises ValueError if theme is empty

    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=512,
        messages=[
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}],
            }
        ],
    )

    raw = response.content[0].text if response.content else ""
    phrases = [line.strip() for line in raw.splitlines() if line.strip()]
    return phrases[:count]


if __name__ == "__main__":
    import sys

    theme_arg = " ".join(sys.argv[1:]).strip()

    if not theme_arg:
        print("使い方: python generate_phrases.py <テーマ>", file=sys.stderr)
        print("例: python generate_phrases.py 日常の挨拶", file=sys.stderr)
        sys.exit(1)

    phrases = generate_stamp_phrases(theme=theme_arg, count=16)
    for phrase in phrases:
        print(phrase)
