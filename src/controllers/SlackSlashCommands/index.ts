import { Request, Response } from "express";
import { command } from "../../lib/slack/slack";

export const postCommand = async (req: Request, res: Response) => {
  const result = command(req.body.text);
  res.send(result);
};
