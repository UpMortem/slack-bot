import { Configuration, OpenAIApi } from "openai";

const configuration = new Configuration({
  apiKey: process.env.OPENAI_API_KEY,
});
const openai = new OpenAIApi(configuration);

type openAiModel =
  | "text-curie-001"
  | "text-davinci-003"
  | "text-babbage-001"
  | "text-ada-001";

const basePrompt =
  "You are a Slack bot named Haly. You are having a conversation with a user.\n\n";

export const runCompletion = async (text) => {
  const completion = await openai.createCompletion({
    model: "text-davinci-003",
    prompt: text,
    max_tokens: 1000,
    temperature: 0.7,
  });
  return completion.data.choices[0].text;
};

export const respondToUser = async (text) => {
  const prompt = `${basePrompt}${text}\nHaly:`;
  const response = await runCompletion(prompt);
  return response;
};

export const getConversationSummary = async (threadMessages) => {
  const filteredThreadMessages = threadMessages
    .filter((m) => m.bot_id === null)
    .map((message) => message.text)
    .join("\n");

  const summary = await runCompletion(
    `This is a conversation between multiple users, each username starts with a '<' character and ends with '>'. Make a summary of the conversation:\n${filteredThreadMessages}\n\nSUMMARY:`
  );

  return summary;
};
