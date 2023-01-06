const router = require("express").Router();

const { postEvent } = require("../controllers/SlackEvents");
const { postCommand } = require("../controllers/SlackSlashCommands");

router.post("/events", postEvent);
router.post("/haly", postCommand);

module.exports = router;
