const router = require("express").Router();

router.use("/slack", require("./slack"));
router.use("/", (req, res) => {
  res.send("Hello World");
});

module.exports = router;
