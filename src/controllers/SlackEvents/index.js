const { sendMessage } = require("../../lib/slack/index");
const { runCompletion } = require("../../lib/openai/index")

module.exports.postEvent = async (req, res) => {
  if (req.body.type === "url_verification") {
    res.send(req.body.challenge);
    return;
  }

  const { channel, type, test, user, ts, blocks, team, text } = req.body.event;

  try {
    let prompt = "The following is a conversation between a Slack user and a Slack bot named Haly. Haly can do things like answer questions, create a thread summary, schedule a meeting."
    const userMessage = text.replace("<@U04HV520KQE>","USER: ").trim();
    prompt = prompt + userMessage + "\nHaly: ";
    const response = await runCompletion(prompt);
    await sendMessage(channel, response);
  } catch (error) {
    console.error(error);
  }

  res.send(req.body.challenge);
};
