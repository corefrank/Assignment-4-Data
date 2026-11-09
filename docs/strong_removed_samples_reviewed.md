# Baseline kept, Strong rejected — real WET sample audit

These are real filtered documents, not fabricated examples.
Baseline-kept documents not found in Strong-kept: 623

## Sample 1
- URL: http://en.xjtu.edu.cn/currentleadership.html
- Strong rejection reason: strong:repetitive_trigrams
- Text excerpt: Current Leadership Welcome to Xi'an Jiaotong University! Contact Us Alumni UASR 中文 nav close Home About+ General Information Message from the President Current Leadership History Organization+ Administration Schools Colleges Affiliate Units Admissions+ Undergraduate Graduate International Exchanges Short Term Scholarship Research+ Labs & Centers Research News+ Latest News Teaching & Learning Academics Student Life Campus+ Campus Pictures Videos Communities & Activities Upcoming Services Maps Contact Us Alumni UASR 中文 search close Search Home> About>Current Leadership 22251 General Information > Message from the President > Current Leadership > History > Videos > Secretary of the CPC Xi'an Jiaotong University Committee Lu Jianjun President and Deputy Secretary of the CPC Xi'an Jiaotong University Committee Zhang Liqun Executive Vice President Bie Zhaohong Deputy Secretary of the CPC Xi'an Jiaotong University Committee Ma Bohu Sun Zao Wang Huan Vice President Chai Wei Yan Junjie Shan Zhiwei Shao Jinyou Secretary of the Discipline Inspection Commission Ma Bohu Assistant President Shan W
- Human verdict (justified / false positive / unclear): **Justified（基本合理）** — 该校领导名单包含真实信息，但摘录的大量重复菜单、栏目和姓名职务列表缺少连续叙述，直接用于自然语言建模价值有限。若应用场景重视实体知识，可考虑先提取正文而非整页丢弃。

## Sample 2
- URL: https://www.remoteworldwide.net/jobs/senior-product-designer-998754bd14c1ccf3a74de23832eb001740212370830
- Strong rejection reason: strong:too_few_alpha_words
- Text excerpt: Senior Product Designer - Remoteworldwide Remote Worldwide Find jobs Companies This job has expired Job Description Senior Product Designer Posted: 22/02/2025 Anywhere in the world Remote Senior Apply Now Job By Toggl Work tools to elevate your productivity - apps for incredibly simple #timetracking and effective #projectplanning Get that unfair advantage! ✨ Join our Telegram group to skip website distractions and receive daily job updates straight to your feed! JOIN NOW! Find JobsCompaniesBlogsPrivacy Policy 2024 - 2026 Worldwideremote
- Human verdict (justified / false positive / unclear): **Justified（合理）** — 过期招聘页很短，主要由职位信息、宣传和网站导航构成，缺乏充足的连贯正文，过滤合理。

## Sample 3
- URL: https://hotchat.ai/character/3e8fd5e7-c6e1-4f9d-8f1a-1a78d11e279c
- Strong rejection reason: strong:too_few_alpha_words
- Text excerpt: Erotic Hypnosis Show - NSFW Character AI Chat Erotic Hypnosis Show Created by : Veram Created at : 2024/08/30 Seductive You're attending an erotic Hypnosis show! Whether you're the Hypnotist, Hypnotized, or just someone in the audience, you're sure to have fun! 0 0 0 Start chat Creator Info View Profile 0 Follow Erotic Hypnosis Show Created by : Veram Created at : 2024/08/30 Seductive You're attending an erotic Hypnosis show! Whether you're the Hypnotist, Hypnotized, or just someone in the audience, you're sure to have fun! Public Chats
- Human verdict (justified / false positive / unclear): **Justified（合理）** — 页面主体是重复的成人向角色介绍和界面元素，不适合作为当前通用英文语料的高质量样本。值得注意的是，它被结构规则而非 NSFW 过滤器排除，提示原有有害内容分类存在漏检可能。

## Sample 4
- URL: https://ecoed.network/about/aims/
- Strong rejection reason: strong:repetitive_trigrams
- Text excerpt: Aims – Global Network for Ecological Education Skip to content Global Network for Ecological Education Educational Resources for an Ecological Civilization About Aims Vision Team Partners Eco-Curriculum Romance Precision Generalization Insights Readings Audiovisuals Events Conferences Seminars Workshops Contact Menu About Aims Vision Team Partners Eco-Curriculum Romance Precision Generalization Insights Readings Audiovisuals Events Conferences Seminars Workshops Contact Aims The Global Network for Ecological Education seeks to . . . establish a platform for ecological education based on the best theories and practices; build a community for those who seek profound educational system reform; offer professional development opportunities to strengthen the voice and scope of ecological education; and create a strong vision for how to implement ecological education. We’re pursuing novel aims and an alternative vision for education. Contact US About Aims Vision Team Partners Eco-Curriculum Romance Precision Generalization Insights Readings Audiovisuals Events Conferences Seminars Workshops
- Human verdict (justified / false positive / unclear): **Possible false positive（潜在误删）** — 虽然菜单重复明显，页面包含关于生态教育目标的连贯、可理解的自然语言段落。理想方案是先移除导航/页脚模板并保留正文，而非依赖整页重复度直接删除。

## Sample 5
- URL: https://www.santafe.edu/events/upcoming?calendar__in=1&calendar__in=1%2C1%2C1%2C1%2C1%2C1%2C2%2C6%2C2%2C4%2C2%2C6%2C6
- Strong rejection reason: strong:repetitive_trigrams
- Text excerpt: Upcoming Events | Santa Fe Institute Santa Fe Institute Research Themes Projects SFI Press Researchers Publications Researcher Resources Fellowships Miller Scholarships News + Events News Newsletters Podcasts SFI in the Media Media Center Events Community Journalism Fellowship Education Programs Projects Alumni Complexity Explorer Education FAQ Postdoctoral Research Education Supporters People Researchers Fractal Faculty Staff Miller Scholars Trustees Governance Resident Artists Research Supporters Applied Complexity Office Applied Projects ACtioN Applied Fellows Studios Applied Events Login Give Give Now Ways to Give Contact About About SFI Engage Complex Systems FAQ Campuses Jobs Contact Library Employee Portal Home Events Upcoming Events Current Events Past Events Science Education ACtioN Community Upcoming Events 2026 Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec Clear Date Select Date March 5, 2026 NewsIcons Science Computational Universality of Fungal Sandpile Automata Noyce Conference Room Seminar 12:30 pm – 1:30 pm US Mountain Time March 5, 2026 Speaker:Eric Goles SFI Host:
- Human verdict (justified / false positive / unclear): **Unclear（有争议）** — 研究机构页面提供真实的学术活动信息，但摘录以导航、日期、场地和活动列表为主，缺乏长篇连贯正文。对通用 C4 风格语言建模，拒绝可能合理；若面向科学事件语料，仍可能有用。


## Audit conclusion (excerpt-level, not full-document labels)

- 审计范围：从 Baseline 保留、Strong 删除的 623 篇真实文档中抽取的 5 篇摘录；并未逐一审阅全部 623 篇。
- 定性结果：3 篇基本合理删除，1 篇潜在误删，1 篇存在争议。该比例**不是** Strong Filter 的总体精准率估计。
- 主要发现：重复导航和列表页是有效的过滤目标；但整页级重复 n-gram 指标也可能误伤含有优质段落的网页。
- 项目建议：记录这一误删风险，在 README 中披露限制。若有后续迭代，可先进行导航/页脚正文抽取，再评估结构质量；当前时间约束下不必追加新一轮实验。
- 结论边界：实验只证明数据体积与文本结构发生变化，**不证明** Strong 数据能带来更低的 Paloma perplexity；需要固定模型的训练评估才能检验。
