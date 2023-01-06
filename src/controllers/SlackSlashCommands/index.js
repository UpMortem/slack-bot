const { command } = require("../../lib/slack/index");

module.exports.postCommand = async (req, res) => {
  const result = command(req.body.text);
  res.send(result);
};
