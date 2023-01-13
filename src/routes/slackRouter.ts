import { Router } from "express";

import { postEvent, postCommand } from "../controllers/slackController";

export const slackRouter: Router = Router();

slackRouter.post("/events", postEvent);
slackRouter.post("/command/:commandName", postCommand);
