import express from "express";
require("dotenv").config();
import cookieParser from "cookie-parser";
import logger from "morgan";
import { slackRouter } from "./routes/slackRouter"

// Init app
const app = express();

// Middlewares
app.use(logger("dev"));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());

// Routes
app.use("/slack", slackRouter);

export default app;
