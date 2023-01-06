const { App } = require("@slack/bolt");

// Initializes your app
const app = new App({
  token: process.env.SLACK_BOT_TOKEN,
  signingSecret: process.env.SLACK_SIGNING_SECRET,
  // appToken: process.env.SLACK_APP_TOKEN,
  // socketMode: true,
});

// Start your app
(async () => {
  // Start the app
  await app.start(3001);
  console.log("⚡️ Haly is running!");
})();

// Publish a message to a channel
// need chat:write scope
const sendMessage = async (channel, text) => {
  try {
    const result = await app.client.chat.postMessage({
      token: process.env.SLACK_BOT_TOKEN,
      channel,
      text,
    });
    return result;
  } catch (error) {
    console.error(error);
  }
};

// Call the users.info method using the WebClient
const findUserById = async (userId) => {
  try {
    const result = await app.client.users.info({
      user: userId,
    });

    return result;
  } catch (error) {
    console.error(error);
  }
};

const command = (text) => {
  return `You said: ${text}`;
};

module.exports = { findUserById, sendMessage, command };
