const { Configuration, OpenAIApi } = require("openai");

(async () => {
  const configuration = new Configuration({
    organization: "org-eZs5fyx4D8tB4TDuGoGvcFot",
    apiKey: process.env.OPENAI_API_KEY,
  });
  const openai = new OpenAIApi(configuration);

  const completion = await openai.createCompletion({
    model: "text-davinci-002",
    prompt: "Hello world",
  });
  console.log(completion.data);
  console.log(completion.data.choices[0].text);
})();
