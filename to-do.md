- Move SD prompt making out of the triage class

- Increase stories in memory.
Have all generated stories in a dict.
reference this every time we need to generate a story.
Save the dict to cloud when we end the game
summarize each story after they have taken place.
keep the most recent generated story uncompressed.

- Improve SD prompting.
We are still having issues with reaching the token limit.
We could have another LLM class to handle the SD prompt.
Make it explicit and learn it how to write proper juggernaut prompts.

- Loras?
We need to shorten the fuck out of the prompt.
Hard cap on 50 tokens to leave place for loras.
Triage identifies if the scene should contain a lora.
Boolean value is sent to SD agent.
Sd agent concatenates the prompt with the lora calling phrase and a hardcoedd weight.
Put the loras at the start of the prompt to avoid truncating them from the prompt.

- Make dice rolls happen slightly more frequent (dont use ai for this, hes is just gonna fuck it up)

