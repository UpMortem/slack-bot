const router = require("express").Router();

const { sendMessage, command } = require("../slack");

router.post("/events", async (req, res) => {
  const { channel, type, test, user, ts, blocks, team } = req.body.event;

  // console.log(req.body);
  // console.log(req.body.event);
  // console.log(blocks);

  try {
    await sendMessage(channel, `Hi <@${user}> ! This is Haly!`);
  } catch (error) {
    console.error(error);
  }

  res.send(req.body.challenge);
});

router.post("/haly", async (req, res) => {
  const result = command(req.body.text);
  res.send(result);
});

module.exports = router;
