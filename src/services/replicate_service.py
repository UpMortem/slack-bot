import logging
import replicate

def replicate_chat(system_prompt, messages):
	try:
		output = replicate.run(
			"meta/llama-2-70b-chat:02e509c789964a7ea8736978a43525956ef40397be9033abf9fd2badfe68c9e3",
			input={
				"debug": False,
				"top_k": 50,
				"top_p": 1,
				"prompt": '\n'.join(messages),
				"temperature": 0.5,
				"system_prompt": system_prompt,
				"max_new_tokens": 500,
				"min_new_tokens": -1
			}
		)
		full_output = ""
		for item in output:
			full_output += str(item)
		return str(full_output)
	except Exception as exception:	
		logging.error(f"Error in chat completion (replicate): {exception}", exc_info=True)
		return "Something went wrong. Please try again later."