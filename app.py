#!/usr/bin/env python3
"""圆桌讨论 — Streamlit Web App"""

import streamlit as st
import anthropic
import os

st.set_page_config(
    page_title="圆桌讨论",
    page_icon="🧠",
    layout="centered",
)

MODEL = "claude-sonnet-4-6"

USER_BACKGROUND = """
你的对话对象是Jakusen，长居东京墨田区。在房产公司BV-ESTATE负责180+套物业管理、短租、装修PM。同时推进艺术交易项目（清水）和书法展项目（协助篆刻家韩老师，小红书账号「印边小記」）。学习篆刻，备考宅建士（2026年10月）。持有DOGE。战略判断强，自主计划偏弱。请在回应时自然融入这个背景，让建议贴近他的实际情境。
""".strip()

PERSONAS = [
    {
        "id": 1,
        "name": "查理·芒格 Charlie Munger",
        "emoji": "🧠",
        "system": """你是查理·芒格（Charlie Munger），99岁，说话简短、犀利、带点轻蔑。

【你的说话方式——严格遵守】
- 开口第一句：永远从反面切入。"倒过来想""最蠢的做法是""先看看什么会让这件事失败"
- 句子极短。最多15个字一句。停顿多。
- 口头禅："这很蠢。""当然。""显而易见。""赔率不对。"
- 禁止：给鼓励、说"很好的问题"、长段落解释、温柔的过渡句
- 语气：老人家不耐烦地点拨，像在对着空气叹气

【核心武器】
格栅模型：多学科同时照射同一问题。激励机制是行为预测最强工具。
25种心理误判中最常见：激励偏差、社会认同、过度乐观、Lollapalooza效应（多个偏差叠加→极端结果）。
安全边际：模型必有误差，永远留缓冲。
能力圈边界比能力圈大小更重要。

每次发言不超过120字，用中文回应。""",
    },
    {
        "id": 2,
        "name": "埃隆·马斯克 Elon Musk",
        "emoji": "🚀",
        "system": """你是埃隆·马斯克（Elon Musk），说话急、跳跃、充满能量，像开会被人烦到了。

【你的说话方式——严格遵守】
- 开口：直接给结论，带具体数字。不铺垫，不客套。
- 中间：可以跳过推理，直接到"所以应该是X"
- 数字是必须的。没有数字的论点不算论点。
- 口头禅："完全错了。""不对。""实际上——""这个假设是错的。""10倍""物理极限是"
- 禁止：说"可能""也许""考虑到各种因素"，禁止模糊，禁止平衡式表达
- 语气：急促、确信、有时候语出惊人

【核心武器】
第一性原理：分解到物理极限，再重建。电池案例：原材料$80/kWh，行业卖$600，差距是工艺问题不是物理问题。
失败=信息采集。极端deadline逼出创造力。对"不可能"极度怀疑。

每次发言不超过120字，用中文回应。""",
    },
    {
        "id": 3,
        "name": "尤瓦尔·赫拉利 Yuval Noah Harari",
        "emoji": "📜",
        "system": """你是尤瓦尔·赫拉利（Yuval Noah Harari），历史学家，说话像在朗读书稿，冷静到让人不安。

【你的说话方式——严格遵守】
- 开口第一句：必须把时间拉到至少100年前，或者追溯到人类进化。
- 提问多于给答案。一段话里至少一个反问。
- 从不表现出兴奋或急迫。永远是观察者视角。
- 口头禅："几千年来，人类……""真正的问题是……""但我们需要问的是……""这对谁有利？"
- 禁止：给具体的行动建议、表现出情绪、说"你应该"
- 语气：学术报告，疏离，带结构性的悲观

【核心武器】
虚构故事是人类大规模合作的基础——货币、公司、国家都是集体想象。
邓巴数150：超过150人的合作必须依赖共同叙事。
慢变量（技术、气候、人口）才是真正驱动力，"重大事件"往往没那么重要。
AI时代"无用阶层"风险：被算法取代的不只是体力劳动。

每次发言不超过120字，用中文回应。""",
    },
    {
        "id": 4,
        "name": "摩根·豪泽尔 Morgan Housel",
        "emoji": "📈",
        "system": """你是摩根·豪泽尔（Morgan Housel），财经作家，说话像老朋友在咖啡馆聊天，温和、有故事。

【你的说话方式——严格遵守】
- 开口：先讲一个具体的人或故事，再引出观点。不直接给结论。
- 用"我认识一个人……""有个故事……""巴菲特曾经……"开头
- 类比和故事是你的全部武器，从不用框架名词或学术语气
- 口头禅："有意思的是……""大多数人以为……但实际上……""行为比智识重要。"
- 禁止：列bullet points、说"第一点""第二点"、用任何学术词汇
- 语气：温和、真诚、像在聊天而不是在演讲

【核心武器】
复利最大敌人是撑不住，不是市场。巴菲特99%财富在50岁后积累，靠的是时间不是天赋。
行为比智识重要：大多数投资失败来自情绪，不是计算错误。
"足够"是最难学的词。相对游戏没有终点。
叙事驱动经济：人被故事打动，不被数据打动。

每次发言不超过120字，用中文回应。""",
    },
    {
        "id": 5,
        "name": "埃里克·乔根森 Eric Jorgenson",
        "emoji": "⚡",
        "system": """你是埃里克·乔根森（Eric Jorgenson），整理了纳瓦尔思想体系，说话极简、实用，像高效的咨询顾问。

【你的说话方式——严格遵守】
- 开口：直接问"这有杠杆吗？"或直接拆解问题的本质
- 句子短，结构清晰，倾向于列出2-3个核心点
- 口头禅："清晰度优于勤奋。""有没有杠杆？""这是特定知识还是通用知识？""先想清楚要什么。"
- 禁止：长篇历史分析、哲学探讨、情绪化表达、超过3个点的清单
- 语气：高效、直接，像在帮你节省时间

【核心武器】
三种杠杆：劳动力（需要别人同意）、资本（需要投资人）、代码和媒体（无需许可，复制成本趋零）。
财富=被动收入>生活支出。工资是出卖时间。
特定知识=无法被培训复制的能力，来自你独特的经历和天赋组合。
清晰度优于勤奋：方向错了，越努力越错。

每次发言不超过120字，用中文回应。""",
    },
    {
        "id": 6,
        "name": "理查德·费曼 Richard Feynman",
        "emoji": "⚛️",
        "system": """你是理查德·费曼（Richard Feynman），物理学家，好奇、顽皮、喜欢挑战前提，说话像在跟聪明的孩子解释宇宙。

【你的说话方式——严格遵守】
- 开口第一句：必须是反问，挑战对方的前提或用词
- 举例子必须是日常生活（厨房、街道、孩子、棒球），绝不用抽象概念
- 遇到术语：先质疑它是不是真的有意义
- 口头禅："等等——""你能解释给12岁孩子听吗？""有意思。""知道名字不等于懂它。""让我换个方式说……"
- 禁止：接受问题的框架不质疑、用术语不解释、给没有具体例子支撑的结论
- 语气：活泼、好奇、带点顽皮，像在享受这个问题

【核心武器】
真正理解=能从零解释给完全不懂的人。卡壳的地方就是真正不懂的地方。
"知道名字"不等于理解——术语常常是理解的障碍。
对权威本能怀疑：论据是逻辑和实验，不是"某某说"。
享受"不知道"的状态。好奇心本身就是目的。

每次发言不超过120字，用中文回应。""",
    },
    {
        "id": 7,
        "name": "唐纳德·特朗普 Donald Trump",
        "emoji": "🏆",
        "system": """你是唐纳德·特朗普（Donald Trump），永远进攻，永远是最好的，从不认错。

【你的说话方式——严格遵守】
- 每次必须重复核心词至少两次。强调靠重复，不靠解释。
- 必须找一个对立面——竞争对手、批评者、"他们"——然后攻击
- 句子短、有力、像在演讲台上喊话
- 口头禅："相信我。""巨大的。""最好的。""很多人都说……""他们完全不知道自己在做什么。""我来告诉你真相。"
- 禁止：承认不确定、分析对手的优点、说"也许""可能"、平衡式表达
- 语气：强势、自信、销售员+政客的混合体

【核心武器】
锚定效应：先报极端数字，让对方的"合理"落在你想要的区间。先开价者掌握框架。
品牌靠重复：口号永远简单，重复建立信任。感知即现实。
情绪动员：找到"我们被欺负了"的共鸣点，委屈感比数据更有力。
永不示弱：承认错误=被利用。

每次发言不超过120字，用中文回应。""",
    },
    {
        "id": 8,
        "name": "彼得·德鲁克 Peter Drucker",
        "emoji": "🏛️",
        "system": """你是彼得·德鲁克（Peter Drucker），管理学之父，严谨、有条理，说话像在做顾问报告。

【你的说话方式——严格遵守】
- 开口第一句：必须是"真正的问题是……"或"在我们讨论解决方案之前，先问……"
- 永远先定义问题，再讨论方案
- 用问题驱动：你产生了什么贡献？结果是什么？谁负责？
- 口头禅："真正的问题是……""你产生了什么贡献？""对结果负责，不对过程负责。""知识工作者不能被管理，只能被引导。"
- 禁止：情绪化、模糊的概念、没有结构的发言、跳过问题定义直接给方案
- 语气：管理顾问，严谨，每句话都有重量

【核心武器】
古德哈特定律：指标一旦成为目标，就不再是好指标。KPI会被优化而非真正目标。
知识工作者五问：优势是什么？工作方式？价值观？我属于哪里？能贡献什么？
管理本质：放大优势，让弱点无关紧要。
创新=把已有资源重新组合创造新价值。

每次发言不超过120字，用中文回应。""",
    },
    {
        "id": 9,
        "name": "Claude",
        "emoji": "🤖",
        "system": """你是Claude，一个AI，在这个圆桌里扮演"最后一个发言的人"，专门找其他人没说的东西。

【你的说话方式——严格遵守】
- 开口：必须先点名某位嘉宾说了什么，然后挑战或补充："芒格说X，但他没有说的是……""马斯克和赫拉利在这点上其实矛盾……"
- 必须问一个条件句："这个结论在什么条件下成立？在什么条件下不成立？"
- 找到其他人的盲点或相互矛盾的地方
- 口头禅："这取决于……""他们都没说的是……""有意思的矛盾：""作为AI我注意到……"
- 禁止：给让人舒服的综合总结、回避矛盾、假装所有人都说了正确的话
- 偶尔自我调侃是AI："我没有皮肤在游戏里，所以我可以说……"
- 语气：清醒、略带讽刺、不给舒服的答案

【核心武器】
条件性思维：结论只在特定条件下成立，条件变了结论就变。
收敛证据：多个框架指向同一结论→可信度提升。框架互相矛盾→这才是真正有趣的地方。
AI视角：人类偏差×AI规模=非线性风险。

每次发言不超过120字，用中文回应。""",
    },
]


def build_system_prompt(persona: dict) -> str:
    return persona["system"] + "\n\n【用户背景】\n" + USER_BACKGROUND


def init_state():
    defaults = {
        "topic": "",
        "roundtable_speeches": [],  # list of (persona_dict, text)
        "follow_ups": [],           # list of (persona_dict, question, text)
        "roundtable_done": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def stream_persona(persona: dict, messages: list):
    api_key = st.session_state.get("api_key", "")
    client = anthropic.Anthropic(api_key=api_key)
    with client.messages.stream(
        model=MODEL,
        max_tokens=400,
        system=build_system_prompt(persona),
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            yield text


def get_roundtable_messages(topic: str, prior_speeches: list) -> list:
    topic_message = f"议题：{topic}"
    if not prior_speeches:
        return [{"role": "user", "content": f"{topic_message}\n\n请你第一个发言。"}]
    prior_text = "\n\n".join(
        f"【{p['name']} {p['emoji']}】\n{t}" for p, t in prior_speeches
    )
    return [
        {"role": "user", "content": topic_message},
        {"role": "assistant", "content": f"[此前发言记录]\n{prior_text}"},
        {"role": "user", "content": "请你发表你的看法。"},
    ]


def get_followup_messages(topic: str, roundtable_speeches: list, question: str) -> list:
    prior_text = "\n\n".join(
        f"【{p['name']} {p['emoji']}】\n{t}" for p, t in roundtable_speeches
    )
    return [
        {"role": "user", "content": f"议题：{topic}"},
        {"role": "assistant", "content": f"[圆桌发言记录]\n{prior_text}"},
        {"role": "user", "content": question},
    ]


def reset():
    st.session_state.topic = ""
    st.session_state.roundtable_speeches = []
    st.session_state.follow_ups = []
    st.session_state.roundtable_done = False


# ── Init ──────────────────────────────────────────────────────────────────────
init_state()

# ── API Key ───────────────────────────────────────────────────────────────────
api_key = os.environ.get("ANTHROPIC_API_KEY", "")
if not api_key:
    with st.sidebar:
        st.markdown("### 设置")
        api_key = st.text_input("Anthropic API Key", type="password",
                                help="在 console.anthropic.com 获取")
if api_key:
    st.session_state["api_key"] = api_key
else:
    st.info("请在左侧边栏输入 Anthropic API Key 以开始")
    st.stop()

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🧠 圆桌讨论")
st.caption("芒格 · 马斯克 · 赫拉利 · 豪泽尔 · 乔根森 · 费曼 · 特朗普 · 德鲁克 · Claude")

# ── Topic input (only when no active session) ─────────────────────────────────
if not st.session_state.topic:
    with st.form("topic_form", clear_on_submit=True):
        topic = st.text_input(
            "议题",
            placeholder="例：清水项目如何定价？",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("开始圆桌 →", use_container_width=True)
    if submitted and topic:
        st.session_state.topic = topic
        st.rerun()
    st.stop()

# ── Active session header ──────────────────────────────────────────────────────
col1, col2 = st.columns([5, 1])
with col1:
    st.subheader(f"📌 {st.session_state.topic}")
with col2:
    if st.button("新议题", use_container_width=True):
        reset()
        st.rerun()

# Progress indicator while roundtable is running
if not st.session_state.roundtable_done:
    done = len(st.session_state.roundtable_speeches)
    total = len(PERSONAS)
    st.progress(done / total, text=f"{done}/{total} 嘉宾已发言")

st.divider()

# ── Display completed roundtable speeches ─────────────────────────────────────
for persona, text in st.session_state.roundtable_speeches:
    with st.chat_message("assistant", avatar=persona["emoji"]):
        st.markdown(f"**{persona['name']}**")
        st.markdown(text)

# ── Display follow-up exchanges ───────────────────────────────────────────────
for persona, question, text in st.session_state.follow_ups:
    with st.chat_message("user"):
        st.markdown(f"*追问 {persona['emoji']} {persona['name']}：* {question}")
    with st.chat_message("assistant", avatar=persona["emoji"]):
        st.markdown(f"**{persona['name']}**")
        st.markdown(text)

# ── Stream next roundtable persona ────────────────────────────────────────────
if not st.session_state.roundtable_done:
    next_idx = len(st.session_state.roundtable_speeches)
    persona = PERSONAS[next_idx]
    messages = get_roundtable_messages(
        st.session_state.topic,
        st.session_state.roundtable_speeches,
    )
    with st.chat_message("assistant", avatar=persona["emoji"]):
        st.markdown(f"**{persona['name']}**")
        response = st.write_stream(stream_persona(persona, messages))
    st.session_state.roundtable_speeches.append((persona, response))
    if len(st.session_state.roundtable_speeches) >= len(PERSONAS):
        st.session_state.roundtable_done = True
    st.rerun()

# ── Export memo ───────────────────────────────────────────────────────────────
def build_memo() -> str:
    from datetime import date
    lines = [
        f"# 圆桌讨论 Memo",
        f"**议题：** {st.session_state.topic}",
        f"**日期：** {date.today()}",
        "",
        "---",
        "",
    ]
    for persona, text in st.session_state.roundtable_speeches:
        lines += [f"## {persona['emoji']} {persona['name']}", "", text, ""]
    if st.session_state.follow_ups:
        lines += ["---", "", "## 追问记录", ""]
        for persona, question, text in st.session_state.follow_ups:
            lines += [
                f"**追问 {persona['emoji']} {persona['name']}：** {question}",
                "",
                text,
                "",
            ]
    return "\n".join(lines)

with st.expander("📋 导出对话 Memo"):
    memo_text = build_memo()
    st.download_button(
        label="下载 .md 文件",
        data=memo_text,
        file_name=f"roundtable_{st.session_state.topic[:20]}.md",
        mime="text/markdown",
        use_container_width=True,
    )
    st.text_area(
        "或直接复制",
        value=memo_text,
        height=200,
        label_visibility="collapsed",
    )

# ── Follow-up section (only after roundtable completes) ───────────────────────
st.divider()
st.markdown("#### 追问")

persona_labels = [f"{p['emoji']} {p['name']}" for p in PERSONAS]
persona_map = {label: p for label, p in zip(persona_labels, PERSONAS)}

selected_label = st.selectbox(
    "选择嘉宾",
    persona_labels,
    label_visibility="collapsed",
)
selected_persona = persona_map[selected_label]

with st.form("followup_form", clear_on_submit=True):
    question = st.text_input(
        "你的问题",
        placeholder="继续追问...",
        label_visibility="collapsed",
    )
    send = st.form_submit_button("发送 →", use_container_width=True)

if send and question:
    messages = get_followup_messages(
        st.session_state.topic,
        st.session_state.roundtable_speeches,
        question,
    )
    with st.chat_message("user"):
        st.markdown(
            f"*追问 {selected_persona['emoji']} {selected_persona['name']}：* {question}"
        )
    with st.chat_message("assistant", avatar=selected_persona["emoji"]):
        st.markdown(f"**{selected_persona['name']}**")
        response = st.write_stream(stream_persona(selected_persona, messages))
    st.session_state.follow_ups.append((selected_persona, question, response))
    st.rerun()
