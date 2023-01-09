import { sendMessage, getThreadMessages } from "../../lib/slack/slack"
import { runCompletion } from "../../lib/openai/openAI"
import { Request, Response } from "express";
import { AppMentionPayload } from 'seratch-slack-types/events-api';


export const postEvent = async (req: Request, res: Response) => {

  if (req.body.type === "url_verification") {
    res.send(req.body.challenge);
    return;
  }

  const payload = req.body as AppMentionPayload;

  const { channel, text, thread_ts } = payload.event;
  const botId = findBotId(payload);
  if (!botId) {
    console.error("botId not found");
    res.sendStatus(500);
    return;
  }

  try {
    const basePrompt = "The following is a conversation between a Slack user and a Slack bot named Haly. Haly can do things like answer questions, create a thread summary, schedule a meeting."
    const userMessage = "USER: " + text.replace(`<@${botId}>`,"").trim();
    let prompt = basePrompt + userMessage + "\nHaly: ";
    if(prompt.indexOf("threadSummary") > -1) {
      prompt = await getThreadSummaryPrompt(channel, thread_ts) || "";
    }
    if(prompt) {
      const response = await runCompletion(prompt) || "";
      await sendMessage(channel, thread_ts, response);
    }
    res.sendStatus(200)
  } catch (error) {
    console.error(error);
    res.status(500).send({ error: "An error occured while processing the request" });
  }

  res.send(req.body.challenge);
};

const getThreadSummaryPrompt = async (channel: string, threadTs: string) => {
  const threadMessages = await getThreadMessages(channel, threadTs);
  if (!threadMessages || !threadMessages.messages || threadMessages.messages.length === 0) {
    const invalidThreadMessage = "Sorry, I couldn't find the thread you were looking for."
    await sendMessage(channel, threadTs, invalidThreadMessage);
    return;
  }

  const filteredThreadMessages = threadMessages.messages
    .filter((m) => m.bot_id === null)
    .map((message) => message.text)
    .join("\n");

  return `This is a conversation between multiple users, each username starts with a '<' character and ends with '>'. Make a summary of the conversation:\n${filteredThreadMessages}\n\nSUMMARY:`;
};

const findBotId = (payload: AppMentionPayload) => {
  const bot = payload.authorizations.find((auth) => auth.is_bot);
  return bot.user_id;
}
