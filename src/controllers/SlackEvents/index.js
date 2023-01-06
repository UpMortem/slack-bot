const { sendMessage } = require("../../lib/slack/index");

module.exports.postEvent = async (req, res) => {
  if (req.body.type === "url_verification") {
    res.send(req.body.challenge);
    return;
  }

  const { channel, type, test, user, ts, blocks, team } = req.body.event;

  try {
    await sendMessage(channel, `Hi <@${user}> ! This is Haly!`);
  } catch (error) {
    console.error(error);
  }

  res.send(req.body.challenge);
};
