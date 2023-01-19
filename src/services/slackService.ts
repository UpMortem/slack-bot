import { App } from "@slack/bolt";

const app = new App({
  token: process.env.SLACK_BOT_TOKEN,
  signingSecret: process.env.SLACK_SIGNING_SECRET,
});

(async () => {
  await app.start(3001);
  console.log("⚡️ Haly is running!");
})();

//Doing this locally until we have a DB / redis
const usersMap = new Map<string, string>();

// Publish a message to a channel
// need chat:write scope
export const sendMessage = async (
  channel: string,
  threadTs: string,
  text: string
) => {
  try {
    await app.client.chat.postMessage({
      token: process.env.SLACK_BOT_TOKEN,
      channel,
      text,
      thread_ts: threadTs,
    });
  } catch (error) {
    console.error(error);
  }
};

export const getThreadMessages = async (channel: string, threadTs: string) => {
  try {
    const result = await app.client.conversations.replies({
      token: process.env.SLACK_BOT_TOKEN,
      channel,
      ts: threadTs,
      include_all_metadata: true,
    });
    return result.messages;
  } catch (error) {
    console.error(error);
  }
};

export const getThreadMessagesWithUsernames = async (
  channel: string,
  threadTs: string,
  botId: string
) => {
  const threadMessages = await getThreadMessages(channel, threadTs);
  const messagesArr = await Promise.all(
    threadMessages.map(async (m) => {
      const username = await getUsername(m.user);
      if (m.bot_id) {
        return `Haly: ${m.text}`;
      } else {
        return `${username}: ${m.text.replace(`<@${botId}>`, "").trim()}`;
      }
    })
  );
  return messagesArr;
};

// Call the users.info method using the WebClient
export const findUserById = async (userId: string) => {
  try {
    const result = await app.client.users.info({
      user: userId,
    });

    return result;
  } catch (error) {
    console.error(error);
  }
};

export const getUsername = async (userId: string) => {
  if (!usersMap.get(userId)) {
    const user = await findUserById(userId);
    usersMap.set(userId, user.user.name);
  }
  return usersMap.get(userId);
};

export const command = (text) => {
  return `You said: ${text}`;
};
