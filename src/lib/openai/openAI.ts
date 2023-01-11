import { Configuration, OpenAIApi } from "openai"

const configuration = new Configuration({
  apiKey: process.env.OPENAI_API_KEY,
});
const openai = new OpenAIApi(configuration);

type openAiModel = "text-curie-001" | "text-davinci-003" | "text-babbage-001" | "text-ada-001"

export const runCompletion = async (text) => {
  const completion = await openai.createCompletion({
    model: "text-davinci-003",
    prompt: text,
    max_tokens: 1000,
    temperature: 0.7
  });
  return completion.data.choices[0].text;
}
