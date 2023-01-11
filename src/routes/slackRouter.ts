import { Router } from 'express';

import { postEvent } from "../controllers/SlackEvents/slackEvents";
import { postCommand } from "../controllers/SlackSlashCommands";

export const slackRouter: Router = Router();

slackRouter.post("/events", postEvent);
slackRouter.post("/haly", postCommand);
