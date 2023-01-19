import { respondToUser } from "./../services/openAIService";
import {
  sendMessage,
  getThreadMessages,
  getThreadMessagesWithUsernames,
} from "../services/slackService";
import { getConversationSummary } from "../services/openAIService";
import { Request, Response } from "express";
import { AppMentionPayload } from "seratch-slack-types/events-api";

export const postEvent = async (req: Request, res: Response) => {
  if (req.body.type === "url_verification") {
    res.send(req.body.challenge);
    return;
  }

  const payload = req.body as AppMentionPayload;
  // console.log(payload);

  const { channel, text, thread_ts, ts } = payload.event;
  const botId = findBotId(payload);
  if (!botId) {
    console.error("botId not found");
    res.sendStatus(500);
    return;
  }

  try {
    res.sendStatus(200);
    let threadToReply = thread_ts;
    // Reply in a new thread if the message is not in a thread
    if (thread_ts !== ts) {
      threadToReply = ts;
    }
    const userMessage = text.replace(`<@${botId}>`, "").trim();
    let messages = [`USER:${userMessage}`];
    if (thread_ts) {
      messages =
        (await getThreadMessagesWithUsernames(channel, thread_ts, botId)) ||
        messages;
    }
    console.log({ messages });
    const response = await respondToUser(messages);

    await sendMessage(channel, threadToReply, response);
    return;
  } catch (error) {
    console.error(error);
  }
};

export const postCommand = async (req: Request, res: Response) => {
  const command = req.params.commandName;

  try {
    switch (command) {
      case "test": {
        res.status(200).send("This is a test command");
      }
      default: {
        const error = `Sorry, I don't know how to handle the command '${command}'`;
        res.status(200).send(error);
      }
    }
  } catch (error) {
    console.error(error);
    res
      .status(500)
      .send({ error: "An error occured while processing the request" });
  }
};

const getThreadSummary = async (channelId, threadTs) => {
  const threadMessages = await getThreadMessages(channelId, threadTs);
  const summary = await getConversationSummary(threadMessages);

  return summary;
};

const findBotId = (payload: AppMentionPayload) => {
  const bot = payload.authorizations.find((auth) => auth.is_bot);
  return bot.user_id;
};
