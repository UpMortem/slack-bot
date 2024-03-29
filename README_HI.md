# Haly AI स्लैक बॉट

एक GPT द्वारा संचालित चैटबॉट जो सांख्यिकीय खोज का उपयोग करके आपके संगठन के बारे में प्रश्नों का उत्तर दे सकता है।

## विशेषताएं

- उपयोगकर्ताओं के प्रश्नों का वास्तविक समय में उत्तर देता है।
- उत्तर उत्पन्न करने के लिए OpenAI API का उपयोग करता है।
- चैट चैनलों में सीधे उत्तर प्रदान करने के लिए स्लैक के साथ एकीकृत होता है।

## स्थापना

1. इस रिपॉजिटरी को क्लोन करें।
2. `pip install -r requirements.txt` के साथ निर्भरताओं को स्थापित करें।
3. आवश्यक वातावरण चर कॉन्फ़िगर करें (विन्यास अनुभाग देखें)।
4. `python main.py` के साथ बॉट चलाएं।

## विन्यास

आपको निम्नलिखित वातावरण चर की आवश्यकता होगी:

- `SLACK_BOT_TOKEN`: आपके स्लैक बॉट का टोकन।
- `SLACK_SIGNING_SECRET`: आपके स्लैक ऐप का हस्ताक्षर रहस्य।
- `OPENAI_API_KEY`: आपकी OpenAI API कुंजी।

## लाइसेंस

यह परियोजना GNU Affero General Public License v3.0 लाइसेंस के तहत लाइसेंस प्राप्त है। अधिक विवरण के लिए [LICENSE](LICENSE) फ़ाइल देखें।
