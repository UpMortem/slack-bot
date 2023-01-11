import { App } from "@slack/bolt"

const app = new App({
  token: process.env.SLACK_BOT_TOKEN,
  signingSecret: process.env.SLACK_SIGNING_SECRET,
});

(async () => {
  await app.start(3001);
  console.log("⚡️ Haly is running!");
})();

// Publish a message to a channel
// need chat:write scope
export const sendMessage = async (channel: string, threadTs: string, text: string) => {
  try {
    const result = await app.client.chat.postMessage({
      token: process.env.SLACK_BOT_TOKEN,
      channel,
      text,
      thread_ts: threadTs,
    });
    return result;
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
      include_all_metadata: true
    });
    return result;
  } catch (error) {
    console.error(error);
  }
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

export const command = (text) => {
  return `You said: ${text}`;
};
