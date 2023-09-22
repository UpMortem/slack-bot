# Haly AI - 你的友好聊天机器人伙伴
![Haly](images/github_readme.png)
## 欢迎来到Haly！
**Haly**在这里，将彻底改变你的沟通和寻求信息的方式。Haly不仅仅是一个聊天机器人，它是你在数字世界中的终极伙伴。

## Haly能做什么？
Haly是一切的专家 - 从提供答案和解释，到生成想法和协助完成各种任务。以下只是Haly可以帮助你的一些事情：
- **语义搜索（SmartSearch）**：向你的组织提问，Haly会根据以前的公共频道消息和主题专家告诉你答案。
- **电子邮件，博客和营销内容**：需要写作帮助？Haly随时为你服务，提供建议，编辑，甚至帮助翻译。
- **信息和研究**：对特定主题感到好奇？Haly可以为你提供准确的信息，并进行深入的研究以满足你的好奇心。
- **问题解决和故障排除**：遇到困难的问题？Haly喜欢挑战，随时准备帮助你找到最佳解决方案。
- **食谱和健康与健身**：寻找美味的食谱或需要一些保持健康的建议？Haly为你提供了各种建议和信息。
- **旅行规划**：需要帮助规划旅行？Haly可以帮助你找到最佳目的地，预订住宿，甚至推荐当地景点。

## 为什么选择Haly？
Haly不仅仅是另一个聊天机器人 - 它是一个真正关心你需求的个人助手。以下是你应该试试Haly的原因：
- **友好和引人入胜**：Haly的热情和亲切的个性使每次对话都变得愉快。你会觉得你正在和一个好朋友聊天。
- **万事通**：无论你需要帮助写作，研究，解决问题，还是其他任何事情，Haly都有知识和专业知识来帮助你。
- **始终可用**：Haly全天候为你服务，随时准备提供帮助。告别等待人工帮助。
- **高效和可靠**：Haly快速，准确，可靠。你可以信任Haly每次都能提供高质量的结果。

## 今天就开始使用Haly吧！
准备体验Haly的力量了吗？加入日益增长的Haly用户社区，看看这个友好的聊天机器人如何提升你的数字生活。只需访问我们的网站https://haly.ai或按照此README中的说明将Haly集成到Slack中，让对话开始吧！
注意：Haly正在不断学习和改进，所以不要犹豫提供反馈和建议。我们一起可以让Haly变得更好！

## 免费试用
https://haly.ai

## 开发设置
### Prereqs
1. 你必须有一个Slack组织，你或管理员可以批准新的应用程序。
2. 能够在Windows，Mac或Linux终端中克隆repo并运行命令的能力。
3. 安装[python](https://www.python.org/downloads/)和[pip](https://pip.pypa.io/en/stable/installation/)。

### 创建你的Slack机器人：
1. 转到https://api.slack.com/apps并点击"Create New App"绿色按钮。选择"From an app manifest"选项。
2. 如果需要，从下拉菜单中选择工作区，并在清单中粘贴以下内容。点击下一步按钮。查看OAuth和Features选项卡，然后点击创建。
3. 选择左侧导航栏中的`Basic information`选项卡，向下滚动并确保保存"Signing Secret"以备后用。
4. 向下滚动，使用[Haly Profile Image](https://github.com/UpMortem/slack-bot/assets/469387/490a891e-379e-4e5c-9f31-4699dce78e01)作为她的应用图标，或者如果你愿意，选择你自己的。
5. 接下来，选择左侧导航栏中的`OAuth & Permissions`选项卡，在`OAuth Tokens for Your Workspace`部分，点击`Install to Workspace`并按照那里的说明操作。
6. 安装后，你会找到一个Bot用户OAuth令牌。保存以备后用。

### 配置你的项目
- 在终端中克隆项目。[如果你不知道如何做，请参阅官方文档](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository)。
- cd到slack-bot目录
- 创建一个新的.env文件。你可以使用touch命令（touch .env）创建文件。然后使用你最喜欢的编辑器编辑它。
- 如果你只想为你自己的工作区使用Haly，你可以在独立模式下使用它。在你的.env文件中放入以下内容：
- 更新SLACK_BOT_TOKEN（OAuth令牌），SLACK_SIGNING_SECRET，OPENAI_API_KEY（[点击这里了解如何从OpenAI获取API密钥](https://www.maisieai.com/help/how-to-get-an-openai-api-key-for-chatgpt)），和SLACK_USER_ID（[点击这里了解如何获取你的Slack用户ID](https://www.workast.com/help/article/how-to-find-a-slack-user-id/)）
- 安装venv `python3 -m pip install virtualenv`
- 在slack-bot项目的根目录下使用`python3 -m virtualenv -p python3 myvenv`创建一个venv
- 要启用虚拟环境，在Linux/MacOS上运行`source myvenv/bin/activate`，在Windows上运行`myvenv\Scripts\activate` - 这将打开一个进入虚拟环境的终端。
- 在上述终端中键入`where python`验证你的python是否被隔离。它应该显示项目内的python路径。
- 在同一终端中运行`pip install -r "requirements.txt"`安装依赖项
- 在同一终端中运行`flask --debug run`启动开发服务器

如果你在运行flask时使用--debug标志，每当源代码更改时，应用程序都会重建。

## Ngrok设置
你需要ngrok来本地测试Bot
- 转到https://ngrok.com/download并按照说明安装ngrok
- 打开一个终端并运行`ngrok http localhost:8080`
- 复制以*https*开头的转发url，然后转到api.slack.com中的你的应用设置。转到'Event subscriptions'。在Request URL输入框中输入你的转发url + /slack/events。
- 订阅必要的bot事件

## 发布
- 每次你推送一个匹配`^v.*$`的git标签时，云构建触发器都会运行
