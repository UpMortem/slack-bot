import replicate
import retry


@retry(delay=3, backoff=2, tries=8)
def replicate_query(prompt):
    output = replicate.run(
        "meta/llama-2-7b:73001d654114dad81ec65da3b834e2f691af1e1526453189b7bf36fb3f32d0f9",
        input={
            "debug": False,
            "top_k": 50,
            "top_p": 0.9,
            "prompt": prompt,
            "temperature": 0.75,
            "max_new_tokens": 500,
            "min_new_tokens": -1
        }
    )
    full_output = ""
    for item in output:
        full_output += str(item)
    return str(full_output)
