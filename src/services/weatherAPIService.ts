import axios from "axios";

const apiKey = process.env.WEATHER_API_KEY;
const baseUrl = "http://api.weatherapi.com/v1/";
const currentWeatherUrl = (city: string) =>
  `${baseUrl}current.json?key=${apiKey}&q=${city}`;

export const getCurrentWeather = async (city: string) => {
  const response = await axios.get(currentWeatherUrl(city));
  return response.data;
};
