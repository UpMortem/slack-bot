const { sendMessage, getThreadMessages } = require("../../lib/slack/index");
const { runCompletion } = require("../../lib/openai/index")

module.exports.postEvent = async (req, res) => {
  // console.log(req.body)
  if (req.body.type === "url_verification") {
    res.send(req.body.challenge);
    return;
  }

  const { channel, text, thread_ts } = req.body.event;

  try {
    const basePrompt = "The following is a conversation between a Slack user and a Slack bot named Haly. Haly can do things like answer questions, create a thread summary, schedule a meeting."
    const userMessage = "USER: " + text.replace("<@U04HV520KQE>","").trim();
    let prompt = basePrompt + userMessage + "\nHaly: ";
    if(prompt.indexOf("threadSummary") > -1) {
      let threadMessages = await getThreadMessages(channel, thread_ts);
      threadMessages = threadMessages.messages.filter(m => m.bot_id == null).map(message => { return message.text }).join("\n")
      // console.log(threadMessages)
      prompt = "This is a conversation between multiple users, each username starts with a '<' character and ends with '>'. Make a summary of the conversation:\n" + threadMessages + "\n\nSUMMARY:"
    }
    const response = await runCompletion(prompt);
    await sendMessage(channel, thread_ts, response);
  } catch (error) {
    console.error(error);
  }

  res.send(req.body.challenge);
};
