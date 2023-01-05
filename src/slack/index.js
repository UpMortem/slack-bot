const { App } = require("@slack/bolt");

// Initializes your app
const app = new App({
  token: process.env.SLACK_BOT_TOKEN,
  signingSecret: process.env.SLACK_SIGNING_SECRET,
  appToken: process.env.SLACK_APP_TOKEN,
  socketMode: true,
});

// subscribe to 'app_mention' event in your App config
// need app_mentions:read and chat:write scopes
// slack bolt recieves app_mention event and responds with a message
app.event("app_mention", async ({ event, say }) => {
  console.log("daskfjsdlkfhkjfghsdfkjg");
  console.log(event);
  await say(`Hey there <@${event.user}>!`);

  try {
    await say({
      blocks: [
        {
          type: "section",
          text: {
            type: "mrkdwn",
            text: `Thanks for the mention <@${event.user}>! Here's a button`,
          },
          accessory: {
            type: "button",
            text: {
              type: "plain_text",
              text: "Button",
              emoji: true,
            },
            value: "click_me_123",
            action_id: "first_button",
          },
        },
      ],
    });
  } catch (error) {
    console.error(error);
  }
});

// Start your app
(async () => {
  // Start the app
  await app.start(3001);
  console.log("⚡️ Haly is running MFers!");
})();

module.exports = app;
