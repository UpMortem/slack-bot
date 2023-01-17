import { Configuration, OpenAIApi } from "openai";
import { getCurrentWeather } from "./weatherAPIService";

const configuration = new Configuration({
  apiKey: process.env.OPENAI_API_KEY,
});
const openai = new OpenAIApi(configuration);

type openAiModel =
  | "text-curie-001"
  | "text-davinci-003"
  | "text-babbage-001"
  | "text-ada-001";

const basePrompt = `You are a Slack bot named Haly. You are having a conversation with other users. If a user wants to know the weather, you should respond with only a valid JSON string and nothing else.
  Example: { "request": "weather", "city": "<city_name>" }
  <city_name> is the name of the requested city, and only the city (no country, no state, no province, etc), and no abreviations.
  remember to use double quotes for the JSON keys and values.`;

const weatherPrompt = (data: string) =>
  `Write a friendly sentence about current weather using the following JSON data:
  ${data}`;

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
  const prompt = `${basePrompt}\n\n${text}\nHALY:`;
  let response = await runCompletion(prompt);
  // Special request to get the weather/time
  console.log({ response });
  const jsonRespose = toJSON(response);
  console.log({ jsonRespose });
  if (jsonRespose) {
    response = await handleSpecialRequest(jsonRespose);
  }
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

export const toJSON = (str: string) => {
  try {
    const json = JSON.parse(str.trim());
    return json;
  } catch (e) {
    return false;
  }
};

const handleSpecialRequest = async (json) => {
  if (json.request === "weather") {
    const city = json.city;
    const weather = await getCurrentWeather(city);
    const response = await runCompletion(
      weatherPrompt(JSON.stringify(weather))
    );
    return response;
  }
};
