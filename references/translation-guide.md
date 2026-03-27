# 专业中英商业文章翻译指南 (Translation Guide)

本指南专为 `business-model-craft-skill` Skill 的 **Step 4.C (英文翻译分支)** 设计。

> **Goal**: 将中文的商业模式深度分析，转化为**地道、优雅且极具影响力的美式英语商业评论**，对标《华尔街日报》(WSJ)、《哈佛商业评论》(HBR) 或 Stratechery。

---

## 前置检查（CRITICAL — 翻译前必做）

1. **已发布提示块检查**：如果中文版 (`[slug].zh.md`) 包含"已发布提示"块（例如指向 `businessmodelcraft.com` 的链接提示），英文版必须在对应位置插入英文版提示块，格式如下：

   ```markdown
   > This analysis is also available on [BusinessModelCraft.com](https://businessmodelcraft.com/en/examples/[slug]).
   ```

2. **章节结构映射**：英文版章节标题必须与中文版一一对应，编号格式改为罗马数字：

   | 中文版 | 英文版 |
   |--------|--------|
   | `## 一、解码商业基因` | `## I. Decoding the Business DNA` |
   | `## 二、赚钱的逻辑` | `## II. How the Money Works` |
   | `## 三、增长飞轮与护城河` | `## III. The Flywheel and the Moat` |
   | `## 四、风险与隐忧` | `## IV. Risks and Cracks` |
   | `## 五、终局` | `## V. The Endgame` |
   | `## 六、总结与点评` | `## VI. The Verdict` |

---

## 核心原则 (Core Principles)

### 1. 美式本土化 (US Localization)
*   **拒绝中式英语 (No Chinglish)**：不要逐字翻译。要转换思维模式。
*   **习语优先**：使用美国商业环境中的标准表达。
    *   *Bad*: "The price is very cheap so many people use it."
    *   *Good*: "The aggressive pricing strategy lowers the barrier to entry, driving mass adoption."

### 2. 信达雅 (Xin Da Ya)
*   **信 (Faithfulness)**：严禁删减内容。原文的信息密度必须完整保留。
*   **达 (Expressiveness)**：行文流畅，逻辑通顺。长短句结合，制造阅读节奏。
*   **雅 (Elegance)**：用词考究，但不要堆砌华丽词藻。
    *   *Instead of*: "big change" → *Try*: "paradigm shift" / "tectonic shift"
    *   *Instead of*: "good advantage" → *Try*: "competitive edge" / "structural moat"

### 3. 金句增强 (Punchline Optimization)
对于原文中的核心观点句，要翻译得有力（Impactful）且易于传播（Shareable）。
*   *原文*："风口过去，剩下的才是壁垒。"
*   *翻译*："When the hype subsides, only the true moats remain."

---

## 去除英文 AI 味（CRITICAL — 这是最重要的质量关）

英文 AI 写作的根本问题：**过度使用高频连接词和正式化词汇，读起来像学术报告摘要而不是商业评论**。

### 高频 AI 词汇禁用清单

以下词汇出现时，必须替换，无例外：

| 禁用 | 替换方向 |
|------|---------|
| `delve into` | `examine`, `look at`, `break down` |
| `testament to` | 直接描述事实本身 |
| `underscore` | `show`, `reveal`, `make clear` |
| `nuanced` | 删掉，直接描述具体细节 |
| `intricate` | `complex`, `layered`，或干脆描述具体情况 |
| `pivotal` | `key`, `critical`, `decisive`，或根本不加形容词 |
| `vibrant` / `bustling` | 描述具体事实，不用形容词替代 |
| `showcase` | `show`, `demonstrate`, `reveal` |
| `foster` | `build`, `develop`, `drive` |
| `align with` | `match`, `fit`, `support`，或重构句子 |
| `leverage` (动词) | `use`, `draw on`, `tap into` |
| `cornerstone` | `foundation`, `core`，或描述具体机制 |
| `unprecedented` | 提供数据说话，不用形容词 |
| `groundbreaking` | 同上 |
| `It's worth noting` | 删掉这句导入，直接陈述 |
| `It's important to note` | 同上 |
| `It goes without saying` | 同上 |

### 禁用句式结构

*   **"Not only X, but also Y"** — 读起来像教科书。直接说 Y 的具体数据。
    *   ❌ "Not only does Apple sell hardware, but it also builds a software ecosystem."
    *   ✅ "Hardware is Apple's distribution channel. The App Store is where it prints money."

*   **"From X to Y"**（两端语义不相关时）— 虚假范围，营造宽度但毫无内容。

*   **连接词堆砌**：`Firstly, ... Moreover, ... Furthermore, ... In conclusion` — 直接跳到下一段，不需要这些铺垫词。

*   **文末升华句**：`In summary`, `In conclusion`, `Overall`, `To sum up` — 删掉，文章不需要道别。

*   **说教式导入**：任何以"It is important to understand that..."或"One must consider..."开头的句子，全部删改。

### 写好英文的正确方向

*   短句优先（平均 12-18 词），偶尔插入长句制造节奏变化
*   允许用 `And` 或 `But` 开始句子（更自然，比 `Moreover` 强十倍）
*   数字说话：`margins expanded from 20% to 35%` 胜过 `profitability improved significantly`
*   比喻来自商业语境，不来自艺术或音乐（AI 爱用 conductor/symphony/orchestra）
*   允许短段落（两三句就是一段），不要每段都要"凑满"
*   观点要锋利，用第三方数据支撑，不要用形容词堆砌

---

## 术语对照表 (Terminology)

| 中文概念 | 推荐英文表达 | 备注 |
| :--- | :--- | :--- |
| **护城河** | **Moat** / Defensive barriers | 巴菲特核心概念 |
| **飞轮效应** | **Flywheel Effect** / Virtuous cycle | 亚马逊核心概念 |
| **颗粒度** | **Granularity** / Level of detail | |
| **降维打击** | **Asymmetric warfare** / Disruption from below | 视语境而定 |
| **私域流量** | **Owned channels** / Direct audience | 避免字面翻译 |
| **下沉市场** | **Lower-tier markets** / Underserved markets | |
| **内卷** | **Race to the bottom** / Zero-sum competition | 推荐用意译 |
| **单位经济** | **Unit Economics** | |
| **获客成本** | **CAC** (Customer Acquisition Cost) | |
| **生命周期价值** | **LTV** (Lifetime Value) | |
| **智商税** | **Premium on ignorance** / Overpriced gimmick | |
| **赋能** | 避免翻译，改用具体描述 | "赋能"是典型套话，用具体动作替代 |
| **生态闭环** | **Closed ecosystem** / Walled garden | |

---

## 翻译工作流 (Workflow)

当执行 `Translate the preceding Chinese analysis...` 指令时，请按以下步骤思考：

1.  **Pre-check（翻译前）**：
    *   查看中文版是否包含已发布提示块，若有则英文版开头同样插入英文版提示块。
    *   **NO H1 Header**: 严禁在输出中包含一级标题（H1, `# Title`）。输出必须直接以引用块（Blockquote）或二级标题（H2）开始。
    *   **No Metadata**: 严禁包含 HTML 注释或 YAML Frontmatter。

2.  **Tone Check**: 确认语调是 **Direct, Analytical, Opinionated**。保留判断力和立场，不要翻译成"balanced overview"风格。

3.  **Strict Translation Rule (CRITICAL)**: 英文版是中文版的翻译，**严禁新增原文没有的实质性分析段落或数据点**。如发现中文版有遗漏内容，应回头修改中文版，再从中文版翻译，而不是直接在英文版中补充。两个版本的信息量必须对等。

3.  **Structure Mapping**: 严格保留 Markdown 结构（H2, H3, Bullet Points, Quotes）。章节编号从中文数字改为罗马数字。

4.  **Opening Block (Company Orientation)**：英文开场白（引用块）必须与中文版等量同质地传递公司定向信息。对于大众不熟悉的公司，读完英文开场白的读者应同样能知道：该公司做什么、处于什么阶段、面临什么核心矛盾。不要因为翻译而让这些信息变得更模糊或更像 boilerplate。

5.  **Drafting**: 逐段翻译。
    *   *遇到成语*：意译为主。如"四面楚歌" → "Besieged on all sides" 或 "Facing headwinds from every direction"。
    *   *遇到数据*：保留原始数字和引用来源。
    *   *第六章（总结与点评）*：这是全文最有立场的部分，翻译时保留判断的锐度，不要平滑成学术腔。如果中文用了"这家公司的护城河，说穿了就是……"，英文要还原这种直接，而不是"The company's competitive moat can be characterized as..."。
    *   *遇到 AI 高频词*：按禁用清单替换，不要直接翻译。

5.  **AI Taste Check（完成后执行）**：按 `ai-taste-guide.md` 的英文版扫描章节逐条执行，命中必须重写。

6.  **Polishing**: 检查节奏。短段落、短句、数字优先。

---

## 示例 (Examples)

### Example 1: 描述商业模式
*   **原文**：瑞幸咖啡不是在卖咖啡，它是在通过数字化重构成本结构，用快取店消灭了第三空间的高昂租金。
*   **翻译**：Luckin Coffee re-engineered the cost structure through digitization. Pick-up stores eliminated the rent premium that "Third Place" models like Starbucks depend on. The result: a cup of coffee at roughly half the price.

### Example 2: 描述竞争
*   **原文**：面对巨头的碾压，这家初创公司毫无还手之力。
*   **翻译**：Against the full weight of incumbent giants, this startup had no real leverage.

### Example 3: 终局推演
*   **原文**：这是一个赢家通吃的市场。
*   **翻译**：This market is structurally winner-takes-most.

### Example 4: 数据驱动观点（避免 AI 味）
*   **AI 味原版**：Nvidia's pivotal role in the AI landscape is a testament to its groundbreaking GPU technology, which aligns with the unprecedented demand for compute.
*   **正确版**：Nvidia owns the picks-and-shovels of the AI gold rush. Its H100 GPU sells for $30,000+, and the waiting list stretches to 2026. That's not a product advantage — that's a structural chokehold.
