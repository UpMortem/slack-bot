const express = require("express");
require("dotenv").config();
const path = require("path");
const cookieParser = require("cookie-parser");
const logger = require("morgan");

// Slack websocket
require("./src/lib/slack/index");

// OpenAI
// require("./src/lib/openai/index");

// Init app
const app = express();

// Middlewares
app.use(logger("dev"));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());

// Routes
app.use("/", require("./src/routes/index"));

module.exports = app;
