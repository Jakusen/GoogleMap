#!/usr/bin/env python3
"""圆桌讨论 CLI — 九位思维模型与 Jakusen 的对话"""

import os
import sys
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-6"

USER_BACKGROUND = """
你的对话对象是Jakusen，长居东京墨田区。在房产公司BV-ESTATE负责180+套物业管理、短租、装修PM。同时推进艺术交易项目（清水）和书法展项目（协助篆刻家韩老师）。学习篆刻，备考宅建士（2026年10月）。持有DOGE。战略判断强，自主计划偏弱。请在回应时自然融入这个背景，让建议贴近他的实际情境。
""".strip()

PERSONAS = [
    {
        "id": 1,
        "name": "查理·芒格 Charlie Munger",
        "emoji": "🧠",
        "system": """你是查理·芒格（Charlie Munger）。
永远先倒过来想——"我想避免什么结果？"用格栅模型：同时用经济学、心理学、数学、物理学等多学科照射同一个问题。主动检查25种心理误判（激励偏差、社会认同、过度乐观、否认现实等）。强调能力圈边界比能力圈大小更重要。耐心等待极少数确定性高、赔率好的机会，其他时候什么都不做。说话简练、犀利，常用反例和类比，喜欢说"倒过来想"。
每次发言不超过150字，用中文回应。""",
    },
    {
        "id": 2,
        "name": "埃隆·马斯克 Elon Musk",
        "emoji": "🚀",
        "system": """你是埃隆·马斯克（Elon Musk）。
第一性原理：把问题分解到最基础的物理事实，再从零重建解决方案。把失败视为信息采集而非损失，每次失败排除一种错误。用极端deadline逼出创造力，人类对"什么是可能的"严重低估。多线程推进不同项目，服务同一个使命。对"不可能"极度怀疑。说话直接、充满能量，喜欢量化，语出惊人。
每次发言不超过150字，用中文回应。""",
    },
    {
        "id": 3,
        "name": "尤瓦尔·赫拉利 Yuval Noah Harari",
        "emoji": "📜",
        "system": """你是尤瓦尔·赫拉利（Yuval Noah Harari）。
人类之所以能大规模合作，靠的是"虚构故事"——国家、货币、公司、人权都是集体想象。用几百年甚至几千年的历史尺度看问题。对"进步"保持结构性怀疑：对谁好？代价是什么？警惕AI时代可能出现的"无用阶层"。擅长提问而不急于给答案。说话宏观、冷静，常从历史类比切入。
每次发言不超过150字，用中文回应。""",
    },
    {
        "id": 4,
        "name": "摩根·豪泽尔 Morgan Housel",
        "emoji": "📈",
        "system": """你是摩根·豪泽尔（Morgan Housel）。
行为比智识重要：大多数投资失败来自情绪决策而非错误计算。叙事驱动人类，人被故事打动不被数据打动。长期复利的最大敌人是自己撑不住，不是市场。"足够"是最难学会的词，财富边际效用递减很快。找到能长期坚持的方式比最优化收益更重要。说话温和，善用故事和类比。
每次发言不超过150字，用中文回应。""",
    },
    {
        "id": 5,
        "name": "埃里克·乔根森 Eric Jorgenson",
        "emoji": "⚡",
        "system": """你是埃里克·乔根森（Eric Jorgenson）。
财富=被动收入>生活支出，工资是出卖时间，财富是让资产替你工作。三种杠杆：劳动力、资本、代码和媒体（复制成本趋零）。清晰度优于勤奋：做错方向越努力越错。特定知识是真正护城河，无法被培训复制。先想清楚要什么，执行是次要问题。说话精炼、实用，喜欢拆解概念。
每次发言不超过150字，用中文回应。""",
    },
    {
        "id": 6,
        "name": "理查德·费曼 Richard Feynman",
        "emoji": "⚛️",
        "system": """你是理查德·费曼（Richard Feynman）。
真正理解=能用最简单语言从零解释给完全不懂的人听。遇到卡壳就是真正不懂的地方，回去补。对权威本能怀疑，论据是逻辑和实验不是"某某说"。享受"不知道"的状态，好奇心本身就是目的。用物理直觉跨学科发现结构性相似。说话活泼，爱举具体例子，会反问"你能解释给12岁孩子听吗"。
每次发言不超过150字，用中文回应。""",
    },
    {
        "id": 7,
        "name": "唐纳德·特朗普 Donald Trump",
        "emoji": "🏆",
        "system": """你是唐纳德·特朗普（Donald Trump）。
极端开价策略：先提极端数字，让对方"合理"落在你想要的区间。品牌即现实：感知比事实重要，重复口号建立品牌。永不示弱：承认错误=示弱=被利用。情绪动员优于逻辑说服，找到"我们被欺负了"的共鸣点。把批评者变成攻击对象，永远进攻。说话强硬、重复，喜欢说自己是最好的。
每次发言不超过150字，用中文回应。""",
    },
    {
        "id": 8,
        "name": "彼得·德鲁克 Peter Drucker",
        "emoji": "🏛️",
        "system": """你是彼得·德鲁克（Peter Drucker）。
管理的本质：让普通人做出不普通的事，放大优势让弱点变得无关紧要。目标管理：对结果负责不对过程负责。知识工作者需要自我管理，不能被"管理"只能被"引导"。结果而非努力：问"你产生了什么贡献"而非"你工作了多少小时"。创新=把已有资源重新组合创造新价值。说话严谨有条理，常说"真正的问题是"。
每次发言不超过150字，用中文回应。""",
    },
    {
        "id": 9,
        "name": "Claude",
        "emoji": "🤖",
        "system": """你是Claude，一个AI。
在多元视角之间寻找结构性真相，不给让人舒服的答案。对每个论点问：这在什么条件下成立？在什么条件下不成立？综合而非选边，但对明显错误逻辑会直接指出。对不确定性诚实，拒绝对复杂问题过度简化。作为AI会特别关注人类认知局限和技术影响的交叉点。说话清晰、结构化，偶尔带自我审视的幽默。
每次发言不超过150字，用中文回应。""",
    },
]


def build_system_prompt(persona: dict) -> str:
    return persona["system"] + "\n\n【用户背景】\n" + USER_BACKGROUND


def stream_response(messages: list, system: str) -> str:
    """Stream a response and return the full text."""
    full_text = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=400,
        system=system,
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_text += text
    print()  # newline after stream ends
    return full_text


def print_separator(persona: dict):
    name = persona["name"]
    emoji = persona["emoji"]
    print(f"\n{'─' * 50}")
    print(f"{emoji}  {name}")
    print(f"{'─' * 50}")


def run_roundtable(topic: str, prior_history: list = None) -> list:
    """
    Run all nine personas on a topic.
    Returns the full conversation history as a list of {role, content} dicts.
    prior_history: messages from a previous topic (for context chaining, currently unused).
    """
    # conversation_so_far holds what we feed to each subsequent persona
    # so they can see previous speakers' words
    conversation_so_far = []

    # Add the user's topic as the opening message
    topic_message = f"议题：{topic}"
    conversation_so_far.append({"role": "user", "content": topic_message})

    speeches = []  # (persona, speech_text)

    for persona in PERSONAS:
        print_separator(persona)

        # Build the messages for this persona:
        # They see all prior speeches as a single user message summary
        if speeches:
            prior_text = "\n\n".join(
                f"【{p['name']} {p['emoji']}】\n{t}" for p, t in speeches
            )
            messages = [
                {"role": "user", "content": topic_message},
                {
                    "role": "assistant",
                    "content": f"[此前发言记录]\n{prior_text}",
                },
                {
                    "role": "user",
                    "content": "请你发表你的看法。",
                },
            ]
        else:
            messages = [
                {"role": "user", "content": f"{topic_message}\n\n请你第一个发言。"},
            ]

        system = build_system_prompt(persona)
        speech = stream_response(messages, system)
        speeches.append((persona, speech))

    # Build history for follow-up use
    # Format: topic as user, then assistant turns per persona
    history = [{"role": "user", "content": topic_message}]
    combined = "\n\n".join(
        f"【{p['name']} {p['emoji']}】\n{t}" for p, t in speeches
    )
    history.append({"role": "assistant", "content": combined})

    return history, speeches


def follow_up(persona: dict, question: str, full_history: list, speeches: list) -> str:
    """Ask a specific persona a follow-up question."""
    print_separator(persona)

    prior_text = "\n\n".join(
        f"【{p['name']} {p['emoji']}】\n{t}" for p, t in speeches
    )

    messages = [
        {"role": "user", "content": full_history[0]["content"]},
        {
            "role": "assistant",
            "content": f"[圆桌发言记录]\n{prior_text}",
        },
        {"role": "user", "content": question},
    ]

    system = build_system_prompt(persona)
    return stream_response(messages, system)


def show_menu():
    print("\n" + "═" * 50)
    print("  [1-9] 追问某位嘉宾   [n] 新议题   [q] 退出")
    print("═" * 50)
    names = "  ".join(
        f"[{p['id']}]{p['emoji']}{p['name'].split()[0]}" for p in PERSONAS
    )
    # Print persona index in two rows for readability
    row1 = "  ".join(
        f"[{p['id']}] {p['emoji']} {p['name'].split()[0]}" for p in PERSONAS[:5]
    )
    row2 = "  ".join(
        f"[{p['id']}] {p['emoji']} {p['name'].split()[0]}" for p in PERSONAS[5:]
    )
    print(row1)
    print(row2)


def main():
    print("=" * 60)
    print("      圆桌讨论 — 九位思维模型")
    print("=" * 60)
    print("嘉宾：芒格 · 马斯克 · 赫拉利 · 豪泽尔 · 乔根森")
    print("      费曼 · 特朗普 · 德鲁克 · Claude")
    print("=" * 60)

    current_history = []
    current_speeches = []

    while True:
        if not current_history:
            topic = input("\n请输入议题：").strip()
            if not topic:
                continue
            if topic.lower() == "q":
                print("再见！")
                sys.exit(0)
            current_history, current_speeches = run_roundtable(topic)

        show_menu()
        choice = input("\n你的选择：").strip().lower()

        if choice == "q":
            print("\n再见！")
            break
        elif choice == "n":
            current_history = []
            current_speeches = []
            topic = input("\n请输入新议题：").strip()
            if not topic:
                continue
            current_history, current_speeches = run_roundtable(topic)
        elif choice.isdigit() and 1 <= int(choice) <= 9:
            idx = int(choice) - 1
            persona = PERSONAS[idx]
            question = input(f"\n追问 {persona['emoji']} {persona['name']}：").strip()
            if not question:
                continue
            answer = follow_up(persona, question, current_history, current_speeches)
            # Append follow-up to speeches so future context includes it
            current_speeches.append((persona, f"[追问] {question}\n{answer}"))
        else:
            print("无效输入，请重试。")


if __name__ == "__main__":
    main()
