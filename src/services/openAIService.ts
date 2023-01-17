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

const basePrompt = `I am a highly intelligent salck bot named Haly.
If you ask me a question that is rooted in truth, I will give you the answer.
If you ask me a question that is nonsense, trickery, or has no clear answer, I will respond with "Sorry, I don't know the answer to that."
If you ask me about any weather condition (temperature, wind, etc.), I will answer with a JSON string as this one: '{ "request": "weather", "city": <CITY> }'. Where <CITY> is the city you are asking about, with no abreviations.

User: How is the weather in London, UK?
Haly: { "request": "weather", "city": "London,UK" }
User: Is it warm in SB?
Haly: { "request": "weather", "city": "Santa Barbara,CA" }
`;

const weatherPrompt = (data: string, thread: string) =>
  `You are a Slack bot named Haly. Use the following data to answer the users request:
${data}

${thread}
Haly:.`;

export const runCompletion = async (text, temperature = 0) => {
  console.log({ prompt: text });
  const completion = await openai.createCompletion({
    model: "text-davinci-003",
    prompt: text,
    max_tokens: 1000,
    temperature: temperature,
    stop: ["Haly:"],
  });
  return completion.data.choices[0].text;
};

export const respondToUser = async (fullThread: string) => {
  const prompt = `${basePrompt}
${fullThread}
Haly:`;
  let response = await runCompletion(prompt);
  // Special request to get the weather/time
  console.log({ response });
  const jsonRespose = toJSON(response);
  console.log({ jsonRespose });
  if (jsonRespose) {
    response = await handleSpecialRequest(jsonRespose, fullThread);
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

const handleSpecialRequest = async (
  json: Record<string, string>,
  thread: string
) => {
  if (json.request === "weather") {
    const city = json.city;
    const weather = await getCurrentWeather(city);
    const response = await runCompletion(
      weatherPrompt(JSON.stringify(weather), thread)
    );
    return response;
  }
};
