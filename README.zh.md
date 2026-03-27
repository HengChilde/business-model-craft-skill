**中文** | [English](README.md)

# business-model-craft-skill

给 Agent 以商业智慧，赋予AI对于公司商业模式思考的能力。business-model-craft-skill ，可以完成对任意一家公司做基于**商业模式画布**的深度商业模式解析，产出中英双语分析报告、结构化数据和本地可预览的网页。

## 它解决什么问题

市面上的 AI 商业分析有一个共同问题：读完一篇，你记不住任何一句有观点的话，千篇一律，讲得都是粗枝大叶的东西，缺少对于商业底层的思考。

满篇是"该公司以客户为中心""面临激烈的市场竞争""商业模式具有可持续性"——每句话都像真的，但加起来等于零。

**business-model-craft-skill 的目标是反过来做**：用商业模式画布（BMC）作为解析框架，逼迫分析回答"它到底怎么赚钱""护城河是真实的还是暂时的领先""哪里藏着别人看不见的风险"。写作风格对标 Stratechery、Not Boring 和哈佛商业评论——有立场，有来源，有让人读完觉得"对，就是这样"的瞬间。

## 商业模式画布

毫无疑问，对于business-model-craft-skill而言，最难的是商业分析的思考方法论。

我们以「人的思考过程」作为参照，人类在分析一家公司时，如果直接对着公司官网进行分析，往往一筹莫展，这个时候，人类会选择一些既定的分析框架，从作文题变成填空题，就能够很快入手，找到链条里精妙的点。

「商业模式画布」就是这样一个思考工具。

「商业模式画布」在 2005 年由亚历山大·奥斯特瓦德提出，亚历山大同时也是咨询公司 Strategyzer 的联合创始人。商业模式画布由 9 个格子组成，向企业提出，在设计商业模式时，需要回答的 9 个问题。

![商业模式画布|112x24](https://github.com/user-attachments/assets/4cf7c6ee-580c-4e28-a60f-2c8cba63cfda)

这 9 个问题，既相互独立，又左右互搏，需要反复权衡。在经营过程中，随着企业在不同的阶段，商业模式画布其实是流动的。

关于商业模式画布的理解和洞察，我写过一篇博客，有兴趣的话，可以深入阅读，[「商业模式画布」深度填写指南](https://mp.weixin.qq.com/s/h23zPl3JExq4lDHzwm27oQ)。同时，我也开发了一个具有自由画板和众多案例的商业模式工具[businessmodelcraft.com](https://businessmodelcraft.com) ，现在，我再次将方法论面向AI，制作成一个Skill。

在business-model-craft-skill中，我将商业模式画布的核心思想，和创业两年我的深度方法论，凝于其中，赋予AI Agent以同等的商业智慧。

-------

## Skill能力

**一句话触发，四件套产出**

指定任意一家公司，或让 Skill 从当日市场中自动挑选一家值得拆解的公司。一次对话结束后，你会得到：

| 文件             | 说明                                                                             |
| -------------- | ------------------------------------------------------------------------------ |
| `[slug].html`  | 在本地的商业模式分析页面，双击打开，方便易读，内置中文 / English 切换                                       |
| `[slug].zh.md` | 中文深度分析，六章结构，有开场判断、有数字、有结论                                                      |
| `[slug].en.md` | 英文版，对标 WSJ / HBR 的美式商业评论语感                                                     |
| `[slug].json`  | 双语结构化 BMC 数据，字段与 [businessmodelcraft.com](https://businessmodelcraft.com) 直接对应 |

**严谨翔实的分析过程**

研究基于 SEC 文件、业绩电话会实录（Seeking Alpha）、创始人访谈、WSJ / Bloomberg 报道，每个数字都有来源。

同时对于Agent的产出，强制进行AI味儿清理，最终的产出物，是接近Stratechery、Not Boring 和哈佛商业评论的专业文笔。

---

## 快速开始

**方式一：让Agent自动安装**

无论是Claude Code、OpenClaw，还是其他的Agent，都可以将下面这句话发给它，让Agent自己安装。

```
帮我安装这个 skill：https://github.com/hengchilde/business-model-craft-skill
```

**方式二：手动下载**

下载这个仓库，解压后，将文件在电脑中的路径告诉Agent，让其安装这个Skill。

1. 打开仓库页面[https://github.com/hengchilde/business-model-craft-skill](https://github.com/hengchilde/business-model-craft-skill)
2. 点击页面右侧绿色的 **`<> Code`** 按钮
3. 在下拉菜单中点击 **Download ZIP**
4. 解压下载好的 ZIP 文件，即可获得完整的 Skill 文件夹

**使用** 

安装完成后，直接在Agent中对话，告知其进行商业模式画布分析，或者直接要求其调用「business-model-craft-skill」这个Skill，即可使用。

---

## 产出报告输出路径

产出的分析报告，会保存在当前电脑里，保存位置的优先级从高到低：

1. 你在本次对话中指定的路径
2. 你为Agent全局规定的产出文件夹（环境变量 `BUSINESSMODELCRAFT_OUTPUT_BASE` 或 `BUSINESSMODELCRAFT_OUTPUT_DIR`）
3. 默认：`~/Documents/BusinessModelCraft/[slug]/`

Skill 完成后，Agent会告知实际路径和本地 `file://` 链接。

---

## 环境依赖

- Python 3.8+（用于 `scripts/` 目录下的脚本，Agent会自动完成依赖）
- 需要有网络连接（用于研究和获取公司数据）

可选：Alpha Vantage API Key

选股脚本默认使用 Google Finance 和 StockAnalysis，但使用者可以手动配置Alpha Vantage Key，通过API从Alpha Vantage获取股票波动数据，免费版本注册方便，填写邮箱即可，每天有25次请求额度。获取Key之后，可以让Agent填入Skill。

## 许可证

MIT
