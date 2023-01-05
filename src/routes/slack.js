const router = require("express").Router();

router.post("/action-endpoint", (req, res) => {
  res.send(req.body.challenge);
});

module.exports = router;
